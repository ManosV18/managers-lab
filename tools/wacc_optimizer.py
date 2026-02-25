import streamlit as st
from core.engine import compute_core_metrics

def show_wacc_optimizer():
    st.header("🏗️ Capital Structure Control Layer")
    st.info("Define the business hurdle rate (WACC) based on debt composition and industry risk proxies.")

    # 1. DEBT MIX ANALYSIS
    st.subheader("1. Debt Composition")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Short-term Debt**")
        st.caption("Overdrafts, Factoring, Working Capital Loans")
        st_debt = st.number_input("Principal Amount (€)", value=50000.0, key="st_d", step=5000.0)
        st_rate = st.slider("Interest Rate (%)", 3.0, 18.0, 8.5, key="st_r") / 100
        
    with col2:
        st.markdown("**Long-term Debt**")
        st.caption("Investment Loans, Mortgages, Bonds")
        lt_debt = st.number_input("Principal Amount (€) ", value=150000.0, key="lt_d", step=5000.0)
        lt_rate = st.slider("Interest Rate (%) ", 1.0, 12.0, 5.5, key="lt_r") / 100

    total_debt = st_debt + lt_debt
    
    # Weighted Average Cost of Debt (Pre-tax)
    if total_debt > 0:
        avg_interest_rate = ((st_debt * st_rate) + (lt_debt * lt_rate)) / total_debt
    else:
        avg_interest_rate = 0.0

    # 2. EQUITY & INDUSTRY PROXY
    st.subheader("2. Equity & Sector Risk")
    equity_val = st.number_input("Owner's Equity / Net Worth (€)", value=300000.0, step=10000.0)
    
    industry_data = {
        "Retail": 0.85, "Manufacturing": 0.95, "Services": 1.05,
        "Technology": 1.25, "F&B": 0.75, "Construction": 1.10, "General SME": 1.00
    }
    
    c1, c2 = st.columns(2)
    sector = c1.selectbox("Industry Benchmark (Unlevered Beta)", list(industry_data.keys()))
    rf = c2.number_input("Risk-Free Rate (e.g., 10Y Gov Bond) %", value=3.5) / 100
    
    # 3. ANALYTICAL ENGINE: LEVERED BETA & CAPM
    tax_rate = 0.22 
    u_beta = industry_data[sector]
    
    de_ratio = total_debt / equity_val if equity_val > 0 else 0
    # Hamada Equation for Levered Beta
    l_beta = u_beta * (1 + (1 - tax_rate) * de_ratio)
    
    # Cost of Equity (CAPM)
    erp = 0.055 
    re = rf + (l_beta * erp)
    rd_after_tax = avg_interest_rate * (1 - tax_rate)

    # 4. FINAL WACC WEIGHTING
    total_cap = total_debt + equity_val
    if total_cap > 0:
        wacc = ((equity_val/total_cap) * re) + ((total_debt/total_cap) * rd_after_tax)
    else:
        wacc = 0.15 

    st.divider()

    # 5. CONTROL PANEL METRICS
    res1, res2, res3 = st.columns(3)
    res1.metric("W.A. Interest Rate", f"{avg_interest_rate:.2%}")
    res2.metric("Cost of Equity (Re)", f"{re:.2%}")
    # FIXED: Parenthesis closed correctly
    res3.metric("Strategic WACC", f"{wacc:.2%}", delta="Global Hurdle Rate")

    

    # 6. COLD ANALYTICAL VERDICT
    st.subheader("📊 Strategic Insight")
    debt_weight = (total_debt/total_cap) if total_cap > 0 else 0
    
    st.write(f"The business capital structure is **{debt_weight:.1%}** Debt and **{(1-debt_weight):.1%}** Equity.")
    
    if st_debt > lt_debt:
        st.warning("🚨 **Observation:** Short-term debt dominates. This increases refinancing risk. Consider long-term restructuring.")

    if st.button("Sync Strategic Hurdle Rate to Global Engine", use_container_width=True):
        st.session_state.wacc = wacc
        st.session_state.debt_to_equity = de_ratio
        st.success("WACC updated successfully.")
