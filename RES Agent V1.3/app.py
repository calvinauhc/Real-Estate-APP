import streamlit as st  # <--- THIS LINE IS CRITICAL
import sys
import os
from modules.data_layer import init_db
from views.agent import render as render_agent, render_sidebar
from views.admin import render_admin
from pathlib import Path
from modules.valuation_engine import process_raw_data

# Force the project root directory into the sys.path
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

# Initialize storage on startup
init_db()

st.set_page_config(page_title="RES Platform V2.0", layout="wide")

def main():
    st.sidebar.title("Navigation")
    # This radio button dictates what 'page' is active
    page = st.sidebar.radio("Select View", ["Agent Dashboard", "Admin Panel"])
    if not os.path.exists("data/avg_valuation_ref.csv"):
        st.warning("Reference data missing. Generating from raw files...")
        process_raw_data()
        st.success("Reference data ready!")
        
    if page == "Agent Dashboard":
        render_sidebar()  # Keeps your portfolio list visible
        render_agent()    # Renders the form/matrix
        
    elif page == "Admin Panel":
        render_admin()    # Renders your master ledger

if __name__ == "__main__":
    main()