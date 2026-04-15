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

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
require_login()
render_sidebar()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}
user = st.session_state["user"]

st.title("📊 Dashboard")

residents = requests.get(f"{API_BASE}/residents", headers=headers, timeout=20).json()
complaints = requests.get(f"{API_BASE}/complaints", headers=headers, timeout=20).json()
notices = requests.get(f"{API_BASE}/notices", headers=headers, timeout=20).json()
maintenance = requests.get(f"{API_BASE}/maintenance", headers=headers, timeout=20).json()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Residents", len(residents))
c2.metric("Open Complaints", len([c for c in complaints if c["status"] in ["Open", "In Progress"]]))
c3.metric("Pending Dues", len([m for m in maintenance if m["status"] in ["Pending", "Overdue"]]))
c4.metric("Active Notices", len(notices))

if complaints:
    st.subheader("Complaint Category Breakdown")
    categories = {}
    for comp in complaints:
        categories[comp["category"]] = categories.get(comp["category"], 0) + 1
    fig = px.pie(names=list(categories.keys()), values=list(categories.values()))
    st.plotly_chart(fig, use_container_width=True)

if user["role"] == "admin":
    st.subheader("Maintenance Collection Progress")
    summary = requests.get(f"{API_BASE}/maintenance/summary", headers=headers, timeout=20).json()
    st.progress(min(int(summary.get("progress_percent", 0)), 100), text=f"{summary.get('progress_percent', 0)}% collected this month")

st.subheader("Recent Complaints")
for item in complaints[:8]:
    st.write(f"**#{item['id']}** {item['subject']} — `{item['status']}` ({item['priority']})")
