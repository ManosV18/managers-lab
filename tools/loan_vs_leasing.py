import streamlit as st
import plotly.graph_objects as go

# Replacement for numpy_financial.pmt to ensure compatibility
def pmt(rate, nper, pv, fv=0, when=0):
    if rate == 0: return -(pv + fv) / nper
    temp = (1 + rate) ** nper
    payment = (pv * temp * rate + fv * rate) / (temp - 1)
    if when == 1:
        payment /= (1 + rate)
    return payment

def format_eur(x):
    return f"€ {x:,.0f}".replace(",", ".")

def calculate_final_burden(loan_rate, wc_rate, years, prop_val, l_fin_pct, ls_fin_pct, e_loan, e_ls, resid, dep_y, tax, pay_when):
    months = 12
    n_months = years * months

    # 1. Acquisition Cost
    acq_loan = prop_val + e_loan
    acq_ls = prop_val + e_ls

    # 2. Working Capital Loans
    wc_loan_amt = prop_val - (prop_val * l_fin_pct) + e_loan 
    wc_ls_amt = prop_val - (prop_val * ls_fin_pct) + e_ls     

    # 3. Monthly Installments
    m_loan = pmt(loan_rate / months, n_months, prop_val * l_fin_pct, 0, pay_when)
    m_ls = pmt(loan_rate / months, n_months, prop_val * ls_fin_pct, 0, pay_when)
    m_wc_loan = pmt(wc_rate / months, n_months, wc_loan_amt, 0, pay_when)
    m_wc_ls = pmt(wc_rate / months, n_months, wc_ls_amt, 0, pay_when)

    # 4. Totals
    total_m_loan = m_loan + m_wc_loan 
    total_m_ls = m_ls + m_wc_ls       

    # 5. Interest
    int_loan = (total_m_loan * n_months) - prop_val 
    int_ls = (total_m_ls * n_months) - prop_val     

    # 6. Total Cost
    cost_loan = int_loan + prop_val
    cost_ls = int_ls + prop_val

    # 7. Depreciation
    dep_loan = acq_loan / dep_y * years 
    dep_ls = acq_ls + resid 

    # 8. Deductible Expenses
    deduct_loan = int_loan + dep_loan 
    deduct_ls = (m_wc_ls * n_months - wc_ls_amt) + dep_ls 

    # 9. Tax Benefit & Final Burden
    tax_b_loan = deduct_loan * tax 
    tax_b_ls = deduct_ls * tax     

    final_loan = cost_loan - tax_b_loan 
    final_ls = cost_ls - tax_b_ls       

    return {
        "final_loan": final_loan, "final_ls": final_ls,
        "m_loan": m_loan, "m_ls": m_ls, "m_wc_l": m_wc_loan, "m_wc_ls": m_wc_ls,
        "int_l": int_loan, "int_ls": int_ls, "dep_l": dep_loan, "dep_ls": dep_ls,
        "tax_l": tax_b_loan, "tax_ls": tax_b_ls
    }

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Analytical Tool")
    
    col1, col2 = st.columns(2)
    with col1:
        l_rate = st.number_input("Loan Interest Rate (%)", value=6.0, key="lvl_loan_rate_in") / 100
        wc_rate = st.number_input("WC Interest Rate (%)", value=8.0, key="lvl_wc_rate_in") / 100
        years = st.number_input("Duration (Years)", value=15, key="lvl_years_in")
        tax = st.number_input("Tax Rate (%)", value=35.0, key="lvl_tax_in") / 100
        pay_when = 1 if st.radio("Payment Timing", ["Beginning", "End"], key="lvl_timing_in") == "Beginning" else 0

    with col2:
        val = st.number_input("Property Value (€)", value=250000.0, key="lvl_val_in")
        l_fin = st.number_input("Loan Financing (%)", value=70.0, key="lvl_lfin_in") / 100
        ls_fin = st.number_input("Leasing Financing (%)", value=100.0, key="lvl_lsfin_in") / 100
        e_loan = st.number_input("Loan Expenses (€)", value=35000.0, key="lvl_eloan_in")
        e_ls = st.number_input("Leasing Expenses (€)", value=30000.0, key="lvl_els_in")
        resid = st.number_input("Residual Value (€)", value=3530.0, key="lvl_resid_in")
        dep_y = st.number_input("Depreciation Period (Years)", value=30, key="lvl_depy_in")

    res = calculate_final_burden(l_rate, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when)

    st.divider()
    c_l, c_ls = st.columns(2)
    c_l.metric("🏦 Loan Final Burden", format_eur(res['final_loan']))
    c_ls.metric("🧾 Leasing Final Burden", format_eur(res['final_ls']))

    # Sensitivity Chart
    st.subheader("📈 Rate Sensitivity")
    test_rates = [l_rate + (i/1000) for i in range(-50, 55, 5)]
    ls_vals = [calculate_final_burden(r, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when)['final_ls'] for r in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=ls_vals, name="Leasing Cost"))
    fig.add_hline(y=res['final_loan'], line_dash="dash", line_color="red", annotation_text="Loan Fixed Cost")
    fig.update_layout(template="plotly_dark", xaxis_title="Interest Rate (%)", yaxis_title="Final Burden (€)")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("⬅️ Back to Library Hub", key="lvl_back_btn"):
        st.session_state.selected_tool = None
        st.rerun()
