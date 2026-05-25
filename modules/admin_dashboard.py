import streamlit as st
import pandas as pd
import os

def render_admin_dashboard():
    st.title("🛡️ Admin Approval Dashboard")
    
    # Load agent data
    if not os.path.exists("agents.csv"):
        st.info("No agents registered yet.")
        return

    df = pd.read_csv("agents.csv", names=["name", "license", "status"])
    
    # Show Pending Agents
    pending = df[df["status"] == "pending"]
    st.subheader("Pending Approvals")
    
    for index, row in pending.iterrows():
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{row['name']}** (License: {row['license']})")
        if col2.button("Approve", key=f"app_{index}"):
            # Logic: Update the status to 'active'
            df.at[index, "status"] = "active"
            df.to_csv("agents.csv", index=False, header=False)
            st.success(f"Approved {row['name']}!")
            st.rerun()

    # Show Active Agents
    st.subheader("Active Agents")
    st.table(df[df["status"] == "active"])