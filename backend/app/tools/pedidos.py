from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import PedidoDB
from app.models.schemas import Pedido


async def buscar_pedido_por_id(
    db: AsyncSession,
    pedido_id: str,
    cliente_id: str,
) -> Pedido | None:
    """Busca um pedido garantindo que pertence ao cliente."""
    stmt = select(PedidoDB).where(
        PedidoDB.id == pedido_id,
        PedidoDB.cliente_id == cliente_id,  # CRÍTICO: filtro de tenant
    )
    result = await db.execute(stmt)
    pedido_db = result.scalar_one_or_none()
    if not pedido_db:
        return None
    return Pedido.model_validate(pedido_db, from_attributes=True)


async def listar_pedidos_cliente(
    db: AsyncSession,
    cliente_id: str,
    limite: int = 10,
) -> list[Pedido]:
    """Lista pedidos do cliente."""
    stmt = (
        select(PedidoDB)
        .where(PedidoDB.cliente_id == cliente_id)
        .order_by(PedidoDB.criado_em.desc())
        .limit(limite)
    )
    result = await db.execute(stmt)
    return [
        Pedido.model_validate(p, from_attributes=True)
        for p in result.scalars().all()
    ]