CREATE EXTENSION IF NOT EXISTS vector;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS pedidos (
    id          VARCHAR PRIMARY KEY,
    cliente_id  VARCHAR NOT NULL,
    status      VARCHAR NOT NULL,
    valor       FLOAT NOT NULL,
    descricao   TEXT NOT NULL,
    criado_em   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_pedidos_cliente_id ON pedidos(cliente_id);

CREATE TABLE IF NOT EXISTS faturas (
    id          VARCHAR PRIMARY KEY,
    cliente_id  VARCHAR NOT NULL,
    valor       FLOAT NOT NULL,
    vencimento  TIMESTAMPTZ NOT NULL,
    status      VARCHAR DEFAULT 'aberta'
);
CREATE INDEX IF NOT EXISTS ix_faturas_cliente_id ON faturas(cliente_id);

CREATE TABLE IF NOT EXISTS produtos (
    id          VARCHAR PRIMARY KEY,
    nome        VARCHAR NOT NULL,
    descricao   TEXT NOT NULL,
    preco       FLOAT NOT NULL,
    estoque     INTEGER DEFAULT 0,
    categoria   VARCHAR NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_produtos_categoria ON produtos(categoria);

CREATE TABLE IF NOT EXISTS artigos_conhecimento (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo      VARCHAR NOT NULL,
    conteudo    TEXT NOT NULL,
    categoria   VARCHAR NOT NULL,
    embedding   vector(1536),
    criado_em   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_artigos_conhecimento_categoria ON artigos_conhecimento(categoria);
