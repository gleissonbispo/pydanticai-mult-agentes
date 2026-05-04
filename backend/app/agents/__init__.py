from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis


@dataclass
class AgentDeps:
    """Dependências injetadas em todos os agentes."""
    db: AsyncSession
    redis: Redis
    cliente_id: str
    sessao_id: str