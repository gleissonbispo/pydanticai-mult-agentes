from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import FaturaDB
from app.models.schemas import Fatura


async def listar_faturas(
    db: AsyncSession,
    cliente_id: str,
) -> list[Fatura]:
    """Lista todas as faturas do cliente."""
    stmt = (
        select(FaturaDB)
        .where(FaturaDB.cliente_id == cliente_id)
        .order_by(FaturaDB.vencimento.desc())
    )
    result = await db.execute(stmt)
    return [
        Fatura.model_validate(f, from_attributes=True)
        for f in result.scalars().all()
    ]


async def buscar_fatura_por_id(
    db: AsyncSession,
    fatura_id: str,
    cliente_id: str,
) -> Fatura | None:
    """Busca uma fatura específica."""
    stmt = select(FaturaDB).where(
        FaturaDB.id == fatura_id,
        FaturaDB.cliente_id == cliente_id,
    )
    result = await db.execute(stmt)
    f = result.scalar_one_or_none()
    return Fatura.model_validate(f, from_attributes=True) if f else None