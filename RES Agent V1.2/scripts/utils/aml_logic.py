# scripts/utils/aml_logic.py
import sys
import os

# Ensure the root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the correct module from the 'layers' folder
from layers import compliance as data_layer

def verify_aml_status(client_id):
    """
    Primary gate for AML compliance.
    """
    # 1. Fetch client data from the vault (data_layer.py)
    client_data = data_layer.load_client(client_id)
    
    # 2. Check against internal sanctions/PEP registry
    if client_data.get('is_sanctioned') or client_data.get('is_pep'):
        return False, "AML_CHECK_FAILED: Client flagged in PEP/Sanctions database."
    
    # 3. Verify identity verification (KYC) documentation exists
    if not client_data.get('has_id_verification'):
        return False, "AML_CHECK_FAILED: Missing mandatory KYC/Identity documents."
        
    return True, "AML_CHECK_PASSED"

def log_compliance_attempt(client_id, result, reason):
    """
    Crucial for audit trails; logs every compliance check for CEA inspections.
    """
    # Saves to feature_logs.json in data/raw/crm/
    log_entry = {"client_id": client_id, "result": result, "reason": reason, "timestamp": "current_time"}
    data_layer.save_audit_log(log_entry)