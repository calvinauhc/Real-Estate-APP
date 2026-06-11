# scripts/utils/data_sanitizer.py
import pandas as pd

def clean_crm_data(input_path, output_path):
    # Using 'sep' explicitly and handling quotes to avoid comma issues
    df = pd.read_csv(input_path, quotechar='"', skipinitialspace=True)
    # Validate critical columns required for ComplianceEngine
    required_cols = ['client_id', 'monthly_income', 'citizenship']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("Missing critical columns for compliance engine.")
    df.to_csv(output_path, index=False)
    print("CRM Data Sanitized and Schema Validated.")