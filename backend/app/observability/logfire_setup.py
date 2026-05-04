import logging

import logfire

from app.config import settings

logger = logging.getLogger(__name__)


def setup_logfire(app=None) -> None:
    """Configura Logfire com auto-instrumentação de todas as camadas.

    A7 FIX: as 4 chamadas de instrument estavam comentadas, tornando o Logfire
    inútil. Agora instrumenta FastAPI, SQLAlchemy, Redis e Pydantic
    automaticamente — cada query SQL, chamada Redis e request HTTP aparecem
    no dashboard do Logfire sem adicionar código nas funções de negócio.
    """
    if not settings.logfire_token.get_secret_value():
        logger.warning("LOGFIRE_TOKEN não configurado — observabilidade desativada")
        return

    logfire.configure(
        token=settings.logfire_token.get_secret_value(),
        service_name="atendimento-multiagente",
        environment=settings.app_env,
    )

    # instrument_pydantic() removido: captura TODOS os modelos Pydantic, incluindo
    # os internos do SDK OpenAI (_ChatCompletion, nullable...), gerando ruído excessivo
    # nos logs. O PydanticAI já instrumenta as chamadas ao LLM via sua própria integração.
    logfire.instrument_sqlalchemy()
    logfire.instrument_redis()
    if app is not None:
        logfire.instrument_fastapi(app)

    logfire.info(
        "Logfire ativo — service={service} env={env}", 
        service="atendimento-multiagente", 
        env=settings.app_env
    )
