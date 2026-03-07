import streamlit as st
from core.sync import lock_baseline

def run_home():
    st.title("🛡️ Strategic Decision Room")
    st.subheader("Global Parameters Setup")
    st.write("Fill in the basic numbers to initialize the system.")

    # Χωρίζουμε την κεντρική οθόνη
    col_input, col_nav = st.columns([2, 1])

    with col_input:
        # --- Group 1: Core Business ---
        with st.container(border=True):
            st.markdown("### ⚙️ Operational Inputs")
            c1, c2 = st.columns(2)
            st.session_state.price = c1.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
            st.session_state.variable_cost = c2.number_input("Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0)))
            st.session_state.volume = c1.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))
            st.session_state.fixed_cost = c2.number_input("Annual Fixed Costs", value=float(st.session_state.get('fixed_cost', 20000.0)))

        # --- Group 2: Financials & Days ---
        with st.container(border=True):
            st.markdown("### ⏳ Working Capital & Debt")
            c1, c2, c3 = st.columns(3)
            st.session_state.ar_days = c1.number_input("AR Days", value=float(st.session_state.get('ar_days', 45.0)))
            st.session_state.inventory_days = c2.number_input("Inv. Days", value=float(st.session_state.get('inventory_days', 60.0)))
            st.session_state.ap_days = c3.number_input("AP Days", value=float(st.session_state.get('ap_days', 30.0)))
            
            st.session_state.annual_debt_service = c1.number_input("Debt Service (€)", value=float(st.session_state.get('annual_debt_service', 0.0)))
            st.session_state.opening_cash = c2.number_input("Opening Cash (€)", value=float(st.session_state.get('opening_cash', 10000.0)))
            
            wacc_val = c3.number_input("WACC (%)", value=float(st.session_state.get('wacc', 0.15)) * 100)
            st.session_state.wacc = wacc_val / 100

        if st.button("🔒 Lock & Sync System", type="primary", use_container_width=True):
            lock_baseline()
            st.success("System Synchronized!")

    with col_nav:
        with st.container(border=True):
            st.markdown("### 🚀 Quick Actions")
            # Dropdown για τα στάδια
            stages = {
                "Stage 1: Survival": "stage1",
                "Stage 2: Dashboard": "stage2",
                "Stage 3: Liquidity": "stage3",
                "Stage 4: Stress Test": "stage4",
                "Stage 5: Decision": "stage5"
            }
            target = st.selectbox("Jump to Analysis:", list(stages.keys()))
            if st.button("Go to Selection"):
                st.session_state.flow_step = stages[target]
                st.rerun()
            
            st.divider()
            st.info("Ensure all numbers on the left are filled. If a value is missing, the system will prompt you in the specific stage.")
