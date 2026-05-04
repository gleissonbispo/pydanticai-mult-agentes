import dotenv
dotenv.load_dotenv()

from unittest.mock import AsyncMock, MagicMock
import pytest
from app.agents import AgentDeps


@pytest.fixture
def deps_mock() -> AgentDeps:
    """Dependências mockadas para testes."""
    # Cria mock do banco que retorna lista vazia nas consultas
    db = AsyncMock()
    
    # Simula result.scalars().all() retornando lista vazia
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    
    return AgentDeps(
        db=db,
        redis=AsyncMock(),
        cliente_id="cliente_test",
        sessao_id="sessao_test",
    )