import streamlit as st
from core.unit_economics import compute_unit_economics
from core.working_capital import compute_working_capital
from core.fragility import compute_fragility
from core.leverage import compute_leverage

def compute_core_metrics():
    """
    The Orchestrator: Integrates all sub-modules into a single 
    Institutional-Grade financial truth.
    """
    s = st.session_state

    # 1. ATOMIC LAYER: Unit Economics
    unit = compute_unit_economics(s.price, s.variable_cost, s.volume)
    
    # 2. OPERATIONAL LAYER
    revenue = s.price * s.volume
    total_vc = s.variable_cost * s.volume
    ebitda = unit["total_cm"] - s.fixed_cost
    
    # 3. LIQUIDITY LAYER: Working Capital
    wc = compute_working_capital(
        revenue, 
        total_vc, 
        s.ar_days, 
        s.inventory_days, 
        s.ap_days
    )
    
    # 4. CASH FLOW LAYER
    tax_impact = max(0, ebitda * s.tax_rate)
    ocf = ebitda - tax_impact
    fcf = ocf - s.annual_loan_payment
    
    # 5. RISK & LEVERAGE LAYER
    monthly_net = fcf / 12
    current_cash_reserve = s.get('opening_cash', 0.0) - wc["total_wc_requirement"]
    
    risk = compute_fragility(fcf, current_cash_reserve, monthly_net)
    debt_risk = compute_leverage(max(1, ocf), s.annual_loan_payment)
    
    # 6. STRATEGIC LAYER
    cash_wall = s.fixed_cost + s.annual_loan_payment + wc["total_wc_requirement"]
    survival_bep = cash_wall / unit["unit_contribution"] if unit["unit_contribution"] > 0 else float('inf')

    # 7. CONSOLIDATED OUTPUT
    return {
        "unit_contribution": unit["unit_contribution"],
        "contribution_ratio": unit["contribution_ratio"],
        "total_cm": unit["total_cm"],
        "revenue": revenue,
        "ebitda": ebitda,
        "ocf": ocf,
        "fcf": fcf,
        "wacc": s.get('wacc', 0.10),  # <--- ΠΡΟΣΘΗΚΗ WACC (Default 10%)
        "wc_requirement": wc["total_wc_requirement"],
        "ccc": wc["ccc"],
        "cash_reserve": current_cash_reserve,
        "fragility_score": risk["fragility_score"],
        "runway_months": risk["coverage_months"],
        "dscr": debt_risk["dscr"],
        "survival_bep": survival_bep,
        "cash_wall": cash_wall,
        "is_non_viable": unit["is_non_viable"]
    }
