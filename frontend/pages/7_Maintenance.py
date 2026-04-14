import os
from datetime import date

import pandas as pd
import requests
import streamlit as st

from frontend.components.auth_gate import require_login
from frontend.components.sidebar import render_sidebar

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Maintenance", page_icon="💰", layout="wide")
require_login()
render_sidebar()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}
user = st.session_state["user"]

st.title("💰 Maintenance Fees")

if user["role"] == "admin":
    with st.expander("Log Payment"):
        with st.form("payment_form"):
            flat = st.text_input("Flat Number")
            month = st.text_input("Month (YYYY-MM)")
            amount = st.number_input("Amount", min_value=1, step=100)
            due_date = st.date_input("Due Date", value=date.today())
            status = st.selectbox("Status", ["Pending", "Paid", "Overdue"])
            paid_on = st.date_input("Paid On", value=None)
            submit = st.form_submit_button("Save", use_container_width=True)
            if submit:
                payload = {
                    "flat_number": flat,
                    "month": month,
                    "amount": int(amount),
                    "due_date": due_date.isoformat(),
                    "status": status,
                    "paid_on": paid_on.isoformat() if isinstance(paid_on, date) else None,
                }
                r = requests.post(f"{API_BASE}/maintenance", headers=headers, json=payload, timeout=30)
                if r.status_code == 200:
                    st.success("Saved")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Failed"))

rows = requests.get(f"{API_BASE}/maintenance", headers=headers, timeout=20).json()
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

if user["role"] == "admin":
    csv_resp = requests.get(f"{API_BASE}/maintenance/export", headers=headers, timeout=20)
    st.download_button("Download CSV", csv_resp.text, file_name="maintenance.csv", mime="text/csv", use_container_width=True)
