import streamlit as st

def show_wacc_optimizer_ui():
    st.header("📉 WACC Optimizer")
    st.info("Calculate the Weighted Average Cost of Capital to set the hurdle rate for all strategic investments.")

    s = st.session_state
    
    # --- DATA SYNC FROM BASELINE ---
    # Τραβάμε το Debt από το baseline. Αν δεν υπάρχει, βάζουμε 0.
    baseline_debt = float(s.get("total_debt", 0.0))
    # Για το Equity, στη "χοντρική" ανάλυση χρησιμοποιούμε το Invested Capital 
    # ή μια εκτίμηση της αγοράς. Εδώ προτείνω το Invested Capital ως αφετηρία.
    baseline_equity = float(s.get("metrics", {}).get("invested_capital", 1000000.0)) - baseline_debt
    baseline_equity = max(baseline_equity, 100000.0) # Guard για να μην είναι 0

    # --- INPUT SECTION ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏦 Capital Structure")
        # market_equity: Ξεκινάει από το baseline αλλά αλλάζει
        market_equity = st.number_input("Market Value of Equity (€)", value=baseline_equity, step=50000.0)
        # total_debt: Έρχεται απευθείας από το Home input
        total_debt = st.number_input("Total Debt (€)", value=baseline_debt, step=50000.0)
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=22.0) / 100
        
        total_capital = market_equity + total_debt
        # Αποφυγή DivisionByZero αν ο χρήστης μηδενίσει τα πάντα
        safe_total_cap = max(total_capital, 1.0)
        
        e_weight = market_equity / safe_total_cap
        d_weight = total_debt / safe_total_cap

    with col2:
        st.subheader("📈 Cost Components")
        risk_free = st.number_input("Risk-Free Rate (%)", value=3.5) / 100
        beta = st.number_input("Equity Beta (Sector Risk)", value=1.2)
        mkt_premium = st.number_input("Market Risk Premium (%)", value=5.5) / 100
        
        cost_of_equity = risk_free + (beta * mkt_premium)
        
        # Το επιτόκιο δανεισμού
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
    res3.metric("Final WACC", f"{wacc_pct:.2f}%", help="This is your hurdle rate.")

    # --- WEIGHTS VISUALIZATION ---
    st.write(f"**Capital Mix:** Equity {e_weight*100:.1f}% | Debt {d_weight*100:.1f}%")
    st.progress(e_weight)
    
    

    # --- GLOBAL SYNC ---
    st.subheader("🔐 Strategic Synchronization")
    st.write("Locking the WACC will update the discount rates in the CLV Simulator and other NPV tools.")
    
    if st.button("🔐 Lock WACC for Global Strategy", use_container_width=True):
        st.session_state.wacc_locked = round(wacc_pct, 2)
        # Αποθηκεύουμε και το κεφαλαιακό μείγμα για άλλα εργαλεία
        st.session_state.capital_mix = {"equity": e_weight, "debt": d_weight}
        st.success(f"WACC of {wacc_pct:.2f}% is now locked in the system memory.")

    # --- NAVIGATION ---
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
