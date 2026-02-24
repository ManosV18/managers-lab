import streamlit as st
from core.engine import compute_core_metrics

def run_stage1():
    st.header("📉 Stage 1: Break-Even Analysis")
    st.caption("Deep dive into structural viability and cash survival thresholds.")

    # 1. Έλεγχος αν υπάρχουν τα δεδομένα (Χωρίς setdefault)
    if "price" not in st.session_state or st.session_state.price <= 0:
        st.warning("⚠️ Baseline data missing. Please return to Stage 0.")
        if st.button("⬅️ Back to Stage 0"):
            st.session_state.flow_step = 0
            st.rerun()
        return

    # 2. Επικαιροποίηση Σταθερών Εξόδων (αν ο χρήστης θέλει να κάνει fine-tuning εδώ)
    st.subheader("Annual Fixed Costs")
    st.session_state.fixed_cost = st.number_input(
        "Total Annual Fixed Costs (€)",
        min_value=0.0,
        value=float(st.session_state.fixed_cost),
        step=1000.0
    )

    # 3. Υπολογισμοί από τον Engine
    metrics = compute_core_metrics()
    
    current_vol = st.session_state.volume
    op_bep = metrics.get("operating_bep", 0)
    surv_bep = metrics.get("survival_bep", 0)
    
    # 4. Display Metrics - Row 1: Break-Even Points
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Operating Break-Even", f"{op_bep:,.0f} units")
    col2.metric("Survival Break-Even", f"{surv_bep:,.0f} units")
    
    # Margin of Safety βάσει του Survival BEP (το πιο κρίσιμο)
    m_safety_pct = ((current_vol - surv_bep) / current_vol) if current_vol > 0 else 0
    col3.metric("Margin of Safety", f"{m_safety_pct:.1%}", 
               delta=f"{current_vol - surv_bep:,.0f} units safe")

    # 

    # 5. Display Metrics - Row 2: Cash Engine
    st.subheader("💳 Liquidity & Survival")
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Free Cash Flow (FCF)", f"{metrics.get('fcf', 0):,.0f} €")
    c2.metric("Ending Cash Projection", f"{metrics.get('ending_cash', 0):,.0f} €")
    
    # Χειρισμός του infinite horizon
    horizon = metrics.get('cash_survival_horizon', 0)
    horizon_disp = "Infinite (Self-Sustained)" if horizon == float('inf') else f"{horizon:.2f} Years"
    c3.metric("Cash Survival Horizon", horizon_disp)

    # 6. Visual Progress (Πόσο μακριά είμαστε από το BEP)
    st.divider()
    progress = min(1.0, current_vol / surv_bep) if surv_bep > 0 else 0
    st.write(f"**Volume vs Survival Break-Even ({current_vol:,.0f} / {surv_bep:,.0f})**")
    st.progress(progress)
    
    if current_vol < surv_bep:
        st.error(f"⚠️ Current volume is {surv_bep - current_vol:,.0f} units BELOW survival threshold.")
    else:
        st.success(f"✅ Volume is {current_vol - surv_bep:,.0f} units above survival threshold.")

    # 7. Navigation
    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back to Calibration", use_container_width=True):
            st.session_state.flow_step = 0
            st.rerun()
    with nav2:
        if st.button("Proceed to Stage 2 ➡️", type="primary", use_container_width=True):
            st.session_state.flow_step = 2
            st.rerun()
