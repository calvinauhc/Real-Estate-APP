import streamlit as st
from modules.data_layer import save_client

def render_tab1():
    # --- CLIENT INDICATOR ---
    client = st.session_state.get('selected_client', {})
    if 'client_name' in client:
        st.info(f"Currently viewing: **{client['client_name']}**")
    else:
        st.warning("Creating a new client profile")
        
    st.subheader("Client Information & Current Property")
    
    # --- STATE ACCESS ---
    # Retrieve existing client from session state, or empty dict if creating new
    client = st.session_state.get('selected_client', {})
    
    # Safely extract the nested property dictionary for pre-loading form values
    curr = client.get('current_property', {})
    
    # Logic to determine if we are performing an UPDATE or an INSERT
    is_editing = 'client_id' in client
    form_label = "Update Current Property Record" if is_editing else "Save Client Profile"
    
    # --- FORM INITIALIZATION ---
    # clear_on_submit=False keeps the data visible after saving
    with st.form("current_property_form", clear_on_submit=False):
        
        # 1. Personal Details Section
        st.markdown("### Personal Details")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Client Name", value=client.get('client_name', ''))
        with col2:
            phone = st.number_input("Last 4 Digits of Phone", value=int(client.get('phone_last4', 1000)), min_value=1000, max_value=9999)
        
        # 2. Current Property Profile (Nested Data)
        st.markdown("### Current Property Details")
        c1, c2 = st.columns(2)
        with c1:
            postal_code = st.text_input("Current Postal Code", value=curr.get('postal_code', ''))
            # Note: Selectbox index handles the mapping from data to UI dropdown position
            prop_type = st.selectbox("Property Type", ["Condominium", "HDB", "Landed"], 
                                     index=["Condominium", "HDB", "Landed"].index(curr.get('property_type', 'Condominium')))
            tenure = st.selectbox("Tenure", ["Freehold", "99-year Leasehold"], 
                                  index=0 if curr.get('tenure') == "Freehold" else 1)
        with c2:
            sqft = st.number_input("Size (Sqft)", min_value=100, max_value=10000, value=int(curr.get('sqft', 1000)))
            floor = st.text_input("Floor", value=curr.get('floor', ''))
            unit = st.text_input("Unit", value=curr.get('unit', ''))
        
        # Trigger the submission process when the button is clicked
        submit = st.form_submit_button(form_label)
        
        # --- SUBMISSION LOGIC ---
        if submit:
            # Create a mutable copy of the client session data to avoid modifying the state prematurely
            updated_client = client.copy()
            
            # Merge current form inputs into the record
            updated_client.update({
                # Generate a unique ID (if missing) based on Name and Phone to ensure consistency
                "client_id": client.get('client_id', f"{name}_{phone}"),
                "client_name": name,
                "phone_last4": phone,
                
                # Bundle property details into a nested dictionary 
                # This maintains your modular data schema for future expansion
                "current_property": {
                    "postal_code": postal_code,
                    "property_type": prop_type,
                    "sqft": sqft,
                    "tenure": tenure,
                    "floor": floor,
                    "unit": unit
                }
            })
            
            # Send the structured dictionary to your CSV data_layer for storage
            # The 'save_client' function handles serialization (JSON dumping) of the nested dicts
            success, message = save_client(updated_client)
            
            if success:
                # Provide immediate visual feedback to the user
                st.success("Client profile saved!")
                
                # Sync the UI session state with the new database record
                # This ensures the rest of the tabs (e.g., Financial Qualifier) see the updated data
                st.session_state['selected_client'] = updated_client
                
                # Force a page reload so that UI elements (like form fields) 
                # display the newly saved data rather than stale previous input
                st.rerun()