import streamlit as st
from sqlalchemy import text
from core.db import engine
from core.config import settings

st.set_page_config(page_title="DB Check", layout="wide")
st.title("🔌 Database Connectivity Check")

st.write("Engine URL (masked):")
masked = settings.database_url
if "@" in masked:
    # mask password segment
    pre, post = masked.split("@", 1)
    if "://" in pre:
        scheme, rest = pre.split("://", 1)
        if ":" in rest:
            user, _ = rest.split(":", 1)
            masked = f"{scheme}://{user}:***@{post}"
st.code(masked)

ok = False
err = None
version = None
try:
    with engine.connect() as conn:
        version = conn.execute(text("SELECT VERSION()")).scalar()
        ok = True
except Exception as e:
    err = f"{type(e).__name__}: {e}"

col1, col2 = st.columns(2)
with col1:
    st.subheader("Status")
    st.success("Connected!") if ok else st.error("Failed to connect.")
with col2:
    if ok:
        st.subheader("MySQL Version")
        st.code(version)
    else:
        st.subheader("Error")
        st.code(err or "No details")
st.caption("Tip: Use a public MySQL host in DATABASE_URL when running on Streamlit Cloud.")
