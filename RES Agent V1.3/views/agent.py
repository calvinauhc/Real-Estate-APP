import streamlit as st
import pandas as pd
from modules.data_layer import load_clients, save_client, update_client_qualification
from modules.financial import calculate_scenarios
from modules.calculator import calculate_affordability
from modules.data_layer import delete_client

def render():
    st.header("Agent Dashboard")
    tab1, tab2 = st.tabs(["Client Registry", "Financial Analysis"])

    district_options = [
        "D01 - CCR (Boat Quay/Marina)", "D02 - CCR (Chinatown/Tanjong Pagar)", 
        "D03 - RCR (Queenstown/Tiong Bahru)", "D04 - RCR (Sentosa/Telok Blangah)", 
        "D05 - RCR (Buona Vista/Clementi)", "D06 - CCR (City Hall/Clarke Quay)", 
        "D07 - CCR (Bugis/Beach Road)", "D08 - RCR (Little India/Farrer Park)", 
        "D09 - CCR (Orchard/River Valley)", "D10 - CCR (Bukit Timah/Holland)", 
        "D11 - CCR (Newton/Novena)", "D12 - RCR (Balestier/Toa Payoh)", 
        "D13 - RCR (Potong Pasir/Macpherson)", "D14 - RCR (Geylang/Paya Lebar)", 
        "D15 - RCR (Katong/Marine Parade)", "D16 - OCR (Bedok/Siglap)", 
        "D17 - OCR (Changi/Loyang)", "D18 - OCR (Tampines/Pasir Ris)", 
        "D19 - OCR (Hougang/Punggol/Sengkang)", "D20 - OCR (Bishan/Ang Mo Kio)", 
        "D21 - OCR (Upper Bukit Timah/Clementi)", "D22 - OCR (Jurong/Boon Lay)", 
        "D23 - OCR (Bukit Panjang/Choa Chu Kang)", "D24 - OCR (Kranji/Tengah)", 
        "D25 - OCR (Woodlands/Admiralty)", "D26 - OCR (Upper Thomson/Mandai)", 
        "D27 - OCR (Sembawang/Yishun)", "D28 - OCR (Seletar/Yio Chu Kang)"
    ]

    with tab1:
        st.subheader("Client Information")
        client = st.session_state.get('selected_client', {})
        
        # 1. Determine editing status and prepare labels/defaults
        is_editing = 'client_id' in client
        form_label = "Update Client Record" if is_editing else "Save New Client"
        
        default_name = client.get('client_name', '')
        default_phone = int(client.get('phone_last4', 1000))

        with st.form("client_form", clear_on_submit=False):
            name = st.text_input("Client Name", value=default_name)
            phone = st.number_input("Last 4 Digits of Phone", value=default_phone, min_value=1000, max_value=9999)
            postal_code = st.text_input("Postal Code", value=client.get('postal_code', ''))
            
            dist_idx = district_options.index(client['district']) if client.get('district') in district_options else 0
            district = st.selectbox("Select District", district_options, index=dist_idx)
            
            price = st.number_input("Desired Property Price", min_value=0.0, step=10000.0, 
                                value=float(client.get('desired_price', 0.0)))
            rooms = st.number_input("Number of Rooms", min_value=1, max_value=7, step=1, 
                                value=int(client.get('rooms', 1)))
            tenure = st.selectbox("Tenure", ["Freehold", "99-year Leasehold"], 
                                index=0 if client.get('tenure') == "Freehold" else 1)
            
            submit = st.form_submit_button(form_label)
            
            if submit:
                # 2. Maintain the static ID
                c_id = client.get('client_id', f"{name}_{phone}")
                
                client_record = {
                    "client_id": c_id,
                    "client_name": name,
                    "phone_last4": phone,
                    "postal_code": postal_code,
                    "district": district,
                    "desired_price": float(price),
                    "rooms": rooms,
                    "tenure": tenure,
                    "monthly_income": client.get('monthly_income', 0.0),
                    "monthly_debt": client.get('monthly_debt', 0.0),
                    "assets_cash": client.get('assets_cash', 0.0),
                    "cpf_available": client.get('cpf_available', 0.0),
                    "property_type": client.get('property_type', ''),
                    "is_active": True
                }
                
                # 3. Call update and force UI refresh
                success, message = save_client(client_record)
                
                if success:
                    st.success(f"Client {'updated' if is_editing else 'saved'} successfully!")
                    st.session_state['selected_client'] = client_record
                    st.rerun()
                else:
                    st.error(f"Error: {message}")

    with tab2:
        # 1. Summary Header
        client = st.session_state.get('selected_client', {})
        if client:
            st.success(f"Currently Analyzing: **{client.get('client_name')}**")
            st.caption(f"Postal Code: {client.get('postal_code', 'Not Provided')} | District: {client.get('district', 'N/A')}")
        else:
            st.warning("Please load a client from the sidebar to begin.")
            st.stop() # Stops execution here if no client is loaded

        st.subheader("1. Client Affordability Qualifier")
        
        # 2. Existing Inputs (Income, Debt, etc.)
        col1, col2 = st.columns(2)
        with col1:
            income = st.number_input("Gross Monthly Income", value=float(client.get('monthly_income', 0.0)))
            debt = st.number_input("Monthly Debt Obligations", value=float(client.get('monthly_debt', 0.0)))
        with col2:
            cash = st.number_input("Cash Savings", value=float(client.get('assets_cash', 0.0)))
            cpf = st.number_input("CPF OA Balance", value=float(client.get('cpf_available', 0.0)))

        # 3. Property & Valuation Block
        sqft = st.number_input("Property Area (SQFT)", min_value=0, value=int(client.get('sqft', 800)))
        base_price = st.number_input("Target Property Price", value=float(client.get('desired_price', 1000000.0)))
        
        # Update client dict locally for calculation
        client['sqft'] = sqft 
        
        # 4. Valuation Component (The "Advisory" Block)
        st.divider()
        render_valuation_test(client)
        st.divider()

        # 5. Eligibility Checks
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Check Eligibility"):
                eligibility = calculate_affordability(income, debt, base_price, cash, cpf)
                if eligibility["is_affordable"]: 
                    st.success("Client qualifies for this property!")
                else: 
                    # Ensure this entire line is on one line:
                    st.error(f"Affordability Gap: ${eligibility['shortfall']:,.0f}")

def render_sidebar():
    st.sidebar.title("My Clients")
    clients = load_clients()
    
    # Check if empty
    if clients.empty:
        st.sidebar.info("No clients yet.")
        return

    for _, row in clients.iterrows():
        display_name = f"{row.get('client_name', 'Unknown')} ({str(row.get('phone_last4', 'N/A'))})"
        with st.sidebar.expander(display_name):
            # 1. The "Load" button logic
            if st.button("Load Client", key=f"load_{row['client_id']}"):
                st.session_state['selected_client'] = row.to_dict()
                st.rerun()
            
            # --- REPLACE THE OLD DELETE BUTTON WITH THIS POPOVER ---
            with st.popover("Delete Client", use_container_width=True):
                st.error(f"Permanently delete {row.get('client_name')}?")
                
                # Confirmation step
                confirm = st.checkbox("I understand this cannot be undone", key=f"chk_{row['client_id']}")
                
                if confirm:
                    if st.button("CONFIRM DELETE", key=f"del_{row['client_id']}", type="primary"):
                        delete_client(row['client_id'])
                        
                        # Clear selection if we deleted the current active client
                        if st.session_state.get('selected_client', {}).get('client_id') == row['client_id']:
                            st.session_state['selected_client'] = None
                        st.rerun()
            # -------------------------------------------------------

def render_audit():
    st.subheader("Admin Audit: All Client Records")
    clients = load_clients()
    # Display only relevant columns for auditing
    audit_df = clients[['client_name', 'affordability_status', 'qualified_loan_amount', 'desired_price']]
    st.dataframe(audit_df)

# 1. Valuation Helper Function
def get_valuation(district_code, category, sqft):
    """Calculates valuation based on the reference file."""
    try:
        # Load the reference data generated by your engine
        ref_path = "data/avg_valuation_ref.csv"
        if not os.path.exists(ref_path):
            return None
            
        ref = pd.read_csv(ref_path)
        
        # Normalize: Match the 'location' (e.g., '01') with the provided district_code
        # Ensure we are comparing strings
        match = ref[(ref['location'].astype(str) == str(district_code)) & 
                    (ref['category'] == category)]
        
        if not match.empty:
            return match.iloc[0]['price_psf'] * float(sqft)
        return None
    except Exception as e:
        st.error(f"Error calculating valuation: {e}")
        return None

# 2. UI Component for Valuation
def render_valuation_test(client_data):
    st.subheader("Market Valuation Estimate")
    
    raw_dist = str(client_data.get('district', ''))
    district_code = raw_dist.split(' - ')[0].replace('D', '')
    
    sqft = client_data.get('sqft', 0)
    
    # --- FIX START ---
    # Force the value to a string first so we can safely check for "HDB"
    prop_type = str(client_data.get('property_type', ''))
    category = 'HDB' if 'HDB' in prop_type else 'Private'
    # --- FIX END ---
    
    val = get_valuation(district_code, category, sqft)
    
    if val:
        st.success(f"Estimated Market Value: **${val:,.0f}**")
        st.caption(f"Based on median PSF for {category} in District {district_code}")
    else:
        st.warning(f"No market data found for District {district_code} ({category}).")

def get_valuation(postal_sector, comparison_key, sqft):
    """Calculates valuation based on the multi-tier reference file."""
    try:
        ref = pd.read_csv("data/avg_valuation_ref.csv")
        # Match using postal_sector (str) and the new comparison_key
        match = ref[(ref['postal_sector'].astype(str) == str(postal_sector)) & 
                    (ref['comparison_key'] == comparison_key)]
        
        if not match.empty:
            return match.iloc[0]['price_psf'] * float(sqft)
        return None
    except:
        return None

def render_valuation_test(client_data):
    st.subheader("Market Valuation Estimate")
    
    # 1. Extract and clean district/sector (D01 -> 01)
    raw_dist = str(client_data.get('district', ''))
    postal_sector = raw_dist.split(' - ')[0].replace('D', '')
    
    # 2. Build the comparison_key to match the engine
    prop_type = str(client_data.get('property_type', ''))
    tenure = str(client_data.get('tenure', ''))
    
    if 'HDB' in prop_type:
        comparison_key = "HDB-Flat-99-year Leasehold"
    else:
        comparison_key = f"Private-{prop_type}-{tenure}"
    
    sqft = client_data.get('sqft', 0)
    
    # 3. Lookup
    val = get_valuation(postal_sector, comparison_key, sqft)
    
    if val:
        st.success(f"Estimated Market Value: **${val:,.0f}**")
        st.caption(f"Based on median PSF for {comparison_key} in District {postal_sector}")
    else:
        st.warning(f"No market data found for {comparison_key} in District {postal_sector}.")