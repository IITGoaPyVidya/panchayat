import os

import requests
import streamlit as st

# In production (Railway), backend runs on same host on port 8000
# In local dev, it runs on localhost:8000
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Society Management", page_icon="🏠", layout="wide")

css_path = os.path.join(os.path.dirname(__file__), "styles", "mobile.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

st.title("🏠 Society Management System")


def save_auth(token: str):
    st.session_state["token"] = token
    user = requests.get(f"{API_BASE}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    user.raise_for_status()
    st.session_state["user"] = user.json()


if "token" not in st.session_state:
    tab_login, tab_signup, tab_guest = st.tabs(["Login", "Signup", "Guest: Emergency Contacts"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                try:
                    res = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"email": email, "password": password},
                        timeout=15,
                    )
                    if res.status_code != 200:
                        st.error(res.json().get("detail", "Login failed"))
                    else:
                        save_auth(res.json()["access_token"])
                        st.success("Login successful")
                        st.rerun()
                except Exception as ex:
                    st.error(f"Unable to login: {ex}")

    with tab_signup:
        with st.form("signup_form"):
            name = st.text_input("Name")
            email = st.text_input("Email", key="signup_email")
            phone = st.text_input("Phone")
            flat_number = st.text_input("Flat Number")
            role = st.selectbox("Role", ["resident", "admin"])
            password = st.text_input("Password", type="password", key="signup_password")
            submitted = st.form_submit_button("Signup", use_container_width=True)
            if submitted:
                try:
                    res = requests.post(
                        f"{API_BASE}/auth/signup",
                        json={
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "password": password,
                            "flat_number": flat_number,
                            "role": role,
                        },
                        timeout=15,
                    )
                    if res.status_code != 200:
                        st.error(res.json().get("detail", "Signup failed"))
                    else:
                        st.success("Signup successful. Please login.")
                except Exception as ex:
                    st.error(f"Unable to signup: {ex}")

    with tab_guest:
        st.caption("Guest users can only access emergency contacts.")
        try:
            contacts = requests.get(f"{API_BASE}/contacts", timeout=15).json()
            emergency = [c for c in contacts if c.get("category", "").lower() in {"emergency", "security", "ambulance", "fire"}]
            if emergency:
                for c in emergency:
                    st.info(f"{c['category']} — {c['name']} ({c['phone']})")
            else:
                st.warning("No emergency contacts added yet.")
        except Exception as ex:
            st.error(f"Unable to load contacts: {ex}")
else:
    user = st.session_state.get("user", {})
    st.success(f"Welcome {user.get('name')}! Open pages from left sidebar.")

    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        notices = requests.get(f"{API_BASE}/notices", headers=headers, timeout=15).json()
        if notices:
            st.subheader("📢 Active Notices")
            for n in notices[:5]:
                badge = "📌 " if n.get("is_pinned") else ""
                st.write(f"{badge}**{n['title']}** — {n['content']}")
    except Exception:
        pass
