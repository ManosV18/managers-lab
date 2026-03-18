import streamlit as st

def show_wacc_optimizer_ui():
    st.header("📉 WACC Optimizer")
    st.info("Calculate the Weighted Average Cost of Capital (Hurdle Rate) based on your actual Capital Structure.")

    s = st.session_state
    
    # --- DATA SYNC & LOGIC ---
    # 1. Παίρνουμε το Debt απευθείας από το Baseline (Home)
    baseline_debt = float(s.get("total_debt", 500000.0))
    
    # 2. Παίρνουμε το Invested Capital από τα metrics
    total_inv_capital = float(s.get("metrics", {}).get("invested_capital", 1300000.0))
    
    # 3. Το Equity είναι η ΔΙΑΦΟΡΑ (Invested Capital - Debt)
    # Βάζουμε ένα max(..., 1000) για να μην βγει αρνητικό αν το χρέος είναι τεράστιο
    baseline_equity = max(total_inv_capital - baseline_debt, 1000.0)

    # --- INPUT SECTION ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏦 Capital Structure (Synced)")
        # Ο χρήστης βλέπει τα ποσά που όρισε στο Baseline, αλλά μπορεί να κάνει what-if
        market_equity = st.number_input("Market Value of Equity ($)", value=baseline_equity, step=50000.0, help="Calculated as: Invested Capital - Total Debt")
        total_debt = st.number_input("Total Debt ($)", value=baseline_debt, step=50000.0)
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=22.0) / 100
        
        actual_total_cap = market_equity + total_debt
        e_weight = market_equity / actual_total_cap if actual_total_cap > 0 else 0
        d_weight = total_debt / actual_total_cap if actual_total_cap > 0 else 0

    with col2:
        st.subheader("📈 Cost Components")
        risk_free = st.number_input("Risk-Free Rate (%)", value=3.5) / 100
        beta = st.number_input("Equity Beta (Sector Risk)", value=1.2)
        mkt_premium = st.number_input("Market Risk Premium (%)", value=5.5) / 100
        
        cost_of_equity = risk_free + (beta * mkt_premium)
        
        avg_interest_rate = st.number_input("Avg. Interest Rate on Debt (%)", value=6.0) / 100
        # Το χρέος έχει φορολογική ασπίδα (Tax Shield)
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

    # --- VISUALIZATION ---
    st.write(f"**Capital Mix:** Equity {e_weight*100:.1f}% (${market_equity:,.0f}) | Debt {d_weight*100:.1f}% (${total_debt:,.0f})")
    st.progress(e_weight)
    
    

    # --- GLOBAL SYNC ---
    if st.button("🔐 Lock WACC for Global Strategy", use_container_width=True):
        st.session_state.wacc_locked = round(wacc_pct, 2)
        st.success(f"WACC of {wacc_pct:.2f}% is now locked. All NPV/CLV tools will use this rate.")

    # --- NAVIGATION ---
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.rerun()
