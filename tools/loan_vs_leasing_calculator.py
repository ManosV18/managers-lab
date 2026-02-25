import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------
# Financial Logic Helpers
# -------------------------------------------------
def calculate_pmt(rate, nper, pv, fv=0, type=0):
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
    loan_principal = value * loan_pct
    loan_inst = calculate_pmt(loan_rate / 12, months, loan_principal, 0, when)
    
    wc_loan_principal = value * (1 - loan_pct) + exp_loan
    wc_inst = calculate_pmt(wc_rate / 12, months, wc_loan_principal, 0, when)

    total_loan_cash_out = (loan_inst + wc_inst) * months
    loan_interest_total = total_loan_cash_out - (value * loan_pct + wc_loan_principal)
    
    annual_depr = (value + exp_loan) / dep_years
    total_depr_shield = (annual_depr * years) * tax_rate
    loan_interest_shield = loan_interest_total * tax_rate
    
    loan_net_burden = total_loan_cash_out - (loan_interest_shield + total_depr_shield)

    # --- LEASING CALCULATIONS ---
    lease_principal = value * lease_pct
    lease_inst = calculate_pmt(loan_rate / 12, months, lease_principal, 0, when)
    
    wc_lease_principal = value * (1 - lease_pct) + exp_lease
    wc_lease_inst = calculate_pmt(wc_rate / 12, months, wc_lease_principal, 0, when)

    total_lease_cash_out = (lease_inst + wc_lease_inst) * months
    
    # Logic: Leasing payments are typically 100% tax deductible as operating expenses
    lease_tax_shield = total_lease_cash_out * tax_rate
    
    # Net Burden = Total Payments - Tax Shield + Residual Buyout
    lease_net_burden = total_lease_cash_out - lease_tax_shield + residual
    
    return {
        "loan_final": loan_net_burden,
        "lease_final": lease_net_burden,
        "loan_cash": total_loan_cash_out,
        "loan_tx": (loan_interest_shield + total_depr_shield),
        "lease_cash": total_lease_cash_out,
        "lease_tx": lease_tax_shield
    }

# -------------------------------------------------
# MAIN INTERFACE
# -------------------------------------------------
def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Analytical Comparison")
    st.info("Compare financing strategies based on Net Financial Burden (after tax shields).")

    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        st.subheader("Financial Terms")
        loan_rate_input = st.number_input("Interest Rate (%)", value=6.0, key="lvl_loan_r") / 100
        wc_rate_input = st.number_input("WC Opportunity Cost (%)", value=8.0, key="lvl_wc_r") / 100
        years_input = st.number_input("Term (years)", value=10, key="lvl_years")
        tax_rate_input = st.number_input("Tax Rate (%)", value=22.0, key="lvl_tax") / 100
        timing = st.radio("Payment Timing", ["End of Period", "Beginning of Period"], key="lvl_timing")
        when_val = 1 if timing == "Beginning of Period" else 0

    with col_in2:
        st.subheader("Asset Details")
        value_input = st.number_input("Asset Value (€)", value=100000.0, key="lvl_val")
        loan_pct_input = st.number_input("Loan LTV (%)", value=80.0, key="lvl_loan_p") / 100
        lease_pct_input = st.number_input("Leasing Fin (%)", value=100.0, key="lvl_lease_p") / 100
        exp_loan_input = st.number_input("Loan Fees (€)", value=2000.0, key="lvl_exp_l")
        residual_input = st.number_input("Residual Value (€)", value=1000.0, key="lvl_res")
        dep_years_input = st.number_input("Depr. Life (years)", value=10, key="lvl_dep")

    st.divider()
    
    # Execute calculations
    res = run_calculations(
        loan_rate_input, wc_rate_input, years_input, tax_rate_input, when_val, 
        value_input, loan_pct_input, lease_pct_input, exp_loan_input, 0, 
        residual_input, dep_years_input
    )

    # Dashboard display
    c1, c2 = st.columns(2)
    with c1:
        st.metric("🏦 Loan Net Cost", format_eur(res['loan_final']))
        st.caption(f"Gross: {format_eur(res['loan_cash'])} | Shield: {format_eur(res['loan_tx'])}")
    with c2:
        st.metric("🧾 Leasing Net Cost", format_eur(res['lease_final']))
        st.caption(f"Gross: {format_eur(res['lease_cash'])} | Shield: {format_eur(res['lease_tx'])}")

    

    # Sensitivity Analysis
    st.subheader("📈 Sensitivity to Interest Rate")
    test_rates = [loan_rate_input + (i/200) for i in range(-10, 11)]
    ls_costs = [run_calculations(r, wc_rate_input, years_input, tax_rate_input, when_val, value_input, loan_pct_input, lease_pct_input, exp_loan_input, 0, residual_input, dep_years_input)['lease_final'] for r in test_rates]
    l_costs = [run_calculations(r, wc_rate_input, years_input, tax_rate_input, when_val, value_input, loan_pct_input, lease_pct_input, exp_loan_input, 0, residual_input, dep_years_input)['loan_final'] for r in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=ls_costs, name="Leasing Net Burden", line=dict(color="#00CC96")))
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=l_costs, name="Loan Net Burden", line=dict(color="#636EFA")))
    fig.update_layout(template="plotly_dark", height=400, xaxis_title="Rate (%)", yaxis_title="Net Cost (€)")
    st.plotly_chart(fig, use_container_width=True)

    # Verdict
    st.divider()
    if res['loan_final'] < res['lease_final']:
        st.success(f"⚖️ **Verdict: LOAN** is cheaper by {format_eur(res['lease_final'] - res['loan_final'])}.")
    else:
        st.success(f"⚖️ **Verdict: LEASING** is cheaper by {format_eur(res['loan_final'] - res['lease_final'])}.")

    if st.button("Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
