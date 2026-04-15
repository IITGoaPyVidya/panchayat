import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
import streamlit as st

from frontend.components.auth_gate import require_login
from frontend.components.sidebar import render_sidebar

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Rulebook", page_icon="📖", layout="wide")
require_login()
render_sidebar()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}
user = st.session_state["user"]

st.title("📖 Society Rulebook")

rulebook = requests.get(f"{API_BASE}/rulebook", headers=headers, timeout=20).json()
if rulebook:
    st.write(f"**Last updated:** {rulebook.get('updated_at')}")
    st.write(rulebook.get("key_rules_text") or "No key rules summary added.")
    st.link_button("Open PDF", f"{API_BASE}{rulebook['file_path']}", use_container_width=True)

q = st.text_input("Search in rulebook")
if q:
    m = requests.get(f"{API_BASE}/rulebook/search", params={"q": q}, headers=headers, timeout=20).json()
    for match in m.get("matches", []):
        st.info(f"Page {match['page']}: {match['snippet'][:250]}...")

if user["role"] == "admin":
    st.subheader("Upload New Rulebook")
    with st.form("upload_rb"):
        title = st.text_input("Title", value="Society Rulebook")
        key_rules_text = st.text_area("Key Rules (for quick reference)")
        file = st.file_uploader("Rulebook PDF", type=["pdf"])
        submit = st.form_submit_button("Upload", use_container_width=True)
        if submit and file:
            files = {"file": (file.name, file, file.type)}
            data = {"title": title, "key_rules_text": key_rules_text}
            r = requests.post(f"{API_BASE}/rulebook", headers=headers, data=data, files=files, timeout=30)
            if r.status_code == 200:
                st.success("Rulebook uploaded")
                st.rerun()
