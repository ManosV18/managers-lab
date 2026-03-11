import streamlit as st

def run_home():
    s = st.session_state
    m = s.get("metrics", {})
    
    # Snapshot Data
    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    net_cash = m.get("net_cash_position", s.get("opening_cash", 10000.0))
    margin = p - vc

    # Title Section
    st.markdown("<h1 style='text-align:center;'>Managers Lab.</h1>", unsafe_allow_html=True)
    st.divider()

    # Layout
    col_input, col_nav = st.columns([0.42, 0.58], gap="large")

    with col_input:
        st.subheader("⚙️ Global Parameters")
        with st.expander("📊 Business Baseline", expanded=True):
            st.number_input("Unit Price (€)", value=float(p), key="price")
            st.number_input("Variable Cost (€)", value=float(vc), key="variable_cost")
            st.number_input("Annual Volume", value=int(v), key="volume")
        
        # Άλλα inputs...
        
        if st.button("🔒 Lock Baseline", type="primary", use_container_width=True):
            st.session_state.baseline_locked = True
            st.rerun()

    with col_nav:
        st.subheader("📊 Strategic Tool Library")
        
        if not s.get("baseline_locked"):
            st.info("🔒 Lock your baseline to enable strategic tools.")
        else:
            # ΕΔΩ ΕΙΝΑΙ Ο LAUNCHER
            st.success("Baseline Synchronized. Select a module:")
            
            # Παράδειγμα Tool Button
            if st.button("⚖️ Launch Cash Survival Horizon", use_container_width=True):
                st.session_state.selected_tool = "survival_simulator"
                st.session_state.flow_step = "tool"
                st.rerun()
                
            if st.button("📡 Launch Pricing Impact Radar", use_container_width=True):
                st.session_state.selected_tool = "pricing_impact"
                st.session_state.flow_step = "tool"
                st.rerun()
