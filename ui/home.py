import streamlit as st
from core.sync import lock_baseline

def run_home():
    s = st.session_state

    # --- HERO SECTION ---
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <div style="font-size:18px; letter-spacing:2px; color:#888;">
                MANAGERS LAB
            </div>

            <h1 style="font-size:48px; margin-top:10px;">
                🛡️ Strategic Decision Room
            </h1>

            <h2 style="font-size:28px; font-weight:600; margin-top:10px;">
                See the real impact on your cash and survival before committing
            </h2>

            <h3 style="font-size:20px; font-weight:normal; color:#555; margin-top:10px;">
                Change prices, costs, or volumes and instantly see the effect on profit,
                break-even, and cash survival.
            </h3>

            <p style="font-size:18px; color:#777; margin-top:15px;">
                Know the outcome before you spend a euro.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- MAIN LAYOUT ---
    col_input, col_nav = st.columns([0.45, 0.55], gap="large")

    # LEFT COLUMN: Global Parameters
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

        # (όλος ο κώδικας των buttons σου μένει ΑΚΡΙΒΩΣ ίδιος)

    # --- FOOTER NAVIGATION ---
    st.divider()
    st.subheader("🏁 Full Sequential Stages")

    cols = st.columns(5)

    for i in range(1, 6):
        if cols[i-1].button(f"Go to Stage {i}", use_container_width=True):
            if s.get('price', 0) > 0:
                s.flow_step = f"stage{i}"
                st.rerun()
            else:
                st.error("Please set Price first.")
