import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.title("Financial Fraud Detection Dashboard")

conn = sqlite3.connect(
    "database/fraud_detection.db"
)

df = pd.read_sql(
    "SELECT * FROM transactions",
    conn
)

st.subheader("Dataset")
st.dataframe(df.head())

fraud_count = df["is_fraud"].sum()

st.metric(
    "Total Fraud Cases",
    int(fraud_count)
)

fig = px.histogram(
    df,
    x="amount",
    color="is_fraud",
    title="Transaction Amount Distribution"
)

st.plotly_chart(fig)

fig2 = px.scatter(
    df,
    x="amount",
    y="hour",
    color="is_fraud",
    title="Fraud Detection Scatter Plot"
)

st.plotly_chart(fig2)