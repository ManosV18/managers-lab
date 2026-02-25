import streamlit as st
from core.engine import compute_core_metrics

def show_wacc_optimizer():
    st.header("⚖️ Capital Structure & WACC Optimizer")
    st.markdown("---")

    # 1. INDUSTRY DATABASE (Unlevered Betas - Proxy data)
    industry_betas = {
        "Retail": 0.85,
        "Manufacturing": 0.95,
        "Services / Consulting": 1.05,
        "Technology / Software": 1.25,
        "Food & Beverage": 0.75,
        "Construction": 1.10,
        "Generic Small Business": 1.00
    }

    # 2. INPUT SECTION
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏦 Debt Profile")
        loan_amt = st.number_input("Total Debt (Loans/Factoring) (€)", value=100000.0, step=10000.0)
        interest_rate = st.slider("Avg. Interest Rate (Before Tax) %", 1.0, 15.0, 6.5) / 100
        tax_rate = 0.22 # Standard Corporate Tax
        
        cost_of_debt = interest_rate * (1 - tax_rate)
        st.caption(f"Effective After-Tax Cost of Debt: **{cost_of_debt:.2%}**")

    with col2:
        st.subheader("股权 Equity Profile")
        equity_val = st.number_input("Owner's Equity (Book Value) (€)", value=200000.0, step=10000.0)
        selected_ind = st.selectbox("Select Business Sector", list(industry_betas.keys()))
        u_beta = industry_betas[selected_ind]
        
        # Risk-Free Rate (e.g., 10Y Government Bond)
        rf = st.number_input("Risk-Free Rate (e.g. 10Y Bond) %", value=3.5) / 100
        erp = 0.055 # Standard Equity Risk Premium

    # 3. THE "HIDDEN" CALCULATIONS (Levering the Beta)
    # Formula: Beta_Levered = Beta_Unlevered * [1 + (1 - Tax)*(Debt/Equity)]
    de_ratio = loan_amt / equity_val if equity_val > 0 else 0
    l_beta = u_beta * (1 + (1 - tax_rate) * de_ratio)
    
    # Cost of Equity (CAPM)
    re = rf + (l_beta * erp)
    
    # 4. WACC COMPOSITION
    total_cap = loan_amt + equity_val
    w_d = loan_amt / total_cap if total_cap > 0 else 0
    w_e = equity_val / total_cap if total_cap > 0 else 0
    
    final_wacc = (w_e * re) + (w_d * cost_of_debt)

    # 5. VISUALIZATION
    st.divider()
    c1, c2, c3 = st.columns([1, 1, 1])
    
    c1.metric("Levered Beta", f"{l_beta:.2f}", help="Adjusted for your specific Debt-to-Equity ratio.")
    c2.metric("Cost of Equity (Re)", f"{re:.2%} ", help="The return your capital 'demands' based on risk.")
    c3.metric("Final WACC", f"{final_wacc:.2%}", delta="Strategic Hurdle Rate")

    

    # 6. COLD ANALYTICAL VERDICT
    st.subheader("📊 Strategic Insight")
    
    st.write(f"""
    Your current WACC is **{final_wacc:.2%}**. 
    * **Interpretation:** Any new investment or project must yield a return higher than this to create value. 
    * **Leverage Effect:** Your Debt/Equity ratio is **{de_ratio:.2f}**. 
    """)
    
    if cost_of_debt < re:
        st.success(f"**Insight:** Debt is cheaper than Equity ({cost_of_debt:.1%} vs {re:.1%}). Controlled leverage could lower your total cost of capital.")
    else:
        st.warning("**Insight:** High interest rates are making debt nearly as expensive as equity. Focus on deleveraging.")

    # SYNC TO GLOBAL SYSTEM
    if st.button("Apply this WACC to Global Model", use_container_width=True):
        st.session_state.wacc = final_wacc
        st.success("WACC updated across all tools!")

if __name__ == "__main__":
    show_wacc_optimizer()
