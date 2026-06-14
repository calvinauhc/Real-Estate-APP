# import pandas as pd
# import os
# import streamlit as st
# import re
# from datetime import datetime

# # --- MAPPING CONSTANT ---
# # Add this so you can convert postal codes to districts later
# SECTOR_TO_DISTRICT_INT = {
#     1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 14: 3, 15: 3, 16: 3,
#     9: 4, 10: 4, 11: 5, 12: 5, 13: 5, 17: 6, 18: 7, 19: 7, 20: 8, 21: 8,
#     22: 9, 23: 9, 24: 10, 25: 10, 26: 10, 27: 10, 28: 11, 29: 11, 30: 11,
#     31: 12, 32: 12, 33: 12, 34: 13, 35: 13, 36: 13, 37: 13, 38: 14, 39: 14,
#     40: 14, 41: 14, 42: 15, 43: 15, 44: 15, 45: 15, 46: 16, 47: 16, 48: 16,
#     49: 17, 50: 17, 51: 18, 52: 18, 53: 19, 54: 19, 55: 19, 56: 20, 57: 20,
#     58: 21, 59: 21, 60: 22, 61: 22, 62: 22, 63: 22, 64: 22, 65: 23, 66: 23,
#     67: 23, 68: 23, 69: 24, 70: 24, 71: 24, 72: 25, 73: 25, 75: 27, 76: 27,
#     77: 26, 78: 26, 79: 28, 80: 28
# }

# # --- HELPER FUNCTIONS ---
# def get_remaining_lease(tenure_str):
#     if not isinstance(tenure_str, str): return 99
#     if "Freehold" in tenure_str: return 999
#     match = re.search(r'(\d{4})', tenure_str)
#     return 99 - (datetime.now().year - int(match.group(1))) if match else 99

# def postal_to_district(postal_code):
#     """Call this to turn 6-digit code into DXX format"""
#     sector = str(postal_code)[:2]
#     return SECTOR_TO_DISTRICT.get(sector, "Unknown")

# # --- CORE LOGIC ---
# def get_valuation(postal_sector, comparison_key, sqft):
#     try:
#         ref_path = "data/avg_valuation_ref.csv"
#         if not os.path.exists(ref_path): return None
        
#         # Load and clean the reference data
#         ref = pd.read_csv(ref_path)
#         ref['postal_sector'] = pd.to_numeric(ref['postal_sector'], errors='coerce')
        
#         # Filter by sector (int) and comparison key
#         match = ref[(ref['postal_sector'] == int(postal_sector)) & 
#                     (ref['comparison_key'] == comparison_key)]
        
#         if match.empty:
#             return None
        
#         # Use mean to get a realistic market average if multiple transactions exist
#         avg_psf = match['price_psf'].mean()
#         return avg_psf * float(sqft)
    
#     except Exception as e:
#         print(f"Valuation error: {e}")
#         return None

# def render_valuation_test(client_data):
#     st.subheader("Market Valuation Estimate")

#     # 1. DEFINE & CLEAN VARIABLES
#     # Ensure prop_type, tenure, and sqft are never 'nan'
#     prop_type = client_data.get('property_type')
#     tenure = client_data.get('tenure')
#     sqft = client_data.get('sqft')
#     postal_code = client_data.get('postal_code')

#     # 2. VALIDATE & DEFAULT
#     # Only proceed if we have the minimum info needed to define our 3 variables
#     if not postal_code or not prop_type or not sqft:
#         st.warning("Please ensure Postal Code, Property Type, and Sqft are provided.")
#         return

#     # 3. CONSTRUCT THE 3 VARIABLES
#     # Variable A: Postal Sector
#     sector_int = int(str(postal_code)[:2])
#     postal_sector = SECTOR_TO_DISTRICT_INT.get(sector_int, 0)
    
#     # Variable B: Comparison Key
#     comparison_key = f"Private-{prop_type}-{tenure}"
    
#     # Variable C: Sqft (already defined above)
    
#     # 4. EXECUTE VALUATION
#     if postal_sector > 0:
#         val = get_valuation(postal_sector, comparison_key, sqft)
#         st.write(f"Estimated Value: {val}")
        
        
# def process_raw_data():
#     # Load the raw file
#     ura_df = pd.read_csv("data/raw/URA_apartment_condo.csv", encoding='latin1')
    
#     # 1. Clean Postal District (Ensure integer)
#     # We use errors='coerce' to turn bad data into NaN, then drop it
#     ura_df['postal_sector'] = pd.to_numeric(ura_df['Postal District'], errors='coerce')
#     ura_df = ura_df.dropna(subset=['postal_sector'])
#     ura_df['postal_sector'] = ura_df['påostal_sector'].astype(int)
    
#     # 2. Clean Price: Strip commas, spaces, and dollar signs, then convert to numeric
#     # This specifically targets the "2,278" format
#     price_col = ura_df['Unit Price ($ PSF)'].astype(str)
#     price_col = price_col.str.replace(r'[$,\s]', '', regex=True)
#     ura_df['price_psf'] = pd.to_numeric(price_col, errors='coerce')
    
#     # 3. Handle any potential rows where price couldn't be converted
#     ura_df = ura_df.dropna(subset=['price_psf'])
    
#     # 4. Finalize
#     ura_df = ura_df.rename(columns={'Tenure': 'tenure_display'})
#     ura_df['comparison_key'] = "Private-" + ura_df['Property Type'] + "-" + ura_df['tenure_display']
    
#     # Save the clean file
#     ura_df.to_csv("data/avg_valuation_ref.csv", index=False)
#     print("Data processed and saved successfully.")

import pandas as pd
import os
import streamlit as st
import re
from datetime import datetime

# --- MAPPING CONSTANT ---
SECTOR_TO_DISTRICT_INT = {
    1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 14: 3, 15: 3, 16: 3,
    9: 4, 10: 4, 11: 5, 12: 5, 13: 5, 17: 6, 18: 7, 19: 7, 20: 8, 21: 8,
    22: 9, 23: 9, 24: 10, 25: 10, 26: 10, 27: 10, 28: 11, 29: 11, 30: 11,
    31: 12, 32: 12, 33: 12, 34: 13, 35: 13, 36: 13, 37: 13, 38: 14, 39: 14,
    40: 14, 41: 14, 42: 15, 43: 15, 44: 15, 45: 15, 46: 16, 47: 16, 48: 16,
    49: 17, 50: 17, 51: 18, 52: 18, 53: 19, 54: 19, 55: 19, 56: 20, 57: 20,
    58: 21, 59: 21, 60: 22, 61: 22, 62: 22, 63: 22, 64: 22, 65: 23, 66: 23,
    67: 23, 68: 23, 69: 24, 70: 24, 71: 24, 72: 25, 73: 25, 75: 27, 76: 27,
    77: 26, 78: 26, 79: 28, 80: 28
}

@st.cache_data
def get_ref_data():
    """Load reference data into memory once for performance."""
    if os.path.exists("data/avg_valuation_ref.csv"):
        return pd.read_csv("data/avg_valuation_ref.csv")
    return pd.DataFrame()

def get_valuation(postal_sector, comparison_key, target_sqft):
    """Calculates valuation using a 15% size buffer for accuracy."""
    try:
        df = get_ref_data()
        if df.empty: return 0.0
        
        # 15% Size buffer for refined matching
        lower = target_sqft * 0.85
        upper = target_sqft * 1.15
        
        match = df[
            (df['postal_sector'] == int(postal_sector)) & 
            (df['comparison_key'] == comparison_key) &
            (df['sqft'] >= lower) & (df['sqft'] <= upper)
        ]
        
        return match['price_psf'].mean() * float(target_sqft) if not match.empty else 0.0
    except Exception as e:
        return 0.0

def process_raw_data():
    """Cleans raw URA data for use in the valuation engine."""
    ura_df = pd.read_csv("data/raw/URA_apartment_condo.csv", encoding='latin1')
    
    # 1. Clean Postal District
    ura_df['postal_sector'] = pd.to_numeric(ura_df['Postal District'], errors='coerce')
    ura_df.dropna(subset=['postal_sector'], inplace=True)
    ura_df['postal_sector'] = ura_df['postal_sector'].astype(int)
    
    # 2. Extract SQFT (Ensure your raw CSV has an 'Area (SQFT)' column)
    ura_df['sqft'] = pd.to_numeric(ura_df['Area (SQFT)'], errors='coerce')
    
    # 3. Clean Price PSF
    price_col = ura_df['Unit Price ($ PSF)'].astype(str).str.replace(r'[$,\s]', '', regex=True)
    ura_df['price_psf'] = pd.to_numeric(price_col, errors='coerce')
    
    # 4. Finalize & Save
    ura_df['comparison_key'] = "Private-" + ura_df['Property Type'] + "-" + ura_df['Tenure']
    ura_df.dropna(subset=['postal_sector', 'sqft', 'price_psf'], inplace=True)
    
    ura_df.to_csv("data/avg_valuation_ref.csv", index=False)
    print("Data processed successfully.")

def render_valuation_test(client_data):
    """UI Helper to test the engine."""
    st.subheader("Market Valuation Estimate")
    # Access nested data
    curr = client_data.get('current_property', {})
    
    postal = curr.get('postal_code')
    prop_type = curr.get('property_type')
    sqft = curr.get('sqft')
    tenure = curr.get('tenure')

    if not all([postal, prop_type, sqft]):
        st.warning("Ensure Postal Code, Type, and Sqft are provided.")
        return

    sector = SECTOR_TO_DISTRICT_INT.get(int(str(postal)[:2]), 0)
    key = f"Private-{prop_type}-{tenure}"
    
    val = get_valuation(sector, key, sqft)
    st.metric("Estimated Market Value", f"${val:,.0f}")