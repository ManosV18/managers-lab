def compute_leverage(ebit: float, annual_loan_payment: float):
    """
    Calculates debt service sustainability.
    """
    
    # 1. Debt Service Coverage Ratio (DSCR)
    # 1.0 σημαίνει ότι όλα τα κέρδη πάνε στο δάνειο
    dscr = ebit / annual_loan_payment if annual_loan_payment > 0 else 10.0
    
    # 2. Structural Burden
    # Πόσο % του λειτουργικού κέρδους "τρώει" το χρέος
    debt_burden_pct = (annual_loan_payment / ebit) if ebit > 0 else 1.0
    
    return {
        "dscr": dscr,
        "debt_burden_pct": min(debt_burden_pct, 1.0),
        "is_overleveraged": dscr < 1.2 # Standard banking limit
    }
