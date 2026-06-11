def calculate_bsd(price):
    return price * 0.03

def calculate_scenarios(base_price, agent_fee_rate=0.01):
    scenarios = [
        {"name": "Scenario 1 (Conservative)", "price": base_price - 500000},
        {"name": "Scenario 2 (Baseline)", "price": base_price},
        {"name": "Scenario 3 (Aggressive)", "price": base_price + 500000}
    ]
    results = []
    for s in scenarios:
        price = max(0, s["price"])
        bsd = calculate_bsd(price)
        agent_fee = price * agent_fee_rate
        total_outlay = price + bsd + agent_fee
        results.append({
            "Scenario": s["name"],
            "Price": f"${price:,.0f}",
            "BSD": f"${bsd:,.0f}",
            "Agent Fee": f"${agent_fee:,.0f}",
            "Total Outlay": f"${total_outlay:,.0f}"
        })
    return results