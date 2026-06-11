# scripts/utils/doc_logic.py
# In hdb_logic.py, aml_logic.py, doc_logic.py:
import sys
import os

# Ensure the root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the correct module from the 'layers' folder
from layers import compliance as data_layer

def get_required_docs(transaction_type):
    """
    Returns a list of mandatory forms based on the property transaction type.
    """
    requirements = {
        "HDB_RESALE": ["Form_HDB_Resale", "CEA_Prescribed_Agreement", "EIP_Declaration"],
        "PRIVATE_SALE": ["CEA_Prescribed_Agreement", "Option_To_Purchase", "AML_KYC_Checklist"]
    }
    return requirements.get(transaction_type, [])

def verify_mandatory_checklists(property_id, client_id, transaction_type): # Added argument
    """
    Cross-references stored documents in the 'Vault' (data_layer.py) 
    against the required forms for the specific transaction.
    """
    # 1. Fetch required forms
    required = get_required_docs(transaction_type)
    
    # 2. Query data_layer.py for stored files
    stored_files = data_layer.get_transaction_documents(property_id, client_id)
    
    # 3. Validation logic
    missing = [doc for doc in required if doc not in stored_files]
    if missing:
        return False, f"MISSING_DOCS: {', '.join(missing)}"
    
    return True, "ALL_DOCUMENTS_VERIFIED"