def calculate_scenarios(sale, loan, cpf):
    # Perform all your heavy math here
    net_cash = sale - loan - cpf # Example logic
    
    return {
        "net_cash": net_cash,
        "total_cpf": cpf,
        "total_fluid": net_cash + cpf,
        "scenarios": {
            "low": [p_low, bsd_l, absd_l, cash_l, req_l, (fluid - req_l), status_l],
            "mid": [p_mid, bsd_m, absd_m, cash_m, req_m, (fluid - req_m), status_m],
            "high": [p_high, bsd_h, absd_h, cash_h, req_h, (fluid - req_h), status_h]
        }
    }