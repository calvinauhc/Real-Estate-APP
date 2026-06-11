def calculate_max_loan(
    fixed_income, 
    variable_income, 
    other_debts, 
    loan_tenure_years, 
    is_hdb_or_ec=False,
    stress_rate=0.04
):
    """
    Calculates maximum loan quantum based on MAS regulations (TDSR 55%, MSR 30%).
    Applies a regulatory 30% haircut to variable income components.
    """
    # 1. Apply 30% haircut to variable income as per MAS rules
    assessable_income = float(fixed_income) + (float(variable_income) * 0.70)
    
    if assessable_income <= 0:
        return {"max_loan": 0.0, "max_monthly_installment": 0.0, "limiting_factor": "No Income"}
        
    # Monthly stress rate
    r = stress_rate / 12
    n = loan_tenure_years * 12
    
    # 2. Compute TDSR Threshold (55% of total assessable income minus existing debts)
    tdsr_max_installment = (assessable_income * 0.55) - float(other_debts)
    
    # 3. Compute MSR Threshold (30% of total assessable income)
    msr_max_installment = assessable_income * 0.30
    
    # 4. Determine limiting factor and max allowable housing installment
    if is_hdb_or_ec:
        if msr_max_installment < tdsr_max_installment:
            max_installment = max(0.0, msr_max_installment)
            limiting_factor = "MSR (30% Cap)"
        else:
            max_installment = max(0.0, tdsr_max_installment)
            limiting_factor = "TDSR (55% Cap - High External Debt)"
    else:
        max_installment = max(0.0, tdsr_max_installment)
        limiting_factor = "TDSR (55% Cap)"
        
    if max_installment <= 0:
        return {"max_loan": 0.0, "max_monthly_installment": 0.0, "limiting_factor": limiting_factor}
        
    # 5. Reverse engineer maximum loan quantum from monthly installment
    # Present Value of an Annuity formula
    max_loan = max_installment * ((1 - (1 + r) ** -n) / r)
    
    return {
        "max_loan": round(max_loan, 2),
        "max_monthly_installment": round(max_installment, 2),
        "limiting_factor": limiting_factor,
        "assessable_monthly_income": round(assessable_income, 2)
    }