# dagster_orchestration/src/sg_property/checks/data_quality.py

def validate_hdb_ingestion(listing_data):
    """
    Validates that incoming HDB data from spatial_engine.py 
    contains the required fields for the EligibilityEngine.
    """
    required_fields = [
        'property_id', 
        'mop_expiry_date', 
        'eip_quota_status', 
        'spr_quota_status', 
        'block_number', 
        'postal_code'
    ]
    
    missing_fields = [field for field in required_fields if field not in listing_data]
    
    if missing_fields:
        # Log failure for audit trail
        print(f"Data Quality Alert: Missing fields in listing {listing_data.get('property_id')}: {missing_fields}")
        return False, missing_fields
    
    return True, []
