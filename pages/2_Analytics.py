import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from core.mongo import get_db

# -------------------------------------------------------------------
# Page Config & Auth
# -------------------------------------------------------------------
st.set_page_config(page_title="Proposal Analytics", layout="wide")

user = st.session_state.get("user")
if not user:
    st.warning("Please login on Home page.")
    st.stop()

db = get_db()

st.title("📊 Proposal Analytics Dashboard")

# -------------------------------------------------------------------
# Load Data from MongoDB
# -------------------------------------------------------------------
proposals = list(db.proposals.find({}, {"_id": 0}))
logs = list(db.analytics_logs.find({}, {"_id": 0}))

p_df = pd.DataFrame(proposals)
l_df = pd.DataFrame(logs)

# -------------------------------------------------------------------
# KPI SECTION (Top Management View)
# -------------------------------------------------------------------
st.subheader("📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_proposals = len(p_df)
unique_clients = p_df["client_code"].nunique() if not p_df.empty else 0
total_downloads = len(l_df[l_df["event"] == "PDF_DOWNLOADED"]) if not l_df.empty else 0
active_users = p_df["created_by"].nunique() if not p_df.empty else 0

col1.metric("Total Proposals", total_proposals)
col2.metric("Active Clients", unique_clients)
col3.metric("PDF Downloads", total_downloads)
col4.metric("Active Users", active_users)

# -------------------------------------------------------------------
# Proposal Master Table
# -------------------------------------------------------------------
st.subheader("📄 Proposal History")

if p_df.empty:
    st.info("No proposals generated yet.")
else:
    p_df["created_at"] = pd.to_datetime(p_df["created_at"])
    p_df = p_df.sort_values("created_at", ascending=False)

    st.dataframe(
        p_df[
            [
                "proposal_no",
                "client_name",
                "template",
                "status",
                "created_by",
                "created_at",
            ]
        ],
        use_container_width=True
    )

# -------------------------------------------------------------------
# Proposals by Client (Bar Chart)
# -------------------------------------------------------------------
st.subheader("🏢 Proposals by Client")

if not p_df.empty:
    client_counts = (
        p_df.groupby("client_name")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    fig = px.bar(
        client_counts,
        x="client_name",
        y="count",
        title="Proposals Generated per Client",
        text="count"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Proposals by Template
# -------------------------------------------------------------------
st.subheader("🧾 Proposals by Template Type")

if not p_df.empty:
    template_counts = (
        p_df.groupby("template")
        .size()
        .reset_index(name="count")
    )

    fig = px.pie(
        template_counts,
        names="template",
        values="count",
        title="Template Usage Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Monthly Proposal Trend
# -------------------------------------------------------------------
st.subheader("📈 Monthly Proposal Trend")

if not p_df.empty:
    p_df["month"] = p_df["created_at"].dt.to_period("M").astype(str)

    monthly = (
        p_df.groupby("month")
        .size()
        .reset_index(name="count")
        .sort_values("month")
    )

    fig = px.line(
        monthly,
        x="month",
        y="count",
        markers=True,
        title="Proposals Generated Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Download & Activity Analytics
# -------------------------------------------------------------------
st.subheader("⬇️ User Activity & Downloads")

if not l_df.empty:
    l_df["timestamp"] = pd.to_datetime(l_df["timestamp"])
    l_df["date"] = l_df["timestamp"].dt.date

    activity = (
        l_df.groupby(["date", "event"])
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        activity,
        x="date",
        y="count",
        color="event",
        title="Daily Activity (Proposal Generation & Downloads)"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Top Users (Optional – Very Useful for Managers)
# -------------------------------------------------------------------
st.subheader("👤 Most Active Users")

if not p_df.empty:
    user_activity = (
        p_df.groupby("created_by")
        .size()
        .reset_index(name="proposals_generated")
        .sort_values("proposals_generated", ascending=False)
    )

    fig = px.bar(
        user_activity,
        x="created_by",
        y="proposals_generated",
        title="Proposals Generated by User",
        text="proposals_generated"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Footer Insight
# -------------------------------------------------------------------
st.markdown(
    """
    ---
    ✅ **This dashboard provides real-time insights into proposal generation,
    client engagement, and user activity.**  
    Designed for **sales tracking, management review, and audit readiness**.
    """
)
