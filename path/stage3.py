import streamlit as st
from core.sync import sync_global_state

def run_stage3():
    st.header("💧 Cash Flow Engine")
    
    # 1. FETCH DATA (Safe Retrieval)
    m = sync_global_state()
    
    # Έλεγχος αν το m είναι κενό (ασφάλεια από το 1ο αρχείο)
    if not m:
        st.warning("⚠️ Please lock the baseline in Stage 0 to view liquidity metrics.")
        if st.button("Go to Stage 0"):
            st.session_state.flow_step = "stage0"
            st.rerun()
        return

    s = st.session_state
    st.caption("Analytical focus: Cash Conversion Cycle and structural liquidity stability.")
    st.divider()

    # 2. METRICS ALIGNMENT (Safe casting with defaults)
    wc_req = float(m.get('wc_requirement', 0.0))
    cash_pos = float(m.get('net_cash_position', 0.0))
    ccc = int(m.get('ccc', 0))
    runway = float(m.get('runway_months', 0.0))

    # 3. INTERFACE: KPI COLUMNS
    c1, c2, c3 = st.columns(3)
    
    # Cash Conversion Cycle
    c1.metric("Cash Conversion Cycle", f"{ccc} Days", 
              help="The time it takes to convert investments in inventory and other resources into cash flows from sales.")
    
    # Working Capital Requirement
    c2.metric("WC Requirement", f"€ {wc_req:,.0f}", 
              delta=f"{wc_req:,.0f}", delta_color="inverse",
              help="Net capital tied up in day-to-day operations.")
    
    # Liquidity Position
    c3.metric("Net Cash Position", f"€ {cash_pos:,.0f}",
              help="Opening cash minus working capital requirements.")

    st.divider()

    # 4. ANALYSIS: SURVIVAL RUNWAY
    st.subheader("Survival Runway")
    
    if runway >= 100:
        st.success("✅ **STABLE:** Positive Free Cash Flow detected. Runway is effectively infinite.")
    elif runway <= 0:
        st.error("🚨 **CRITICAL:** Immediate cash depletion or negative net cash position.")
    else:
        st.warning(f"⚠️ **LIQUIDITY BURN:** System exhaustion in {runway:.1f} months.")
        # Progress bar normalized to 12 months for visualization
        progress_val = min(max(runway / 12, 0.0), 1.0)
        st.progress(progress_val)

    # 5. DETAILED BREAKDOWN (Επιπλέον πληροφορία από το 1ο αρχείο)
    with st.expander("🔍 View Component Breakdown", expanded=False):
        col_a, col_b = st.columns(2)
        col_a.write(f"**Accounts Receivable:** €{m.get('accounts_receivable', 0):,.0f}")
        col_a.write(f"**Operating Days Base:** 365 Days")
        
        # Υπολογισμός AP σε Ευρώ (αν υπάρχει στην engine)
        ap_val = m.get('accounts_payable', 0) # Αν το επιστρέφει η engine
        col_b.write(f"**AP Management:** {m.get('ap_days', 0)} days")

    # 6. NAVIGATION
    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back to Stage 2", use_container_width=True): 
        st.session_state.flow_step = "stage2"
        st.rerun()
    if col2.button("Proceed to Stage 4 ➡️", use_container_width=True): 
        st.session_state.flow_step = "stage4"
        st.rerun()
