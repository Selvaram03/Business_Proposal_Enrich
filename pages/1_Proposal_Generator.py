import streamlit as st
import pandas as pd
import os, tempfile
from io import BytesIO
from services.proposal_generator import fill_template
from services.backups import backup_proposal
from core.db import get_session
from core.models import Proposal
from core.logging_utils import attach_db_sink
from utils.security import can_use_template
from loguru import logger

st.set_page_config(page_title="Proposal Generator", layout="wide")

user = st.session_state.get('user')
if not user:
    st.warning("Please login on Home page.")
    st.stop()

st.title("🧩 Proposal Generator")

# Role‑restricted template selection
choice = st.radio("Template", ("EPC Template", "BESS Template"), horizontal=True)
if not can_use_template(user['role'], choice):
    st.error(f"Your role ({user['role']}) is not permitted to use {choice}.")
    st.stop()

# File paths
TEMPLATE_PATH = os.path.join('templates', 'EPC_Template.docx' if choice.startswith('EPC') else 'BESS_Template.docx')
TEMPLATE_EXCEL = os.path.join('templates', 'Input_EPC_Proposal.xlsx' if choice.startswith('EPC') else 'Input_BESS_Proposal.xlsx')

# Download sample Excel (if present)
try:
    with open(TEMPLATE_EXCEL, 'rb') as f:
        st.download_button(label=f"📥 Download {choice} Excel Template", data=f, file_name=os.path.basename(TEMPLATE_EXCEL))
except FileNotFoundError:
    st.warning("Sample Excel template not found. Please add it to templates/.")

# Inputs
reference_no = st.text_input("Business Proposal Reference No", placeholder="e.g., ENR-2025-000123")
uploaded_excel = st.file_uploader("Upload filled Excel", type=["xlsx"]) 

if not reference_no:
    st.info("Enter a Reference No to enable generation and logging.")
    st.stop()

if uploaded_excel is None:
    st.stop()

# Read Excel
try:
    df = pd.read_excel(uploaded_excel, engine='openpyxl')
    df.columns = df.columns.str.strip()
    if 'Parameters' not in df.columns or 'Value' not in df.columns:
        st.error("Excel must have 'Parameters' and 'Value' columns")
        st.stop()
    df["Parameters"] = df["Parameters"].astype(str).str.strip()
    df["Value"] = df["Value"].astype(str)
    st.dataframe(df)
except Exception as e:
    st.error(f"Error reading Excel: {e}")
    st.stop()

if st.button("🚀 Generate Word Proposal"):
    with get_session() as session:
        # Create or get proposal row
        existing = session.query(Proposal).filter_by(reference_no=reference_no).one_or_none()
        if existing:
            proposal = existing
        else:
            proposal = Proposal(reference_no=reference_no, template_type='EPC' if choice.startswith('EPC') else 'BESS', created_by=user['id'], meta={})
            session.add(proposal)
            session.flush()

        sink_id = attach_db_sink(session, reference_no, proposal.id)
        try:
            logger.info(f"Starting generation for {reference_no} using {choice}")
            doc = fill_template(df, TEMPLATE_PATH)
            buf = BytesIO(); doc.save(buf); buf.seek(0)

            st.success("✅ Word generated")
            st.download_button(label=f"⬇️ Download {choice.split()[0]} Word", data=buf.getvalue(), file_name=f"Generated_{choice.split()[0]}_{reference_no}.docx")

            # Optional PDF conversion if Word/LibreOffice exists on host
            pdf_bytes = None
            try:
                from docx2pdf import convert
                with tempfile.TemporaryDirectory() as td:
                    docx_path = os.path.join(td, "temp.docx")
                    pdf_path = os.path.join(td, "temp.pdf")
                    with open(docx_path, 'wb') as f: f.write(buf.getvalue())
                    convert(docx_path, pdf_path)
                    with open(pdf_path, 'rb') as f: pdf_bytes = f.read()
                st.download_button(label=f"⬇️ Download {choice.split()[0]} PDF", data=pdf_bytes, file_name=f"Generated_{choice.split()[0]}_{reference_no}.pdf")
            except Exception as e:
                logger.warning(f"PDF conversion skipped: {e}")

            # Backup artifacts
            artifacts = {f"{reference_no}.docx": buf.getvalue()}
            if pdf_bytes:
                artifacts[f"{reference_no}.pdf"] = pdf_bytes
            meta = {"reference_no": reference_no, "template": choice, "user": user}
            result = backup_proposal(reference_no, artifacts=artifacts, meta=meta)
            logger.info(f"Backup stored: {result}")
            st.info(f"Backup created at: {result.get('local_path')}")
        finally:
            from loguru import logger as _lg
            _lg.remove(sink_id)
