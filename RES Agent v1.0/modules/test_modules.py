# test_modules.py
from modules.financial_engine import calculate_waterfall
from modules.formatter import format_currency

def test_financial_engine():
    print("--- Testing Financial Engine ---")
    # Scenario: $1.5M property, Buy First Sell Later
    result = calculate_waterfall(1500000, is_buy_first_sell_later=True)
    
    print(f"Total Upfront Cash Needed: {format_currency(result['total_upfront_cash_needed'])}")
    
    # Validation check
    if result['absd'] > 0:
        print("PASS: ABSD successfully calculated.")
    else:
        print("FAIL: ABSD not triggered.")

if __name__ == "__main__":
    test_financial_engine()