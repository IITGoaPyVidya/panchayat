import streamlit as st


def require_login(roles: list[str] | None = None):
    token = st.session_state.get("token")
    user = st.session_state.get("user")
    if not token or not user:
        st.warning("Please login to continue")
        st.stop()
    if roles and user.get("role") not in roles:
        st.error("You do not have permission to view this page.")
        st.stop()
