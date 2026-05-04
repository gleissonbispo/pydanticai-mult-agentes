import json
import os

import streamlit as st
import websocket


st.set_page_config(
    page_title="Atendimento IA",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Atendimento Multi-Agente")
st.caption("Sistema de atendimento ao cliente com IA")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

with st.sidebar:
    st.header("Configurações")
    cliente_id = st.text_input("ID do cliente:", value="cliente_001")
    # B5 FIX: URL vem de variável de ambiente.
    # Dentro do Docker: BACKEND_URL=ws://backend:8000 (definido no compose)
    # Fora do Docker: fallback para localhost
    _default_url = os.getenv("BACKEND_URL", "ws://localhost:8000")
    backend_url = st.text_input("URL do backend:", value=_default_url)
    if st.button("Limpar conversa"):
        st.session_state.mensagens = []
        st.rerun()

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Como posso ajudar?"):
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        resposta_completa = ""

        try:
            ws = websocket.create_connection(
                f"{backend_url}/api/ws/chat/{cliente_id}",
                timeout=30,
            )

            primeira_msg = json.loads(ws.recv())

            ws.send(json.dumps({"texto": pergunta}))

            while True:
                msg = json.loads(ws.recv())
                if msg["tipo"] == "chunk":
                    resposta_completa += msg["conteudo"]
                    placeholder.markdown(resposta_completa + "▌")
                elif msg["tipo"] == "final":
                    placeholder.markdown(resposta_completa)
                    if msg["resposta"].get("precisa_escalar_humano"):
                        st.warning("⚠️ Esta conversa será encaminhada a um atendente humano.")
                    break
                elif msg["tipo"] == "erro":
                    placeholder.error(f"Erro: {msg['mensagem']}")
                    resposta_completa = msg["mensagem"]
                    break

            ws.close()
        except Exception as e:
            placeholder.error(f"Erro de conexão: {e}")
            resposta_completa = "Erro ao conectar"

    st.session_state.mensagens.append({
        "role": "assistant",
        "content": resposta_completa,
    })
