import os
import pandas as pd
import threading

# Thread lock to guarantee multi-agent safety during simultaneous writes
_csv_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_CSV = os.path.join(BASE_DIR, "agents.csv")
CLIENTS_CSV = os.path.join(BASE_DIR, "clients.csv")

REQUIRED_HEADERS = ['client_pk', 'client_name', 'phone_last4', 'sale_val', 'loan', 'cpf_accrued', 'target_price', 'cash', 'cpf_static']

def init_databases():
    """Initializes CSV files with correct headers if missing or empty."""
    with _csv_lock:
        if not os.path.exists(CLIENTS_CSV) or os.path.getsize(CLIENTS_CSV) == 0:
            pd.DataFrame(columns=REQUIRED_HEADERS).to_csv(CLIENTS_CSV, index=False)
        else:
            try:
                test_df = pd.read_csv(CLIENTS_CSV, nrows=0)
                if 'client_name' not in test_df.columns or 'phone_last4' not in test_df.columns:
                    pd.DataFrame(columns=REQUIRED_HEADERS).to_csv(CLIENTS_CSV, index=False)
            except Exception:
                pd.DataFrame(columns=REQUIRED_HEADERS).to_csv(CLIENTS_CSV, index=False)

        if not os.path.exists(AGENTS_CSV) or os.path.getsize(AGENTS_CSV) == 0:
            pd.DataFrame(columns=['name', 'license', 'status']).to_csv(AGENTS_CSV, index=False, header=False)

def get_master_ledger():
    """Optimized generator for the sidebar portfolio table."""
    if not os.path.exists(CLIENTS_CSV) or os.path.getsize(CLIENTS_CSV) == 0:
        return pd.DataFrame(columns=["Client Name", "Phone (Last 4)", "Target Price Limit"])
    
    with _csv_lock:
        df = pd.read_csv(CLIENTS_CSV)
    if df.empty or 'client_name' not in df.columns:
        return pd.DataFrame(columns=["Client Name", "Phone (Last 4)", "Target Price Limit"])
        
    clean_master = df[['client_name', 'phone_last4', 'target_price']].copy()
    clean_master.columns = ["Client Name", "Phone (Last 4)", "Target Price Limit"]
    return clean_master

def search_clients_by_phone(phone_last4):
    """Finds all clients matching the last 4 digits of a phone number."""
    if not os.path.exists(CLIENTS_CSV) or os.path.getsize(CLIENTS_CSV) == 0:
        return pd.DataFrame()
        
    with _csv_lock:
        df = pd.read_csv(CLIENTS_CSV)
    if df.empty:
        return pd.DataFrame()
        
    df['phone_last4'] = df['phone_last4'].astype(str).str.strip()
    return df[df['phone_last4'] == str(phone_last4).strip()]

def save_client_profile(client_name, phone_last4, current_property_value, outstanding_loan, total_accrued_cpf_to_return, p_high, available_cash_savings, total_static_cpf):
    """Sanitizes inputs, enforces spacing rules, and locks file for safe commit."""
    # Strict space protection guardrail
    clean_name = str(client_name).strip()
    if " " in clean_name:
        raise ValueError("🚨 Formatting Violation: Client Name strings cannot contain spaces.")
        
    clean_phone = str(phone_last4).strip()
    client_primary_key = f"{clean_name}_{clean_phone}"
    
    row_payload = [
        client_primary_key, clean_name, clean_phone, 
        float(current_property_value), float(outstanding_loan), 
        float(total_accrued_cpf_to_return), float(p_high), 
        float(available_cash_savings), float(total_static_cpf)
    ]
    
    with _csv_lock:
        df_ex = pd.read_csv(CLIENTS_CSV)
        if not df_ex.empty and 'client_pk' in df_ex.columns:
            df_ex = df_ex[df_ex['client_pk'] != client_primary_key]
            
        df_new_row = pd.DataFrame([row_payload], columns=REQUIRED_HEADERS)
        pd.concat([df_ex, df_new_row]).to_csv(CLIENTS_CSV, index=False)
        
    return client_primary_key