import streamlit as st
import pandas as pd
import base64
import os          # <--- Add this missing import right here!
import data_layer  # Implements the optimized, thread-safe data access layer
import spatial_engine

# Page configuration
st.set_page_config(page_title="RES Advisor Engine", layout="wide")

# Page configuration
st.set_page_config(page_title="RES Advisor Engine", layout="wide")

# --- INITIALIZE DATABASES ON LAUNCH ---
data_layer.init_databases()

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "agent_license" not in st.session_state: st.session_state["agent_license"] = ""

st.title("🛡️ RES Advisor Engine (Singapore Edition)")

# --- HELPER FORMATTING FUNCTION ---
def fmt_sgd(val):
    return f"SGD ${val:,.2f}"

# --- COMPLIANCE GATE FUNCTION ---
def check_access_flexible(login_input):
    if os.path.getsize(data_layer.AGENTS_CSV) == 0: return False, "not_found"
    clean_input = login_input.strip().lower()
    rejected_match, matched_name = False, ""
    
    with open(data_layer.AGENTS_CSV, "r") as f:
        import csv
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3: continue
            name, license_no, status = row[0].strip().lower(), row[1].strip().lower(), row[2].strip().lower()
            if clean_input == name or clean_input == license_no:
                if status == "active": return True, row[1].upper()
                elif status == "pending": return False, "pending"
                elif status == "rejected":
                    rejected_match = True
                    matched_name = row[0]
                    
    if rejected_match:
        try:
            df = pd.read_csv(data_layer.AGENTS_CSV, names=["name", "license", "status"])
            df = df[df["name"] != matched_name].to_csv(data_layer.AGENTS_CSV, index=False, header=False)
        except: pass
        return False, "rejected"
    return False, "not_found"

# --- SIDEBAR CONTROL ---
if st.session_state["logged_in"]:
    st.sidebar.markdown(f"### 👤 Active Agent\n**License:** `{st.session_state['agent_license']}`")
    view_mode = st.sidebar.radio("Go To Workspace:", ["Client Presentation Dashboard"])
    
    st.sidebar.markdown("---")
    # --- AGENT PORTFOLIO MASTER VAULT (Optimized Data Layer Call) ---
    st.sidebar.markdown("### 🗄️ Master Client Ledger Database")
    with st.sidebar.expander("👁️ View Full Portfolio Records", expanded=False):
        master_df = data_layer.get_master_ledger()
        if not master_df.empty:
            st.dataframe(master_df, hide_index=True)
        else:
            st.caption("No records logged yet.")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout 🚪"):
        st.session_state["logged_in"] = False
        st.session_state["agent_license"] = ""
        st.rerun()
else:
    view_mode = st.sidebar.radio("Go To:", ["Agent Portal Gateway", "Admin Dashboard Backend"])

# ==========================================
# ADMIN CONTROL BACKEND
# ==========================================
if view_mode == "Admin Dashboard Backend":
    st.header("🔑 Admin Approval Console")
    admin_password = st.text_input("Enter Admin Password", type="password")
    
    if admin_password == "admin123":
        st.success("Access Granted")
        # Load your agent registry
        df = pd.read_csv(data_layer.AGENTS_CSV, names=["name", "license", "status"]) 
        
        st.subheader("Manage Agent Approvals")
        for index, row in df.iterrows():
            col1, col2, col3 = st.columns([3, 1, 2])
            col1.write(f"👤 **{row['name']}** ({row['license']})")
            col2.write(f"Status: {row['status']}")
            
            # Action Logic
            if row['status'] == "pending":
                if col3.button("✅ Approve", key=f"app_{index}"):
                    df.at[index, "status"] = "active"
                    df.to_csv(data_layer.AGENTS_CSV, index=False, header=False)
                    st.rerun()
            elif row['status'] == "active":
                if col3.button("⏸️ Put On Hold", key=f"hold_{index}"):
                    df.at[index, "status"] = "on hold"
                    df.to_csv(data_layer.AGENTS_CSV, index=False, header=False)
                    st.rerun()
            elif row['status'] == "on hold":
                if col3.button("✅ Approve", key=f"app_{index}"):
                    df.at[index, "status"] = "active"
                    df.to_csv(data_layer.AGENTS_CSV, index=False, header=False)
                    st.rerun()
                if col3.button("❌ Reject", key=f"rej_{index}"):
                    df.at[index, "status"] = "rejected"
                    df.to_csv(data_layer.AGENTS_CSV, index=False, header=False)
                    st.rerun()
    else:
        st.warning("Please enter admin credentials.")

# ==========================================
# CORE AGENT DASHBOARD WORKSPACE (LOGGED IN)
# ==========================================
elif view_mode == "Client Presentation Dashboard" and st.session_state["logged_in"]:
    st.subheader("📊 Comprehensive Financial Planner & Property Assessor")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Tab 1: Profile & Desires", 
        "💰 Tab 2: Financials & Matrix Scenarios", 
        "⏳ Tab 3: Timeline Gantt Execution", 
        "📈 Tab 4: Live Listing Insights"
    ])
    
    # --- TAB 1: CLIENT PROFILE & DESIRES ---
    with tab1:
        st.markdown("### 📋 Client Case Profile Manager")
        with st.expander("🔍 Smart Client Profile Lookup", expanded=False):
            st.caption("Search by entering the client's last 4 digits of their mobile number.")
            lookup_phone = st.text_input("Enter Mobile Number (Last 4 Digits)", max_chars=4, key="lk_phone")
            
            if lookup_phone:
                # Optimized extraction using your data layer
                matched_subset = data_layer.search_clients_by_phone(lookup_phone)
                
                if matched_subset.empty: 
                    st.info("No records match this phone number.")
                elif len(matched_subset) == 1:
                    rec = matched_subset.iloc[0]
                    st.success(f"🎉 Found Profile: `{rec['client_name']}`! Synchronizing records...")
                    st.session_state["cached_name"] = str(rec['client_name'])
                    st.session_state["cached_phone"] = str(rec['phone_last4'])
                    st.session_state["cached_sale_val"] = float(rec['sale_val'])
                    st.session_state["cached_loan"] = float(rec['loan'])
                    st.session_state["cached_cpf_accrued"] = float(rec['cpf_accrued'])
                    st.session_state["cached_cash"] = float(rec['cash'])
                    st.session_state["cached_cpf_static"] = float(rec['cpf_static'])
                else:
                    st.warning("⚠️ Multiple records found with those same last 4 digits. Please verify the client's name below:")
                    verify_name_input = st.text_input("Enter Client Name (Spaces not allowed, case-insensitive)", key="verify_name")
                    if verify_name_input:
                        if " " in verify_name_input: 
                            st.error("🚨 Formatting Violation Error: Client Name lookup strings cannot contain spaces.")
                        else:
                            final_match = matched_subset[matched_subset['client_name'].str.lower() == verify_name_input.strip().lower()]
                            if not final_match.empty:
                                rec = final_match.iloc[0]
                                st.success(f"🔒 Identity Authenticated: `{rec['client_name']}` profile synced successfully.")
                                st.session_state["cached_name"] = str(rec['client_name'])
                                st.session_state["cached_phone"] = str(rec['phone_last4'])
                                st.session_state["cached_sale_val"] = float(rec['sale_val'])
                                st.session_state["cached_loan"] = float(rec['loan'])
                                st.session_state["cached_cpf_accrued"] = float(rec['cpf_accrued'])
                                st.session_state["cached_cash"] = float(rec['cash'])
                                st.session_state["cached_cpf_static"] = float(rec['cpf_static'])
                            else: 
                                st.error("Access Denied: The name entered does not align with this phone number subset.")

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("#### 📱 1. Client Identifier (PDPA Primary Key)")
            init_name = st.session_state.get("cached_name", "JohnTan")
            init_phone = st.session_state.get("cached_phone", "8831")
            
            c_name = st.text_input("Client First/Full Name (No Spaces Allowed)", value=init_name)
            c_phone = st.text_input("Last 4 Digits of Phone Number", value=init_phone, max_chars=4)
            
            space_violation = " " in c_name
            if space_violation:
                st.error("🚨 Formatting Violation Error: Spaces are strictly prohibited within the client name input field. Please remove all empty spacing blocks.")
            
            client_primary_key = f"{c_name}_{c_phone}"
            st.caption(f"**Active Operating Key Variant:** `{client_primary_key}`")
            
            st.markdown("---")
            st.markdown("#### 🏠 2. Current Asset Disposal Parameters")
            val_sale = st.session_state.get("cached_sale_val", 800000.0)
            val_loan = st.session_state.get("cached_loan", 300000.0)
            val_accrued = st.session_state.get("cached_cpf_accrued", 200000.0)
            
            current_property_value = st.number_input("Current Asset Sale Value (SGD)", value=val_sale, step=50000.0)
            outstanding_loan = st.number_input("Outstanding Housing Loan Balance (SGD)", value=val_loan, step=10000.0)
            cpf_used_with_accrued = st.number_input("Buyer 1 CPF OA to Return (Principal + Accrued) (SGD)", value=val_accrued, step=10000.0)
            
            st.markdown("##### ⚖️ Professional Fee Custom Overwrites")
            agent_fee_selling = st.number_input("Selling Agent Commission Fee (SGD)", value=current_property_value * 0.02, step=1000.0)
            legal_fee_selling = st.number_input("Disposal Legal Fee (SGD)", value=2500.0, step=250.0)
            
            resale_levy_needed = st.checkbox("Subject to HDB Resale Levy?")
            resale_levy_amt = st.number_input("Resale Levy Amount (SGD)", value=40000, step=5000) if resale_levy_needed else 0.0

        with col_right:
            st.markdown("#### 👥 3. Buyer Demographics & Co-Mingled Funds")
            st.markdown("**👤 Buyer 1 (Primary)**")
            b1_residency = st.selectbox("Buyer 1 Residency Status", ["Singapore Citizen (SC)", "Permanent Resident (PR)", "Foreigner"])
            b1_age = st.number_input("Buyer 1 Current Age", min_value=21, max_value=99, value=35)
            b1_prop_count = st.number_input("Buyer 1 Residential Properties Owned *After* This Sale", min_value=0, max_value=5, value=0)
            b1_has_overseas = st.checkbox("Buyer 1 owns any overseas residential property?")
            
            val_cpf1 = st.session_state.get("cached_cpf_static", 100000.0)
            current_b1_cpf_balance = st.number_input("Buyer 1 Static CPF OA Balance (SGD)", value=val_cpf1, step=10000.0)
            
            has_multiple_buyers = st.checkbox("👥 Include Multiple Buyers / Co-Applicant?")
            if has_multiple_buyers:
                st.markdown("---")
                st.markdown("**👤 Buyer 2 (Co-Applicant)**")
                b2_residency = st.selectbox("Buyer 2 Residency Status", ["Singapore Citizen (SC)", "Permanent Resident (PR)", "Foreigner"])
                b2_age = st.number_input("Buyer 2 Current Age", min_value=21, max_value=99, value=35)
                b2_prop_count = st.number_input("Buyer 2 Residential Properties Owned *After* This Sale", min_value=0, max_value=5, value=0)
                b2_has_overseas = st.checkbox("Buyer 2 owns any overseas residential property?")
                current_b2_cpf_balance = st.number_input("Buyer 2 Static CPF OA Balance (SGD)", value=50000, step=10000)
                b2_cpf_used_with_accrued = st.number_input("Buyer 2 CPF OA to Return (Principal + Accrued) (SGD)", value=50000, step=10000)
                
                target_age = max(b1_age, b2_age)
                overseas_flag = b1_has_overseas or b2_has_overseas
                total_static_cpf = current_b1_cpf_balance + current_b2_cpf_balance
                total_accrued_cpf_to_return = cpf_used_with_accrued + b2_cpf_used_with_accrued
            else:
                target_age = b1_age
                overseas_flag = b1_has_overseas
                total_static_cpf = current_b1_cpf_balance
                total_accrued_cpf_to_return = cpf_used_with_accrued

            st.markdown("---")
            st.markdown("#### 🎯 4. Future Desired Target Preferences")
            target_property_type = st.selectbox("Target Property Category", ["Landed", "Private Condominium", "HDB Resale Flat"])
            district_options = [f"D{i:02d}" for i in range(1, 29)]
            selected_districts = st.multiselect("Preferred Geographic Districts (Leave blank for 'All Districts')", options=district_options)
            
            price_range = st.slider("Desired Property Price Bracket Range (SGD)", 300000, 5000000, (1200000, 1600000), step=50000)
            p_low = float(price_range[0])
            p_high_raw = float(price_range[1])
            if (p_high_raw - p_low) > 2000000.0:
                p_high = p_low + 2000000.0
                st.caption(f"⚠️ Slider variance restricted to max limit of $2M. Upper bounds set to: **{fmt_sgd(p_high)}**")
            else: p_high = p_high_raw
                
            val_cash = st.session_state.get("cached_cash", 150000.0)
            available_cash_savings = st.number_input("Available Liquid Cash Reserves (SGD)", value=val_cash, step=10000.0)
            legal_fee_buying = st.number_input("Acquisition Legal Fee (SGD)", value=3000.0, step=250.0)

        st.markdown("---")
        # --- OPTIMIZED TRANSACTION ENGINE COMMIT TO DATA LAYER ---
        if st.button("💾 Save / Update Client Case Profile Record"):
            if space_violation: 
                st.error("🚨 Save Failed: You cannot commit a record containing spaces in the client name field.")
            elif c_name and c_phone:
                try:
                    pk_saved = data_layer.save_client_profile(
                        c_name, 
                        c_phone, 
                        current_property_value, 
                        outstanding_loan,
                        total_accrued_cpf_to_return, 
                        p_low,                
                        p_high, 
                        target_property_type, 
                        available_cash_savings, 
                        total_static_cpf
                    )
                    st.success(f"File Vault Lock Confirmed: `{pk_saved}` committed to safe memory arrays.")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))
            else: 
                st.error("Both a valid name and phone code are required to finalize a save.")

    # --- CORE MATH CALCULATION ENGINE ---
    gross_cash_profit = current_property_value - outstanding_loan - total_accrued_cpf_to_return - agent_fee_selling - legal_fee_selling - resale_levy_amt
    total_refunded_cpf_oa_pool = total_static_cpf + total_accrued_cpf_to_return
    total_fluid_reserves_pool = available_cash_savings + max(0, gross_cash_profit) + total_refunded_cpf_oa_pool
    p_mid = (p_low + p_high) / 2.0

    b1_rate = 0.05 if b1_residency == "Permanent Resident (PR)" and b1_prop_count == 0 else (0.30 if b1_residency == "Permanent Resident (PR)" else (0.00 if b1_residency == "Singapore Citizen (SC)" and b1_prop_count == 0 else (0.20 if b1_residency == "Singapore Citizen (SC)" and b1_prop_count == 1 else (0.30 if b1_residency == "Singapore Citizen (SC)" else 0.60))))
    b2_rate = (0.05 if b2_residency == "Permanent Resident (PR)" and b2_prop_count == 0 else (0.30 if b2_residency == "Permanent Resident (PR)" else (0.00 if b2_residency == "Singapore Citizen (SC)" and b2_prop_count == 0 else (0.20 if b2_residency == "Singapore Citizen (SC)" and b2_prop_count == 1 else (0.30 if b2_residency == "Singapore Citizen (SC)" else 0.60))))) if has_multiple_buyers else 0.0
    effective_absd_rate = max(b1_rate, b2_rate)

    tenure = min(65 - target_age, 25 if target_property_type == "HDB Resale Flat" else 30)
    effective_ltv_cap = 0.55 if (target_age + tenure > 65) else 0.75

    def compute_scenario_metrics(price_point):
        if price_point <= 180000: b_sd = price_point * 0.01
        elif price_point <= 360000: b_sd = (price_point * 0.02) - 1800
        elif price_point <= 1000000: b_sd = (price_point * 0.03) - 5400
        elif price_point <= 1500000: b_sd = (price_point * 0.04) - 15400
        elif price_point <= 3000000: b_sd = (price_point * 0.05) - 30400
        else: b_sd = (price_point * 0.06) - 60400
        a_sd = price_point * effective_absd_rate
        min_cash = price_point * (0.05 if effective_ltv_cap == 0.75 else 0.10)
        req_entry = (price_point * (1.0 - effective_ltv_cap)) + b_sd + a_sd + legal_fee_buying
        status = "Safe Match 👍" if total_fluid_reserves_pool >= req_entry else "Budget Overstretch 🚨"
        if total_fluid_reserves_pool >= (req_entry + 150000.0) and status != "Budget Overstretch 🚨": status = "High Surplus ✅"
        return b_sd, a_sd, min_cash, req_entry, status

    bsd_l, absd_l, cash_l, req_l, status_l = compute_scenario_metrics(p_low)
    bsd_m, absd_m, cash_m, req_m, status_m = compute_scenario_metrics(p_mid)
    bsd_h, absd_h, cash_h, req_h, status_h = compute_scenario_metrics(p_high)

    # --- TAB 2: FINANCIAL MATRIX ---
    with tab2:
        st.markdown("### 💰 Comparative Financial Scenarios Matrix")
        col_summary, col_table = st.columns([1, 3])
        with col_summary:
            st.markdown("##### 🧾 Summary Pool of Capital")
            st.metric(label="Net Cash Proceeds (Sale)", value=fmt_sgd(gross_cash_profit))
            st.metric(label="Total Co-Mingled CPF OA", value=fmt_sgd(total_refunded_cpf_oa_pool))
            st.metric(label="Total Aggregate Liquid Capital", value=fmt_sgd(total_fluid_reserves_pool))
        with col_table:
            scenario_df = pd.DataFrame({
                "Financial Breakdown Components": ["Target Purchase Price Point", "Buyer's Stamp Duty (BSD)", "Additional Buyer's Stamp Duty (ABSD)", "Minimum Hard Cash Downpayment Component", "Total Initial Outlay Entry Cost Required", "Net Capital Surplus / (Shortfall Position)", "Affordability Profile Status Evaluation"],
                "Scenario 1 (Lowest Range Bounds)": [fmt_sgd(p_low), fmt_sgd(bsd_l), fmt_sgd(absd_l), fmt_sgd(cash_l), fmt_sgd(req_l), fmt_sgd(total_fluid_reserves_pool - req_l), status_l],
                "Scenario 2 (Midpoint Bounds)": [fmt_sgd(p_mid), fmt_sgd(bsd_m), fmt_sgd(absd_m), fmt_sgd(cash_m), fmt_sgd(req_m), fmt_sgd(total_fluid_reserves_pool - req_m), status_m],
                "Scenario 3 (Highest Range Ceiling)": [fmt_sgd(p_high), fmt_sgd(bsd_h), fmt_sgd(absd_h), fmt_sgd(cash_h), fmt_sgd(req_h), fmt_sgd(total_fluid_reserves_pool - req_h), status_h]
            })
            st.table(scenario_df)

    # --- TAB 3: TIMELINE ---
    with tab3:
        st.markdown("### ⏳ Chronological Gantt Project Capital Flight Schedule")
        gantt_clean_data = pd.DataFrame([
            {"Stage Component Description": "Stage 1: OTP Option Booking", "Start Week": 0, "Duration Weeks": 1},
            {"Stage Component Description": "Stage 2: Contract Execution / Duties", "Start Week": 1, "Duration Weeks": 3},
            {"Stage Component Description": "Stage 3: Completion & Conveyancing Balance", "Start Week": 4, "Duration Weeks": 8}
        ])
        st.bar_chart(gantt_clean_data, x="Stage Component Description", y=["Start Week", "Duration Weeks"], horizontal=True, use_container_width=True)

    # TAB 4: LIVE LISTING INSIGHTS (CONNECTED TO SPATIAL ENGINE) ---
    with tab4:
        st.markdown("### 📈 Live Dynamic Property Matching Portfolio")
        
        # Dynamic market extraction call replaces your old hardcoded raw_listings array
        filtered_listings = spatial_engine.generate_live_inventory(
            selected_districts=selected_districts,
            target_property_type=target_property_type,
            price_min=p_low,
            price_max=p_high
        )
        
        if not filtered_listings: 
            st.info("No live inventory listings match your specified price parameters and District filters.")
        else:
            processed_listings_rows = []
            for serial_num, item in enumerate(filtered_listings, start=1):
                price_val = item["Price"]
                req_entry = (price_val * (1.0 - effective_ltv_cap)) + bsd_h + absd_h + legal_fee_buying
                status_label = "Budget Overstretch 🚨" if total_fluid_reserves_pool < req_entry else ("High Surplus ✅" if total_fluid_reserves_pool >= (req_entry + 150000.0) else "Safe Match 👍")
                
                processed_listings_rows.append({
                    "S/N": f"{serial_num:02d}", 
                    "Project Name Location": item["Project"], 
                    "Geographic District": item["District"], 
                    "Est. Size / PSF": f"{item['Size (Sqft)']} @ {item['Est. PSF']}",
                    "Market Valuation Listing Price": fmt_sgd(price_val), 
                    "Affordability Diagnostic Metric": status_label, 
                    "Live Advertisement Reference Link": item["URL"]
                })
            st.dataframe(
                pd.DataFrame(processed_listings_rows), 
                column_config={"Live Advertisement Reference Link": st.column_config.LinkColumn("View Marketplace Property Listing URL")}, 
                hide_index=True, 
                use_container_width=True
            )

    # --- EXECUTIVE SUMMARY PDF EXPORTER ---
    st.markdown("---")
    st.subheader("📄 Executive Client Deliverable Workspace")
    
    report_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; line-height: 1.5; }}
            .header {{ border-bottom: 3px solid #1f77b4; padding-bottom: 10px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; color: #1f77b4; font-size: 24px; }}
            .header p {{ margin: 5px 0 0 0; font-size: 12px; color: #666; }}
            .section {{ margin-bottom: 25px; }}
            .section h2 {{ font-size: 16px; border-left: 4px solid #1f77b4; padding-left: 8px; color: #222; margin-bottom: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 12px; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .highlight {{ font-weight: bold; color: #1f77b4; }}
            .footer {{ margin-top: 40px; font-size: 10px; color: #999; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ RES Financial Assessment Report</h1>
            <p>Prepared dynamically by system advisor engine framework under registered CEA License Assignment: <strong>{st.session_state['agent_license']}</strong></p>
        </div>
        <div class="section">
            <h2>👤 Client Case Context</h2>
            <p>Operating Primary Identifier Target Profile Sequence Variant: <strong>{client_primary_key}</strong></p>
        </div>
        <div class="section">
            <h2>💰 Capital Runway & Balance Sheet Summary</h2>
            <table>
                <tr><th>Component Field Category Description</th><th>Assigned Asset Valuation Weight</th></tr>
                <tr><td>Net Property Disposal Cash Proceeds Target</td><td>{fmt_sgd(gross_cash_profit)}</td></tr>
                <tr><td>Total Co-Mingled/Combined CPF OA Allocation Pool</td><td>{fmt_sgd(total_refunded_cpf_oa_pool)}</td></tr>
                <tr><td class="highlight">Total Aggregate Liquid Financial Reserves Availability</td><td class="highlight">{fmt_sgd(total_fluid_reserves_pool)}</td></tr>
            </table>
        </div>
        <div class="section">
            <h2>📊 Comparative Pricing Matrix Strategy</h2>
            <table>
                <tr><th>Metric Parameters</th><th>Scenario 1 (Lowest)</th><th>Scenario 2 (Midpoint)</th><th>Scenario 3 (Highest Ceiling)</th></tr>
                <tr><td>Valuation Target Point</td><td>{fmt_sgd(p_low)}</td><td>{fmt_sgd(p_mid)}</td><td>{fmt_sgd(p_high)}</td></tr>
                <tr><td>Buyer's Stamp Duty (BSD)</td><td>{fmt_sgd(bsd_l)}</td><td>{fmt_sgd(bsd_m)}</td><td>{fmt_sgd(bsd_h)}</td></tr>
                <tr><td>Additional Buyer's Stamp Duty (ABSD)</td><td>{fmt_sgd(absd_l)}</td><td>{fmt_sgd(absd_m)}</td><td>{fmt_sgd(absd_h)}</td></tr>
                <tr><td>Minimum Capital Required</td><td>{fmt_sgd(req_l)}</td><td>{fmt_sgd(req_m)}</td><td>{fmt_sgd(req_h)}</td></tr>
                <tr class="highlight"><td>Affordability Status</td><td>{status_l}</td><td>{status_m}</td><td>{status_h}</td></tr>
            </table>
        </div>
        <div class="footer">
            <p>Confidential Deliverable Statement. Isolated in memory under full PDPA compliance minimisation standard principles. Printed on: 2026-05-24.</p>
        </div>
    </body>
    </html>
    """

    st.info("💡 **Advisor Action Tool:** Click the button below to review the formatted executive summary canvas. To print or save it seamlessly as a premium client deliverable, press **Cmd + P** (Mac) or **Ctrl + P** (Windows) within the popup window layout.")
    
    if st.button("🖥️ Open Professional Print-Ready Report Canvas"):
        b64_html = base64.b64encode(report_html.encode('utf-8')).decode('utf-8')
        custom_js_popup = f"""
            <script>
                var win = window.open();
                win.document.write(atob("{b64_html}"));
                win.document.close();
                win.print();
            </script>
        """
        st.components.v1.html(custom_js_popup, height=0, width=0)

# ==========================================
# AGENT LOGIN GATEWAY LAYOUT
# ==========================================
else:
    action = st.radio("Choose Action:", ["Existing Agent Sign-In", "New Agent Registration"])
    if action == "New Agent Registration":
        st.subheader("📝 Register for Engine Access")
        new_name = st.text_input("Full Name (as per CEA)")
        new_license = st.text_input("CEA License Number (e.g., R123456A)")
        st.caption("🔒 **PDPA Notice:** Registration collects data solely for CEA verification.")
        consent = st.checkbox("I consent to data processing for verification purposes.")
        if st.button("Submit Registration"):
            if not consent: st.error("🚨 You must consent to the PDPA policy to register.")
            elif new_name and new_license:
                with open(data_layer.AGENTS_CSV, "a", newline='') as f:
                    import csv
                    csv.writer(f).writerow([new_name.strip(), new_license.strip().upper(), "pending"])
                st.success("🎉 Registration submitted! Awaiting Admin Approval within 3 business day.")
            else: st.error("Please fill in all fields.")
    elif action == "Existing Agent Sign-In":
        st.subheader("🔑 Agent Authentication Gate")
        login_credential = st.text_input("Enter Your Registered Full Name OR CEA License Number")
        if st.button("Sign In"):
            if login_credential:
                is_allowed, result_flag = check_access_flexible(login_credential)
                if is_allowed:
                    st.session_state["logged_in"] = True
                    st.session_state["agent_license"] = result_flag
                    st.rerun()
                elif result_flag == "pending": st.info("⏳ Status: Pending Admin approval.")
                elif result_flag == "rejected": st.error("🚨 Access Denied / Application Rejected.")
                else: st.error("🚨 Access Denied: Identifier not found.")