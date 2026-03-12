import streamlit as st

def show_wacc_optimizer_ui():
    st.header("📉 WACC Optimizer")
    st.info("Calculate the Weighted Average Cost of Capital to set the hurdle rate for all strategic investments.")

    s = st.session_state
    
    # --- INPUT SECTION ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏦 Capital Structure")
        market_equity = st.number_input("Market Value of Equity (€)", value=1000000.0, step=50000.0)
        total_debt = st.number_input("Total Debt (€)", value=500000.0, step=50000.0)
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=22.0) / 100
        
        total_capital = market_equity + total_debt
        e_weight = market_equity / total_capital
        d_weight = total_debt / total_capital

    with col2:
        st.subheader("📈 Cost Components")
        # Cost of Equity (CAPM Logic)
        risk_free = st.number_input("Risk-Free Rate (%)", value=3.5) / 100
        beta = st.number_input("Equity Beta (Sector Risk)", value=1.2)
        mkt_premium = st.number_input("Market Risk Premium (%)", value=5.5) / 100
        
        cost_of_equity = risk_free + (beta * mkt_premium)
        
        # Cost of Debt
        avg_interest_rate = st.number_input("Avg. Interest Rate on Debt (%)", value=6.0) / 100
        cost_of_debt = avg_interest_rate * (1 - tax_rate)

    # --- CALCULATIONS ---
    wacc = (e_weight * cost_of_equity) + (d_weight * cost_of_debt)
    wacc_pct = wacc * 100

    st.divider()

    # --- RESULTS ---
    res1, res2, res3 = st.columns(3)
    res1.metric("Cost of Equity (Ke)", f"{cost_of_equity*100:.2f}%")
    res2.metric("After-Tax Cost of Debt (Kd)", f"{cost_of_debt*100:.2f}%")
    res3.metric("Final WACC", f"{wacc_pct:.2f}%")

    

    # --- WEIGHTS VISUALIZATION ---
    st.write(f"**Capital Mix:** Equity {e_weight*100:.1f}% | Debt {d_weight*100:.1f}%")
    st.progress(e_weight)

    # --- GLOBAL SYNC ---
    st.subheader("🔐 Strategic Synchronization")
    st.write("Locking the WACC will update the discount rates in the CLV Simulator and other NPV tools.")
    
    if st.button("🔐 Lock WACC for Global Strategy", use_container_width=True):
        st.session_state.wacc_locked = round(wacc_pct, 2)
        st.success(f"WACC of {wacc_pct:.2f}% is now locked in the system memory.")

    # --- NAVIGATION ---
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

if __name__ == "__main__":
    show_wacc_optimizer_ui()
