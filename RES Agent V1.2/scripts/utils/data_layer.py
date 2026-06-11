# scripts/utils/data_layer.py

def load_client(client_id):
    """Retrieves client profile data."""
    mock_clients = {
        "VALID_USER_001": {
            "citizenship": "Singapore Citizen",
            "family_structure": "Nuclear Family",
            "eligible_grants": ["Family Grant"]
        }
    }
    return mock_clients.get(client_id, {})

def load_listing(property_id):
    """Retrieves property constraints."""
    # This must be present for your compliance logic to work
    mock_listings = {
        "PROP_001": {
            "mop_passed": False, 
            "eip_status": "OK", 
            "spr_quota_status": "OK"
        }
    }
    return mock_listings.get(property_id, {"mop_passed": True})

def get_compliance_ready_listing(property_id, client_id):
    listing = load_listing(property_id)
    # Note: If you want to use the client data later, keep this:
    client = load_client(client_id)
    return listing

def save_audit_log(event_data):
    """Records every compliance check."""
    # Placeholder for future file I/O
    print(f"Log recorded: {event_data}")