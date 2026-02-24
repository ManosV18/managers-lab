def compute_working_capital(revenue: float, variable_costs: float, ar_days: int, inventory_days: int, ap_days: int):
    """
    Calculates the liquidity tied up in operations. 
    This is the 'Blood Pressure' of the financial system.
    """
    
    # 1. Daily Operations Baseline
    daily_revenue = revenue / 365
    daily_cogs = variable_costs / 365 # Χρησιμοποιούμε τα VC ως βάση για Inventory & AP

    # 2. Asset Components (Cash Out)
    accounts_receivable = daily_revenue * ar_days
    inventory_value = daily_cogs * inventory_days
    
    # 3. Liability Components (Cash In)
    accounts_payable = daily_cogs * ap_days
    
    # 4. Total Structural Requirement
    # Πόσα μετρητά πρέπει να είναι "κλειδωμένα" για να λειτουργεί η επιχείρηση
    total_wc_requirement = accounts_receivable + inventory_value - accounts_payable
    
    # 5. Efficiency Metric: Cash Conversion Cycle (CCC)
    ccc = ar_days + inventory_days - ap_days
    
    return {
        "total_wc_requirement": total_wc_requirement,
        "accounts_receivable": accounts_receivable,
        "inventory_value": inventory_value,
        "accounts_payable": accounts_payable,
        "ccc": ccc,
        "wc_intensity": total_wc_requirement / revenue if revenue > 0 else 0
    }
