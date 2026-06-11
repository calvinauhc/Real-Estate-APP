# scripts/utils/financial_calc.py

class FinancialEngine:
    def __init__(self, client_profile):
        self.client = client_profile
        self.tdsr_limit = 0.55
        self.stress_test_rate = 0.04  # MAS standard stress test rate

    def calculate_grants(self, property_type):
        """
        Estimates total CPF housing grants available to the client.
        """
        total_grants = 0
        if property_type == "HDB" and self.client.get('is_first_timer'):
            total_grants += 80000
        if self.client.get('living_near_parents'):
            total_grants += 20000
        return total_grants

    def run_mas_stress_test(self, loan_amount, tenure_years):
        """
        Calculates monthly payment using MAS stress test rate (4%).
        """
        monthly_rate = self.stress_test_rate / 12
        num_payments = tenure_years * 12
        
        # Standard mortgage formula
        payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                  ((1 + monthly_rate)**num_payments - 1)
        return payment

    def calculate_monthly_repayment(self, loan_amount, tenure_years, interest_rate=0.03):
        """
        Calculates actual monthly repayment based on current market rates.
        """
        monthly_rate = interest_rate / 12
        num_payments = tenure_years * 12
        payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                  ((1 + monthly_rate)**num_payments - 1)
        return payment



def calculate_tdsr(monthly_income, monthly_debt, stress_test_payment=0):
    """
    Calculates the TDSR ratio. 
    Added stress_test_payment with a default of 0 for backward compatibility.
    """
    if monthly_income <= 0:
        return 0
        
    ratio = (monthly_debt + stress_test_payment) / monthly_income
    return ratio