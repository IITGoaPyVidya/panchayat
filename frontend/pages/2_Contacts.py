import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
import streamlit as st

from frontend.components.auth_gate import require_login
from frontend.components.cards import render_contact_card
from frontend.components.sidebar import render_sidebar

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Contacts", page_icon="📞", layout="wide")
require_login()
render_sidebar()

st.title("📞 Useful Contacts")
headers = {"Authorization": f"Bearer {st.session_state['token']}"}
user = st.session_state["user"]

search = st.text_input("Search by name/category")
contacts = requests.get(f"{API_BASE}/contacts", headers=headers, timeout=20).json()
if search:
    contacts = [c for c in contacts if search.lower() in c["name"].lower() or search.lower() in c["category"].lower()]

with st.expander("Add Contact"):
    with st.form("add_contact"):
        name = st.text_input("Name")
        category = st.text_input("Category")
        phone = st.text_input("Phone")
        add = st.form_submit_button("Add", use_container_width=True)
        if add:
            resp = requests.post(f"{API_BASE}/contacts", headers=headers, json={"name": name, "category": category, "phone": phone}, timeout=20)
            if resp.status_code == 200:
                st.success("Added")
                st.rerun()
            st.error(resp.json().get("detail", "Failed"))

grouped = defaultdict(list)
for c in contacts:
    grouped[c["category"]].append(c)

for category, rows in grouped.items():
    st.subheader(category)
    cols = st.columns(2)
    for i, row in enumerate(rows):
        with cols[i % 2]:
            render_contact_card(row)
            can_manage = user["role"] == "admin" or row["owner_id"] == user["id"]
            if can_manage:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"Delete #{row['id']}", key=f"del_{row['id']}", use_container_width=True):
                        d = requests.delete(f"{API_BASE}/contacts/{row['id']}", headers=headers, timeout=20)
                        if d.status_code == 200:
                            st.toast("Deleted")
                            st.rerun()
                with c2:
                    with st.popover(f"Edit #{row['id']}"):
                        ename = st.text_input("Name", value=row["name"], key=f"en_{row['id']}")
                        ecat = st.text_input("Category", value=row["category"], key=f"ec_{row['id']}")
                        ephone = st.text_input("Phone", value=row["phone"], key=f"ep_{row['id']}")
                        if st.button("Save", key=f"sv_{row['id']}", use_container_width=True):
                            u = requests.put(
                                f"{API_BASE}/contacts/{row['id']}",
                                headers=headers,
                                json={"name": ename, "category": ecat, "phone": ephone},
                                timeout=20,
                            )
                            if u.status_code == 200:
                                st.toast("Updated")
                                st.rerun()
