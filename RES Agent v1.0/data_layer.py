import os
import pandas as pd
import threading

# Thread lock to guarantee multi-agent safety during simultaneous writes
_csv_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_CSV = os.path.join(BASE_DIR, "agents.csv")
CLIENTS_CSV = os.path.join(BASE_DIR, "clients.csv")

REQUIRED_HEADERS = [
    "client_pk", "client_name", "phone_last4", "created_at",
    "sale_val", "loan", "cpf_accrued", "p_low", "p_high", 
    "target_type", "cash", "cpf_static"
]

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
            # Create agents file with blank dataframe structurally matching layout
            if not os.path.exists(AGENTS_CSV):
                with open(AGENTS_CSV, "w") as f: pass

def get_master_ledger():
    """Optimized generator for the sidebar portfolio table."""
    if not os.path.exists(CLIENTS_CSV) or os.path.getsize(CLIENTS_CSV) == 0:
        return pd.DataFrame(columns=["Client Name", "Phone (Last 4)", "Logged On", "Days Active"])
    
    with _csv_lock:
        df = pd.read_csv(CLIENTS_CSV)
        
    if df.empty or 'client_name' not in df.columns:
        return pd.DataFrame(columns=["Client Name", "Phone (Last 4)", "Logged On", "Days Active"])
        
    # 1. Select the relevant columns
    clean_master = df[['client_name', 'phone_last4', 'created_at']].copy()
    
    # 2. Robust conversion (handles both old YYYY-MM-DD and new DD/MM/YYYY)
    clean_master['created_at'] = pd.to_datetime(clean_master['created_at'], dayfirst=True, format='mixed')
    
    # 3. Calculate duration before converting to string
    today = pd.Timestamp.now().normalize()
    clean_master['Days Active'] = (today - clean_master['created_at']).dt.days
    
    # 4. Sort by the actual datetime object
    clean_master = clean_master.sort_values(by="created_at", ascending=False)
    
    # 5. Format for UI
    clean_master['created_at'] = clean_master['created_at'].dt.strftime('%d/%m/%Y')
    
    # 6. Final rename
    clean_master.columns = ["Client Name", "Phone (Last 4)", "Logged On", "Days Active"]
    
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

from datetime import datetime

def save_client_profile(client_name, phone_last4, current_property_value, outstanding_loan, 
                        total_accrued_cpf_to_return, p_low, p_high, target_type, 
                        available_cash_savings, total_static_cpf):
    """Sanitizes inputs and locks the client profile with preferences and timestamp."""
    
    clean_name = str(client_name).strip()
    if " " in clean_name:
        raise ValueError("🚨 Formatting Violation: Client Name strings cannot contain spaces.")
        
    clean_phone = str(phone_last4).strip()
    client_primary_key = f"{clean_name}_{clean_phone}"
    timestamp = datetime.now().strftime("%d/%m/%Y")
    
    # Add new fields to the payload
    row_payload = [
        client_primary_key, clean_name, clean_phone, timestamp,
        float(current_property_value), float(outstanding_loan), 
        float(total_accrued_cpf_to_return), float(p_low), float(p_high), 
        target_type, float(available_cash_savings), float(total_static_cpf)
    ]
    
    with _csv_lock:
        df_ex = pd.read_csv(CLIENTS_CSV)
        if not df_ex.empty and 'client_pk' in df_ex.columns:
            df_ex = df_ex[df_ex['client_pk'] != client_primary_key]
            
        df_new_row = pd.DataFrame([row_payload], columns=REQUIRED_HEADERS)
        pd.concat([df_ex, df_new_row]).to_csv(CLIENTS_CSV, index=False)
        
    return client_primary_key

# Start (agent list)
def update_agent_status(license_id, new_status):
    """Updates an agent's status to Pending, On Hold, Active, or Rejected."""
    with _csv_lock:
        df = get_agent_registry()
        # Find the row by License ID and update the Status column
        df.loc[df['License ID'] == license_id, 'Status'] = new_status
        df.to_csv(AGENTS_CSV, index=False)
# End (agent list)