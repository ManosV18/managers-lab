import streamlit as st
from core.sync import sync_global_state

def run_stage3():
    st.header("💧 Stage 3: Liquidity & Working Capital Physics")
    m = sync_global_state()
    s = st.session_state
    st.caption("Analytical focus: Cash Conversion Cycle and structural liquidity stability.")
    st.divider()

    # Metrics Alignment
    wc_req = float(m.get('wc_requirement', 0.0))
    cash_pos = float(m.get('net_cash_position', 0.0))
    ccc = int(m.get('ccc', 0))

    c1, c2, c3 = st.columns(3)
    c1.metric("Cash Conversion Cycle", f"{ccc} Days")
    c2.metric("WC Requirement", f"€ {wc_req:,.0f}", delta=f"{wc_req:,.0f}", delta_color="inverse")
    c3.metric("Net Cash Position", f"€ {cash_pos:,.0f}")

    

    st.subheader("Survival Runway")
    runway = float(m.get('runway_months', 0.0))
    if runway >= 100 or runway < 0:
        st.success("✅ **STABLE:** Positive FCF detected. Runway is effectively infinite.")
    else:
        st.warning(f"⚠️ **LIQUIDITY BURN:** System exhaustion in {runway:.1f} months.")
        st.progress(min(runway/12, 1.0))

    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back to Stage 2"): st.session_state.flow_step = "stage2"; st.rerun()
    if col2.button("Proceed to Stage 4 ➡️"): st.session_state.flow_step = "stage4"; st.rerun()


