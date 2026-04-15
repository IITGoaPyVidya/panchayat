import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import plotly.express as px
import requests
import streamlit as st

from frontend.components.auth_gate import require_login
from frontend.components.sidebar import render_sidebar

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Polls", page_icon="🗳️", layout="wide")
require_login()
render_sidebar()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}
user = st.session_state["user"]

st.title("🗳️ Polls & Voting")

if user["role"] == "admin":
    with st.expander("Create Poll"):
        with st.form("create_poll"):
            question = st.text_input("Question")
            poll_type = st.selectbox("Type", ["yesno", "multiple"])
            options_text = st.text_area("Options (comma-separated, ignored for Yes/No)")
            submit = st.form_submit_button("Create", use_container_width=True)
            if submit:
                options = [o.strip() for o in options_text.split(",") if o.strip()] if poll_type == "multiple" else ["Yes", "No"]
                r = requests.post(
                    f"{API_BASE}/polls",
                    headers=headers,
                    json={"question": question, "poll_type": poll_type, "options": options},
                    timeout=20,
                )
                if r.status_code == 200:
                    st.success("Poll created")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Failed"))

polls = requests.get(f"{API_BASE}/polls", headers=headers, timeout=20).json()
for poll in polls:
    st.subheader(poll["question"])
    voted = False
    if poll["is_active"]:
        choice = st.radio("Select", poll["options"], key=f"choice_{poll['id']}", horizontal=True)
        if st.button("Vote", key=f"vote_{poll['id']}", use_container_width=True):
            v = requests.post(f"{API_BASE}/polls/{poll['id']}/vote", headers=headers, json={"selected_option": choice}, timeout=20)
            if v.status_code == 200:
                st.success("Vote recorded")
                voted = True
            else:
                st.info(v.json().get("detail", "Could not vote"))

    if voted or st.checkbox("Show Results", key=f"results_{poll['id']}"):
        result = requests.get(f"{API_BASE}/polls/{poll['id']}/results", headers=headers, timeout=20).json()
        fig = px.bar(x=list(result["counts"].keys()), y=list(result["counts"].values()), labels={"x": "Option", "y": "Votes"})
        st.plotly_chart(fig, use_container_width=True)
