import streamlit as st
from core.sync import lock_baseline

def run_stage0():
    st.header("🏗️ Stage 0: Baseline Configuration")
    st.caption("Strategic Phase: Defining the economic foundation and cost structure.")
    st.divider()

    # 1. ANALYSIS SELECTION
    input_method = st.radio(
        "How would you like to define your unit costs?", 
        ["Quick Entry (Sidebar)", "🧪 Advanced Unit Cost Analyzer"],
        horizontal=True
    )

    if input_method == "🧪 Advanced Unit Cost Analyzer":
        st.subheader("Unit Cost Breakdown")
        st.write("Decompose your variable costs to ensure no hidden expenses are missed.")
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            
            # Sub-components of Variable Cost
            raw_mat = col1.number_input("Raw Materials / COGS (€/unit)", min_value=0.0, value=float(st.session_state.get('raw_mat', 30.0)))
            labor = col2.number_input("Direct Labor / Outsourcing (€/unit)", min_value=0.0, value=float(st.session_state.get('labor', 15.0)))
            shipping = col1.number_input("Logistics & Packaging (€/unit)", min_value=0.0, value=float(st.session_state.get('shipping', 5.0)))
            commissions = col2.number_input("Sales Commissions / Fees (€/unit)", min_value=0.0, value=float(st.session_state.get('commissions', 0.0)))

            # Save sub-components for persistence
            st.session_state.raw_mat = raw_mat
            st.session_state.labor = labor
            st.session_state.shipping = shipping
            st.session_state.commissions = commissions

            # Total Calculation
            calculated_vc = raw_mat + labor + shipping + commissions
            
            # Sync with Main Variable Cost
            st.session_state.variable_cost = calculated_vc
            
            st.success(f"### Total Variable Cost: €{calculated_vc:,.2f}")
            st.caption("This value has been automatically synced to the Global Parameters.")

    else:
        st.info("ℹ️ Using values currently defined in the Sidebar. Adjust them there or switch to the Analyzer for more precision.")

    st.divider()

    # 2. FINAL VERIFICATION BEFORE LOCK
    st.subheader("Baseline Verification")
    v1, v2, v3 = st.columns(3)
    
    price = float(st.session_state.get('price', 0.0))
    vc = float(st.session_state.get('variable_cost', 0.0))
    vol = int(st.session_state.get('volume', 0))

    v1.metric("Unit Price", f"€{price:,.2f}")
    v2.metric("Variable Cost", f"€{vc:,.2f}")
    v3.metric("Annual Volume", f"{vol:,}")

    # 3. LOCKING MECHANISM
    if price <= vc:
        st.error("⚠️ **Action Required:** Your Variable Cost is higher than or equal to your Price. This results in a negative margin. Please adjust before locking.")
    else:
        if st.button("🔒 Lock Baseline & Start Analysis", use_container_width=True):
            lock_baseline()
            st.session_state.flow_step = "stage1"
            st.rerun()
