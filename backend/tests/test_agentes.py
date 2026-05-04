import pytest
from pydantic_ai.models.test import TestModel

from app.agents.financeiro import financeiro_agent
from app.agents.tecnico import tecnico_agent
from app.agents.orchestrator import orchestrator_agent


@pytest.mark.asyncio
async def test_tecnico_retorna_resposta_valida(deps_mock):
    """Agente técnico retorna estrutura RespostaAgente completa."""
    with tecnico_agent.override(model=TestModel()):
        result = await tecnico_agent.run(
            "Não consigo fazer login",
            deps=deps_mock,
        )

    assert result.output.mensagem
    assert result.output.sentimento_cliente in [
        "positivo", "neutro", "negativo", "frustrado"
    ]
    assert isinstance(result.output.precisa_escalar_humano, bool)
    assert isinstance(result.output.tags, list)


@pytest.mark.asyncio
async def test_financeiro_retorna_resposta_valida(deps_mock):
    """Agente financeiro retorna estrutura RespostaAgente completa."""
    with financeiro_agent.override(model=TestModel()):
        result = await financeiro_agent.run(
            "Quero ver minha última fatura",
            deps=deps_mock,
        )

    assert result.output.mensagem
    assert result.output.sentimento_cliente in [
        "positivo", "neutro", "negativo", "frustrado"
    ]
    assert isinstance(result.output.precisa_escalar_humano, bool)


@pytest.mark.asyncio
async def test_orchestrator_retorna_estrutura_valida(deps_mock):
    """Orchestrator produz RespostaAgente válida com todos os campos obrigatórios.

    Nota: TestModel gera respostas sintéticas sem chamar tools reais.
    Para testar delegação de verdade, use um modelo real com VCR ou mocking
    da tool de delegação.
    """
    with orchestrator_agent.override(model=TestModel()):
        result = await orchestrator_agent.run(
            "Quero ver minhas faturas",
            deps=deps_mock,
        )

    assert result.output.mensagem
    assert result.output.sentimento_cliente in [
        "positivo", "neutro", "negativo", "frustrado"
    ]
    assert isinstance(result.output.precisa_escalar_humano, bool)
    assert isinstance(result.output.tags, list)
