import streamlit as st
import pandas as pd
from sqlalchemy import select
from core.db import get_session
from core.models import Proposal, ProposalLog
import plotly.express as px

st.set_page_config(page_title="Analytics", layout="wide")

user = st.session_state.get('user')
if not user:
    st.warning("Please login on Home page.")
    st.stop()

st.title("📊 Proposal Analytics")

with get_session() as session:
    proposals = session.execute(select(Proposal)).scalars().all()
    logs = session.execute(select(ProposalLog)).scalars().all()

p_df = pd.DataFrame([{
    "reference_no": p.reference_no,
    "template": p.template_type,
    "created_at": p.created_at,
    "created_by": p.created_by,
} for p in proposals])

l_df = pd.DataFrame([{
    "reference_no": l.reference_no,
    "timestamp": l.at,
    "level": l.level,
    "message": l.message,
} for l in logs])

st.subheader("Proposals")
st.dataframe(p_df)

st.subheader("Logs")
st.dataframe(l_df)

if not p_df.empty:
    counts = p_df.groupby('template').size().reset_index(name='count')
    fig = px.bar(counts, x='template', y='count', title='Proposals by Template')
    st.plotly_chart(fig, use_container_width=True)

if not l_df.empty:
    l_df['date'] = pd.to_datetime(l_df['timestamp']).dt.date
    per_day = l_df.groupby('date').size().reset_index(name='logs')
    fig2 = px.line(per_day, x='date', y='logs', title='Logs per Day')
    st.plotly_chart(fig2, use_container_width=True)
