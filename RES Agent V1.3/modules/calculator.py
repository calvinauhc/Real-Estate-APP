def calculate_affordability(monthly_income, monthly_debt, property_price, cash_savings, cpf_oa):
    """
    Calculates loan eligibility based on Singapore's 55% TDSR limit.
    """
    # 1. Constants
    TDSR_LIMIT = 0.55
    INTEREST_RATE = 0.04  # 4% stress-test rate (conservative estimate)
    LOAN_TENURE = 30      # Max years
    
    # 2. Maximum Monthly Debt Servicing allowed
    max_monthly_repayment = (monthly_income * TDSR_LIMIT) - monthly_debt
    
    # 3. Max Loan Amount (using annuity formula)
    # Simple version: PMT = P * [r(1+r)^n] / [(1+r)^n - 1]
    # We solve for P (Principal)
    r = INTEREST_RATE / 12
    n = LOAN_TENURE * 12
    max_loan = max_monthly_repayment * ((1 + r)**n - 1) / (r * (1 + r)**n)
    
    # 4. Cash/CPF Required (Assuming 25% downpayment)
    min_downpayment = property_price * 0.25
    available_funds = cash_savings + cpf_oa
    
    return {
        "max_loan_eligible": round(max_loan, 2),
        "min_downpayment_required": round(min_downpayment, 2),
        "is_affordable": (max_loan + available_funds) >= property_price,
        "shortfall": max(0, property_price - (max_loan + available_funds))
    }