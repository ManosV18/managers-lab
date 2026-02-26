import streamlit as st
from core.sync import sync_global_state

def run_stage1():

    st.header("⚖️ Stage 1: Operating Leverage & Break-Even Analysis")

    m = sync_global_state()

    # ------------------------------------------------
    # If baseline NOT locked → user guidance
    # ------------------------------------------------
    if m is None:
        st.warning("⚠️ Please complete Stage 0 and lock the baseline first.")

        if st.button("⬅️ Return to Stage 0", key="return_stage0"):
            st.session_state.flow_step = "stage0"
            st.rerun()

        st.stop()

    # ------------------------------------------------
    # Safe metric extraction
    # ------------------------------------------------
    volume = float(st.session_state.get("volume", 0))
    bep = float(m.get("bep_units", 0))
    ebit = float(m.get("ebit", 0))
    contribution = float(m.get("contribution_margin", 0))
    fcf = float(m.get("fcf", 0))
    net_cash_position = float(m.get("net_cash_position", 0))

    st.divider()

    # ------------------------------------------------
    # KPIs
    # ------------------------------------------------
    c1, c2, c3 = st.columns(3)

    c1.metric("Survival BEP", f"{bep:,.0f} Units")

    safety_margin = ((volume - bep) / volume) if volume > 0 else 0
    c2.metric("Margin of Safety", f"{safety_margin:.1%}")

    c3.metric("EBIT", f"€ {ebit:,.0f}")

    # ------------------------------------------------
    # DOL
    # ------------------------------------------------
    st.subheader("Operating Leverage")

    if ebit > 0:
        dol = contribution / ebit
        st.write(f"Degree of Operating Leverage: **{dol:.2f}**")
    else:
        st.warning("DOL cannot be calculated (EBIT ≤ 0).")

    # ------------------------------------------------
    # Cash Runway (Division by zero safe)
    # ------------------------------------------------
    st.subheader("Cash Survival Logic")

    if net_cash_position < 0:
        st.error("Company already in negative cash position. Immediate restructuring required.")
    elif fcf <= 0:
        st.warning("No positive Free Cash Flow. Cash runway cannot be computed.")
    else:
        runway_years = net_cash_position / fcf
        st.write(f"Estimated Cash Survival Horizon: **{runway_years:.2f} years**")
