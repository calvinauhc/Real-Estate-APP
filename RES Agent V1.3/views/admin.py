import streamlit as st
from modules.data_layer import load_clients

def render_admin():
    st.header("Admin Audit Ledger")
    
    # 1. Load the full client dataset
    clients = load_clients()
    
    # 2. Check if the file is empty
    if clients.empty:
        st.warning("No client records found in the database.")
    else:
        # 3. Display the full dataframe
        # You can use st.dataframe for an interactive table 
        # or st.table for a static one
        st.dataframe(clients, use_container_width=True)
        
        # Optional: Add a download button for the audit logs
        csv = clients.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Full Audit CSV",
            data=csv,
            file_name="full_client_audit.csv",
            mime="text/csv",
        )