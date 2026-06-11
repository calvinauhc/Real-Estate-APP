import streamlit as st
import sqlite3
import pandas as pd
from utils.db_manager import DB_PATH

def show_profiler_page():
    st.header("👤 Client Asset Profiler & Target Requirement Matrix")
    
    # 1. Initialize session state keys safely to prevent state drops on sync refresh
    if "owner_model_select" not in st.session_state:
        st.session_state.owner_model_select = "Single"

    # 2. REACTIVE CONTROLLER: Dropped right before the form container block
    st.subheader("Ownership Structure Selection")
    ownership_type = st.selectbox(
        "Choose Account Ownership Model (Changing this auto-adjusts applicant sections below)", 
        ["Single", "Joint-Tenancy", "Tenancy-In-Common"],
        key="owner_model_select"
    )

    # Detect real-time joint-tenancy boolean states
    is_joint = ownership_type in ["Joint-Tenancy", "Tenancy-In-Common"]

    # 3. Form initialization container handles structural batching safely
    with st.form("client_intake_form"):
        st.subheader("Section 1: Primary Applicant Financials & Residency")
        col1, col2, col3 = st.columns(3)
        with col1:
            client_id = st.text_input("Primary Client ID (NRIC / Phone)", value="S1234567A")
            client_name = st.text_input("Primary Legal Name", value="John Doe")
        with col2:
            citizenship = st.selectbox("Primary Residency Status", ["SC", "PR", "Foreigner"], key="p_citizen")
        with col3:
            prop_count = st.selectbox(
                "Primary Property Count Status AFTER this purchase", 
                [1, 2, 3], 
                format_func=lambda x: "1st Property" if x==1 else ("2nd Property" if x==2 else "3rd+ Property"),
                key="p_count"
            )
            cash = st.number_input("Primary Liquid Cash ($)", min_value=0.0, value=150000.0, step=1000.0)

        # --- AUTO-REFRESH TRIGGERED CONDITIONAL RENDER AREA ---
        if is_joint:
            st.markdown("---")
            st.markdown("### 👥 Section 1B: Co-Applicant Financials & Residency")
            co_col1, co_col2, co_col3 = st.columns(3)
            with co_col1:
                co_client_id = st.text_input("Co-Applicant Client ID (NRIC / Phone)", value="S7654321B")
                co_client_name = st.text_input("Co-Applicant Legal Name", value="Jane Doe")
            with co_col2:
                co_citizenship = st.selectbox("Co-Applicant Residency Status", ["SC", "PR", "Foreigner"], key="co_citizen")
            with co_col3:
                co_prop_count = st.selectbox(
                    "Co-Applicant Property Count Status AFTER this purchase", 
                    [1, 2, 3], 
                    format_func=lambda x: "1st Property" if x==1 else ("2nd Property" if x==2 else "3rd+ Property"),
                    key="co_count"
                )
                co_cash = st.number_input("Co-Applicant Liquid Cash ($)", min_value=0.0, value=50000.0, step=1000.0)
        else:
            # Reverting selection clears downstream cache entries silently
            co_client_id, co_client_name, co_citizenship, co_prop_count, co_cash = "", "", "SC", 1, 0.0

        st.markdown("---")
        st.subheader("Section 2: Asset Under Management (Current Home to Sell)")
        
        # Row 1: Selling Expectations & Outstanding Mortgage Liabilities
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            est_selling_price = st.number_input("Expected Selling Price of Current Home ($)", min_value=0.0, value=650000.0)
        with c_col2:
            outstanding_loan_old = st.number_input("Combined Outstanding Mortgage Balance ($)", min_value=0.0, value=200000.0)

        # Row 2: NEW HDB SUBSIDY & RESALE LEVY TRACKER
        c_col3, c_col4 = st.columns(2)
        with c_col3:
            was_subsidized = st.selectbox(
                "Was current home bought directly from HDB or with a CPF Housing Grant?", 
                ["No", "Yes"],
                key="was_subsidized"
            )
        with c_col4:
            # Only relevant if the answer above is "Yes"
            current_flat_type = st.selectbox(
                "Current Flat Configuration Type (Used to determine Resale Levy if applicable)",
                ["2-Room", "3-Room", "4-Room", "5-Room", "Executive"],
                index=2, # Defaults to 4-Room
                key="current_flat_type"
            )
        st.markdown("---")
        
        st.subheader("Section 3: Combined Target Future Acquisition Criteria")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            target_type = st.selectbox("Desired Property Class", ["Condo", "HDB", "Landed"])
            target_district = st.text_input("Target Postal District", value="D19")
            loan_elig = st.number_input("Joint Maximum Approved Loan Eligibility ($)", min_value=0.0, value=800000.0, step=5000.0)
        with t_col2:
            target_rooms = st.selectbox("Rooms Count", ["2-Bedder", "3-Bedder", "4-Bedder", "5-Bedder / Landed"])
            target_tenure = st.selectbox("Preferred Tenure Type", ["Freehold", "99-year Leasehold"])
            cpf_oa = st.number_input("Combined CPF OA Balance ($)", min_value=0.0, value=120000.0, step=1000.0)
        with t_col3:
            target_price = st.number_input("Target Purchase Price Horizon ($)", min_value=0.0, value=1500000.0, step=10000.0)
            land_size = st.number_input("Desired Size/Land Area (SQFT)", min_value=0.0, value=0.0)
            cpf_accrued = st.number_input("Combined CPF Accrued Interest to Return ($)", min_value=0.0, value=35000.0, step=500.0)

        submit = st.form_submit_button("Save & Update Joint Profiles to Database")

    if submit:
        compliance_passed = True
        
        if target_type == "Landed" and (citizenship == "Foreigner" or co_citizenship == "Foreigner"):
            st.error("🚫 **URA/LDAU Regulation Breach**: Landed purchases involving non-Singapore Citizens require explicit LDAU approval clearances.")
            compliance_passed = False

        if compliance_passed:
            if is_joint:
                structure_payload = f"{ownership_type}|{co_client_name}|{co_citizenship}|{co_prop_count}|{co_cash}|{was_subsidized}|{current_flat_type}"
            else:
                structure_payload = f"{ownership_type}||SC|1|0.0|{was_subsidized}|{current_flat_type}"

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO client_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(client_id) DO UPDATE SET
                    name=excluded.name, citizenship=excluded.citizenship, current_properties_count=excluded.current_properties_count,
                    cash_savings=excluded.cash_savings, loan_eligibility=excluded.loan_eligibility,
                    cpf_ordinary_account=excluded.cpf_ordinary_account, cpf_accrued_interest=excluded.cpf_accrued_interest,
                    ownership_structure=excluded.ownership_structure
                """, (client_id, client_name, citizenship, prop_count, cash, loan_elig, cpf_oa, cpf_accrued, structure_payload))
                
                cursor.execute("""
                    INSERT INTO client_targets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(client_id) DO UPDATE SET
                    property_type=excluded.property_type, district=excluded.district, rooms_required=excluded.rooms_required,
                    tenure=excluded.tenure, land_size_sqft=excluded.land_size_sqft, target_price=excluded.target_price,
                    estimated_selling_price=excluded.estimated_selling_price, outstanding_loan_old=excluded.outstanding_loan_old
                """, (client_id, target_type, target_district, target_rooms, target_tenure, land_size, target_price, est_selling_price, outstanding_loan_old))
                
                conn.commit()
                st.success(f"🎉 Success! Financial profile saved for {client_name} " + (f"& {co_client_name}" if is_joint else ""))
            except Exception as e:
                st.error(f"Database write error: {e}")
            finally:
                conn.close()