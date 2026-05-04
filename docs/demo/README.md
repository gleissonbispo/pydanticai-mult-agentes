# Demo

Screenshots e GIF da interface em ação.

## Como capturar

1. Suba o projeto: `docker-compose up --build`
2. Rode o seed: `docker-compose exec backend python scripts/seed_data.py`
3. Acesse http://localhost:8501
4. Use `cliente_001` e teste os fluxos abaixo

## Fluxos recomendados para gravar

**Fluxo financeiro (histórico + contexto):**
```
1. "Quero ver minha fatura atrasada"
2. "Posso parcelar ela?"
3. "Como funciona o parcelamento?"
```

**Fluxo RAG (busca semântica):**
```
1. "Qual é a política de garantia dos produtos?"
2. "Como faço para devolver um notebook com defeito?"
```

**Fluxo técnico (consulta de pedidos):**
```
1. "Não consigo rastrear meu pedido"
2. "Qual o status do PED-001?"
```

## Ferramentas sugeridas

- **Windows**: [ScreenToGif](https://www.screentogif.com/) — gratuito, exporta .gif otimizado
- **Mac**: QuickTime Player → depois converte com [gifski](https://gif.ski/)
- **Web**: [Loom](https://loom.com) — captura e hospeda o vídeo automaticamente
