# streamlit_app.py

import streamlit as st
import pandas as pd
from Pipeline.loader import get_connection

st.set_page_config(page_title="Currency Dashboard", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    }
    h1 {
        color: #00d4ff;
        text-align: center;
        font-weight: 800;
    }
        h2, h3, h4 {
        color: #e2e8f0;
    }
        p, label, .stMarkdown {
        color: #cbd5e0;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
        padding: 15px;
    }
    [data-testid="stMetricValue"] {
        color: #00d4ff;
        font-size: 28px;
    }
    [data-testid="stMetricLabel"] {
        color: #a0aec0;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💱 Live Currency Exchange Dashboard")
st.markdown(
    "<p style='text-align:center; color:#a0aec0;'>Powered by Azure MySQL · Updated daily by the pipeline</p>",
    unsafe_allow_html=True
)


@st.cache_data(ttl=600)
def load_features():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT target_currency, current_rate, daily_change_pct,
               weekly_change_pct, volatility, anomaly_flag,
               moving_average, computed_at
        FROM currency_features
        WHERE computed_at = (SELECT MAX(computed_at) FROM currency_features)
        ORDER BY target_currency
    """, conn)
    conn.close()
    return df


df = load_features()

# Metrics row
st.markdown("###")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Currencies", len(df))
col2.metric("Anomalies", int((df["anomaly_flag"] == "Anomaly").sum()))
col3.metric("Avg Volatility", f"{df['volatility'].mean():.4f}" if len(df) else "—")
col4.metric("Last Updated", str(df["computed_at"].iloc[0])[:16] if len(df) else "—")

st.markdown("###")

# Search filter
search = st.text_input("🔍 Search currency", "")
filtered = df[df["target_currency"].str.contains(search.upper())] if search else df

# Table
st.subheader("Currency Features")
st.dataframe(filtered, use_container_width=True, height=500)