import streamlit as st
import pandas as pd
from views.dashboard import show_dashboard_page 

# 1. Page Configuration
st.set_page_config(
    layout="wide", 
    page_title="RES Agent Analytics Suite"
)

# 2. Global Dataset Loader (Cached for performance)
@st.cache_data
def load_processed_data():
    try:
        df = pd.read_csv("data/processed_data.csv")
        # Ensure lat/lon columns are clean floats
        if 'lat' in df.columns and 'lon' in df.columns:
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading system database file: {e}")
        return None

# 3. Initialize the data
historical_transactions = load_processed_data()

# 4. Render Main Dashboard and PASS the data into it
if historical_transactions is not None:
    show_dashboard_page(historical_transactions)
else:
    st.warning("⚠️ Please ensure 'data/processed_data.csv' is populated and accessible.")