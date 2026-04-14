import os

import requests
import streamlit as st

from frontend.components.auth_gate import require_login
from frontend.components.sidebar import render_sidebar

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="SocietyBot", page_icon="🤖", layout="wide")
require_login()
render_sidebar()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

st.title("🤖 SocietyBot 🏠")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for m in st.session_state["chat_history"]:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Ask about rules, contacts, complaints, maintenance..."):
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    payload = {"message": prompt, "history": st.session_state["chat_history"][-10:]}
    resp = requests.post(f"{API_BASE}/chatbot/ask", headers=headers, json=payload, timeout=60)
    answer = resp.json().get("answer", "Sorry, I couldn't answer right now.")

    st.session_state["chat_history"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)
