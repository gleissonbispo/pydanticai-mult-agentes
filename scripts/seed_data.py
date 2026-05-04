"""
Script de seed — popula o banco com dados realistas para demo e testes.

Uso dentro do Docker:
    docker-compose exec backend python scripts/seed_data.py

Uso local (com .env configurado):
    cd backend && python ../scripts/seed_data.py
"""

import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
from uuid import uuid4

# Localiza o módulo 'app' independente do ambiente de execução:
#   - Local (dev): scripts/ está na raiz, app/ está em backend/app/
#   - Docker: scripts/ monta em /app/scripts/, app/ está em /app/app/
_script_dir = os.path.dirname(os.path.abspath(__file__))
_local_backend = os.path.join(_script_dir, "..", "backend")  # dev local
_docker_root = os.path.join(_script_dir, "..")               # container Docker

if os.path.isdir(os.path.join(_local_backend, "app")):
    sys.path.insert(0, _local_backend)
else:
    sys.path.insert(0, _docker_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(_script_dir, "..", ".env"))

from app.models.db import PedidoDB, FaturaDB, ProdutoDB, ArtigoConhecimento, Base
from app.services.database import engine, SessionLocal


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _limpar_dados(db) -> None:
    """Remove dados de seed anteriores para evitar duplicatas."""
    from sqlalchemy import delete
    for Model in [ArtigoConhecimento, ProdutoDB, FaturaDB, PedidoDB]:
        await db.execute(delete(Model))
    await db.flush()


async def _seed_pedidos(db) -> None:
    now = _now()
    pedidos = [
        PedidoDB(id="PED-001", cliente_id="cliente_001", status="entregue",
                 valor=3499.00, descricao="Notebook Dell Inspiron 15",
                 criado_em=now - timedelta(days=45)),
        PedidoDB(id="PED-002", cliente_id="cliente_001", status="enviado",
                 valor=899.00, descricao="Monitor LG 24 Full HD",
                 criado_em=now - timedelta(days=3)),
        PedidoDB(id="PED-003", cliente_id="cliente_001", status="pendente",
                 valor=549.00, descricao="Mouse Logitech MX Master 3",
                 criado_em=now - timedelta(hours=12)),
        PedidoDB(id="PED-004", cliente_id="cliente_002", status="entregue",
                 valor=1399.00, descricao="Headphone Sony WH-1000XM5",
                 criado_em=now - timedelta(days=20)),
        PedidoDB(id="PED-005", cliente_id="cliente_002", status="cancelado",
                 valor=2299.00, descricao="Notebook Lenovo IdeaPad",
                 criado_em=now - timedelta(days=60)),
        PedidoDB(id="PED-006", cliente_id="cliente_002", status="enviado",
                 valor=389.00, descricao="Teclado Mecânico Keychron K2",
                 criado_em=now - timedelta(days=1)),
        PedidoDB(id="PED-007", cliente_id="cliente_003", status="pago",
                 valor=1799.00, descricao="Monitor Samsung 27 4K",
                 criado_em=now - timedelta(hours=6)),
        PedidoDB(id="PED-008", cliente_id="cliente_003", status="entregue",
                 valor=399.00, descricao="Webcam Logitech C920",
                 criado_em=now - timedelta(days=15)),
    ]
    db.add_all(pedidos)
    print(f"  ✓ {len(pedidos)} pedidos")


async def _seed_faturas(db) -> None:
    now = _now()
    faturas = [
        FaturaDB(id="FAT-001", cliente_id="cliente_001", valor=3499.00,
                 vencimento=now - timedelta(days=15), status="paga"),
        FaturaDB(id="FAT-002", cliente_id="cliente_001", valor=899.00,
                 vencimento=now + timedelta(days=7), status="aberta"),
        FaturaDB(id="FAT-003", cliente_id="cliente_001", valor=549.00,
                 vencimento=now - timedelta(days=2), status="atrasada"),
        FaturaDB(id="FAT-004", cliente_id="cliente_002", valor=1399.00,
                 vencimento=now - timedelta(days=30), status="paga"),
        FaturaDB(id="FAT-005", cliente_id="cliente_002", valor=2299.00,
                 vencimento=now + timedelta(days=15), status="aberta"),
        FaturaDB(id="FAT-006", cliente_id="cliente_003", valor=1799.00,
                 vencimento=now + timedelta(days=3), status="aberta"),
    ]
    db.add_all(faturas)
    print(f"  ✓ {len(faturas)} faturas")


async def _seed_produtos(db) -> None:
    produtos = [
        ProdutoDB(id="PROD-001", nome="Notebook Dell Inspiron 15",
                  descricao="Intel i5 12ª geração, 16GB RAM, SSD 512GB, Tela Full HD 15.6'",
                  preco=3499.00, estoque=12, categoria="notebooks"),
        ProdutoDB(id="PROD-002", nome="Notebook Lenovo IdeaPad 3",
                  descricao="AMD Ryzen 5 5500U, 8GB RAM, SSD 256GB, Tela HD 15.6'",
                  preco=2299.00, estoque=8, categoria="notebooks"),
        ProdutoDB(id="PROD-003", nome="Monitor LG 24' Full HD",
                  descricao="Painel IPS, 75Hz, HDMI + VGA, flicker-free, ajuste de altura",
                  preco=899.00, estoque=25, categoria="monitores"),
        ProdutoDB(id="PROD-004", nome="Monitor Samsung 27' 4K",
                  descricao="Painel VA, 60Hz, USB-C, HDR400, ideal para design e fotografia",
                  preco=1799.00, estoque=5, categoria="monitores"),
        ProdutoDB(id="PROD-005", nome="Mouse Logitech MX Master 3",
                  descricao="Sem fio 2.4GHz + Bluetooth, scroll magnético, 7 botões, 70 dias de bateria",
                  preco=549.00, estoque=30, categoria="perifericos"),
        ProdutoDB(id="PROD-006", nome="Teclado Mecânico Keychron K2",
                  descricao="Bluetooth 5.1 + USB-C, switches Red, retroiluminado RGB, layout ABNT2",
                  preco=389.00, estoque=15, categoria="perifericos"),
        ProdutoDB(id="PROD-007", nome="Headphone Sony WH-1000XM5",
                  descricao="Cancelamento ativo de ruído, 30h de bateria, Bluetooth 5.2, Hi-Res Audio",
                  preco=1399.00, estoque=7, categoria="audio"),
        ProdutoDB(id="PROD-008", nome="Webcam Logitech C920",
                  descricao="Full HD 1080p 30fps, microfone estéreo embutido, autofoco, USB",
                  preco=399.00, estoque=20, categoria="perifericos"),
        ProdutoDB(id="PROD-009", nome="Cabo USB-C 2m Premium",
                  descricao="Cabo trançado USB-C para USB-C, suporta 100W carregamento rápido e 10Gbps",
                  preco=89.00, estoque=60, categoria="acessorios"),
        ProdutoDB(id="PROD-010", nome="Hub USB-C 7 em 1",
                  descricao="HDMI 4K, 3x USB-A 3.0, USB-C PD 87W, SD Card, compatível Mac e Windows",
                  preco=249.00, estoque=18, categoria="acessorios"),
    ]
    db.add_all(produtos)
    print(f"  ✓ {len(produtos)} produtos")


async def _seed_artigos(db) -> None:
    """
    Insere artigos de conhecimento.
    Se OPENAI_API_KEY estiver configurada, gera embeddings reais.
    Caso contrário, insere sem embedding (RAG não funcionará, mas o resto sim).
    """
    artigos_dados = [
        # Técnico
        ("Como redefinir sua senha", "tecnico",
         "Para redefinir sua senha: 1) Acesse a página de login, 2) Clique em 'Esqueci minha senha', "
         "3) Digite seu email cadastrado, 4) Verifique sua caixa de entrada em até 5 minutos, "
         "5) Siga o link recebido (válido por 24 horas). Se não receber o email, verifique a pasta de spam."),

        ("Problemas para fazer login na conta", "tecnico",
         "Se não consegue fazer login, verifique: 1) Email digitado corretamente, "
         "2) CAPS LOCK desativado, 3) Conta não bloqueada por tentativas excessivas (aguarde 30 min), "
         "4) Use Chrome ou Firefox (versão atualizada), 5) Limpe o cache do navegador. "
         "Se persistir, use a opção de redefinição de senha."),

        ("Como rastrear meu pedido", "tecnico",
         "Para rastrear seu pedido: 1) Acesse 'Meus Pedidos' no menu, 2) Clique no número do pedido, "
         "3) Veja o status atual e histórico. Status: Pendente (aguardando pagamento), Pago (em separação), "
         "Enviado (em trânsito — código de rastreio disponível), Entregue, Cancelado. "
         "Prazo de entrega: 3-7 dias úteis para capitais, 5-12 para interior."),

        ("Pedido com status incorreto ou parado", "tecnico",
         "Se seu pedido está parado há mais de 48h no mesmo status: 1) Verifique se o pagamento foi confirmado, "
         "2) Confira o email por notificações, 3) Acesse 'Meus Pedidos' e verifique se há pendência. "
         "Pedidos Pago mas sem movimentação após 24h: nossa equipe é notificada automaticamente. "
         "Entre em contato se passar de 48h sem atualização."),

        # Financeiro
        ("Como contestar uma cobrança indevida", "financeiro",
         "Para contestar uma cobrança: 1) Acesse 'Minhas Faturas', 2) Localize a cobrança, "
         "3) Clique em 'Contestar cobrança', 4) Descreva o motivo detalhadamente. "
         "Nossa equipe analisa em até 5 dias úteis. Cobranças duplicadas: resolução em 24h. "
         "Enquanto a análise está em andamento, o vencimento da fatura é suspenso."),

        ("Parcelamento e negociação de faturas em atraso", "financeiro",
         "Faturas com mais de 3 dias de atraso podem ser parceladas em até 6x. "
         "Condições: primeira parcela à vista (quita a multa de 2%), demais parcelas com juros de 1.5% a.m. "
         "Para negociar, acesse 'Minhas Faturas' > 'Negociar parcelas' ou fale com nosso time. "
         "Após acordo, o novo boleto é enviado em até 2 horas para o email cadastrado."),

        ("Métodos de pagamento aceitos", "financeiro",
         "Aceitamos: Cartão de crédito (Visa, Mastercard, Amex, Elo — até 12x), "
         "Boleto bancário (compensação em 1-3 dias úteis), PIX (aprovação imediata), "
         "Cartão de débito (aprovação imediata). "
         "Pagamentos via boleto: pedido fica em 'Pendente' até compensação. "
         "PIX e cartão: aprovação em minutos e pedido entra em separação imediatamente."),

        # Vendas
        ("Política de devolução e troca", "vendas",
         "Você tem 30 dias corridos para devolver produtos sem defeito (direito de arrependimento). "
         "Condições: produto sem uso, na embalagem original, com todos os acessórios e nota fiscal. "
         "Produtos com defeito: troca garantida em até 90 dias. "
         "Para iniciar: 'Meus Pedidos' > selecione o pedido > 'Solicitar devolução'. "
         "Frete de devolução: gratuito para defeitos de fábrica, por conta do cliente nos demais casos."),

        ("Como escolher o notebook ideal", "vendas",
         "Para escolher o notebook certo, considere: 1) Uso principal — tarefas básicas (i3/Ryzen 3, 8GB RAM), "
         "design/foto (i5/Ryzen 5, 16GB, tela IPS), programação (i7/Ryzen 7, 16-32GB, SSD rápido), "
         "games (GPU dedicada, mínimo 16GB). 2) Portabilidade: peso < 1.5kg para viagens frequentes. "
         "3) Autonomia: bateria > 8h para uso externo. Nossos consultores podem ajudar a escolher!"),

        ("Garantia dos produtos", "vendas",
         "Todos os produtos têm garantia mínima de 12 meses contra defeitos de fábrica, "
         "conforme CDC (Código de Defesa do Consumidor). Alguns fabricantes oferecem garantia estendida: "
         "Dell: 12 meses, extensível a 36. Sony: 12 meses. Logitech: 24 meses. "
         "Para acionar a garantia: 'Meus Pedidos' > 'Solicitar garantia' > descreva o problema. "
         "Tempo de análise: até 3 dias úteis."),
    ]

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and not openai_key.startswith("sk-coloque"):
        print("  ⏳ Gerando embeddings reais (OpenAI)...")
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=openai_key)

        textos = [f"{titulo}: {conteudo}" for titulo, _, conteudo in artigos_dados]
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=textos,
        )
        embeddings = [item.embedding for item in response.data]
        print(f"  ✓ {len(artigos_dados)} embeddings gerados")
    else:
        print("  ⚠  OPENAI_API_KEY não configurada — artigos inseridos SEM embedding")
        print("     (RAG não funcionará; configure a chave e re-execute para gerar embeddings)")
        embeddings = [None] * len(artigos_dados)

    for (titulo, categoria, conteudo), embedding in zip(artigos_dados, embeddings):
        artigo = ArtigoConhecimento(
            id=uuid4(),
            titulo=titulo,
            conteudo=conteudo,
            categoria=categoria,
            embedding=embedding,
        )
        db.add(artigo)

    print(f"  ✓ {len(artigos_dados)} artigos de conhecimento (técnico, financeiro, vendas)")


async def seed() -> None:
    print("🌱 Iniciando seed do banco de dados...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("  ✓ Schema verificado/criado")

    async with SessionLocal() as db:
        print("🗑  Limpando dados anteriores...")
        await _limpar_dados(db)

        print("📦 Inserindo dados...")
        await _seed_pedidos(db)
        await _seed_faturas(db)
        await _seed_produtos(db)
        await _seed_artigos(db)

        await db.commit()

    print()
    print("✅ Seed concluído! Clientes disponíveis para teste:")
    print("   → cliente_001: 3 pedidos, 3 faturas (1 atrasada)")
    print("   → cliente_002: 3 pedidos, 2 faturas")
    print("   → cliente_003: 2 pedidos, 1 fatura")


if __name__ == "__main__":
    asyncio.run(seed())
