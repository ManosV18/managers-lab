import streamlit as st

def show_sidebar():
    # Εξασφάλιση αρχικοποίησης flow_step
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:
        # Branding Header
        st.markdown(
            """
            <div style="text-align:center; padding: 10px; border-radius:10px; background-color:#f8fafc; border: 1px solid #e2e8f0; margin-bottom:20px;">
                <h2 style="margin:0; color:#1E3A8A; font-size:24px;">🧠 Managers Lab</h2>
                <p style="font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:1px; margin-top:5px;">
                    Strategic Finance Tools
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Main Navigation
        if st.button("🏠 Control Tower (Home)", use_container_width=True, type="primary" if st.session_state.flow_step == "home" else "secondary"):
            st.session_state.selected_tool = None
            st.session_state.flow_step = "home"
            st.rerun()

        st.divider()

        # --- STRATEGIC TOOL LIBRARY ---
        st.subheader("🛠️ Strategic Tools")
        
        # Μόνο αν είναι κλειδωμένα τα δεδομένα επιτρέπουμε την πλοήγηση στα εργαλεία
        is_locked = st.session_state.get('baseline_locked', False)
        
        if is_locked:
            # Tool 1: Survival Simulator
            if st.button("⚖️ Cash Survival Horizon", use_container_width=True):
                st.session_state.selected_tool = "survival_simulator"
                st.session_state.flow_step = "tool"
                st.rerun()

            # Tool 2: Pricing Radar
            if st.button("📡 Pricing Impact Radar", use_container_width=True):
                st.session_state.selected_tool = "pricing_impact"
                st.session_state.flow_step = "tool"
                st.rerun()

            # Tool 3: CLV Analyzer
            if st.button("💎 Customer Lifetime Value", use_container_width=True):
                st.session_state.selected_tool = "clv_analyzer"
                st.session_state.flow_step = "tool"
                st.rerun()
        else:
            st.info("🔒 Lock Baseline on Home to unlock tools.")

        st.divider()
        
        # System Integrity & Reset
        st.subheader("🛡️ System")
        if is_locked:
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN")

        if st.button("🔄 Global Reset", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.rerun()

        st.caption("v2.0 | [2026-02-18] 365-Day Engine")
