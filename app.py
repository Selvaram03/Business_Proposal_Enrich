import streamlit as st
from services.auth_service import authenticate, init_db
from core.config import settings

# =========================================================
# MUST BE FIRST STREAMLIT COMMAND (ONLY ONCE)
# =========================================================
st.set_page_config(
    page_title="Proposal Platform",
    layout="wide"
)

# =========================================================
# INITIALIZE DATABASE
# =========================================================
init_db()

# =========================================================
# SESSION STATE
# =========================================================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================================================
# SIDEBAR (LOGO → NAVIGATION → STATUS)
# =========================================================
with st.sidebar:
    # ---- LOGO FIRST ----
    st.image("enrich_logo.png", width=170)
    st.markdown("---")

    # ---- NAVIGATION BELOW LOGO ----
    page = st.navigation({
        "app": [
            st.Page("pages/1_Proposal_Generator.py", title="Proposal Generator"),
            st.Page("pages/2_Analytics.py", title="Analytics"),
        ]
    })

    st.markdown("---")

    # ---- USER STATUS ----
    if st.session_state.user:
        st.success(f"Logged in as {st.session_state.user['name']}")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

# =========================================================
# LOGIN SCREEN
# =========================================================
if not st.session_state.user:
    st.title("📄 Techno-Commercial Proposal Platform")

    with st.form("login_form"):
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

    st.write("Use the sidebar to open pages: Proposal Generator, Analytics.")

# =========================================================
# RENDER SELECTED PAGE
# =========================================================
else:
    page.run()
