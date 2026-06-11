def format_currency(amount_str):
    # .strip() removes the \n and spaces
    # float() converts '100.0' to 100.0
    # int() then converts 100.0 to 100
    clean_amount = int(float(amount_str.strip()))
    return f"${clean_amount:,}"