import os
from datetime import date

import requests
import streamlit as st

from frontend.components.auth_gate import require_login
from frontend.components.sidebar import render_sidebar

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Notices", page_icon="📢", layout="wide")
require_login()
render_sidebar()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}
user = st.session_state["user"]

st.title("📢 Notice Board")

if user["role"] == "admin":
    with st.expander("Post Notice"):
        with st.form("notice_form"):
            title = st.text_input("Title")
            content = st.text_area("Content")
            is_pinned = st.checkbox("Pin notice")
            expires = st.date_input("Expiry Date", value=None)
            image = st.file_uploader("Optional image", type=["png", "jpg", "jpeg"])
            submit = st.form_submit_button("Publish", use_container_width=True)
            if submit:
                data = {"title": title, "content": content, "is_pinned": str(is_pinned).lower()}
                if isinstance(expires, date):
                    data["expires_on"] = expires.isoformat()
                files = {"image": (image.name, image, image.type)} if image else None
                r = requests.post(f"{API_BASE}/notices", headers=headers, data=data, files=files, timeout=30)
                if r.status_code == 200:
                    st.success("Notice posted")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Failed"))

notices = requests.get(f"{API_BASE}/notices", headers=headers, timeout=20).json()
for n in notices:
    pin = "📌 " if n["is_pinned"] else ""
    st.subheader(f"{pin}{n['title']}")
    st.write(n["content"])
    if n.get("image_path"):
        st.image(f"{API_BASE}{n['image_path']}", width=300)
    if user["role"] == "admin" and st.button(f"Delete #{n['id']}", key=f"dn_{n['id']}", use_container_width=True):
        d = requests.delete(f"{API_BASE}/notices/{n['id']}", headers=headers, timeout=20)
        if d.status_code == 200:
            st.toast("Deleted")
            st.rerun()
