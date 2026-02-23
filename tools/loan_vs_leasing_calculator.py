import streamlit as st
import numpy_financial as npf
import matplotlib.pyplot as plt

# -------------------------------------------------
# Formatting Helpers
# -------------------------------------------------
def pmt(rate, nper, pv, fv=0, when=0):
    return -npf.pmt(rate, nper, pv, fv, when)

def format_eur(x):
    return f"€ {x:,.0f}".replace(",", ".")

# CALCULATION ENGINE
def run_calculations(loan_rate, wc_rate, years, tax_rate, when, value, loan_pct, lease_pct, exp_loan, exp_lease, residual, dep_years):
    months = years * 12
    
    # --- LOAN ---
    loan_inst = pmt(loan_rate / 12, months, value * loan_pct, 0, when)
    wc_loan = value * (1 - loan_pct) + exp_loan
    wc_inst = pmt(wc_rate / 12, months, wc_loan, 0, when)

    loan_cash = (loan_inst + wc_inst) * months
    loan_interest = loan_cash - value
    loan_depr = (value + exp_loan) / dep_years * years
    loan_tax = (loan_interest + loan_depr) * tax_rate
    loan_final = value + loan_interest - loan_tax

    # --- LEASING ---
    lease_inst = pmt(loan_rate / 12, months, value * lease_pct, 0, when)
    wc_lease = value * (1 - lease_pct) + exp_lease
    wc_lease_inst = pmt(wc_rate / 12, months, wc_lease, 0, when)

    lease_cash = (lease_inst + wc_lease_inst) * months
    lease_interest = lease_cash - value
    lease_depr = value + exp_lease + residual
    lease_tax = ((wc_lease_inst * months - wc_lease) + lease_depr) * tax_rate
    lease_final = value + lease_interest - lease_tax
    
    return loan_final, lease_final, loan_cash, loan_interest, loan_depr, loan_tax, lease_cash, lease_interest, lease_depr, lease_tax

# -------------------------------------------------
# MAIN INTERFACE
# -------------------------------------------------
def loan_vs_leasing_ui():
    st.header("📊 Loan vs Leasing – Analytical Comparison")
    st.info("Independent evaluation module. Enter asset-specific financial terms below.")

    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        st.subheader("Financial Terms")
        loan_rate_input = st.number_input("Interest Rate (%)", value=6.0, key="lvl_loan_r") / 100
        wc_rate_input = st.number_input("Working Capital Interest Rate (%)", value=8.0, key="lvl_wc_r") / 100
        years_input = st.number_input("Duration (years)", value=15, key="lvl_years")
        tax_rate_input = st.number_input("Corporate Tax Rate (%)", value=35.0, key="lvl_tax") / 100
        timing = st.radio("Payment Timing", ["End of Period", "Beginning of Period"], key="lvl_timing")
        when_val = 1 if timing == "Beginning of Period" else 0

    with col_in2:
        st.subheader("Asset & Costs")
        value_input = st.number_input("Property Value (€)", value=250000.0, key="lvl_val")
        loan_pct_input = st.number_input("Loan Financing (%)", value=70.0, key="lvl_loan_p") / 100
        lease_pct_input = st.number_input("Leasing Financing (%)", value=100.0, key="lvl_lease_p") / 100
        exp_loan_input = st.number_input("Acquisition Costs – Loan (€)", value=35000.0, key="lvl_exp_l")
        exp_lease_input = st.number_input("Acquisition Costs – Leasing (€)", value=30000.0, key="lvl_exp_ls")
        residual_input = st.number_input("Residual Value (€)", value=3530.0, key="lvl_res")
        dep_years_input = st.number_input("Depreciation Period (years)", value=30, key="lvl_dep")

    st.divider()
    
    # Execution Button
    if st.button("🚀 Run Financial Analysis", use_container_width=True):
        l_final, ls_final, l_cash, l_int, l_dep, l_tx, ls_cash, ls_int, ls_dep, ls_tx = run_calculations(
            loan_rate_input, wc_rate_input, years_input, tax_rate_input, when_val, 
            value_input, loan_pct_input, lease_pct_input, exp_loan_input, exp_lease_input, 
            residual_input, dep_years_input
        )

        # RESULTS DASHBOARD
        st.subheader("📉 Analytical Breakdown")
        c1, c2 = st.columns(2)

        with c1:
            st.info("### 🏦 Loan Option")
            st.write("**Total Cash Outflows:**", format_eur(l_cash))
            st.write("**Interest Cost:**", format_eur(l_int))
            st.write("**Tax Shield:**", format_eur(l_tx))
            st.metric("Final Burden", format_eur(l_final))

        with c2:
            st.success("### 🧾 Leasing Option")
            st.write("**Total Cash Outflows:**", format_eur(ls_cash))
            st.write("**Financing Cost:**", format_eur(ls_int))
            st.write("**Tax Shield:**", format_eur(ls_tx))
            st.metric("Final Burden", format_eur(ls_final))

        st.divider()

        # EQUILIBRIUM ANALYSIS
        st.subheader("📈 Rate Equilibrium (Sensitivity)")
        test_rates = [loan_rate_input + (i/1000) for i in range(-50, 55, 5)]
        ls_burdens = []
        for r in test_rates:
            res = run_calculations(r, wc_rate_input, years_input, tax_rate_input, when_val, 
                                 value_input, loan_pct_input, lease_pct_input, exp_loan_input, 
                                 exp_lease_input, residual_input, dep_years_input)
            ls_burdens.append(res[1])
            
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot([r*100 for r in test_rates], ls_burdens, label='Leasing Cost Curve', color='#1f77b4', marker='o')
        ax.axhline(y=l_final, color='r', linestyle='--', label=f'Loan Fixed Burden')
        ax.set_xlabel("Leasing Rate (%)")
        ax.set_ylabel("Final Burden (€)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        # Indifference Point Logic
        indifference_rate = None
        for i in range(len(test_rates) - 1):
            if (ls_burdens[i] - l_final) * (ls_burdens[i+1] - l_final) <= 0:
                r1, r2 = test_rates[i], test_rates[i+1]
                b1, b2 = ls_burdens[i], ls_burdens[i+1]
                indifference_rate = r1 + (l_final - b1) * (r2 - r1) / (b2 - b1)
                break
        
        if indifference_rate:
            st.warning(f"**Indifference Point:** Leasing is superior if its rate is below **{indifference_rate*100:.2f}%**.")
        
        st.divider()
        if l_final < ls_final:
            st.success("✅ **Verdict: Loan financing results in a lower net financial burden.**")
        else:
            st.success("✅ **Verdict: Leasing results in a lower net financial burden.**")
