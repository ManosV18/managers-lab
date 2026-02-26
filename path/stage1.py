import streamlit as st
from core.engine import calculate_metrics

# --------------------------------
# Safe sync function (auto lock baseline)
# --------------------------------
def safe_sync_global_state():
    """
    Returns metrics from sidebar inputs.
    If baseline not locked, lock it automatically.
    """
    s = st.session_state
    if not s.get('baseline_locked', False):
        try:
            s.baseline = calculate_metrics(
                float(s.get('price', 100.0)),
                int(s.get('volume', 1000)),
                float(s.get('variable_cost', 50.0)),
                float(s.get('fixed_cost', 20000.0)),
                float(s.get('wacc', 0.15)),
                float(s.get('tax_rate', 0.22)),
                float(s.get('ar_days', 45.0)),
                float(s.get('inventory_days', 60.0)),
                float(s.get('ap_days', 30.0)),
                float(s.get('annual_debt_service', 0.0)),
                float(s.get('opening_cash', 10000.0))
            )
            s.baseline_locked = True
        except Exception as e:
            st.error(f"Engine Error: {e}")
            return {}
    return s.baseline

# --------------------------------
# Stage 1
# --------------------------------
def run_stage1():
    st.header("⚖️ Stage 1: Operating Leverage & Break-Even Analysis")

    # -------------------------------
    # 1. Fetch metrics safely
    # -------------------------------
    m = safe_sync_global_state()
    s = st.session_state

    if not m:
        st.error("Engine returned no metrics. Check sidebar inputs.")
        st.stop()

    # Debug info (can remove in production)
    st.write("DEBUG: Engine metrics", m)

    st.caption("Analyzing the structural sensitivity of EBIT relative to volume fluctuations.")
    st.divider()

    # -------------------------------
    # 2. KPIs
    # -------------------------------
    c1, c2, c3 = st.columns(3)
    
    bep = float(m.get('bep_units', 0.0))
    ebit = float(m.get('ebit', 0.0))
    vol = float(s.get('volume', 0.0))

    c1.metric("Survival BEP", f"{bep:,.0f} Units", help="Volume required to cover all fixed costs and debt.")

    safety_margin = ((vol - bep) / vol) if vol > 0 else 0
    c2.metric("Margin of Safety", f"{safety_margin:.1%}",
              delta="Secure" if safety_margin > 0.2 else "Risk",
              delta_color="normal" if safety_margin > 0.2 else "inverse")

    c3.metric("Annual EBIT", f"€ {ebit:,.0f}")

    # -------------------------------
    # 3. Visual Break-Even Gauge
    # -------------------------------
    st.subheader("📊 Break-Even Status")
    if vol > 0 and bep > 0:
        progress_value = min(max(vol / bep, 0.0), 2.0)
        st.progress(progress_value if progress_value <= 1 else 1)
        if vol < bep:
            st.warning(f"⚠️ Current volume ({vol:,.0f}) is below BEP ({bep:,.0f})! High risk.")
        else:
            st.success(f"✅ Current volume ({vol:,.0f}) is above BEP ({bep:,.0f}).")
    else:
        st.info("Cannot display visual BEP: Volume or BEP data missing or zero.")

    # -------------------------------
    # 4. Leverage Metrics (DOL)
    # -------------------------------
    st.subheader("Leverage Metrics")
    total_contribution = float(m.get('contribution_margin', 0.0))
    dol = (total_contribution / ebit) if ebit > 0 else 0
    st.write(f"**Degree of Operating Leverage (DOL):** {dol:.2f}")

    if dol > 3.0:
        st.warning(f"🚨 High leverage! A 1% change in sales → {dol:.2f}% change in EBIT. Extreme caution!")
    elif dol > 0:
        st.info(f"Moderate leverage: 1% change in sales → {dol:.2f}% change in EBIT.")
    else:
        st.error("DOL cannot be calculated with zero or negative EBIT.")

    # -------------------------------
    # 5. Capital Allocation
    # -------------------------------
    st.subheader("💰 Capital Allocation Potential")
    fcf = float(m.get('fcf', 0.0))
    st.write(f"Current Free Cash Flow (after tax and debt): **€ {fcf:,.2f}**")
    st.caption("Recommended allocation: 70% reinvestment, 30% debt repayment or distribution.")

    # -------------------------------
    # 6. Navigation with unique keys
    # -------------------------------
    st.divider()
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Back to Stage 0", key="nav_back_stage1"):
            st.session_state.flow_step = "stage0"
            st.rerun()
    with col_next:
        if st.button("Proceed to Stage 2 ➡️", key="nav_next_stage3"):
            st.session_state.flow_step = "stage2"
            st.rerun()
