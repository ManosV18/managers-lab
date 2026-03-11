import streamlit as st

def run_home():
    s = st.session_state

    # Ενοποίηση ονομάτων μεταβλητών (Keys)
    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    ads = s.get("annual_debt_service", 0.0) 
    cash = s.get("opening_cash", 10000.0)
    tp = s.get("target_profit_goal", 0.0)

    # Quick Calculations για το Snapshot
    margin = p - vc
    bep_units = (fc + ads + tp) / margin if margin > 0 else 0
    
    st.markdown("<h1 style='text-align:center;'>Managers Lab.</h1>", unsafe_allow_html=True)

    # --- EXECUTIVE SNAPSHOT ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Simulated Volume", f"{v:,.0f} units")
    c2.metric("Cash Break-Even", f"{bep_units:,.0f} units")
    c3.metric("Survival Buffer", f"{((v-bep_units)/v*100) if v>0 else 0:.1f}%")

    st.divider()

    col_input, col_nav = st.columns([0.45, 0.55], gap="large")

    with col_input:
        st.subheader("⚙️ Global Parameters")
        with st.expander("📊 Business Baseline", expanded=True):
            st.number_input("Unit Price (€)", value=float(p), key="price")
            st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
            st.number_input("Annual Volume", value=int(v), key="volume")
            st.number_input("Annual Fixed Costs (€)", value=float(fc), key="fixed_cost")
            st.number_input("Target Profit Goal (€)", value=float(tp), key="target_profit_goal")

        with st.expander("💰 Liquidity & Debt", expanded=False):
            st.number_input("Opening Cash (€)", value=float(cash), key="opening_cash")
            st.number_input("Annual Debt Service (€)", value=float(ads), key="annual_debt_service")

        if st.button("🔒 Lock & Initialize Engine", type="primary", use_container_width=True):
            st.session_state.baseline_locked = True
            st.success("Engine Ready!")

    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        # Εδώ παραμένουν τα κουμπιά πλοήγησης όπως τα είχες...
