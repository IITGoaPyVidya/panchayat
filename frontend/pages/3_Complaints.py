import os

import requests
import streamlit as st

from frontend.components.auth_gate import require_login
from frontend.components.sidebar import render_sidebar

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Complaints", page_icon="🛠️", layout="wide")
require_login()
render_sidebar()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}
user = st.session_state["user"]

st.title("🛠️ Complaint Management")

with st.form("complaint_form"):
    st.text_input("Flat Number", value=user["flat_number"], disabled=True)
    st.text_input("Resident Name", value=user["name"], disabled=True)
    category = st.selectbox("Category", ["Water", "Electricity", "Cleanliness", "Noise", "Security", "Parking", "Other"])
    subject = st.text_input("Subject")
    description = st.text_area("Description")
    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
    photo = st.file_uploader("Photo Attachment", type=["png", "jpg", "jpeg"])
    submit = st.form_submit_button("Raise Complaint", use_container_width=True)
    if submit:
        data = {"category": category, "subject": subject, "description": description, "priority": priority}
        files = {"photo": (photo.name, photo, photo.type)} if photo else None
        r = requests.post(f"{API_BASE}/complaints", headers=headers, data=data, files=files, timeout=30)
        if r.status_code == 200:
            st.success("Complaint raised")
            st.rerun()
        else:
            st.error(r.json().get("detail", "Failed"))

status_filter = st.selectbox("Filter by status", ["All", "Open", "In Progress", "Resolved", "Closed"])
params = {} if status_filter == "All" else {"status": status_filter}
complaints = requests.get(f"{API_BASE}/complaints", headers=headers, params=params, timeout=30).json()

for item in complaints:
    st.markdown(f"### #{item['id']} {item['subject']}")
    st.write(f"**Category:** {item['category']} | **Priority:** {item['priority']} | **Status:** `{item['status']}`")
    st.write(item["description"])
    if item.get("photo_path"):
        st.image(f"{API_BASE}{item['photo_path']}", width=280)

    if user["role"] == "admin":
        with st.expander(f"Admin Update #{item['id']}"):
            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"], key=f"st_{item['id']}")
            assigned_to = st.text_input("Assign To", value=item.get("assigned_to") or "", key=f"as_{item['id']}")
            notes = st.text_area("Resolution Notes", value=item.get("resolution_notes") or "", key=f"rn_{item['id']}")
            if st.button("Update Status", key=f"up_{item['id']}", use_container_width=True):
                u = requests.put(
                    f"{API_BASE}/complaints/{item['id']}",
                    headers=headers,
                    json={"status": new_status, "assigned_to": assigned_to, "resolution_notes": notes},
                    timeout=30,
                )
                if u.status_code == 200:
                    st.toast("Status updated")
                    st.rerun()
