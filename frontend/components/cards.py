import streamlit as st


def render_contact_card(contact: dict):
    st.markdown(
        f"""
        <div class='contact-card'>
            <h4>{contact['name']}</h4>
            <p><strong>Category:</strong> {contact['category']}</p>
            <p><strong>Phone:</strong> {contact['phone']}</p>
            <p><strong>Added by Flat:</strong> {contact['added_by_flat']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
