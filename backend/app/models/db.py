from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import String, Float, DateTime, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    """Classe base para todos os modelos do banco."""
    pass


class PedidoDB(Base):
    __tablename__ = "pedidos"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    cliente_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String)
    valor: Mapped[float] = mapped_column(Float)
    descricao: Mapped[str] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class FaturaDB(Base):
    __tablename__ = "faturas"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    cliente_id: Mapped[str] = mapped_column(String, index=True)
    valor: Mapped[float] = mapped_column(Float)
    vencimento: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String, default="aberta")


class ProdutoDB(Base):
    __tablename__ = "produtos"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    nome: Mapped[str] = mapped_column(String)
    descricao: Mapped[str] = mapped_column(Text)
    preco: Mapped[float] = mapped_column(Float)
    estoque: Mapped[int] = mapped_column(Integer, default=0)
    categoria: Mapped[str] = mapped_column(String, index=True)


class ArtigoConhecimento(Base):
    """Artigos da base de conhecimento usados pelo RAG."""
    __tablename__ = "artigos_conhecimento"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    titulo: Mapped[str] = mapped_column(String)
    conteudo: Mapped[str] = mapped_column(Text)
    categoria: Mapped[str] = mapped_column(String, index=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )