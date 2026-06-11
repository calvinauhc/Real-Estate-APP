# scripts/utils/hdb_logic.py
from scripts.utils import data_layer
# scripts/utils/hdb_logic.py

def check_eip_compliance(client, listing):
    # Add your logic here. For now, we return True (eligible)
    return True

def check_mop_status(listing):
    # This checks if MOP has passed. 
    # If mop_passed is False, this returns False (ineligible)
    return listing.get('mop_passed', True)

def check_spr_quota(listing):
    return True

# Now your existing validate_hdb_eligibility function will work:
def validate_hdb_eligibility(client_id, property_id):
    client = data_layer.load_client(client_id)
    listing = data_layer.load_listing(property_id)
    
    if not check_eip_compliance(client, listing):
        return False, "EIP_QUOTA_EXCEEDED"
    
    if not check_mop_status(listing):
        return False, "PROPERTY_STILL_UNDER_MOP"
        
    if client.get('citizenship') == 'SPR' and not check_spr_quota(listing):
        return False, "SPR_QUOTA_REACHED"
        
    return True, "ELIGIBLE_FOR_PURCHASE"
def validate_hdb_eligibility(client_id, property_id):
    """
    Determines if a client meets the regulatory requirements for a specific HDB unit.
    """
    # 1. Fetch Client Profile (Citizenship, Family Structure) 
    client = data_layer.load_client(client_id)
    # 2. Fetch Property Constraints (MOP, EIP, SPR Quota)
    listing = data_layer.load_listing(property_id)
    
    # 3. Decision Matrix
    # Check EIP Quota
    if not check_eip_compliance(client, listing):
        return False, "EIP_QUOTA_EXCEEDED"
    
    # Check MOP Status
    if not check_mop_status(listing):
        return False, "PROPERTY_STILL_UNDER_MOP"
        
    # Check SPR Quota
    if client.get('citizenship') == 'SPR' and not check_spr_quota(listing):
        return False, "SPR_QUOTA_REACHED"
        
    return True, "ELIGIBLE_FOR_PURCHASE"