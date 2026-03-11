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
    # Το Inventory και το AP βασίζονται στο COGS (Variable Cost)
    daily_vc = total_vc / 365 if total_vc > 0 else 0

    # 3. Working Capital & Cash Position
    # AR (Απαιτήσεις) + Inventory (Αποθέματα) - AP (Υποχρεώσεις)
    # 
    ar_value = daily_rev * ar_days
    inv_value = daily_vc * inv_days
    ap_value = daily_vc * ap_days
    wc_req = ar_value + inv_value - ap_value
    
    # Η τελική ταμειακή θέση: Αρχικό Ταμείο + Κέρδη - Δόσεις Δανείων - Ανάγκες Working Capital
    # Σημείωση: Το net_profit είναι λογιστικό, το wc_req είναι ταμειακή δέσμευση
    net_cash = opening_cash + net_profit - annual_debt_service - wc_req

    # 4. Break-Even Analysis (Cash Basis)
    # Πόσες μονάδες πρέπει να πουλήσει για να καλύψει Σταθερά + Δάνεια + Στόχο Κέρδους
    cash_wall_requirements = fixed_cost + annual_debt_service + target_profit
    
    if unit_contribution > 0:
        bep_units = cash_wall_requirements / unit_contribution
        margin_of_safety = (volume - bep_units) / volume if volume > 0 else -1.0
    else:
        bep_units = None
        margin_of_safety = -1.0 # Καταστροφή αξίας

    # 5. Cash Conversion Cycle (CCC)
    ccc = ar_days + inv_days - ap_days
    # 

    return {
        "unit_contribution": unit_contribution,
        "revenue": revenue,
        "ebit": ebit,
        "net_profit": net_profit,
        "bep_units": bep_units,
        "margin_of_safety": margin_of_safety,
        "net_cash_position": net_cash,
        "wc_requirement": wc_req,
        "ar_value": ar_value,
        "inv_value": inv_value,
        "ap_value": ap_value,
        "ccc": ccc
    }
