from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import ArtigoConhecimento
from app.rag.embeddings import gerar_embedding

# cosine_distance: 0 = idêntico, 2 = oposto
# Artigos com distância >= threshold são considerados fora do assunto
_DISTANCE_THRESHOLD = 0.70


async def buscar_artigos(
    db: AsyncSession,
    consulta: str,
    categoria: str | None = None,
    top_k: int = 3,
) -> list[ArtigoConhecimento]:
    """Busca artigos semanticamente relevantes.

    Retorna lista vazia quando nenhum artigo passa o threshold de relevância,
    permitindo que o agente escale para humano em vez de alucinar.
    """
    embedding_consulta = await gerar_embedding(consulta)

    stmt = (
        select(ArtigoConhecimento)
        .where(ArtigoConhecimento.embedding.isnot(None))
        .where(
            ArtigoConhecimento.embedding.cosine_distance(embedding_consulta)
            < _DISTANCE_THRESHOLD
        )
    )
    if categoria:
        stmt = stmt.where(ArtigoConhecimento.categoria == categoria)

    stmt = stmt.order_by(
        ArtigoConhecimento.embedding.cosine_distance(embedding_consulta)
    ).limit(top_k)

    result = await db.execute(stmt)
    return list(result.scalars().all())