import streamlit as st
import pandas as pd
import pydeck as pdk
import os
import urllib.parse
from utils.analytics import extract_cma_insights  # Import math calculator

def show_dashboard_page(df):
    col_title, col_logout = st.columns([0.85, 0.15])
    with col_title:
        st.title("📊 HDB Admin Dashboard")
    with col_logout:
        if st.button("Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if df is None or df.empty:
        st.warning("⚠️ Waiting for data pipeline data...")
        return

    # --- RENAME STEP: Map pipeline headers to the short names your dashboard expects ---
    df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
    
    # Clean spatial anomalies safely
    df = df.dropna(subset=['lat', 'lon'])
    df = df[(df['lat'] != 'N/A') & (df['lon'] != 'N/A')]
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
    if 'resale_price' in df.columns:
        df['resale_price'] = df['resale_price'].astype(float)
    
    # Clean temporal anomalies
    df = df.dropna(subset=['month'])  
    df = df[df['month'].astype(str).str.contains('-', na=False)] 
    
    # Safely extract Year integer
    def extract_year(val):
        try:
            return int(str(val).split('-')[0])
        except (ValueError, IndexError, TypeError):
            return None
            
    df['year'] = df['month'].apply(extract_year)
    df = df.dropna(subset=['year']) 
    df['year'] = df['year'].astype(int) 

    # --- SIDEBAR FILTERS (Shared across views) ---
    st.sidebar.header("Admin Controls")
    
    town_list = sorted(df['town'].unique())
    selected_town = st.sidebar.selectbox("Select Target Town", ["All"] + town_list)

    safe_years = df['year'].dropna()
    if not safe_years.empty:
        min_year = int(safe_years.min())
        max_year = int(safe_years.max())
    else:
        min_year = 2020
        max_year = 2026
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Timeline Filter")
    
    if min_year < max_year:
        selected_year_range = st.sidebar.slider(
            "Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year), step=1
        )
    else:
        st.sidebar.info(f"📅 Currently showing data for year: **{min_year}**")
        selected_year_range = (min_year, max_year)

    # Filter Data for the Map/Logs
    filtered_df = df.copy()
    if selected_town != "All":
        filtered_df = filtered_df[filtered_df['town'] == selected_town]
    filtered_df = filtered_df[
        (filtered_df['year'] >= selected_year_range[0]) & (filtered_df['year'] <= selected_year_range[1])
    ]

    # --- CREATE THE TABS ---
    tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Spatial Map", "📋 System Logs", "🎯 Instant Comparative Market Analysis"])

    # ==========================================
    # TAB 1: ORIGINAL SPATIAL MAP VIEW
    # ==========================================
    with tab1:
        st.metric("Total Active Records", f"{len(filtered_df):,}")
        st.subheader("Interactive Property Spatial Map")
        view_state = pdk.ViewState(latitude=1.3521, longitude=103.8198, zoom=11, pitch=30)
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            filtered_df,
            get_position="[lon, lat]",
            get_fill_color=[76, 201, 240, 160], 
            get_radius=50,
            pickable=True,
        )
        
        st.pydeck_chart(pdk.Deck(
            layers=[layer], 
            initial_view_state=view_state,
            tooltip={
                "html": """
                    <b>📍 Location:</b> BLK {block} {street_name}<br/>
                    <b>📅 Transacted:</b> {month}<br/>
                    <b>🛏️ Rooms:</b> {flat_type}<br/>
                    <b>📐 Unit Variant:</b> {flat_model}<br/>
                    <b>🏢 Storey Height:</b> {storey_range}<br/>
                    <b>💰 Transacted Price:</b> ${resale_price}
                """,
                "style": {
                    "backgroundColor": "rgba(0, 0, 0, 0.85)", "color": "white",
                    "fontFamily": "sans-serif", "fontSize": "13px", "padding": "10px", "borderRadius": "5px"
                }
            }
        ))

    # ==========================================
    # TAB 2: ORIGINAL SYSTEM LOGS DATA FRAME
    # ==========================================
    with tab2:
        st.subheader("System Data Log")
        st.dataframe(filtered_df[['month', 'town', 'flat_type', 'block', 'street_name', 'resale_price']].head(50), use_container_width=True)

    # ==========================================
    # UX OPTIMIZED TAB 3: CMA ENGINE
    # ==========================================
    with tab3:
        st.subheader("🎯 Instant Comparative Market Analysis")
        st.markdown(
            "Select an asset anchor below. The engine will seamlessly isolate identical property classes "
            "within a strict **500m walking radius** transacted over a 5-year rolling horizon."
        )
        
        if 'display_address' in df.columns:
            unique_addresses = sorted(df['display_address'].dropna().unique())
            selected_address = st.selectbox(
                "🔍 Search target property street or block:", 
                unique_addresses,
                index=0,
                help="Type to autocomplete any block or street name from the pipeline database."
            )
            matched_rows = df[df['display_address'] == selected_address]
        else:
            matched_rows = pd.DataFrame()

        if not matched_rows.empty:
            sample_row = matched_rows.iloc[0]
            default_lat = float(sample_row['lat'])
            default_lon = float(sample_row['lon'])
            default_town = str(sample_row['town'])
            default_size = float(sample_row.get('floor_area_sqm', 93.0))
            default_type = "HDB" 
        else:
            default_lat, default_lon, default_town, default_size, default_type = 1.3521, 103.8198, "Ang Mo Kio", 93.0, "HDB"

        with st.expander("⚙️ Refine Comparison Parameters", expanded=True):
            exp_col1, exp_col2, exp_col3 = st.columns(3)
            with exp_col1:
                p_type = st.selectbox("Property Class Match:", ["HDB", "Condo", "Landed"], index=0)
            with exp_col2:
                size_metric = st.radio("Measurement System:", ["Sqm", "Sqft"], horizontal=True)
            with exp_col3:
                initial_size_display = default_size if size_metric == "Sqm" else default_size * 10.764
                size_input = st.number_input(f"Target Size ({size_metric}):", min_value=10.0, value=float(initial_size_display))
                
                target_size_sqm = size_input if size_metric == "Sqm" else size_input / 10.764

        st.markdown("### 📊 Valuation Insights")
        
        cma_data, median_val, total_matches = extract_cma_insights(
            target_lat=default_lat, target_lon=default_lon, target_sqft=target_size_sqm, target_type=p_type, historical_df=df
        )
            
        if total_matches > 0:
            k1, k2 = st.columns(2)
            with k1:
                st.metric(
                    label="Estimated Fair Market Median", 
                    value=f"${median_val:,.0f}",
                    delta=f"Based on {total_matches} local comparables",
                    delta_color="off"
                )
            with k2:
                st.success(f"✅ Data Density Confirmed: Strong valuation statistical support within 500m of {default_town}.")
            
            st.markdown("#### Price Trend vs Proximity Distance (Meters)")
            chart_data = cma_data[['distance_meters', 'resale_price']].copy()
            chart_data = chart_data.sort_values('distance_meters').set_index('distance_meters')
            st.scatter_chart(chart_data, y="resale_price", use_container_width=True)
            
            st.markdown("#### Micro-Neighborhood Comparable Ledger")
            display_cols = [c for c in ['month', 'block', 'street_name', 'storey_range', 'floor_area_sqm', 'resale_price', 'distance_meters'] if c in cma_data.columns]
            
            formatted_cma = cma_data[display_cols].copy()
            formatted_cma['distance_meters'] = formatted_cma['distance_meters'].round(1).astype(str) + " m"
            if 'resale_price' in formatted_cma.columns:
                formatted_cma['resale_price'] = formatted_cma['resale_price'].map('${:,.0f}'.format)
                
            st.dataframe(formatted_cma.sort_values(by='distance_meters').head(15), use_container_width=True)
        else:
            st.info(f"ℹ️ No identical historical matches discovered inside a 500m loop around this coordinate matching a {size_input} {size_metric} footprint.")
            
        st.markdown("---")
        st.subheader("🌐 External Live Market Validation")
        
        min_size_sqft = int(target_size_sqm * 10.764 * 0.90)
        max_size_sqft = int(target_size_sqm * 10.764 * 1.10)
        
        pg_freetext = urllib.parse.quote(default_town)
        pg_resource_url = f"https://www.propertyguru.com.sg/property-for-sale?freetext={pg_freetext}&market=residential&minSize={min_size_sqft}&maxSize={max_size_sqft}"
        
        st.link_button(
            label=f"🚀 Launch Targeted PropertyGuru Portal ({min_size_sqft}-{max_size_sqft} sqft in {default_town})",
            url=pg_resource_url, 
            use_container_width=True,
            type="secondary"
        )