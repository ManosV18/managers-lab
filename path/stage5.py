import streamlit as st
from core.sync import sync_global_state

def run_stage5():
    st.header("⚖️ Stage 5: Strategic Decision & Recovery")
    
    metrics = sync_global_state()
    st.subheader("💡 Recommendations")

    runway = metrics.get('runway_months',0)
    
    if runway < 6:
        st.warning("⚠️ Cash runway < 6 months. Consider cost reduction or financing.")
    elif runway < 12:
        st.info("Runway is moderate. Monitor working capital and FCF.")
    else:
        st.success("Runway healthy. Sufficient liquidity for planned investments.")

    st.divider()
    st.subheader("📈 Key Metrics Summary")
    st.write(metrics)

