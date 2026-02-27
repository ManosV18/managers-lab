import streamlit as st
from core.sync import sync_global_state

def run_stage2():
    st.header("🏁 Stage 2: Executive Dashboard")
    
    metrics = sync_global_state()
    is_locked = st.session_state.get('baseline_locked', False)

    if not is_locked:
        st.info("💡 Please complete Stage 0 to lock baseline parameters.")
        return

    st.subheader("📊 Key Metrics Overview")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Revenue", f"€{metrics.get('revenue',0):,.0f}")
    c2.metric("EBIT", f"€{metrics.get('ebit',0):,.0f}")
    c3.metric("Free Cash Flow", f"€{metrics.get('fcf',0):,.0f}")
    c4.metric("Break-Even Units", f"{metrics.get('bep_units',0):,.0f}")

    st.divider()
    st.subheader("📌 Liquidity & Runway")
    st.write(f"Net Cash Position: €{metrics.get('net_cash_position',0):,.0f}")
    st.write(f"Cash Runway (Months): {metrics.get('runway_months',0):.1f}")
    st.write(f"Cash Wall: €{metrics.get('cash_wall',0):,.0f}")
