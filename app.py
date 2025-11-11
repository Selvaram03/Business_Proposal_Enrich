import streamlit as st
from services.auth_service import authenticate, init_db
from sqlalchemy.exc import OperationalError

st.set_page_config(page_title="Proposal Platform", layout="wide")
st.title("📄 Techno-Commercial Proposal Platform")

try:
    init_db()
except OperationalError as e:
    st.error(
        "❌ Cannot connect to the database.\n\n"
        "• On Streamlit Cloud, do not use localhost.\n"
        "• Open the “DB Check” page to verify connectivity.\n"
        "• Confirm your DATABASE_URL & SSL settings in Secrets."
    )
    st.stop()
except RuntimeError as e:
    # Our localhost-on-cloud guard lands here
    st.error(str(e))
    st.stop()
