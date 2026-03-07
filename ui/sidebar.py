import streamlit as st
from core.sync import lock_baseline

def show_sidebar():
    # --- DEFAULTS ---
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:
        st.title("💧 Cash Survival OS")

        # --- BASELINE LOCK STATUS ---
        st.subheader("🛡️ System Integrity")
        if st.session_state.get("baseline_locked", False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN (Setup Phase)")

        st.divider()

        # --- GLOBAL PARAMETERS ---
        st.subheader("⚙️ Global Parameters")
        st.session_state.price = st.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
        st.session_state.variable_cost = st.number_input("Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0)))
        st.session_state.volume = st.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))
        st.session_state.fixed_cost = st.number_input("Annual Fixed Costs (€)", value=float(st.session_state.get('fixed_cost', 20000.0)))

        st.divider()

        # --- ALL TOOLS LISTED ---
        st.subheader("📚 Tools Library")
        tools = [
            "Break-Even Calculator",
            "CLV Simulator",
            "Cash Conversion Cycle (CCC)",
            "Receivables Analyzer",
            "Inventory Optimizer (EOQ)",
            "Payables Manager",
            "Unit Cost Analyzer",
            "Executive Dashboard",
            "Cash Fragility Index",
            "Stress Test Simulator"
        ]

        for t in tools:
            if st.button(t, key=f"tool_{t}"):
                st.session_state.selected_tool = t
                st.session_state.flow_step = "library"
                st.rerun()

        st.divider()

        # --- ACTIONS ---
        if not st.session_state.get("baseline_locked", False):
            if st.button("🔒 Lock Baseline", use_container_width=True):
                lock_baseline()
                st.session_state.flow_step = "stage1"
                st.rerun()

        if st.button("🔄 Reset All Data", use_container_width=True):
            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.rerun()
