# scripts/tests/test_compliance.py
from scripts.utils.compliance_gate import run_full_compliance_check

# Mock data for testing
mock_client = {
    "citizenship": "Singaporean",
    "monthly_income": 10000, 
    "existing_debt": 500
}

mock_hdb_data = {"mop_passed": False}

def test_aml_blocker():
    result = run_full_compliance_check(
        client_id="PROHIBITED_USER_001",
        property_id="PROP_001",
        property_type="HDB",
        client_profile=mock_client,
        property_data=mock_hdb_data
    )
    assert result['eligible'] == False
    assert "AML_CHECK_FAILED" in result['reason']

def test_hdb_mop_blocker():
    result = run_full_compliance_check(
        client_id="VALID_USER_001",
        property_id="PROP_001",
        property_type="HDB",
        client_profile=mock_client,
        property_data=mock_hdb_data
    )
    assert result['eligible'] == False
    assert result['reason'] == "PROPERTY_STILL_UNDER_MOP"

def test_financial_eligibility_pass():
    result = run_full_compliance_check(
        client_id="VALID_USER_001",
        property_id="PROP_001",
        property_type="CONDO",
        client_profile=mock_client,
        property_data={"price": 800000}
    )
    assert result['eligible'] == True
    assert result['reason'] == "PASSED"

def test_financial_eligibility_fail_high_debt():
    # Use "VALID_USER_001" to ensure we get past AML
    poor_client = {"monthly_income": 2000, "existing_debt": 1500}
    
    result = run_full_compliance_check(
        client_id="VALID_USER_001", 
        property_id="PROP_001",
        property_type="CONDO",
        client_profile=poor_client,
        property_data={"price": 2000000}
    )
    assert result['eligible'] == False
    assert "TDSR_EXCEEDED" in result['reason']

# scripts/tests/test_compliance.py 
# (Existing content remains above...)

def test_grant_calculation_eligibility():
    """
    Test that grants are correctly calculated and appended to the 
    compliance eligibility response for a first-timer HDB buyer.
    """
    # Setup a mock client eligible for maximum grants
    grant_eligible_client = {
        "monthly_income": 5000,
        "existing_debt": 0,
        "is_first_timer": True,
        "living_near_parents": True
    }
    
    # Run the compliance check using the updated financial logic
    result = run_full_compliance_check(
        client_id="VALID_USER_001",
        property_id="PROP_HDB_001",
        property_type="HDB",
        client_profile=grant_eligible_client,
        property_data={"price": 500000}
    )
    
    # Assert eligibility passed
    assert result['eligible'] == True
    
    # Assert specific grant values (Family Grant 80k + PHG 20k = 100k)
    assert result['estimated_grants'] == 100000