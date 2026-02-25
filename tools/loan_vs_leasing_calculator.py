import streamlit as st
import plotly.graph_objects as go

# 1. PMT Math Replacement (to avoid numpy_financial dependency)
def calculate_pmt(rate, nper, pv, fv=0, type=0):
    if rate == 0: return -(pv + fv) / nper
    pv_factor = (1 + rate) ** nper
    payment = (rate * (pv * pv_factor + fv)) / ((pv_factor - 1) * (1 + rate * type))
    return payment

def format_eur(x):
    return f"€ {x:,.0f}"

# 2. CALCULATION ENGINE (Your Original Formulas)
def run_calculations(loan_rate, wc_rate, years, tax_rate, when, value, loan_pct, lease_pct, exp_loan, exp_lease, residual, dep_years):
    months = years * 12
    
    # --- LOAN (Your exact formula) ---
    loan_inst = calculate_pmt(loan_rate / 12, months, value * loan_pct, 0, when)
    wc_loan = value * (1 - loan_pct) + exp_loan
    wc_inst = calculate_pmt(wc_rate / 12, months, wc_loan, 0, when)

    loan_cash = (loan_inst + wc_inst) * months
    loan_interest = loan_cash - value
    loan_depr = (value + exp_loan) / dep_years * years
    loan_tax = (loan_interest + loan_depr) * tax_rate
    loan_final = value + loan_interest - loan_tax

    # --- LEASING (Your exact formula) ---
    lease_inst = calculate_pmt(loan_rate / 12, months, value * lease_pct, 0, when)
    wc_lease = value * (1 - lease_pct) + exp_lease
    wc_lease_inst = calculate_pmt(wc_rate / 12, months, wc_lease, 0, when)

    lease_cash = (lease_inst + wc_lease_inst) * months
    lease_interest = lease_cash - value
    lease_depr = value + exp_lease + residual
    lease_tax = ((wc_lease_inst * months - wc_lease) + lease_depr) * tax_rate
    lease_final = value + lease_interest - lease_tax
    
    return {
        "l_final": loan_final, "ls_final": lease_final,
        "l_cash": loan_cash, "l_int": loan_interest, "l_tx": loan_tax,
        "ls_cash": lease_cash, "ls_int": lease_interest, "ls_tx": lease_tax
    }

# 3. INTERFACE
def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Analytical Comparison")
    st.info("Independent evaluation based on your specific financial formulas.")

    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        st.subheader("Financial Terms")
        loan_r = st.number_input("Interest Rate (%)", value=6.0, key="r1") / 100
        wc_r = st.number_input("Working Capital Interest Rate (%)", value=8.0, key="r2") / 100
        years = st.number_input("Duration (years)", value=15, key="y1")
        tax = st.number_input("Corporate Tax Rate (%)", value=35.0, key="t1") / 100
        timing = st.radio("Payment Timing", ["End of Period", "Beginning of Period"])
        when_val = 1 if timing == "Beginning of Period" else 0

    with col_in2:
        st.subheader("Asset & Costs")
        val = st.number_input("Property Value (€)", value=250000.0, key="v1")
        loan_p = st.number_input("Loan Financing (%)", value=70.0, key="p1") / 100
        lease_p = st.number_input("Leasing Financing (%)", value=100.0, key="p2") / 100
        e_loan = st.number_input("Acquisition Costs – Loan (€)", value=35000.0)
        e_lease = st.number_input("Acquisition Costs – Leasing (€)", value=30000.0)
        resid = st.number_input("Residual Value (€)", value=3530.0)
        dep_y = st.number_input("Depreciation Period (years)", value=30)

    st.divider()
    
    res = run_calculations(loan_r, wc_r, years, tax, when_val, val, loan_p, lease_p, e_loan, e_lease, resid, dep_y)

    c1, c2 = st.columns(2)
    c1.metric("🏦 Loan Final Burden", format_eur(res['l_final']))
    c1.write(f"Cash Outflow: {format_eur(res['l_cash'])}")
    
    c2.metric("🧾 Leasing Final Burden", format_eur(res['ls_final']))
    c2.write(f"Cash Outflow: {format_eur(res['ls_cash'])}")

    

    # Sensitivity Logic
    st.subheader("📈 Rate Sensitivity")
    test_rates = [loan_r + (i/1000) for i in range(-50, 55, 5)]
    ls_burdens = [run_calculations(r, wc_r, years, tax, when_val, val, loan_p, lease_p, e_loan, e_lease, resid, dep_y)['ls_final'] for r in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=ls_burdens, name="Leasing Burden"))
    fig.add_hline(y=res['l_final'], line_dash="dash", line_color="red", annotation_text="Loan Fixed Burden")
    fig.update_layout(template="plotly_dark", xaxis_title="Leasing Rate (%)", yaxis_title="Final Burden (€)")
    st.plotly_chart(fig, use_container_width=True)

    if res['l_final'] < res['ls_final']:
        st.success("✅ **Verdict: Loan results in a lower net financial burden.**")
    else:
        st.success("✅ **Verdict: Leasing results in a lower net financial burden.**")

    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
