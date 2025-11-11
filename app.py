import streamlit as st
from services.auth_service import authenticate, init_db, get_user
from core.config import settings

st.set_page_config(page_title="Proposal Platform", layout="wide")

# Initialize DB & seed users on first run
init_db()

st.title("📄 Techno‑Commercial Proposal Platform")

if 'user' not in st.session_state:
    st.session_state.user = None

# Login Panel
if not st.session_state.user:
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign in")
    if submit:
        user = authenticate(email, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome {user['name']} ({user['role']})")
            st.rerun()
        else:
            st.error("Invalid credentials")
else:
    u = st.session_state.user
    st.info(f"Logged in as **{u['name']}** · Role: **{u['role']}** · {settings.app_name}")
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

st.write("Use the sidebar to open pages: Proposal Generator, Analytics.")
