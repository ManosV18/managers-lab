import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -------------------------------------------------
# Financial Logic Helpers
# -------------------------------------------------
def calculate_pmt(rate, nper, pv, fv=0, type=0):
    """Standard PMT formula implementation"""
    if rate == 0:
        return -(pv + fv) / nper
    
    pv_factor = (1 + rate) ** nper
    payment = (rate * (pv * pv_factor + fv)) / ((pv_factor - 1) * (1 + rate * type))
    return payment

def format_eur(x):
    return f"€ {x:,.0f}"

# -------------------------------------------------
# CALCULATION ENGINE
# -------------------------------------------------
def run_calculations(loan_rate, wc_rate, years, tax_rate, when, value, loan_pct, lease_pct, exp_loan, exp_lease, residual, dep_years):
    months = years * 12
    
    # --- LOAN CALCULATIONS ---
    # Monthly payment for the bank loan portion
    loan_inst = calculate_pmt(loan_rate / 12, months, value * loan_pct, 0, when)
    # The equity part + acquisition costs are financed by Working Capital (opportunity cost)
    wc_loan_principal = value * (1 - loan_pct) + exp_loan
    wc_inst = calculate_pmt(wc_rate / 12, months, wc_loan_principal, 0, when)

    total_loan_cash_out = (loan_inst + wc_inst) * months
    loan_interest = total_loan_cash_out - (value + exp_loan)
    # Depreciation provides a tax shield (Straight Line)
    annual_depr = (value + exp_loan) / dep_years
    total_depr_during_term = annual_depr * years
    
    loan_tax_shield = (loan_interest + total_depr_during_term) * tax_rate
    loan_net_burden = total_loan_cash_out - loan_tax_shield

    # --- LEASING CALCULATIONS ---
    lease_inst = calculate_pmt(loan_rate / 12, months, value * lease_pct, 0, when)
    wc_lease_principal = value * (1 - lease_pct) + exp_lease
    wc_lease_inst = calculate_pmt(wc_rate / 12, months, wc_lease_principal, 0, when)

    total_lease_cash_out = (lease_inst + wc_lease_inst) * months
    
    # In leasing, the whole payment is usually tax-deductible as an expense
    # or Interest + Depreciation if capitalized (IFRS 16). 
    # Here we use the standard operational tax benefit logic.
    lease_interest = total_lease_cash_out - (value + exp_lease)
    lease_depr_benefit = (value + exp_lease + residual) # Simplified full deduction
    lease_tax_shield = (total_lease_cash_out - (value * (1-lease_pct))) * tax_rate
    
    lease_net_burden = total_lease_cash_out - lease_tax_shield + residual
    
    return {
        "loan_final": loan_net_burden,
        "lease_final": lease_net_burden,
        "loan_cash": total_loan_cash_out,
        "loan_int": loan_interest,
        "loan_tx": loan_tax_shield,
        "lease_cash": total_lease_cash_out,
        "lease_int": lease_interest,
        "lease_tx": lease_tax_shield
    }

# -------------------------------------------------
# MAIN INTERFACE
# -------------------------------------------------
def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Analytical Comparison")
    st.info("Evaluate asset financing options by comparing net financial burden after tax shields and opportunity costs.")

    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        st.subheader("Financial Terms")
        loan_rate_input = st.number_input("Nominal Interest Rate (%)", value=6.0, key="lvl_loan_r") / 100
        wc_rate_input = st.number_input("Working Capital Opportunity Cost (%)", value=8.0, key="lvl_wc_r") / 100
        years_input = st.number_input("Analysis Duration (years)", value=10, key="lvl_years")
        tax_rate_input = st.number_input("Corporate Tax Rate (%)", value=22.0, key="lvl_tax") / 100
        timing = st.radio("Payment Timing", ["End of Period", "Beginning of Period"], key="lvl_timing")
        when_val = 1 if timing == "Beginning of Period" else 0

    with col_in2:
        st.subheader("Asset & Acquisition")
        value_input = st.number_input("Asset Value (€)", value=100000.0, key="lvl_val")
        loan_pct_input = st.number_input("Loan LTV (%)", value=80.0, key="lvl_loan_p") / 100
        lease_pct_input = st.number_input("Leasing Financing (%)", value=100.0, key="lvl_lease_p") / 100
        exp_loan_input = st.number_input("Acquisition Fees - Loan (€)", value=2000.0, key="lvl_exp_l")
        exp_lease_input = st.number_input("Acquisition Fees - Leasing (€)", value=1000.0, key="lvl_exp_ls")
        residual_input = st.number_input("Residual Buy-out Value (€)", value=1000.0, key="lvl_res")
        dep_years_input = st.number_input("Tax Depreciation Life (years)", value=10, key="lvl_dep")

    st.divider()
    
    # Execution
    results = run_calculations(
        loan_rate_input, wc_rate_input, years_input, tax_rate_input, when_val, 
        value_input, loan_pct_input, lease_pct_input, exp_loan_input, exp_lease_input, 
        residual_input, dep_years_input
    )

    # RESULTS DASHBOARD
    st.subheader("📉 Net Financial Burden (After-Tax)")
    c1, c2 = st.columns(2)

    with c1:
        st.metric("🏦 Loan Net Cost", format_eur(results['loan_final']))
        st.caption(f"Total Outflow: {format_eur(results['loan_cash'])}")
        st.caption(f"Tax Shield: -{format_eur(results['loan_tx'])}")

    with c2:
        st.metric("🧾 Leasing Net Cost", format_eur(results['lease_final']))
        st.caption(f"Total Outflow: {format_eur(results['lease_cash'])}")
        st.caption(f"Tax Shield: -{format_eur(results['lease_tx'])}")

    

    # SENSITIVITY CHART
    st.subheader("📈 Rate Sensitivity Analysis")
    test_rates = [loan_rate_input + (i/200) for i in range(-10, 11)]
    ls_burdens = []
    l_burdens = []
    
    for r in test_rates:
        res_test = run_calculations(r, wc_rate_input, years_input, tax_rate_input, when_val, 
                                    value_input, loan_pct_input, lease_pct_input, exp_loan_input, 
                                    exp_lease_input, residual_input, dep_years_input)
        ls_burdens.append(res_test['lease_final'])
        l_burdens.append(res_test['loan_final'])
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=ls_burdens, name="Leasing Cost", line=dict(color="#00CC96")))
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=l_burdens, name="Loan Cost", line=dict(color="#636EFA")))
    
    fig.update_layout(template="plotly_dark", xaxis_title="Interest Rate (%)", yaxis_title="Total Net Burden (€)", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # COLD VERDICT
    st.divider()
    if results['
