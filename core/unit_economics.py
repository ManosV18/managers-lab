def compute_unit_economics(price: float, variable_cost: float, volume: int):
    """
    Calculates the fundamental viability of a single unit sold.
    This is the 'Atomic Level' of the business model.
    """
    # 1. Unit Profitability
    contribution_margin = price - variable_cost
    
    # 2. Efficiency Metric (Margin %)
    contribution_ratio = contribution_margin / price if price > 0 else 0
    
    # 3. Structural Viability Check
    # If CM <= 0, the business loses money on every sale (Fatal Flaw)
    is_non_viable = contribution_margin <= 0
    
    # 4. Total Output at Current Scale
    total_cm = contribution_margin * volume
    
    return {
        "unit_contribution": contribution_margin,
        "contribution_ratio": contribution_ratio,
        "is_non_viable": is_non_viable,
        "total_cm": total_cm,
        "is_breakeven_possible": not is_non_viable
    }
