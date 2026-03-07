import streamlit as st
from core.sync import sync_global_state, lock_baseline

def run_home():
    # --- Sync metrics ---
    metrics = sync_global_state() if st.session_state.get("baseline_locked", False) else {}

    # --- HERO SECTION ---
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <h1 style="font-size:48px;">🛡️ Strategic Decision Room</h1>
            <h2 style="font-size:28px; font-weight:600; margin-top:10px;">
                Test your business decisions before you risk real money
            </h2>
            <h3 style="font-size:20px; font-weight:normal; color:#555; margin-top:10px;">
                Enter your baseline numbers and see the impact on profit, break-even, and cash survival
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --- STATUS ---
    if not st.session_state.get("baseline_locked", False):
        st.info("💡 System Ready: Please enter baseline numbers to start.")
    else:
        st.success("✅ Baseline Active: Metrics calculated successfully.")

    st.divider()

    # --- QUICK ACTIONS ---
    st.subheader("1️⃣ Business Setup")
    st.write("Enter your basic numbers to begin analysis:")

    col1, col2 = st.columns(2)

    # BUSINESS SETUP BUTTON
    with col1:
        if st.button("🔧 Business Setup / Input Basic Numbers", use_container_width=True):
            st.session_state.flow_step = "stage0"
            st.rerun()

    # TOOL ACCESS BUTTON
    with col2:
        if st.button("📚 Open Tools Library", use_container_width=True):
            st.session_state.flow_step = "library"
            st.rerun()

    st.divider()

    # --- KPI DASHBOARD ---
    if metrics:
        st.markdown("### KPI Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Projected Revenue", f"€{metrics['revenue']:,.0f}")
        c2.metric("EBIT", f"€{metrics['ebit']:,.0f}")
        c3.metric("Break-Even Units", f"{metrics['bep_units']:,.0f}")
        c4.metric("Free Cash Flow", f"€{metrics['fcf']:,.0f}")
