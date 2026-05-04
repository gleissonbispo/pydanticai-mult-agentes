from openai import AsyncOpenAI

from app.config import settings


_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """Retorna cliente OpenAI singleton."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
        )
    return _client


async def gerar_embedding(texto: str) -> list[float]:
    """Gera embedding usando text-embedding-3-small (1536 dims)."""
    client = get_openai_client()
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texto,
    )
    return response.data[0].embedding


async def gerar_embeddings_lote(textos: list[str]) -> list[list[float]]:
    """Gera embeddings em lote (mais eficiente)."""
    client = get_openai_client()
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=textos,
    )
    return [item.embedding for item in response.data]