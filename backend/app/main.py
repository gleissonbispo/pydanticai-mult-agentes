import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.db import Base
from app.observability.logfire_setup import setup_logfire
from app.routes import chat
from app.services.database import engine
from app.services.session import SessionService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Observabilidade primeiro — assim captura tudo que vem a seguir
    setup_logfire(app)

    # 2. Cria tabelas se não existirem (safety net para dev sem Docker)
    #    Em produção o init_db.sql já fez isso, mas create_all é idempotente
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 3. SessionService como singleton: uma conexão Redis para toda a app
    app.state.session_service = SessionService()

    logger.info("Aplicação iniciada em modo '%s'", settings.app_env)
    yield

    # Cleanup ordenado no shutdown
    await app.state.session_service.close()
    await engine.dispose()
    logger.info("Aplicação encerrada")


app = FastAPI(
    title="Atendimento Multi-Agente",
    version="0.1.0",
    lifespan=lifespan,
)

# A5 FIX: CORS necessário para o frontend Streamlit chamar o backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root():
    return {"servico": "atendimento-multiagente", "status": "online"}


@app.get("/health")
async def health():
    """Health check profundo — verifica conectividade com DB e Redis.

    Retorna 200 se tudo ok, 200 com status 'degraded' se algum serviço falhou
    (mantemos 200 para não derrubar o load balancer em degradação parcial).
    """
    from sqlalchemy import text

    result: dict = {"status": "ok", "version": "0.1.0", "checks": {}}

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        result["checks"]["database"] = "ok"
    except Exception as e:
        result["checks"]["database"] = f"error: {e}"
        result["status"] = "degraded"

    try:
        await app.state.session_service.redis.ping()
        result["checks"]["redis"] = "ok"
    except Exception as e:
        result["checks"]["redis"] = f"error: {e}"
        result["status"] = "degraded"

    return result
