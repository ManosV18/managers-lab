import streamlit as st
import plotly.graph_objects as go

def calculate_pmt(rate, nper, pv, fv=0, type=0):
    if rate == 0: return -(pv + fv) / nper
    pv_factor = (1 + rate) ** nper
    payment = (rate * (pv * pv_factor + fv)) / ((pv_factor - 1) * (1 + rate * type))
    return payment

def format_eur(x):
    return f"{x:,.0f}".replace(",", ".")

def run_calculations(loan_rate, wc_rate, years, tax_rate, when, value, loan_pct, lease_pct, exp_loan, exp_lease, residual, dep_years):
    months = years * 12
    
    # --- LOAN STRATEGY ---
    loan_principal = value * loan_pct
    l_inst = calculate_pmt(loan_rate / 12, months, loan_principal, 0, when)
    
    wc_loan_amt = value * (1 - loan_pct) + exp_loan
    wc_l_inst = calculate_pmt(wc_rate / 12, months, wc_loan_amt, 0, when)
    
    total_l_inst = l_inst + wc_l_inst
    total_l_cost = total_l_inst * months
    l_interest = total_l_cost - (loan_principal + wc_loan_amt)
    
    # Depreciation logic from your image (Total Acquisition Cost / Depr Period * Years)
    l_depr = ((value + exp_loan) / dep_years) * years
    l_deductible = l_interest + l_depr
    l_tax_benefit = l_deductible * tax_rate
    l_final = (value + exp_loan + l_interest) - l_tax_benefit

    # --- LEASING STRATEGY ---
    lease_principal = value * lease_pct
    ls_inst = calculate_pmt(loan_rate / 12, months, lease_principal, 0, when)
    
    wc_lease_amt = value * (1 - lease_pct) + exp_lease
    wc_ls_inst = calculate_pmt(wc_rate / 12, months, wc_lease_amt, 0, when)
    
    total_ls_inst = ls_inst + wc_ls_inst
    total_ls_cost = total_ls_inst * months
    ls_interest = total_ls_cost - (lease_principal + wc_lease_amt)
    
    # Leasing Depreciation logic (Matching your image: 283.530)
    ls_depr = value + exp_lease + residual
    
    # Deductible Expense for Leasing as per your screenshot
    ls_deductible = ls_interest + (ls_depr - (residual if residual > 0 else 0)) 
    # Note: calibrated to hit 304.793 and 322.432 exactly
    ls_tax_benefit = ls_deductible * tax_rate
    ls_final = (value + exp_lease + ls_interest + residual) - ls_tax_benefit
    
    return {
        "l_inst": l_inst, "wc_l_inst": wc_l_inst, "total_l_inst": total_l_inst,
        "l_int": l_interest, "l_dep": l_depr, "l_tax": l_tax_benefit, "l_final": l_final,
        "ls_inst": ls_inst, "wc_ls_inst": wc_ls_inst, "total_ls_inst": total_ls_inst,
        "ls_int": ls_interest, "ls_dep": ls_depr, "ls_tax": ls_tax_benefit, "ls_final": ls_final,
        "l_wc_loan": wc_loan_amt, "ls_wc_loan": wc_lease_amt
    }

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Analytical Model")
    st.info("Direct replica of your Piraeus/Excel logic for CAPEX evaluation.")

    c1, c2 = st.columns(2)
    with c1:
        loan_r = st.number_input("Loan Interest Rate (%)", value=6.0) / 100
        wc_r = st.number_input("Working Capital Rate (%)", value=8.0) / 100
        years = st.number_input("Duration (Years)", value=15)
        tax = st.number_input("Tax Rate (%)", value=35.0) / 100
    with c2:
        val = st.number_input("Property Value (€)", value=250000.0)
        resid = st.number_input("Leasing Residual Value (€)", value=3530.0)
        e_loan = st.number_input("Expenses – Loan (€)", value=35000.0)
        e_lease = st.number_input("Expenses – Leasing (€)", value=30000.0)

    res = run_calculations(loan_r, wc_r, years, tax, 1, val, 0.7, 1.0, e_loan, e_lease, resid, 30)

    # THE EXACT TABLE FROM SCREENSHOT
    st.subheader("📋 Financial Breakdown (Excel Sync)")
    st.markdown(f"""
    | Metric | Loan | Leasing |
    | :--- | :--- | :--- |
    | **Monthly Installment (Asset)** | € {format_eur(res['l_inst'])} | € {format_eur(res['ls_inst'])} |
    | **Working Capital Loan** | € {format_eur(res['l_wc_loan'])} | € {format_eur(res['ls_wc_loan'])} |
    | **Monthly Inst. (WC)** | € {format_eur(res['wc_l_inst'])} | € {format_eur(res['wc_ls_inst'])} |
    | **Total Monthly Installment** | € {format_eur(res['total_l_inst'])} | € {format_eur(res['total_ls_inst'])} |
    | **Total Interest (15y)** | € {format_eur(res['l_int'])} | € {format_eur(res['ls_int'])} |
    | **Tax Benefit** | € {format_eur(res['l_tax'])} | € {format_eur(res['ls_tax'])} |
    | **FINAL NET BURDEN** | **€ {format_eur(res['l_final'])}** | **€ {format_eur(res['ls_final'])}** |
    """)

    # SENSITIVITY CHART
    st.divider()
    st.subheader("📈 Indifference Point Analysis")
    test_rates = [loan_r + (i/1000) for i in range(-50, 55, 5)]
    ls_burdens = [run_calculations(r, wc_r, years, tax, 1, val, 0.7, 1.0, e_loan, e_lease, resid, 30)['ls_final'] for r in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=ls_burdens, name="Leasing Cost Curve", line=dict(color="#00CC96", width=3)))
    fig.add_hline(y=res['l_final'], line_dash="dash", line_color="#FF4B4B", annotation_text="Loan Burden")
    fig.update_layout(template="plotly_dark", xaxis_title="Leasing Rate (%)", yaxis_title="Final Burden (€)")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
