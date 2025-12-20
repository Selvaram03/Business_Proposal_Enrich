import streamlit as st
from services.auth_service import authenticate, init_db
from core.config import settings

# MUST BE FIRST
st.set_page_config(page_title="Proposal Platform", layout="wide")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image("enrich_logo.png", use_container_width=True)
    st.markdown("---")

    page = st.navigation({
        "app": [
            st.Page("pages/1_Proposal_Generator.py", title="Proposal Generator"),
            st.Page("pages/2_Analytics.py", title="Analytics"),
        ]
    })

# ---------------- APP ----------------
init_db()

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    with st.form("login_form"):
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign in")

    if submit:
        user = authenticate(email, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials")
else:
    u = st.session_state.user
    st.sidebar.success(f"Logged in as {u['name']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

# Render selected page
page.run()
