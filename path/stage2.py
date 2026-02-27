import streamlit as st
from core.sync import sync_global_state

def run_stage2():
    st.header("🏁 Stage 2: Executive Dashboard")
    
    # 1. FETCH DATA
    m = sync_global_state()
    is_locked = st.session_state.get('baseline_locked', False)

    if not is_locked:
        st.info("💡 **System Pending:** Please complete Stage 0 to lock baseline parameters.")
        if st.button("Go to Stage 0"):
            st.session_state.flow_step = "stage0"
            st.rerun()
        return

    st.caption("Strategic overview of profitability, efficiency, and survival threshold.")
    st.divider()

    # 2. TOP TIER KPIs (Revenue & Profits)
    st.subheader("📊 Core Performance")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Projected Revenue", f"€{m.get('revenue', 0):,.0f}")
    
    ebit = m.get('ebit', 0)
    c2.metric("EBIT", f"€{ebit:,.0f}", delta=f"{(ebit/m.get('revenue',1)):.1%}" if m.get('revenue',0) > 0 else None)
    
    c3.metric("Free Cash Flow", f"€{m.get('fcf', 0):,.0f}")
    c4.metric("Break-Even Units", f"{m.get('bep_units', 0):,.0f}")

    st.divider()

    # 3. LIQUIDITY & SURVIVAL (Visual Focus)
    st.subheader("📌 Liquidity & Runway Status")
    
    col_a, col_b, col_c = st.columns(3)
    
    cash_pos = m.get('net_cash_position', 0)
    runway = m.get('runway_months', 0)
    cash_wall = m.get('cash_wall', 0)

    col_a.metric("Net Cash Position", f"€{cash_pos:,.0f}", help="Opening cash adjusted for WC requirements.")
    
    # Runway Logic with Color
    if runway >= 100:
        col_b.metric("Cash Runway", "Infinite", delta="Positive FCF", delta_color="normal")
    else:
        col_b.metric("Cash Runway", f"{runway:.1f} Months", delta="Limited", delta_color="inverse")

    col_c.metric("Cash Wall (Fixed + Debt)", f"€{cash_wall:,.0f}", help="The total fixed obligations that must be met annually.")

    # 4. ANALYSIS PROGRESS BAR (Όπως στο Stage 3)
    if runway < 100:
        st.write(f"**System Exhaustion Risk:**")
        progress_val = min(max(runway / 12, 0.0), 1.0)
        st.progress(progress_val)
        if runway < 6:
            st.warning("⚠️ Critical liquidity window detected (< 6 months).")

    # 5. NAVIGATION CONTROLS (The Missing Link)
    st.divider()
    col_prev, col_next = st.columns(2)
    
    with col_prev:
        if st.button("⬅️ Back to Stage 1", use_container_width=True):
            st.session_state.flow_step = "stage1"
            st.rerun()
            
    with col_next:
        if st.button("Proceed to Stage 3 ➡️", use_container_width=True, type="primary"):
            st.session_state.flow_step = "stage3"
            st.rerun()
