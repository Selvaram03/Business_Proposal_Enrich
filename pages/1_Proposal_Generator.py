import streamlit as st
import pandas as pd
import os
import tempfile
from io import BytesIO
from datetime import datetime
from loguru import logger

# Services & utils
from services.proposal_generator import fill_template
from services.backups import backup_proposal
from services.proposal_number import generate_proposal_no
from core.mongo import get_db
from utils.security import can_use_template

# -------------------------------------------------------------------
# Page Config & Session Check
# -------------------------------------------------------------------
st.set_page_config(page_title="Proposal Generator", layout="wide")

user = st.session_state.get("user")
if not user:
    st.warning("Please login from the Home page.")
    st.stop()

db = get_db()

st.title("🧩 Business Proposal Generator")

# -------------------------------------------------------------------
# Template Selection (Role Restricted)
# -------------------------------------------------------------------
template_choice = st.radio(
    "Select Template",
    ("EPC Template", "BESS Template"),
    horizontal=True
)

if not can_use_template(user["role"], template_choice):
    st.error(
        f"Your role ({user['role']}) is not permitted to use {template_choice}."
    )
    st.stop()

# -------------------------------------------------------------------
# Template File Paths
# -------------------------------------------------------------------
TEMPLATE_DOCX = os.path.join(
    "templates",
    "EPC_Template.docx" if template_choice.startswith("EPC") else "BESS_Template.docx"
)

TEMPLATE_EXCEL = os.path.join(
    "templates",
    "Input_EPC_Proposal.xlsx" if template_choice.startswith("EPC") else "Input_BESS_Proposal.xlsx"
)

# -------------------------------------------------------------------
# Download Sample Excel
# -------------------------------------------------------------------
if os.path.exists(TEMPLATE_EXCEL):
    with open(TEMPLATE_EXCEL, "rb") as f:
        st.download_button(
            label=f"📥 Download {template_choice} Excel Template",
            data=f,
            file_name=os.path.basename(TEMPLATE_EXCEL)
        )
else:
    st.warning("Sample Excel template not found in templates/")

# -------------------------------------------------------------------
# Client Input
# -------------------------------------------------------------------
client_name = st.text_input(
    "Client / Company Name",
    placeholder="e.g., Tata Power"
)

if not client_name:
    st.info("Enter Client / Company Name to proceed.")
    st.stop()

# Create a short client code (can be replaced later with master table)
client_code = client_name.upper().replace(" ", "")[:5]

# -------------------------------------------------------------------
# Excel Upload
# -------------------------------------------------------------------
uploaded_excel = st.file_uploader(
    "Upload Filled Excel",
    type=["xlsx"]
)

if uploaded_excel is None:
    st.stop()

# -------------------------------------------------------------------
# Read & Validate Excel
# -------------------------------------------------------------------
try:
    df = pd.read_excel(uploaded_excel, engine="openpyxl")
    df.columns = df.columns.str.strip()

    if not {"Parameters", "Value"}.issubset(df.columns):
        st.error("Excel must contain 'Parameters' and 'Value' columns.")
        st.stop()

    df["Parameters"] = df["Parameters"].astype(str).str.strip()
    df["Value"] = df["Value"].astype(str)

    st.subheader("📋 Preview Input Data")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error reading Excel file: {e}")
    st.stop()

# -------------------------------------------------------------------
# Generate Proposal
# -------------------------------------------------------------------
if st.button("🚀 Generate Proposal"):
    try:
        # Generate unique proposal number
        proposal_no = generate_proposal_no(client_code)

        logger.info(f"Generating proposal {proposal_no}")

        # Generate Word document
        doc = fill_template(df, TEMPLATE_DOCX)
        word_buffer = BytesIO()
        doc.save(word_buffer)
        word_buffer.seek(0)

        # Save proposal metadata in MongoDB
        db.proposals.insert_one({
            "proposal_no": proposal_no,
            "client_name": client_name,
            "client_code": client_code,
            "template": template_choice,
            "created_by": user["id"],
            "created_at": datetime.utcnow(),
            "status": "Generated",
            "parameters": df.to_dict("records")
        })

        # Analytics log
        db.analytics_logs.insert_one({
            "proposal_no": proposal_no,
            "client_code": client_code,
            "event": "PROPOSAL_GENERATED",
            "user": user["id"],
            "timestamp": datetime.utcnow()
        })

        st.success(f"✅ Proposal Generated: {proposal_no}")

        # -------------------------------------------------------------------
        # Download Word
        # -------------------------------------------------------------------
        st.download_button(
            label="⬇️ Download Word Proposal",
            data=word_buffer.getvalue(),
            file_name=f"{proposal_no}.docx"
        )

        # -------------------------------------------------------------------
        # Optional PDF Conversion
        # -------------------------------------------------------------------
        pdf_bytes = None
        try:
            from docx2pdf import convert
            with tempfile.TemporaryDirectory() as tmp:
                docx_path = os.path.join(tmp, "temp.docx")
                pdf_path = os.path.join(tmp, "temp.pdf")

                with open(docx_path, "wb") as f:
                    f.write(word_buffer.getvalue())

                convert(docx_path, pdf_path)

                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

            st.download_button(
                label="⬇️ Download PDF Proposal",
                data=pdf_bytes,
                file_name=f"{proposal_no}.pdf"
            )

            # Analytics for PDF download
            db.analytics_logs.insert_one({
                "proposal_no": proposal_no,
                "event": "PDF_DOWNLOADED",
                "timestamp": datetime.utcnow()
            })

        except Exception as e:
            logger.warning(f"PDF conversion skipped: {e}")

        # -------------------------------------------------------------------
        # Backup Artifacts
        # -------------------------------------------------------------------
        artifacts = {
            f"{proposal_no}.docx": word_buffer.getvalue()
        }
        if pdf_bytes:
            artifacts[f"{proposal_no}.pdf"] = pdf_bytes

        backup_meta = {
            "proposal_no": proposal_no,
            "client": client_name,
            "template": template_choice,
            "user": user
        }

        backup_result = backup_proposal(
            proposal_no,
            artifacts=artifacts,
            meta=backup_meta
        )

        st.info(f"📦 Backup created at: {backup_result.get('local_path')}")

    except Exception as e:
        logger.exception("Proposal generation failed")
        st.error(f"Proposal generation failed: {e}")
