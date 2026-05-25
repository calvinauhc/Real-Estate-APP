def calculate_net_capital(cash_on_hand, cpf_oa, existing_loans):
    """
    Determines the total capital available for downpayment.
    """
    return cash_on_hand + cpf_oa - existing_loans

def calculate_waterfall(property_price, is_buy_first_sell_later=False):
    """
    Executes the financial waterfall deduction.
    Deducts commissions and calculates upfront ABSD if applicable.
    """
    # 1. Agent Commission (Standard 2% + 9% GST on commission)
    commission = property_price * 0.02
    gst_on_comm = commission * 0.09
    
    # 2. ABSD Logic (30% penalty if Buy First, Sell Later)
    absd = (property_price * 0.30) if is_buy_first_sell_later else 0
    
    # 3. Stamp Duty (Simplified BSD estimate for >$1M)
    bsd = (property_price * 0.04) - 15400 # Simplified proxy for demo
    
    total_outlay = property_price + commission + gst_on_comm + absd + bsd
    
    return {
        "net_price": property_price,
        "commission": commission + gst_on_comm,
        "absd": absd,
        "bsd": bsd,
        "total_upfront_cash_needed": total_outlay
    }