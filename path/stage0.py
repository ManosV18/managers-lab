import streamlit as st
from core.sync import lock_baseline

def run_stage0():
    st.header("🏗️ Stage 0: Baseline Configuration")
    st.caption("Strategic Phase: Establishing the fundamental economic reality of the model.")
    
    # 1. Verification Section
    st.subheader("Current Parameter Preview")
    st.write("Review the values from the sidebar before finalizing the baseline:")
    
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Price:** €{st.session_state.get('price', 0):,.2f}")
    c2.write(f"**Var. Cost:** €{st.session_state.get('variable_cost', 0):,.2f}")
    c3.write(f"**Fixed Costs:** €{st.session_state.get('fixed_cost', 0):,.2f}")

    # 2. Clinical Integrity Check
    price = st.session_state.get('price', 0.0)
    vc = st.session_state.get('variable_cost', 0.0)
    
    if price <= vc:
        st.error("⚠️ **CRITICAL ERROR:** Negative or Zero Contribution Margin. Selling price must exceed variable costs for the model to function.")
    else:
        st.info("💡 **Logic Check:** Contribution margin is positive. The system is ready for break-even and liquidity analysis.")

    

    st.divider()
    
    # 3. Execution Lock
    st.write("Once locked, these parameters will serve as the benchmark for all strategic simulations and stress tests.")
    
    if st.button("🔒 Lock Baseline & Initialize Engine", use_container_width=True):
        if price > vc:
            lock_baseline()  # Sets baseline_locked = True
            st.success("Baseline Locked. Strategic paths decrypted. Transitioning to Stage 1...")
            st.session_state.flow_step = "stage1"
            st.rerun()
        else:
            st.warning("Action Denied: Correct marginal errors in the sidebar first.")
