import streamlit as st
from pathlib import Path
from views.agent import render_agent

st.set_page_config(page_title="RES Platform V2.0", layout="wide")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select View", ["Agent Dashboard", "Admin Panel"])
    if page == "Agent Dashboard":
        render_agent()

if __name__ == "__main__":
    main()