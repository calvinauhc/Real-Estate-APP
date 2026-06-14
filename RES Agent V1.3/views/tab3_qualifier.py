import streamlit as st
import modules.calculator
from modules.valuation_engine import get_valuation
from modules.data_layer import save_client
import pandas as pd

def render_tab3():
    # --- CLIENT INDICATOR ---
    client = st.session_state.get('selected_client', {})
    if 'client_name' not in client:
        st.warning("Please load a client from the sidebar first.")
        return 
        
    st.subheader("Financial Analysis & Eligibility")
    dream_prop = client.get('dream_property', {})
    st.success(f"Analyzing: **{client.get('client_name')}**")

    # --- INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Exit Strategy (Sale)")
        est_selling_price = st.number_input("Est. Selling Price ($)", min_value=0.0, value=1200000.0, step=1000.0)
        mortgage_balance = st.number_input("Outstanding Mortgage ($)", min_value=0.0, value=500000.0, step=1000.0)
        cpf_refund = st.number_input("Total CPF to Refund ($)", min_value=0.0, value=200000.0, step=1000.0)
        agent_fee_pct = st.slider("Agent Commission % (Sale)", 0.0, 3.0, 2.0) / 100
    
    with col2:
        st.subheader("2. Entry Financing")
        max_loan_ipa = st.number_input("Max Loan Amount (IPA) ($)", min_value=0.0, value=float(client.get('max_loan_ipa', 0.0)), step=1000.0)
        cpf_oa = st.number_input("Current CPF OA Balance ($)", min_value=0.0, value=float(client.get('cpf_available', 0.0)), step=1000.0)
        cash = st.number_input("Liquid Cash Savings ($)", min_value=0.0, value=float(client.get('assets_cash', 0.0)), step=1000.0)
        accrued_interest = st.number_input("Accrued Interest ($)", min_value=0.0, value=float(client.get('accrued_interest', 0.0)), step=1000.0)

    # --- EXECUTION ---
    if st.button("Calculate Liquidity Waterfall"):
        # Waterfall Calculation
        wf_data = modules.calculator.calculate_liquidity_waterfall(
            sale_price=float(est_selling_price),
            mortgage_balance=float(mortgage_balance),
            cpf_refund=float(cpf_refund),
            purchase_price=float(dream_prop.get('budget', 0)),
            ipa_loan=float(max_loan_ipa),
            custom_agent_rate=float(agent_fee_pct),
            custom_legal_fee=3000.0
        )
        
        # Eligibility Calculation
        elig_data = modules.calculator.calculate_affordability(
            max_loan_ipa=max_loan_ipa,
            target_price=dream_prop.get('budget', 0),
            cash=cash,
            cpf_oa=cpf_oa,
            accrued_interest=accrued_interest,
            property_type=dream_prop.get('type', 'Condominium'),
            tenure=dream_prop.get('tenure', 'Freehold'),
            is_first_timer=client.get('is_first_timer', True)
        )
        
        st.session_state['last_waterfall'] = wf_data
        st.session_state['last_eligibility'] = elig_data
        st.rerun()

    # --- DISPLAY LOGIC (Always render if data exists) ---
    if 'last_waterfall' in st.session_state:
        wf = st.session_state['last_waterfall']
        st.divider()
        st.subheader("Executive Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Cash", f"${wf['net_cash_proceeds']:,.0f}")
        m2.metric("Required", f"${wf['total_required']:,.0f}")
        m3.metric("Status", "Fully Funded" if wf['is_fully_funded'] else "Shortfall")

        if 'last_eligibility' in st.session_state:
            res = st.session_state['last_eligibility']
            st.subheader("Sensitivity Analysis: Budget Scenarios")
            cols = st.columns(3)
            for i, s in enumerate(res.get('scenarios', [])):
                if i < 3:
                    with cols[i]:
                        st.metric(s['label'], f"${s['price']/1_000_000:.2f}M")
                        if s.get('is_affordable'): st.success("✅ Affordable")
                        else: st.error("❌ Shortfall")

        st.subheader("Your Next Home Funding Plan")
        df_flow = [
                {"Source": "Net Sale Proceeds", "Amount": f"{wf['net_cash_proceeds']:,.0f}"},
                {"Source": "CPF OA Utilization", "Amount": f"{cpf_oa:,.0f}"},
                {"Source": "Liquid Savings", "Amount": f"{cash:,.0f}"},
                {"Source": "IPA Loan Facility", "Amount": f"{max_loan_ipa:,.0f}"}
            ]
            
            # Display as a table for the clientß
        st.table(pd.DataFrame(df_flow))