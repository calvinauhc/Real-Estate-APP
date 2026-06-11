import pandas as pd
import os

# Ensure the folder structure exists
DATA_DIR = "data/crm"
DATA_PATH = os.path.join(DATA_DIR, "dim_clients.csv")

def init_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(DATA_PATH):
        # Update this list to include all your new tracking fields
        columns = [
            "client_id", "client_name", "phone_last4", "district", "agent_license", 
            "assets_cash", "loan_amount", "cpf_available", "cpf_accrued_return", 
            "ownership_type", "desired_price", "property_type", "rooms", "tenure", "is_active",
            "monthly_income", "monthly_debt", "qualified_loan_amount", "affordability_status"
        ]
        df = pd.DataFrame(columns=columns)
        df['affordability_status'] = df['affordability_status'].astype(str) # Set explicitly
        df['affordability_status'] = "" # Fill with empty string
        df.to_csv(DATA_PATH, index=False)

# This points to the folder where data_layer.py is, then looks for 'data/dim_client.csv'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up from 'modules/' to the root, then into 'data/'
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'dim_client.csv'))

def load_clients():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame() # Return empty if file missing
    return pd.read_csv(DATA_PATH)

def save_client(client_record):
    # 1. Load the existing file
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        # If no file, start with an empty dataframe
        df = pd.DataFrame()

    # 2. Check if the record already exists and remove the OLD version
    # This prevents duplicates and overwrites
    if 'client_id' in df.columns:
        # Keep only the rows where the ID is NOT the one we are updating
        df = df[df['client_id'] != client_record['client_id']]
    
    # 3. Create a DataFrame for the new/updated record
    new_record_df = pd.DataFrame([client_record])
    
    # 4. Combine the old data (minus the old version) with the new version
    final_df = pd.concat([df, new_record_df], ignore_index=True)
    
    # 5. Save the combined data back to the file
    final_df.to_csv(DATA_PATH, index=False)
    
    return True, "Client saved successfully."

def update_client_qualification(client_id, qualification_data, inputs):
    df = load_clients()
    
    # 1. Update Input Fields (including new Bank/CPF fields)
    df.loc[df['client_id'] == client_id, 'monthly_income'] = float(inputs['income'])
    df.loc[df['client_id'] == client_id, 'monthly_debt'] = float(inputs['debt'])
    df.loc[df['client_id'] == client_id, 'assets_cash'] = float(inputs['cash'])
    df.loc[df['client_id'] == client_id, 'cpf_available'] = float(inputs['cpf'])
    
    # NEW FIELDS
    df.loc[df['client_id'] == client_id, 'loan_amount'] = float(inputs['loan_amt'])
    df.loc[df['client_id'] == client_id, 'cpf_accrued_return'] = float(inputs['cpf_accrued'])
    
    # 2. Update Result Fields
    df.loc[df['client_id'] == client_id, 'qualified_loan_amount'] = float(qualification_data['max_loan_eligible'])
    df.loc[df['client_id'] == client_id, 'affordability_status'] = 'Qualified' if qualification_data['is_affordable'] else 'Shortfall'
    
    df.to_csv(DATA_PATH, index=False)
    return True, "Client profile updated successfully!"

def delete_client(client_id):
    df = load_clients()
    # Filter out the row with the matching ID
    df = df[df['client_id'] != client_id]
    df.to_csv(DATA_PATH, index=False)
    return True, "Client deleted successfully!"