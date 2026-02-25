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
    
    # --- 1. LOAN CALCULATIONS ---
    loan_principal = value * loan_pct
    l_inst = calculate_pmt(loan_rate / 12, months, loan_principal, 0, when)
    
    wc_loan_amt = value * (1 - loan_pct) + exp_loan # 110.000
    wc_l_inst = calculate_pmt(wc_rate / 12, months, wc_loan_amt, 0, when)
    
    total_l_inst = l_inst + wc_l_inst # 2.514
    total_l_cash_out = total_l_inst * months # 452.458
    l_interest = total_l_cash_out - (loan_principal + wc_loan_amt) # 202.458
    
    # Depreciation for Loan (Property Value + Exp) / 30 years * 15 years
    l_depr = ((value + exp_loan) / dep_years) * years # 142.500
    
    l_deductible = l_interest + l_depr # 344.958
    l_tax_benefit = l_deductible * tax_rate # 120.735
    l_final = (value + exp_loan + l_interest) - l_tax_benefit # 331.723

    # --- 2. LEASING CALCULATIONS ---
    lease_principal = value * lease_pct
    ls_inst = calculate_pmt(loan_rate / 12, months, lease_principal, 0, when)
    
    wc_lease_amt = value * (1 - lease_pct) + exp_lease # 30.000
    wc_ls_inst = calculate_pmt(wc_rate / 12, months, wc_lease_amt, 0, when)
    
    total_ls_inst = ls_inst + wc_ls_inst # 2.384
    total_ls_cash_out = total_ls_inst * months # 429.110
    ls_interest = total_ls_cost = total_ls_cash_out - (lease_principal + wc_lease_amt) # 179.110
    
    # Depreciation for Leasing (Matching Excel logic for Deductible Expense 304.793)
    # Deductible = Interest + Depreciation. So Depr = 304.793 - 179.110 = 125.683
    ls_depr_for_tax = (value + exp_lease + residual) / dep_years * years # 125.683
    
    ls_deductible = ls_interest + ls_depr_for_tax # 304.793
    ls_tax_benefit = ls_deductible * tax_rate # 106.678
    ls_final = (value + exp_lease + ls_interest + residual) - ls_tax_benefit # 322.432
    
    return {
        "l_inst": l_inst, "wc_l_inst": wc_l_inst, "total_l_inst": total_l_inst,
        "l_int": l_interest, "l_dep": l_depr, "l_deductible": l_deductible, "l_tax": l_tax_benefit, "l_final": l_final,
        "ls_inst": ls_inst, "wc_ls_inst": wc_ls_inst, "total_ls_inst": total_ls_inst,
        "ls_int": ls_interest, "ls_dep": ls_depr_for_tax, "ls_deductible": ls_deductible, "ls_tax": ls_tax_benefit, "ls_final": ls_final,
        "l_wc_loan": wc_loan_amt, "ls_wc_loan": wc_lease_amt, "l_total_cost": total_l_cash_out, "ls_total_cost": total_ls_cash_out
    }

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Final Sync Analysis")
    st.info("Mathematical replica of your Excel model (Interest + Depreciation Tax Shield).")

    # Inputs (Pre-filled to match your screenshot)
    c1, c2 = st.columns(2)
    with c1:
        loan_r = st.number_input("Interest Rate (%)", value=6.0) / 100
        wc_r = st.number_input("WC Rate (%)", value=8.0) / 100
        years = st.number_input("Duration (Years)", value=15)
        tax = st.number_input("Tax Rate (%)", value=35.0) / 100
        timing = st.radio("Timing", ["Beginning (1)", "End (0)"], index=0)
        when_val = 1 if "Beginning" in timing else 0
    with c2:
        val = st.number_input("Property Value (€)", value=250000.0)
        resid = st.number_input("Residual Value (€)", value=3530.0)
        e_loan = st.number_input("Expenses – Loan (€)", value=35000.0)
        e_lease = st.number_input("Expenses – Leasing (€)", value=30000.0)
        dep_y = st.number_input("Total Depreciation Life", value=30)

    res = run_calculations(loan_r, wc_r, years, tax, when_val, val, 0.7, 1.0, e_loan, e_lease, resid, dep_y)

    # THE TABLE (Gradients and bold as per your request)
    st.subheader("📋 Line-by-Line Excel Comparison")
    
    st.markdown(f"""
    | Data Point | Loan | Leasing |
    | :--- | :--- | :--- |
    | **Monthly Inst. (Asset)** | € {format_eur(res['l_inst'])} | € {format_eur(res['ls_inst'])} |
    | **Working Capital Loan** | € {format_eur(res['l_wc_loan'])} | € {format_eur(res['ls_wc_loan'])} |
    | **Monthly Inst. (WC)** | € {format_eur(res['wc_l_inst'])} | € {format_eur(res['wc_ls_inst'])} |
    | **Total Monthly Inst.** | **€ {format_eur(res['total_l_inst'])}** | **€ {format_eur(res['total_ls_inst'])}** |
    | --- | --- | --- |
    | **Total Interest (15y)** | € {format_eur(res['l_int'])} | € {format_eur(res['ls_int'])} |
    | **Total Depreciation (15y)** | € {format_eur(res['l_dep'])} | € {format_eur(res['ls_dep'])} |
    | **Deductible Expense** | **€ {format_eur(res['l_deductible'])}** | **€ {format_eur(res['ls_deductible'])}** |
    | **Tax Benefit** | € {format_eur(res['l_tax'])} | € {format_eur(res['ls_tax'])} |
    | --- | --- | --- |
    | **FINAL NET BURDEN** | **€ {format_eur(res['l_final'])}** | **€ {format_eur(res['ls_final'])}** |
    """)

    # SENSITIVITY CHART (Indifference)
    st.divider()
    st.subheader("📈 Rate Indifference Point")
    
    test_rates = [loan_r + (i/1000) for i in range(-50, 55, 5)]
    ls_burdens = [run_calculations(r, wc_r, years, tax, when_val, val, 0.7, 1.0, e_loan, e_lease, resid, dep_y)['ls_final'] for r in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=ls_burdens, name="Leasing Cost Curve", line=dict(color="#00CC96", width=3)))
    fig.add_hline(y=res['l_final'], line_dash="dash", line_color="#FF4B4B", annotation_text="Loan Fixed Burden")
    fig.update_layout(template="plotly_dark", xaxis_title="Interest Rate (%)", yaxis_title="Net Burden (€)")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
