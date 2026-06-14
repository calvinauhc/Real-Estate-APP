import pandas as pd
import os
import numpy as np
import json

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'dim_client.csv'))

def safe_int(value, default=0):
    """Safely converts a value to an integer."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def save_client(record_to_save):
    # Ensure client_id exists (critical for new records)
    if 'client_id' not in record_to_save or not record_to_save['client_id']:
        record_to_save['client_id'] = f"{record_to_save.get('client_name', 'New')}_{record_to_save.get('phone_last4', '0000')}"

    # Load existing
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        df = pd.DataFrame(columns=['client_id', 'client_name', 'phone_last4', 'current_property', 'dream_property'])

    # Remove old version if it exists to avoid duplicates
    df = df[df['client_id'] != record_to_save['client_id']]
    
    # Prepare new row
    new_record = record_to_save.copy()
    # Serialize JSON fields
    import json
    for col in ['current_property', 'dream_property']:
        if col in new_record and isinstance(new_record[col], dict):
            new_record[col] = json.dumps(new_record[col])
            
    # Add to dataframe
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)
    return True, "Saved successfully"

def load_clients():
    """Loads clients and deserializes JSON strings back into dictionaries."""
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    
    df = pd.read_csv(DATA_PATH)
    
    # 1. Deserialize district string back to list
    if 'district' in df.columns:
        df['district'] = df['district'].apply(
            lambda x: x.split(";") if isinstance(x, str) and ";" in x else ( [x] if pd.notna(x) else [])
        )
        
    # 2. Deserialize JSON strings back into dictionaries
    for key in ['current_property', 'dream_property']:
        if key in df.columns:
            df[key] = df[key].apply(
                lambda x: json.loads(x) if isinstance(x, str) else {}
            )
            
    return df

def update_client_qualification(client_id, qualification_data, inputs):
    """Updates qualification fields for a specific client."""
    df = load_clients()
    
    # Update logic...
    mask = df['client_id'] == client_id
    df.loc[mask, 'monthly_income'] = float(inputs.get('income', 0))
    df.loc[mask, 'qualified_loan_amount'] = float(qualification_data.get('max_loan_eligible', 0))
    df.loc[mask, 'affordability_status'] = 'Qualified' if qualification_data.get('is_affordable') else 'Shortfall'
    
    # Re-serialize before saving
    for key in ['current_property', 'dream_property']:
        if key in df.columns:
            df[key] = df[key].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
            
    df.to_csv(DATA_PATH, index=False)
    return True, "Client profile updated successfully!"

def delete_client(client_id):
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        if 'client_id' in df.columns:
            df = df[df['client_id'] != client_id]
            df.to_csv(DATA_PATH, index=False)
            return True
    return False