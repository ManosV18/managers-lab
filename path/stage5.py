import streamlit as st
from core.sync import sync_global_state

def run_stage5():
    st.header("🏁 Stage 5: Strategic Synthesis")
    
    m = sync_global_state()
    s = st.session_state
    st.caption("Final analytical conclusion and mandate.")
    st.divider()

    fcf = m.get('fcf', 0.0)
    runway = m.get('runway_months', 0.0)

    # 1. Final Verdict
    if fcf > 0:
        st.success("✅ **VIABLE:** The business model is structurally sound. Focus on expansion.")
    elif runway > 6:
        st.warning("⚠️ **FRAGILE:** Model is in deficit but has runway. Immediate pivot required.")
    else:
        st.error("❌ **CRITICAL:** Immediate liquidation or capital injection required. System is terminal.")

    # 2. Key Metrics Table
    st.table({
        "Metric": ["Annual FCF", "Survival BEP", "Runway (Months)", "Cash Wall"],
        "Value": [f"{fcf:,.0f} €", f"{m.get('survival_bep',0):,.0f} Units", f"{runway:.1f}", f"{m.get('cash_wall',0):,.0f} €"]
    })

    # 3. Reset or Home
    if st.button("🔄 Restart Full Analysis", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.baseline_locked = False
        st.rerun()
