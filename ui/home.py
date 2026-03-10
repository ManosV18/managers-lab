import streamlit as st
from core.sync import lock_baseline

def run_home():
    s = st.session_state

    # --- HERO SECTION ---
    st.markdown(
        f"""
        <div style="text-align:center; padding: 20px 0 30px 0;">
            <h1 style="font-size:72px; font-weight:900; color:#1E3A8A; margin-bottom:0px; letter-spacing:-1px; line-height:1;">Managers Lab<span style="color:#ef4444;">.</span></h1>
            <div style="font-size:22px; font-weight:400; color:#64748b; letter-spacing:3px; text-transform:uppercase; margin-top:10px; margin-bottom:30px;">🛡️ Strategic Decision Room</div>
            <div style="max-width:850px; margin: 0 auto; border-top: 2px solid #f1f5f9; padding-top: 25px;">
                <h2 style="font-size:28px; font-weight:600; color:#1e293b; line-height:1.2; margin-bottom:10px;">Test your business decisions before you risk real money.</h2>
                <p style="font-size:19px; color:#475569; line-height:1.5;">Change prices, costs, or volumes and instantly see the effect on profit, break-even, and cash survival.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- EXECUTIVE SNAPSHOT ---
    st.subheader("📊 Executive Snapshot")

    price = s.get("price", 100.0)
    variable_cost = s.get("variable_cost", 60.0)
    volume = s.get("volume", 1000)
    fixed_cost = s.get("fixed_cost", 20000.0)
    cash = s.get("opening_cash", 10000.0)

    margin = price - variable_cost
    revenue = price * volume
    contribution = margin * volume

    bep_units = fixed_cost / margin if margin != 0 else 0

    ar = s.get("ar_days", 45)
    inv = s.get("inventory_days", 60)
    ap = s.get("ap_days", 30)

    ccc = ar + inv - ap

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Revenue", f"€{revenue:,.0f}")
    col2.metric("Contribution", f"€{contribution:,.0f}")
    col3.metric("Break-Even Units", f"{bep_units:,.0f}")
    col4.metric("Cash", f"€{cash:,.0f}")
    col5.metric("CCC", f"{ccc:.0f} days")

    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.45, 0.55], gap="large")

    # LEFT COLUMN
    with col_input:
        st.subheader("⚙️ Global Parameters")

        if s.get('baseline_locked', False):
            st.success("✅ Baseline is currently LOCKED")
        else:
            st.warning("🔓 Baseline is OPEN (Adjust values below)")

        with st.expander("Business Baseline", expanded=True):
            s.price = st.number_input("Unit Price (€)", value=float(s.get('price', 100.0)))
            s.variable_cost = st.number_input("Variable Cost (€)", value=float(s.get('variable_cost', 60.0)))
            s.volume = st.number_input("Annual Volume", value=int(s.get('volume', 1000)))
            s.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=float(s.get('fixed_cost', 20000.0)))

        with st.expander("Financials & Working Capital"):
            s.opening_cash = st.number_input("Opening Cash (€)", value=float(s.get('opening_cash', 10000.0)))
            s.annual_debt_service = st.number_input("Annual Debt Service (€)", value=float(s.get('annual_debt_service', 0.0)))
            s.ar_days = st.number_input("AR Days (Collection)", value=float(s.get('ar_days', 45.0)))
            s.inventory_days = st.number_input("Inventory Days", value=float(s.get('inventory_days', 60.0)))
            s.ap_days = st.number_input("AP Days (Payment)", value=float(s.get('ap_days', 30.0)))

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("🔒 Lock Baseline", use_container_width=True, type="primary"):
                lock_baseline()
                st.rerun()

        with col_btn2:
            if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
                st.session_state.clear()
                st.session_state.flow_step = "home"
                st.rerun()

    # RIGHT COLUMN
    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        t1, t2, t3, t4 = st.tabs(["🚀 Strategy", "💰 Finance", "⚙️ Ops", "🛡️ Risk"])
