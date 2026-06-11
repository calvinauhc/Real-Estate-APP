import sys
import os
import streamlit as st
import pandas as pd

# 1. ARCHITECTURAL ANCHOR: Ensure root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. IMPORT MODULES
from scripts.utils.scorer import PropertyScorer
from scripts.utils.compliance import ComplianceEngine
from scripts.utils.financial_calc import calculate_tdsr

# 3. DATA VAULT: Load the sanitized data
try:
    df = pd.read_csv(
        'data/raw/crm/clients.csv', 
        quotechar='"', 
        skipinitialspace=True
    )
except Exception as e:
    st.error(f"Vault Connection Error: {e}")
    st.stop()

st.title("🤝 CRM Matching")
# 3. Dashboard rendering
st.subheader("Client Financial Profile")

# Ensure your dataframe 'df' is defined before this point
if not df.empty:
    st.write(f"Displaying {len(df)} clients:")
    st.dataframe(df) # This creates an interactive, scrollable table
else:
    st.warning("No client data found.")
    
# 4. LOGIC: Add automated "Affordability" column
def get_max_loan(row):
    # Ensure income/debt are numeric to avoid math errors
    income = float(row['monthly_income'])
    debt = float(row['monthly_debt'])
    
    # Calculate using imported financial_calc logic
    eligible_ratio = calculate_tdsr(income, debt)
    
    # Return max loan (Example logic: 60% of income * tenure factor)
    return eligible_ratio * 1000000 

# Apply the function
df['max_loan'] = df.apply(get_max_loan, axis=1)

# 5. DASHBOARD: Rendering
st.subheader("Client Financial Profile")
st.dataframe(df[['client_name', 'monthly_income', 'max_loan']])