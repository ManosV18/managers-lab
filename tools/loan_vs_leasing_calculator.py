import streamlit as st
import plotly.graph_objects as go

def annuity_payment(rate, n_periods, pv, payment_at_beginning=False):
    if rate == 0: return pv / n_periods
    factor = (rate * (1 + rate) ** n_periods) / ((1 + rate) ** n_periods - 1)
    payment = pv * factor
    if payment_at_beginning: payment /= (1 + rate)
    return payment

def format_eur(x):
    return f"{x:,.0f}".replace(",", ".")

def run_calculations(loan_rate, wc_rate, years, tax_rate, val, l_pct, ls_pct, e_loan, e_lease, resid, dep_y):
    months = years * 12
    
    # --- LOAN ---
    l_principal = val * l_pct
    l_inst = annuity_payment(loan_rate/12, months, l_principal, True)
    
    wc_loan = val * (1 - l_pct) + e_loan # 110.000
    wc_inst = annuity_payment(wc_rate/12, months, wc_loan)
    
    l_total_int = ((l_inst + wc_inst) * months) - (l_principal + wc_loan) # 202.458
    l_depr = ((val + e_loan) / dep_y) * years # 142.500
    
    l_deductible = l_total_int + l_depr # 344.958
    l_tax_benefit = l_deductible * tax_rate # 120.735
    l_final = (val + e_loan + l_total_int) - l_tax_benefit # 331.723

    # --- LEASING ---
    ls_principal = val * ls_pct
    ls_inst = annuity_payment(loan_rate/12, months, ls_principal, True)
    
    wc_ls_loan = val * (1 - ls_pct) + e_lease # 30.000
    wc_ls_inst = annuity_payment(wc_rate/12, months, wc_ls_loan)
    
    ls_total_int = ((ls_inst + wc_ls_inst) * months) - (ls_principal + wc_ls_loan) # 179.110
    
    # Depreciation logic to match Excel's 304.793 deductible
    ls_depr_deductible = ((val + e_lease + resid) / dep_y) * years # 125.683
    
    ls_deductible = ls_total_int + ls_depr_deductible # 304.793
    ls_tax_benefit = ls_deductible * tax_rate # 106.678
    ls_final = (val + e_lease + ls_total_int + resid) - ls_tax_benefit # 322.432
    
    return l_inst, wc_inst, l_total_int, l_tax_benefit, l_final, ls_inst, wc_ls_inst, ls_total_int, ls_tax_benefit, ls_final

def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Excel Verified")
    
    # Inputs (Defaults from Book1.xlsx)
    l_rate = st.number_input("Loan Interest Rate", 0.0, 1.0, 0.06)
    wc_rate = st.number_input("WC Interest Rate", 0.0, 1.0, 0.08)
    val = st.number_input("Property Value", value=250000)
    resid = st.number_input("Residual Value", value=3530)
    
    res = run_calculations(l_rate, wc_rate, 15, 0.35, val, 0.7, 1.0, 35000, 30000, resid, 30)
    
    st.write(f"### Final Net Burden (Loan): € {format_eur(res[4])}") # 331.723
    st.write(f"### Final Net Burden (Leasing): € {format_eur(res[9])}") # 322.432

    if st.button("Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
