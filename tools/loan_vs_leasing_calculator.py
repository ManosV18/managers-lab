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

    # 1. Acquisition Cost (Αξία Απόκτησης)
    acq_loan = prop_val + e_loan
    acq_ls = prop_val + e_ls

    # 2. Working Capital Loans (Δάνεια Κεφαλαίου Κίνησης)
    wc_loan_amt = prop_val - (prop_val * l_fin_pct) + e_loan # 110,000
    wc_ls_amt = prop_val - (prop_val * ls_fin_pct) + e_ls     # 30,000

    # 3. Monthly Installments (Μηνιαίες Δόσεις)
    m_loan = pmt(loan_rate / months, n_months, prop_val * l_fin_pct, 0, pay_when)
    m_ls = pmt(loan_rate / months, n_months, prop_val * ls_fin_pct, 0, pay_when)
    m_wc_loan = pmt(wc_rate / months, n_months, wc_loan_amt, 0, pay_when)
    m_wc_ls = pmt(wc_rate / months, n_months, wc_ls_amt, 0, pay_when)

    # 4. Totals (Σύνολα)
    total_m_loan = m_loan + m_wc_loan # 2,514
    total_m_ls = m_ls + m_wc_ls       # 2,384

    # 5. Interest (Τόκοι)
    int_loan = (total_m_loan * n_months) - prop_val # 202,458
    int_ls = (total_m_ls * n_months) - prop_val     # 179,110

    # 6. Total 15-year Cost (Ολικό Κόστος)
    cost_loan = int_loan + prop_val
    cost_ls = int_ls + prop_val

    # 7. Depreciation (Αποσβέσεις) - Based on your logic
    dep_loan = acq_loan / dep_y * years # 142,500
    # Logic from your code: (acq_ls / years * years) + residual
    dep_ls = acq_ls + resid # 283,530

    # 8. Deductible Expenses (Εκπιπτέα Έξοδα)
    deduct_loan = int_loan + dep_loan # 344,958
    # Your specific logic for leasing deductible:
    deduct_ls = (m_wc_ls * n_months - wc_ls_amt) + dep_ls # 304,793

    # 9. Tax Benefit & Final Burden
    tax_b_loan = deduct_loan * tax # 120,735
    tax_b_ls = deduct_ls * tax     # 106,678

    final_loan = cost_loan - tax_b_loan # 331,723
    final_ls = cost_ls - tax_b_ls       # 322,432

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
        l_rate = st.number_input("Loan Interest Rate (%)", value=6.0) / 100
        wc_rate = st.number_input("WC Interest Rate (%)", value=8.0) / 100
        years = st.number_input("Duration (Years)", value=15)
        tax = st.number_input("Tax Rate (%)", value=35.0) / 100
        pay_when = 1 if st.radio("Payment Timing", ["Beginning", "End"]) == "Beginning" else 0

    with col2:
        val = st.number_input("Property Value (€)", value=250000.0)
        l_fin = st.number_input("Loan Financing (%)", value=70.0) / 100
        ls_fin = st.number_input("Leasing Financing (%)", value=100.0) / 100
        e_loan = st.number_input("Loan Expenses (€)", value=35000.0)
        e_ls = st.number_input("Leasing Expenses (€)", value=30000.0)
        resid = st.number_input("Residual Value (€)", value=3530.0)
        dep_y = st.number_input("Depreciation Period (Years)", value=30)

    res = calculate_final_burden(l_rate, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when)

    # 📋 Results Comparison
    st.divider()
    c_l, c_ls = st.columns(2)
    c_l.metric("🏦 Loan Final Burden", format_eur(res['final_loan']))
    c_ls.metric("🧾 Leasing Final Burden", format_eur(res['final_ls']))

    # 📈 Sensitivity Chart
    st.subheader("📈 Rate Sensitivity & Indifference")
    test_rates = [l_rate + (i/1000) for i in range(-50, 55, 5)]
    ls_vals = [calculate_final_burden(r, wc_rate, years, val, l_fin, ls_fin, e_loan, e_ls, resid, dep_y, tax, pay_when)['final_ls'] for r in test_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in test_rates], y=ls_vals, name="Leasing Cost"))
    fig.add_hline(y=res['final_loan'], line_dash="dash", line_color="red", annotation_text="Loan Fixed Cost")
    fig.update_layout(template="plotly_dark", xaxis_title="Interest Rate (%)", yaxis_title="Final Burden (€)")
    st.plotly_chart(fig, use_container_width=True)
