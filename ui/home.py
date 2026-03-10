import streamlit as st
from core.sync import lock_baseline

def run_home():
    s = st.session_state

    # --- 1. DATA SYNC (Η καρδιά του προβλήματος) ---
    # Διαβάζουμε πρώτα από τα inputs αν υπάρχουν, αλλιώς από το session state
    p = float(s.get("input_price", 100.0))
    vc = float(s.get("input_vc", 60.0))
    v = int(s.get("input_volume", 1000))
    fc = float(s.get("input_fc", 20000.0))
    ads = float(s.get("annual_debt_service", 0.0))
    cash = float(s.get("opening_cash", 10000.0))

    # --- 2. CALCULATIONS ---
    margin = p - vc
    revenue = p * v
    contribution = margin * v
    bep_units = (fc + ads) / margin if margin > 0 else 0
    margin_of_safety = v - bep_units
    buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0
    ccc = s.get("ar_days", 45) + s.get("inventory_days", 60) - s.get("ap_days", 30)

    # --- HERO SECTION ---
    st.markdown(
        f"""
        <div style="text-align:center; padding: 20px 0 30px 0;">
            <h1 style="font-size:72px; font-weight:900; color:#1E3A8A; margin-bottom:0px; letter-spacing:-1px; line-height:1;">Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:22px; font-weight:400; color:#64748b; letter-spacing:3px; text-transform:uppercase; margin-top:10px; margin-bottom:30px;">🛡️ Strategic Decision Room</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- EXECUTIVE SNAPSHOT ---
    st.subheader("📊 Executive Snapshot")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Εδώ είναι η αλλαγή που ζήτησες: Το delta δείχνει το surplus
    col1.metric(
        label="Simulated Volume", 
        value=f"{v:,.0f} units",
        delta=f"+{margin_of_safety:,.0f} surplus" if margin_of_safety >= 0 else f"{margin_of_safety:,.0f} deficit",
        delta_color="normal" if margin_of_safety >= 0 else "inverse"
    )
    col2.metric("Contribution", f"€{contribution:,.0f}")
    col3.metric("Survival BEP", f"{bep_units:,.0f} units")
    col4.metric("Survival Buffer", f"{buffer_pct:.1f}%", delta="Risk Headroom")
    col5.metric("Cash Position", f"€{cash:,.0f}")

    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.45, 0.55], gap="large")

    with col_input:
        st.subheader("⚙️ Global Parameters")
        
        # Business Baseline
        with st.expander("📊 Business Baseline", expanded=True):
            # Χρησιμοποιούμε το on_change=st.rerun για άμεση ενημέρωση
            s.price = st.number_input("Unit Price (€)", value=p, key="input_price")
            s.variable_cost = st.number_input("Variable Cost (€)", value=vc, key="input_vc")
            s.volume = st.number_input("Annual Volume", value=v, key="input_volume")
            s.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=fc, key="input_fc")

        with st.expander("🔄 Working Capital Cycle", expanded=False):
            s.ar_days = st.number_input("AR Days", value=float(s.get('ar_days', 45.0)))
            s.inventory_days = st.number_input("Inventory Days", value=float(s.get('inventory_days', 60.0)))
            s.ap_days = st.number_input("AP Days", value=float(s.get('ap_days', 30.0)))

        with st.expander("💰 Liquidity & Obligations", expanded=False):
            s.opening_cash = st.number_input("Opening Cash (€)", value=cash)
            s.annual_debt_service = st.number_input("Annual Debt Service (€)", value=ads)

        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        # (Εδώ παραμένουν τα tabs όπως τα είχες, δεν αλλάζει κάτι)
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])
        # ... τα buttons σου ...
