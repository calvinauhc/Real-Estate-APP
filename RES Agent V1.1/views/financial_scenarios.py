import streamlit as st
import sqlite3
import pandas as pd
import os
from utils.db_manager import DB_PATH
from utils.finance_engine import calculate_max_loan

def calculate_bsd(price):
    """Calculates Singapore Buyer's Stamp Duty (BSD) based on property purchase price."""
    if price <= 0: return 0
    duty = 0
    if price > 3000000:
        duty += (price - 3000000) * 0.06
        price = 3000000
    if price > 1500000:
        duty += (price - 1500000) * 0.05
        price = 1500000
    if price > 1000000:
        duty += (price - 1000000) * 0.04
        price = 1000000
    if price > 360000:
        duty += (price - 360000) * 0.03
        price = 360000
    if price > 180000:
        duty += (price - 180000) * 0.02
        price = 180000
    duty += price * 0.01
    return duty

def get_individual_absd_rate(citizenship, tier):
    """Returns the individual ABSD rate based on profile demographics."""
    if citizenship == "SC":
        if tier == 1: return 0.0
        elif tier == 2: return 0.20
        else: return 0.30
    elif citizenship == "PR":
        if tier == 1: return 0.05
        elif tier == 2: return 0.30
        else: return 0.35
    else:
        return 0.60

def render_advanced_calculator(default_is_hdb=False):
    """Renders the MAS Regulatory Loan Capacity Optimizer UI Component with Employment Status & Landed frameworks."""
    st.markdown("---")
    st.subheader("🛡️ MAS Regulatory Loan Capacity Optimizer")
    st.caption("Computes maximum borrowing capacity using current regulatory frameworks (TDSR, MSR, and Income Haircuts).")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💵 Income & Commitment Inputs")
        
        # Employment Status Track Selection
        employment_status = st.radio(
            "Client Employment Status",
            ["Salaried Employee (Fixed + Variable)", "Self-Employed / Business Owner / Freelancer"],
            index=0,
            key="calc_employment"
        )
        is_self_employed = True if "Self-Employed" in employment_status else False

        # --- 🛠️ UPDATED: EXPLICITLY INCLUDE LANDED PROPERTY ---
        prop_type = st.radio(
            "Target Property Category", 
            ["Private Property / Condo / Landed", "HDB Flat / Executive Condo (EC)"],
            index=1 if default_is_hdb else 0,
            key="calc_prop_type"
        )
        is_hdb = True if "HDB" in prop_type else False
        
        if is_self_employed:
            # Under MAS guidelines, Self-Employed documented gross income gets an absolute flat 30% haircut
            fixed_inc = st.number_input("Average Monthly Net Trade Income (From IRAS NOA) ($)", min_value=0, value=8000, step=500, key="calc_fixed_inc")
            var_inc = 0.0  # Force variable entry to zero because the full pool is haircutted together
            st.caption("💡 *MAS Notice 645 Framework: 30% haircut will automatically be enforced on your entire Net Trade Income stream.*")
        else:
            fixed_inc = st.number_input("Gross Fixed Monthly Base Income ($)", min_value=0, value=6000, step=500, key="calc_fixed_inc")
            var_inc = st.number_input("Variable Income (Average Bonuses/Commissions) ($)", min_value=0, value=2000, step=500, key="calc_var_inc")
            st.caption("💡 *MAS Notice 645 Framework: 30% haircut applies strictly to the variable component; fixed salary remains unhaircutted.*")
            
        debts = st.number_input("Existing Monthly Debt Obligations (Car loan, cards, etc.) ($)", min_value=0, value=800, step=100, key="calc_debts")
        
        # --- 🛠️ UPDATED: DYNAMIC TENURE SLIDER LIMITS (30 Yrs HDB vs 35 Yrs Private) ---
        max_tenure_limit = 30 if is_hdb else 35
        tenure = st.slider("Desired Loan Tenure (Years)", min_value=5, max_value=max_tenure_limit, value=25, step=1, key="calc_tenure")
        stress_test = st.slider("MAS Regulatory Stress-Test Interest Rate (%)", min_value=3.0, max_value=5.0, value=4.0, step=1.0, format="%.2f%%", key="calc_stress")

    with col2:
        st.markdown("#### 📊 Borrowing Capacity Output")
        
        # Route processing through our financial formula module
        # If client is self-employed, pass total income into variable pool to cleanly enforce 30% haircut on everything
        calc_fixed = 0.0 if is_self_employed else fixed_inc
        calc_var = fixed_inc if is_self_employed else var_inc

        res = calculate_max_loan(
            fixed_income=calc_fixed,
            variable_income=calc_var,
            other_debts=debts,
            loan_tenure_years=tenure,
            is_hdb_or_ec=is_hdb,
            stress_rate=stress_test / 100
        )
        
        # Display Results Metric cards
        st.metric(
            label="Maximum Qualified Loan Quantum", 
            value=f"${res['max_loan']:,.0f}"
        )
        st.metric(
            label="Max Allowable Monthly Repayment", 
            value=f"${res['max_monthly_installment']:,.0f}"
        )
        
        # Dynamic Visual Alert Framework Cards
        limiting_factor = res['limiting_factor']
        
        if "MSR" in limiting_factor:
            st.error("⚠️ **ACTIVE FRAMEWORK: MSR (Mortgage Servicing Ratio)**")
            st.info(
                f"Because the target is an HDB/EC, housing repayments are strictly capped at **30%** "
                f"of your assessable income (${res['max_monthly_installment']:,.0f}/mo). TDSR was bypassed because MSR is the lower, tighter ceiling."
            )
        elif "High External Debt" in limiting_factor:
            st.error("🚨 **ACTIVE FRAMEWORK: TDSR (Total Debt Servicing Ratio - Debt Strain)**")
            st.warning(
                "Even though this is an HDB property, the client's heavy outside commitments (car loans, credit cards) "
                "have breached the **55%** total debt pool constraint. External liabilities are aggressively dragging down their maximum housing budget!"
            )
        else:
            st.success("🏢 **ACTIVE FRAMEWORK: TDSR (Total Debt Servicing Ratio)**")
            st.info(
                "Private/Landed property framework applied. Total combined monthly debt obligations (housing loan + outside commitments) "
                "are capped at a maximum of **55%** of your assessable income."
            )
        
        # Explanatory breakdown container
        with st.expander("Show Regulatory Audit Breakdown"):
            if is_self_employed:
                st.markdown(f"""
                * **Gross Documented Trade Income:** `${fixed_inc:,.0f}`
                * **MAS Assessable Income:** `${res['assessable_monthly_income']:,.0f}` *(Includes mandatory flat 30% regulatory haircut on entire self-employed pool)*
                * **Allocated Total Debt Pool Max:** `${res['assessable_monthly_income'] * 0.55:,.0f}` *(Absolute 55% constraint across all structural liabilities)*
                """)
            else:
                st.markdown(f"""
                * **Gross Declared Income:** `${fixed_inc + var_inc:,.0f}`
                * **MAS Assessable Income:** `${res['assessable_monthly_income']:,.0f}` *(Includes mandatory 30% haircut on variable components only)*
                * **Allocated Total Debt Pool Max:** `${res['assessable_monthly_income'] * 0.55:,.0f}` *(Absolute 55% constraint across all structural liabilities)*
                """)

def show_scenarios_page():
    st.header("📊 Stress-Test Capital Budget Scenarios")
    
    if not os.path.exists(DB_PATH):
        st.error(f"❌ Database file not found at path: {DB_PATH}.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        profiles_df = pd.read_sql_query("SELECT * FROM client_profiles", conn)
    except Exception as e:
        st.error(f"❌ Error loading profiles table: {e}")
        conn.close()
        return
    conn.close()
    
    if profiles_df.empty:
        st.info("ℹ️ No active client profiles discovered. Please register a profile in Tab 2 first.")
        return
        
    opts = {}
    for _, r in profiles_df.iterrows():
        label = f"{r['name']} ({r['client_id']})"
        opts[label] = r['client_id']
        
    sel_label = st.selectbox("Select Active Client Profile", list(opts.keys()), key="scenario_active_client")
    cid = opts[sel_label]
    
    conn = sqlite3.connect(DB_PATH)
    p_df_raw = pd.read_sql_query(f"SELECT * FROM client_profiles WHERE client_id='{cid}'", conn)
    t_df_raw = pd.read_sql_query(f"SELECT * FROM client_targets WHERE client_id='{cid}'", conn)
    conn.close()
    
    if p_df_raw.empty:
        st.warning("⚠️ Selected client profile data could not be parsed.")
        return
        
    if t_df_raw.empty:
        st.error(f"❌ Target Details Missing: Profile '{sel_label}' has no target property specs recorded! Configure target price details in Setup to unblock this view.")
        return

    p_df = p_df_raw.iloc[0]
    t_df = t_df_raw.iloc[0]
    
    struct_str = str(p_df.get('ownership_structure', '')).strip()
    owner_mode = struct_str
    co_name = ""
    co_citizen = "SC"
    co_prop_tier = 1
    co_extra_cash = 0.0
    was_subsidized = "No"
    current_flat_type = "4-Room"
    
    if "|" in struct_str:
        parts = struct_str.split("|")
        owner_mode = parts[0]
        if len(parts) >= 7:
            co_name = parts[1]
            co_citizen = parts[2]
            try:
                co_prop_tier = int(parts[3])
            except ValueError:
                co_prop_tier = 1
            try:
                co_extra_cash = float(parts[4])
            except ValueError:
                co_extra_cash = 0.0
            was_subsidized = parts[5]
            current_flat_type = parts[6]

    p_rate = get_individual_absd_rate(p_df['citizenship'], int(p_df['current_properties_count']))
    co_rate = get_individual_absd_rate(co_citizen, co_prop_tier) if co_name else 0.0
    effective_absd_rate = max(p_rate, co_rate)

    st.markdown("### Transaction Scheme Overlays")
    is_buying_new_subsidized = st.checkbox("Is target a brand new BTO flat or EC?", value=False, key="scenario_is_bto_ec")

    resale_levy_amt = 0.0
    if was_subsidized == "Yes" and is_buying_new_subsidized:
        levy_table = {
            "2-Room": 15000, 
            "3-Room": 30000, 
            "4-Room": 40000, 
            "5-Room": 45000, 
            "Executive": 50000
        }
        resale_levy_amt = float(levy_table.get(current_flat_type, 0.0))

    gross_sell = float(t_df.get('estimated_selling_price', 0.0))
    loan_repay = float(t_df.get('outstanding_loan_old', 0.0))
    cpf_refund = float(p_df.get('cpf_accrued_interest', 0.0))
    
    net_cash_sale_proceeds = gross_sell - loan_repay - cpf_refund
    base_onhand_assets = float(p_df.get('cash_savings', 0.0)) + co_extra_cash + float(p_df.get('cpf_ordinary_account', 0.0))
    
    heading = f"### Profile: {p_df['name']}"
    if co_name:
        heading += f" & {co_name} ({owner_mode})"
    st.markdown(heading)
    
    if was_subsidized == "Yes" and resale_levy_amt > 0:
        st.warning(f"⚠️ Resale Levy Activated: ${resale_levy_amt:,.0f} due upon booking.")

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Net Sale Proceeds", f"${net_cash_sale_proceeds:,.0f}")
    m_col2.metric("Static Cash/CPF Pool", f"${base_onhand_assets:,.0f}")
    m_col3.metric("Max Loan Capacity", f"${p_df['loan_eligibility']:,.0f}")
    
    base_target = float(t_df.get('target_price', 0.0))
    scenarios = {
        "Scenario 1 (-$500k)": max(0.0, base_target - 500000),
        "Scenario 2 (Base)": base_target,
        "Scenario 3 (+$500k)": base_target + 500000
    }
    
    sc_columns = st.columns(3)
    
    for idx, (sc_name, sc_price) in enumerate(scenarios.items()):
        with sc_columns[idx]:
            st.subheader(sc_name)
            st.metric("Price", f"${sc_price:,.0f}")
            
            bsd = calculate_bsd(sc_price)
            absd = sc_price * effective_absd_rate
            legal_fee = 2500.0 if t_df['property_type'] != "HDB" else 900.0
            agent_fee = gross_sell * 0.02 if gross_sell > 0 else sc_price * 0.01
            
            total_acq = sc_price + bsd + absd + legal_fee + agent_fee + resale_levy_amt
            avail_fin = base_onhand_assets + p_df['loan_eligibility']
            shortfall = total_acq - avail_fin - net_cash_sale_proceeds
            
            data_breakdown = {
                "Purchase Price (+)": sc_price,
                "BSD (+)": bsd,
                "ABSD (+)": absd,
                "Legal Costs (+)": legal_fee,
                "Agent Fee (+)": agent_fee,
                "HDB Levy (+)": resale_levy_amt,
                "------": 0,
                "📊 TOTAL COSTS": total_acq,
                "💰 Loan + On-Hand (-)": avail_fin,
                "🏡 Net Sale Proceeds (-)": net_cash_sale_proceeds,
            }
            
            df_display = pd.DataFrame.from_dict(data_breakdown, orient='index', columns=['Amount ($)'])
            st.dataframe(df_display.style.format(lambda x: f"${x:,.0f}" if x != 0 else ""))
            
            if shortfall <= 0:
                st.success("✅ Viable")
                st.caption(f"Buffer: ${abs(shortfall):,.0f}")
            else:
                st.error("❌ Shortfall")
                st.markdown(f"Need: **${shortfall:,.0f}**")

    # 1. Dynamically toggle property type on the advanced calculator panel
    is_target_hdb = True if t_df['property_type'] == "HDB" else False
    render_advanced_calculator(default_is_hdb=is_target_hdb)
    
    # 2. Native Streamlit Reference Legend
    st.markdown("---")
    with st.expander("⚖️ MAS Regulatory Underwriting Mandates Reference Table", expanded=True):
        st.markdown("""
        When calculating maximum housing loan capacity, commercial banks in Singapore are bound by MAS Notice 645 to test debt servicing thresholds against structural framework floors rather than prevailing promo market rates:
        
        * **3.00% Floor Cap (HDB Concessionary Framework):** Enforced exclusively on concessionary housing loans disbursed directly via the Housing & Development Board framework.
        * **4.00% Floor Cap (Residential Framework):** Governs Private Condominiums, Landed Estates, and HDB properties financed via bank packages. Applied using the floor rate or the actual bank package rate, whichever is higher.
        * **5.00% Floor Cap (Non-Residential Framework):** Governs Commercial assets and Industrial property structures.
        """)
    