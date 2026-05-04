import asyncio
import logging

from pydantic import ValidationError
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agents import AgentDeps
from app.agents.orchestrator import orchestrator_agent
from app.guardrails import detectar_injecao_prompt, validar_cliente_id
from app.models.schemas import MensagemWS
from app.services.database import get_db
from app.services.session import SessionService

logger = logging.getLogger(__name__)
router = APIRouter()

# Velocidade do efeito typewriter: ~20 palavras/segundo
_CHUNK_DELAY = 0.05


def _montar_prompt_com_historico(texto: str, historico: list[dict]) -> str:
    """Prepend das últimas 3 trocas ao prompt atual para dar contexto ao agente.

    Por que aqui e não dentro do agente?
    Porque o orquestrador já recebe o texto pronto. Formatar o contexto
    no handler mantém os agentes agnósticos ao mecanismo de sessão.
    """
    if not historico:
        return texto

    linhas = ["Histórico recente da conversa:"]
    for troca in historico[-3:]:  # últimas 3 trocas
        linhas.append(f"  Cliente: {troca['user']}")
        linhas.append(f"  Atendente: {troca['agent']}")

    linhas.append(f"\nNova mensagem: {texto}")
    return "\n".join(linhas)


async def _enviar_streaming(websocket: WebSocket, mensagem: str) -> None:
    """Envia a resposta palavra a palavra, criando efeito typewriter.

    Por que não streaming real de tokens do LLM?
    PydanticAI com output_type estruturado (RespostaAgente) instrui o LLM
    a retornar JSON. Os tokens streamados seriam JSON fragmentado, não texto
    legível. A solução limpa é: obter o output completo e entregar a mensagem
    progressivamente. Streaming real de tokens requer separar output_type da
    camada de resposta ao usuário — está no roadmap (v2).
    """
    palavras = mensagem.split(" ")
    for i, palavra in enumerate(palavras):
        sufixo = " " if i < len(palavras) - 1 else ""
        await websocket.send_json({"tipo": "chunk", "conteudo": palavra + sufixo})
        await asyncio.sleep(_CHUNK_DELAY)


@router.websocket("/ws/chat/{cliente_id}")
async def chat_websocket(websocket: WebSocket, cliente_id: str):
    """Endpoint WebSocket para chat em tempo real com suporte a histórico."""
    await websocket.accept()

    if not validar_cliente_id(cliente_id):
        await websocket.send_json({"tipo": "erro", "mensagem": "ID de cliente inválido"})
        await websocket.close(1008)
        return

    session_service: SessionService = websocket.app.state.session_service

    try:
        sessao_id = await session_service.criar_ou_recuperar_sessao(cliente_id)
        await websocket.send_json({
            "tipo": "sessao_iniciada",
            "sessao_id": sessao_id,
        })

        async for raw in websocket.iter_text():
            try:
                msg = MensagemWS.model_validate_json(raw)
            except (ValidationError, ValueError):
                await websocket.send_json({
                    "tipo": "erro",
                    "mensagem": 'Formato inválido. Esperado: {"texto": "..."}',
                })
                continue

            if detectar_injecao_prompt(msg.texto):
                await websocket.send_json({
                    "tipo": "erro",
                    "mensagem": "Mensagem bloqueada pelo sistema de segurança",
                })
                continue

            try:
                async with get_db() as db:
                    deps = AgentDeps(
                        db=db,
                        redis=session_service.redis,
                        cliente_id=cliente_id,
                        sessao_id=sessao_id,
                    )

                    historico = await session_service.get_historico(sessao_id)
                    prompt = _montar_prompt_com_historico(msg.texto, historico)

                    result = await orchestrator_agent.run(prompt, deps=deps)
                    final = result.output

                    # Persiste antes de enviar — garante que histórico está salvo
                    # mesmo se a conexão cair durante o streaming
                    await session_service.adicionar_mensagem(
                        sessao_id=sessao_id,
                        mensagem_usuario=msg.texto,
                        resposta_agente=final.mensagem,
                    )

                    await _enviar_streaming(websocket, final.mensagem)

                    await websocket.send_json({
                        "tipo": "final",
                        "resposta": final.model_dump(mode="json"),
                    })

            except Exception:
                logger.exception("Erro ao processar mensagem do cliente '%s'", cliente_id)
                await websocket.send_json({
                    "tipo": "erro",
                    "mensagem": "Erro interno ao processar sua mensagem. Tente novamente.",
                })

    except WebSocketDisconnect:
        logger.info("Cliente '%s' desconectou", cliente_id)
