import streamlit as st
from core.sync import sync_global_state

def run_stage5():
    st.header("🏁 Stage 5: Strategic Decision & Synthesis")
    m = sync_global_state()
    s = st.session_state
    st.divider()

    fcf = float(m.get('fcf', 0.0))
    bep = float(m.get('bep_units', 0.0))
    runway = float(m.get('runway_months', 0.0))

    st.subheader("Operational Vital Signs")
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Annual FCF", f"€ {fcf:,.0f}")
    c2.metric("Survival BEP", f"{bep:,.0f} Units")
    c3.metric("Runway Status", "Stable (∞)" if (runway >= 100 or runway < 0) else f"{runway:.1f} Mo")

    st.subheader("Strategic Pivot Selection")
    choice = st.radio("Primary Viability Path:", ["Efficiency (Margin Focus)", "Growth (Volume Focus)"])

    if choice == "Efficiency (Margin Focus)":
        st.info("🎯 **Mandate:** Maximize unit contribution to lower the break-even threshold.")
    else:
        st.info("🚀 **Mandate:** Aggressive market share acquisition to outrun fixed obligations.")

    

    st.divider()
    if st.button("🔄 Restart War Room Analysis"):
        st.session_state.clear()
        st.rerun()
