import streamlit as st
from modules.data_layer import save_client

def render_tab2():
    # --- CLIENT INDICATOR ---
    client = st.session_state.get('selected_client', {})
    if 'client_name' in client:
        st.info(f"Currently viewing: **{client['client_name']}**")
    else:
        st.warning("Creating a new client profile")
        
    st.subheader("Desired Property (Dream House)")
    
    # Access existing client data
    client = st.session_state.get('selected_client', {})
    if not client:
        st.warning("Please complete the Client Profile in Tab 1 first.")
        return

    district_options = [
        "D01 - CCR (Boat Quay/Marina)", "D02 - CCR (Chinatown/Tanjong Pagar)", 
        "D03 - RCR (Queenstown/Tiong Bahru)", "D04 - RCR (Telok Blangah/Harbourfront)", 
        "D05 - RCR (Pasir Panjang/Clementi)", "D06 - CCR (City Hall/Clarke Quay)", 
        "D07 - CCR (Beach Road/Bugis)", "D08 - RCR (Little India/Farrer Park)", 
        "D09 - CCR (Orchard/River Valley)", "D10 - CCR (Tanglin/Holland)", 
        "D11 - CCR (Newton/Novena)", "D12 - RCR (Balestier/Toa Payoh)", 
        "D13 - RCR (Macpherson/Potong Pasir)", "D14 - RCR (Eunos/Geylang/Paya Lebar)", 
        "D15 - RCR (East Coast/Marine Parade)", "D16 - OCR (Bedok/Upper East Coast)", 
        "D17 - OCR (Loyang/Changi)", "D18 - OCR (Tampines/Pasir Ris)", 
        "D19 - OCR (Serangoon/Hougang)", "D20 - OCR (Bishan/Ang Mo Kio)", 
        "D21 - OCR (Upper Bukit Timah/Clementi Park)", "D22 - OCR (Jurong/Boon Lay)", 
        "D23 - OCR (Dairy Farm/Bukit Panjang/Choa Chu Kang)", "D24 - OCR (Lim Chu Kang/Tengah)", 
        "D25 - OCR (Admiralty/Woodlands)", "D26 - OCR (Mandai/Upper Thomson)", 
        "D27 - OCR (Sembawang/Yishun)", "D28 - OCR (Seletar/Yio Chu Kang)"
    ]

    # Pre-load existing dream data if available
    dream = client.get('dream_property', {})
    
    with st.form("dream_property_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            districts = st.multiselect("Target Districts (Max 3)", options=district_options, 
                                       default=dream.get('districts', []), max_selections=3)
            
            # --- CHANGE: Added safety check for index ---
            prop_options = ["Condominium", "HDB", "Landed"]
            # Get the current value from dict, default to 'Condominium'
            current_prop = dream.get('type', 'Condominium')
            # Look up index, but default to 0 if the value is not in our list
            prop_idx = prop_options.index(current_prop) if current_prop in prop_options else 0
            property_type = st.selectbox("Property Type", prop_options, index=prop_idx)
            
            rooms = st.number_input("Desired Rooms", min_value=1, max_value=7, value=int(dream.get('rooms', 2)))
        
        with col2:
            budget = st.number_input("Max Budget", min_value=0.0, step=50000.0, value=float(dream.get('budget', 1000000.0)))
            sqft = st.number_input("Desired Size (Sqft)", min_value=100, value=int(dream.get('sqft', 1000)))
            toilets = st.number_input("Min Toilets", min_value=1, max_value=5, value=int(dream.get('toilets', 2)))
            
            # --- CHANGE: Added safety check for index ---
            tenure_options = ["Freehold", "99-year Leasehold"]
            # Get the current value from dict, default to 'Freehold'
            current_tenure = dream.get('tenure', 'Freehold')
            # Look up index, but default to 0 if the value is not in our list
            tenure_idx = tenure_options.index(current_tenure) if current_tenure in tenure_options else 0
            tenure = st.selectbox("Desired Tenure", tenure_options, index=tenure_idx)

        submit = st.form_submit_button("Save Dream Property")
        
        if submit:
            # Update the existing client dictionary with new dream_property data
            client['dream_property'] = {
                "districts": districts,
                "type": property_type,
                "rooms": rooms,
                "budget": budget,
                "sqft": sqft,
                "toilets": toilets,
                "tenure": tenure
            }
            
            # Save the updated full client object
            success, message = save_client(client)
            if success:
                st.success("Dream property requirements saved!")
                st.session_state['selected_client'] = client
                st.rerun()