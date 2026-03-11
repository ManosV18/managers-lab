def calculate_metrics(price, volume, variable_cost, fixed_cost,
                      ar_days, inv_days, ap_days,
                      annual_debt_service, opening_cash,
                      target_profit=0.0):
    
    # 1. Βασικοί Υπολογισμοί Unit Economics
    unit_contribution = price - variable_cost
    revenue = price * volume
    total_vc = variable_cost * volume
    ebit = (unit_contribution * volume) - fixed_cost
    
    # Φόρος 22% (Cold Logic: Υπολογίζουμε πάντα το net μετά από φόρους)
    tax_rate = 0.22
    net_profit = ebit * (1 - tax_rate) if ebit > 0 else ebit

    # 2. 365-Day Logic [User Instruction 2026-02-18]
    # Υπολογισμός καθημερινού τζίρου και κόστους για το Working Capital
    daily_rev = revenue / 365 if revenue > 0 else 0
    # Το Inventory και το AP βασίζονται συνήθως στο COGS (Variable Cost)
    daily_vc = total_vc / 365 if total_vc > 0 else 0

    # 3. Working Capital & Cash Position
    # AR (Απαιτήσεις) + Inventory (Αποθέματα) - AP (Υποχρεώσεις)
    wc_req = (daily_rev * ar_days) + (daily_vc * inv_days) - (daily_vc * ap_days)
    
    # Η τελική ταμειακή θέση: Αρχικό Ταμείο + Κέρδη - Δόσεις Δανείων - Ανάγκες Working Capital
    net_cash = opening_cash + net_profit - annual_debt_service - wc_req

    # 4. Break-Even Analysis (Cash Basis)
    # Πόσες μονάδες πρέπει να πουλήσει για να καλύψει Σταθερά + Δάνεια + Στόχο Κέρδους
    cash_wall_requirements = fixed_cost + annual_debt_service + target_profit
    bep_units = cash_wall_requirements / unit_contribution if unit_contribution > 0 else None

    

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "net_profit": net_profit,
        "bep_units": bep_units,
        "net_cash_position": net_cash,
        "wc_requirement": wc_req,
        "ccc": ar_days + inv_days - ap_days
    }
