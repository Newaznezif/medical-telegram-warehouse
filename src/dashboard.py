import streamlit as st
import pandas as pd
import logging
<<<<<<< HEAD
=======
import sys
import os
from pathlib import Path

# Add project root to sys.path for direct execution
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.etl import ingest_data, clean_data
from src.analytics import calculate_kpis, detect_anomalies
>>>>>>> main

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
=======
@st.cache_data
def load_dashboard_data():
    """Load and clean data for the dashboard."""
    raw_messages = ingest_data()
    if not raw_messages:
        return pd.DataFrame()
    cleaned_df = clean_data(raw_messages)
    return detect_anomalies(cleaned_df)

>>>>>>> main
def main():
    st.set_page_config(page_title="Medical Telegram Warehouse Dashboard", layout="wide")
    
    st.title("📊 Medical Telegram Warehouse - Interim Dashboard")
    st.markdown("""
<<<<<<< HEAD
    This is a placeholder for the future Streamlit dashboard.
    The current submission focuses on code quality, structure, and testable functionality.
    """)
    
    st.info("The full implementation of Streamlit charts and SHAP/LIME interpretations will be added in the next phase.")
    
    # Sidebar for filters
    st.sidebar.header("Filters")
    channel = st.sidebar.selectbox("Select Channel", ["All", "CheMed123", "lobelia4cosmetics"])
    
    # Metric placeholders
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Messages", "0")
    col2.metric("Total Views", "0")
    col3.metric("Anomalies Detected", "0")
    
    st.warning("Connect to the database to see live data.")
=======
    This dashboard provides real-time insights into medical and cosmetics data scraped from Telegram.
    *Focus: Data integrity, code structure, and automated KPI tracking.*
    """)
    
    # Load data
    with st.spinner("Loading live data from warehouse..."):
        df = load_dashboard_data()
    
    if df.empty:
        st.error("No data found in the warehouse. Please run the ingestion pipeline first.")
        return

    # KPI Calculation
    kpis = calculate_kpis(df)
    anomalies_count = df["is_anomaly"].sum()

    # Sidebar for filters
    st.sidebar.header("📊 Filter Analytics")
    channels = ["All"] + list(df["channel_name"].unique())
    selected_channel = st.sidebar.selectbox("Select Channel", channels)
    
    display_df = df if selected_channel == "All" else df[df["channel_name"] == selected_channel]
    
    # Metric rows
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Messages", f"{len(display_df):,}")
    col2.metric("Total Views", f"{display_df['views'].sum():,}")
    col3.metric("Anomalies Detected", f"{display_df['is_anomaly'].sum():,}")
    col4.metric("Avg Views", f"{int(display_df['views'].mean()):,}")
    
    # Visualizations
    st.divider()
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Messages per Channel")
        st.bar_chart(df["channel_name"].value_counts())
        
    with c2:
        st.subheader("Anomaly Distribution")
        anomaly_stats = df["is_anomaly"].value_counts().rename({True: "Anomaly", False: "Normal"})
        st.bar_chart(anomaly_stats)

    st.subheader("Latest Processed Messages")
    st.dataframe(display_df[["channel_name", "message_date", "views", "forwards", "is_anomaly"]].head(10), use_container_width=True)

    st.success("Dashboard connected to live data successfully! ✅")
>>>>>>> main

if __name__ == "__main__":
    main()
