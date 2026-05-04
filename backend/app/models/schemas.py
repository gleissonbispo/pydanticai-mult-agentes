from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
from uuid import UUID


class MensagemWS(BaseModel):
    """Payload recebido pelo WebSocket a cada mensagem do cliente."""
    texto: str = Field(min_length=1, max_length=2000)


class MensagemEntrada(BaseModel):
    """Schema para endpoints REST futuros (não usado no WebSocket)."""
    sessao_id: UUID
    cliente_id: str
    texto: str = Field(min_length=1, max_length=2000)


class IntencaoClassificada(BaseModel):
    """Classificação de intenção — planejado para v2 do orquestrador."""
    categoria: Literal['tecnico', 'financeiro', 'vendas', 'outro']
    confianca: float = Field(ge=0, le=1)
    justificativa: str


class RespostaAgente(BaseModel):
    """Formato padrão de resposta de qualquer agente."""
    mensagem: str = Field(min_length=1, max_length=2000)
    sentimento_cliente: Literal['positivo', 'neutro', 'negativo', 'frustrado']
    precisa_escalar_humano: bool = False
    tags: list[str] = Field(default_factory=list, max_length=10)


class Pedido(BaseModel):
    """Representa um pedido no sistema."""
    id: str
    cliente_id: str
    status: Literal['pendente', 'pago', 'enviado', 'entregue', 'cancelado']
    valor: float
    descricao: str
    criado_em: datetime


class Fatura(BaseModel):
    """Representa uma fatura."""
    id: str
    cliente_id: str
    valor: float
    vencimento: datetime
    status: Literal['aberta', 'paga', 'atrasada', 'contestada']


class Produto(BaseModel):
    """Representa um produto do catálogo."""
    id: str
    nome: str
    descricao: str
    preco: float
    estoque: int
    categoria: str