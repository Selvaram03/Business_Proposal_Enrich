import os
import streamlit as st
from pymongo import MongoClient

def get_db():
    mongo_uri = None

    # Priority 1: Streamlit secrets
    if "MONGO_URI" in st.secrets:
        mongo_uri = st.secrets["MONGO_URI"]

    # Priority 2: Environment variable
    else:
        mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise RuntimeError(
            "MONGO_URI not found. Set it in .streamlit/secrets.toml or environment variable."
        )

    client = MongoClient(mongo_uri)
    return client["proposal_db"]
