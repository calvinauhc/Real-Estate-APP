def calculate_bsd(price):
    """Calculates tiered BSD based on current Singapore rates."""
    if price <= 180000:
        return price * 0.01
    elif price <= 360000:
        return (180000 * 0.01) + ((price - 180000) * 0.02)
    elif price <= 1000000:
        return (180000 * 0.01) + (180000 * 0.02) + ((price - 360000) * 0.03)
    else:
        # Tiered calculation for amounts above $1M
        return (180000 * 0.01) + (180000 * 0.02) + (640000 * 0.03) + ((price - 1000000) * 0.04)

def calculate_scenarios(base_price, agent_fee_rate=0.01):
    """Calculates cost scenarios including stamp duties and agent fees."""
    scenarios = [
        {"name": "Conservative (-$500k)", "price": base_price - 500000},
        {"name": "Baseline (Target)", "price": base_price},
        {"name": "Aggressive (+$500k)", "price": base_price + 500000}
    ]
    results = []
    for s in scenarios:
        price = max(0, s["price"])
        bsd = calculate_bsd(price)
        agent_fee = price * agent_fee_rate
        total_outlay = price + bsd + agent_fee
        results.append({
            "Scenario": s["name"],
            "Price": price,
            "BSD": bsd,
            "Agent Fee": agent_fee,
            "Total Outlay": total_outlay
        })
    return results