import json
import uuid

from redis.asyncio import Redis

from app.config import settings

_SESSION_TTL = 3600  # segundos — 1 hora de inatividade


class SessionService:
    """Gerencia sessões de conversa no Redis."""

    def __init__(self):
        self.redis: Redis = Redis.from_url(
            settings.redis_url.get_secret_value(),
            decode_responses=True,
        )

    async def criar_ou_recuperar_sessao(self, cliente_id: str) -> str:
        """Retorna o ID da sessão ativa do cliente, criando se necessário.

        M2 FIX: renova o TTL a cada acesso — impede que sessões expirem
        durante conversas ativas. Antes o TTL só era definido na criação.
        """
        chave = f"sessao_ativa:{cliente_id}"
        sessao_id = await self.redis.get(chave)
        if not sessao_id:
            sessao_id = str(uuid.uuid4())
        # SET com EX sempre: cria ou renova o TTL
        await self.redis.set(chave, sessao_id, ex=_SESSION_TTL)
        return sessao_id

    async def adicionar_mensagem(
        self,
        sessao_id: str,
        mensagem_usuario: str,
        resposta_agente: str,
    ) -> None:
        """Adiciona um par (pergunta, resposta) ao histórico."""
        chave = f"historico:{sessao_id}"
        item = json.dumps({"user": mensagem_usuario, "agent": resposta_agente})
        await self.redis.rpush(chave, item)
        await self.redis.ltrim(chave, -20, -1)  # mantém últimas 20 trocas
        await self.redis.expire(chave, _SESSION_TTL)

    async def get_historico(self, sessao_id: str) -> list[dict[str, str]]:
        """Retorna o histórico da sessão."""
        chave = f"historico:{sessao_id}"
        itens = await self.redis.lrange(chave, 0, -1)
        return [json.loads(item) for item in itens]

    async def limpar_sessao(self, sessao_id: str) -> None:
        """Apaga o histórico de uma sessão."""
        await self.redis.delete(f"historico:{sessao_id}")

    async def close(self) -> None:
        """Fecha a conexão com o Redis."""
        await self.redis.aclose()
