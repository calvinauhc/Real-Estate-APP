import streamlit as st
from modules.data_layer import load_clients
from modules.valuation_engine import process_raw_data # Add this import

def render_admin():
    st.header("Admin Audit Ledger")
    
    # --- ADDED: Data Management Section ---
    with st.expander("System Configuration"):
        if st.button("Refresh Valuation Reference Data"):
            with st.spinner("Processing raw files..."):
                process_raw_data()
                st.success("Reference data updated successfully!")
    # --------------------------------------
    
    clients = load_clients()
    
    if clients.empty:
        st.warning("No client records found in the database.")
    else:
        st.dataframe(clients, use_container_width=True)
        
        csv = clients.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Full Audit CSV",
            data=csv,
            file_name="full_client_audit.csv",
            mime="text/csv",
        )