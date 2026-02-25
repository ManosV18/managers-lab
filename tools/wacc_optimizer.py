import streamlit as st
from core.engine import compute_core_metrics

def show_wacc_optimizer():
    st.header("🏗️ Capital Structure Control Layer")
    st.markdown("Καθορισμός του Hurdle Rate (WACC) βάσει κλαδικού κινδύνου και χρηματοοικονομικής μόχλευσης.")
    
    # Industry Data (Unlevered Beta Proxies)
    industry_data = {
        "Retail": 0.85, "Manufacturing": 0.95, "Services": 1.05,
        "Technology": 1.25, "F&B": 0.75, "Construction": 1.10
    }

    # 1. CAPITAL MIX INPUTS
    st.subheader("1. Capital Composition")
    c1, c2 = st.columns(2)
    
    debt_val = c1.number_input("Total Interest-Bearing Debt (€)", value=150000.0, step=10000.0)
    equity_val = c2.number_input("Shareholder Equity (Book Value) (€)", value=300000.0, step=10000.0)
    
    # 2. COST OF DEBT (Rd)
    st.subheader("2. Debt Risk Profile")
    interest_rate = st.slider("Pre-tax Average Interest Rate (%)", 1.0, 15.0, 6.5) / 100
    tax_rate = 0.22 
    rd_after_tax = interest_rate * (1 - tax_rate)

    # 3. COST OF EQUITY (Re) - THE PROXY LAYER
    st.subheader("3. Equity Risk & Market Proxy")
    col_a, col_b = st.columns(2)
    sector = col_a.selectbox("Industry Benchmark", list(industry_data.keys()))
    rf = col_b.number_input("Risk-Free Rate (10Y Bond) %", value=3.5) / 100
    
    u_beta = industry_data[sector]
    erp = 0.055 # Equity Risk Premium
    
    # Leverage Logic: Re-levering Beta based on D/E
    de_ratio = debt_val / equity_val if equity_val > 0 else 0
    l_beta = u_beta * (1 + (1 - tax_rate) * de_ratio)
    re = rf + (l_beta * erp)

    # 4. WACC CALCULATION
    total_cap = debt_val + equity_val
    w_d = debt_val / total_cap if total_cap > 0 else 0
    w_e = equity_val / total_cap if total_cap > 0 else 0
    wacc = (w_e * re) + (w_d * rd_after_tax)

    st.divider()

    # 5. CONTROL PANEL METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Levered Beta", f"{l_beta:.2f}", help="Risk volatility adjusted for your debt.")
    m2.metric("Cost of Equity", f"{re:.2%}")
    m3.metric("Strategic WACC", f"{wacc:.2%}", delta="Hurdle Rate")

    # 6. ANALYTICAL VERDICT
    st.subheader("💡 Strategic Verdict")
    if de_ratio > 1.5:
        st.warning(f"**High Leverage Alert:** Your D/E ratio ({de_ratio:.2f}) is elevating your Cost of Equity. The market perceives your equity as high-risk due to debt levels.")
    
    st.info(f"To create value, any strategic move (Inventory, Receivables) must provide a return > **{wacc:.2%}**.")

    if st.button("Sync Capital Structure to Global Engine", use_container_width=True):
        st.session_state.wacc = wacc
        st.session_state.debt_to_equity = de_ratio
        st.success("Capital Structure Control Layer updated.")

if __name__ == "__main__":
    show_wacc_optimizer()
