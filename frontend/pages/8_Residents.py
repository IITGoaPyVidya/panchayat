import os

import pandas as pd
import requests
import streamlit as st

from frontend.components.auth_gate import require_login
from frontend.components.sidebar import render_sidebar

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Residents", page_icon="🏠", layout="wide")
require_login()
render_sidebar()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}
user = st.session_state["user"]

st.title("🏠 Resident Directory")

residents = requests.get(f"{API_BASE}/residents", headers=headers, timeout=20).json()
st.dataframe(pd.DataFrame(residents), use_container_width=True)

st.subheader("Update My Profile")
with st.form("profile_update"):
    name = st.text_input("Name", value=user["name"])
    phone = st.text_input("Phone", value=user.get("phone", ""))
    email = st.text_input("Email", value=user["email"])
    members_count = st.number_input("Number of members", min_value=1, value=int(user.get("members_count", 1)))
    vehicle_numbers = st.text_area("Vehicle numbers", value=user.get("vehicle_numbers", ""))
    submit = st.form_submit_button("Update", use_container_width=True)
    if submit:
        payload = {
            "name": name,
            "phone": phone,
            "email": email,
            "members_count": int(members_count),
            "vehicle_numbers": vehicle_numbers,
        }
        r = requests.put(f"{API_BASE}/residents/me", headers=headers, json=payload, timeout=20)
        if r.status_code == 200:
            st.session_state["user"] = r.json()
            st.success("Profile updated")
            st.rerun()
        else:
            st.error(r.json().get("detail", "Failed"))

if user["role"] == "admin":
    csv_resp = requests.get(f"{API_BASE}/residents/export", headers=headers, timeout=20)
    st.download_button("Export residents CSV", csv_resp.text, file_name="residents.csv", mime="text/csv", use_container_width=True)
