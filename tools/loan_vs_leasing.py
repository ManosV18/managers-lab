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

    # 6. Total 15-year Cost
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
    final_
