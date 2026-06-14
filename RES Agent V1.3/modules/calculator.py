def calculate_bsd(price):
    """
    Calculates Singapore progressive Buyer Stamp Duty (BSD).
    The tax uses a marginal tiered approach.
    """
    bsd = 0
    # Tiered logic: Calculate the cumulative tax by summing fixed amounts from previous tiers
    # plus the marginal percentage for the portion of the price within the current tier.
    if price <= 180000:
        bsd = price * 0.01
    elif price <= 360000:
        bsd = (180000 * 0.01) + ((price - 180000) * 0.02)
    elif price <= 1000000:
        bsd = 1800 + 3600 + ((price - 360000) * 0.03)
    elif price <= 1500000:
        bsd = 1800 + 3600 + 19200 + ((price - 1000000) * 0.04)
    elif price <= 3000000:
        bsd = 1800 + 3600 + 19200 + 20000 + ((price - 1500000) * 0.05)
    else:
        bsd = 1800 + 3600 + 19200 + 20000 + 75000 + ((price - 3000000) * 0.06)
    return bsd

def calculate_liquidity_waterfall(sale_price, mortgage_balance, cpf_refund, purchase_price, ipa_loan, custom_agent_rate, custom_legal_fee=3000):
    """
    Maps the 'Liquidity Waterfall': Sale Proceeds -> New Purchase Entry Costs.
    """
    # 1. Exit Phase: Determine liquid cash remaining after selling the current home
    agent_comm_sale = sale_price * custom_agent_rate
    net_cash_proceeds = sale_price - mortgage_balance - cpf_refund - agent_comm_sale - custom_legal_fee
    
    # 2. Entry Phase: Determine capital required for the new property
    bsd = calculate_bsd(purchase_price)
    agent_comm_buy = purchase_price * custom_agent_rate
    # Total Required assumes 25% downpayment (LTV 75% standard) + taxes/fees
    total_required = (purchase_price * 0.25) + bsd + agent_comm_buy + custom_legal_fee
    
    # 3. Gap Analysis: Compare available cash flow against acquisition requirements
    total_available = net_cash_proceeds + cpf_refund + ipa_loan
    gap = total_required - total_available
    
    return {
        "net_cash_proceeds": net_cash_proceeds,
        "total_required": total_required,
        "gap": gap,
        "is_fully_funded": gap <= 0
    }

def calculate_affordability(max_loan_ipa, target_price, cash, cpf_oa, accrued_interest, property_type, tenure, is_first_timer=True):
    """
    Stress-tests affordability across different budget multipliers.
    """
    # Calculate net usable CPF (OA balance after accounting for interest already used)
    net_cpf = max(0, cpf_oa - accrued_interest)
    total_buying_power = cash + net_cpf + max_loan_ipa
    
    scenario_details = []
    # Loop through multipliers to visualize price sensitivity
    for multiplier in [0.8, 1.0, 1.2]:
        price = target_price * multiplier
        bsd = calculate_bsd(price)
        # Entry costs assume 25% cash/CPF down + 2% agent fee + fixed legal fee
        total_cash_required = (price * 0.25) + bsd + (price * 0.02) + 3000
        
        scenario_details.append({
            "label": f"{int(multiplier*100)}% Budget",
            "price": price,
            "total_cash": total_cash_required,
            "is_affordable": total_buying_power >= total_cash_required
        })
        
    return {"is_affordable": scenario_details[1]["is_affordable"], "scenarios": scenario_details}