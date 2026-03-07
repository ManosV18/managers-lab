import streamlit as st
from core.sync import sync_global_state, lock_baseline

def run_home():
    # --- Sync metrics ---
    metrics = sync_global_state()
    is_locked = st.session_state.get("baseline_locked", False)

    # --- HERO SECTION ---
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <h1 style="font-size:48px;">🛡️ Strategic Decision Room</h1>
            <h2 style="font-size:28px; font-weight:600; margin-top:10px;">
                Test your business decisions before you risk real money
            </h2>
            <h3 style="font-size:20px; font-weight:normal; color:#555; margin-top:10px;">
                Change prices, costs or investments and instantly see the impact on
                profit, break-even and cash survival.
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- STATUS ---
    if not is_locked:
        st.info("💡 System Ready: Please lock your baseline parameters to activate the dashboard.")
    else:
        st.success("✅ Baseline Active: Metrics calculated successfully.")

    st.divider()

    # --- KPI DASHBOARD ---
    c1, c2, c3, c4 = st.columns(4)

    rev_val = metrics.get("revenue") if is_locked else None
    ebit_val = metrics.get("ebit") if is_locked else None
    bep_val = metrics.get("bep_units") if is_locked else None
    fcf_val = metrics.get("fcf") if is_locked else None

    def colorize(value, low, high, suffix=""):
        if value is None:
            return "—"
        if value < low:
            return f"🔴 {value:,.0f}{suffix}"
        elif value < high:
            return f"🟠 {value:,.0f}{suffix}"
        else:
            return f"🟢 {value:,.0f}{suffix}"

    c1.metric("Projected Revenue", colorize(rev_val, 20000, 50000, " €"))
    c2.metric("EBIT", colorize(ebit_val, 5000, 20000, " €"))
    c3.metric("Break-Even Units", colorize(bep_val, 50, 200))
    c4.metric("Free Cash Flow", colorize(fcf_val, 5000, 15000, " €"))

    st.divider()

    # --- ACTIONS: Business Setup + Tools ---
    st.subheader("⚙️ Business Setup & Tools")

    col1, col2 = st.columns([1,2])

    # --- BUSINESS SETUP ---
    with col1:
        st.markdown("### 🏗️ Business Setup")
        if st.button("Input Basic Numbers / Lock Baseline", use_container_width=True):
            lock_baseline()
            st.session_state.flow_step = "stage1"
            st.rerun()

    # --- TOOL SELECTION ---
    with col2:
        st.markdown("### 🛠️ Tools (Available)")
        # Δείχνουμε μόνο τα 10 λειτουργικά εργαλεία
        tools = [
            ("Break-Even Calculator", "break_even", "show_break_even_tool"),
            ("Cash Conversion Cycle (CCC)", "cash_cycle", "run_cash_cycle_app"),
            ("Receivables Analyzer", "receivables_analyzer", "show_receivables_analyzer_ui"),
            ("Inventory Optimizer (EOQ)", "inventory_manager", "show_inventory_manager"),
            ("Payables Manager", "INTERNAL", "show_payables_manager_internal"),
            ("Unit Cost Analyzer", "unit_cost_analyzer", "show_unit_cost_app"),
            ("Executive Dashboard", "executive_dashboard", "show_executive_dashboard"),
            ("Cash Fragility Index", "cash_fragility_index", "show_cash_fragility_index"),
            ("Stress Test Simulator", "stress_test_simulator", "show_stress_test_tool"),
            ("Loan vs Leasing Analyzer", "loan_vs_leasing", "loan_vs_leasing_ui")
        ]

        for t_name, mod_name, func_name in tools:
            if st.button(t_name, key=f"home_tool_{t_name}", use_container_width=True):
                st.session_state.selected_tool = (mod_name, func_name)
                st.session_state.flow_step = "library"
                st.rerun()
