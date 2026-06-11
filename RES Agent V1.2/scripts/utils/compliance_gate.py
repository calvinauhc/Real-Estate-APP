# scripts/utils/compliance_gate.py
from . import aml_logic, hdb_logic, doc_logic, data_layer
from .financial_calc import FinancialEngine

def run_full_compliance_check(client_id, property_id, property_type, client_profile, property_data):
    """
    The master gatekeeper for all compliance checks, now including grant estimations.
    """
    
    # 1. Gate 1: AML Check
    is_eligible, reason = aml_logic.verify_aml_status(client_id)
    if not is_eligible:
        aml_logic.log_compliance_attempt(client_id, "FAILED", reason)
        return {"eligible": False, "reason": reason}

    # 2. Gate 2: Property Type Specific Checks
    if property_type == "HDB":
        eligible, hdb_reason = hdb_logic.validate_hdb_eligibility(client_id, property_id)
        if not eligible:
            return {"eligible": False, "reason": hdb_reason}

    # 3. Gate 3: Financial Stress Test & Grant Calculation
    engine = FinancialEngine(client_profile)
    monthly_income = client_profile.get('monthly_income', 0)
    monthly_debt = client_profile.get('existing_debt', 0)
    property_price = property_data.get('price', 800000) 
    loan_amount = property_price * 0.8 
    
    # Grant Estimation
    estimated_grants = engine.calculate_grants(property_type)
    
    stress_test_payment = engine.run_mas_stress_test(loan_amount, 30)
    tdsr_eligible, ratio = engine.validate_tdsr(monthly_debt, stress_test_payment)
    
    if not tdsr_eligible:
        return {"eligible": False, "reason": f"TDSR_EXCEEDED: {ratio:.2%}"}

    # 4. Gate 4: Documentation Check
    tx_type = "HDB_RESALE" if property_type == "HDB" else "PRIVATE_SALE"
    is_doc_verified, doc_reason = doc_logic.verify_mandatory_checklists(property_id, client_id, tx_type)
    
    if not is_doc_verified:
        return {"eligible": False, "reason": doc_reason}

    # All gates passed - return eligibility plus grant insights
    return {
        "eligible": True, 
        "reason": "PASSED",
        "estimated_grants": estimated_grants
    }