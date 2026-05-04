from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import ProdutoDB
from app.models.schemas import Produto


async def buscar_produtos(
    db: AsyncSession,
    termo_busca: str,
    preco_max: float | None = None,
    limite: int = 10,
) -> list[Produto]:
    """Busca produtos pelo nome ou descrição."""
    stmt = select(ProdutoDB).where(
        ProdutoDB.nome.ilike(f"%{termo_busca}%")
        | ProdutoDB.descricao.ilike(f"%{termo_busca}%")
    )
    if preco_max is not None:
        stmt = stmt.where(ProdutoDB.preco <= preco_max)
    stmt = stmt.where(ProdutoDB.estoque > 0).limit(limite)
    
    result = await db.execute(stmt)
    return [
        Produto.model_validate(p, from_attributes=True)
        for p in result.scalars().all()
    ]