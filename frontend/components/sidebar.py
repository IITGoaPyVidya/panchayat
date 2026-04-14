import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.title("🏠 Society App")
        user = st.session_state.get("user")
        if user:
            st.caption(f"{user.get('name')} ({user.get('role')})")
            st.caption(f"Flat: {user.get('flat_number')}")
            if st.button("Logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()
