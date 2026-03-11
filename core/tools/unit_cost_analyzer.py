import streamlit as st

def show_unit_cost_app():
    st.header("📊 Industrial Unit Cost Calculator")
    st.info("Analytical Breakdown: Deconstruct your Variable Cost components to identify efficiency gaps.")

    # 1. LOAD & INITIALIZE STATE
    # Ensuring consistency with global variables
    if 'variable_cost' not in st.session_state:
        st.session_state.variable_cost = 50.0

    st.subheader("1. Variable Cost Decomposition")
    
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠 Direct Production Costs")
        raw_materials = st.number_input("Raw Materials / unit (€)", min_value=0.0, 
                                        value=float(st.session_state.variable_cost * 0.7),
                                        help="Direct cost of ingredients or components.")
        labor_cost = st.number_input("Direct Labor / unit (€)", min_value=0.0, 
                                     value=float(st.session_state.variable_cost * 0.2),
                                     help="Variable labor associated directly with production output.")
        
    with col2:
        st.markdown("### ⚡ Variable Overheads")
        energy_cost = st.number_input("Energy & Utilities / unit (€)", min_value=0.0, 
                                      value=float(st.session_state.variable_cost * 0.05))
        packaging_shipping = st.number_input("Logistics & Packaging (€)", min_value=0.0, 
                                             value=float(st.session_state.variable_cost * 0.05))

    # 2. CALCULATION ENGINE
    total_vc = raw_materials + labor_cost + energy_cost + packaging_shipping
    
    st.divider()
    
    # 3. ANALYSIS & SYSTEM SYNC
    c1, c2 = st.columns([2, 1])
    
    with c1:
        global_vc = st.session_state.get('variable_cost', 0.0)
        diff = total_vc - global_vc
        st.metric("Calculated Variable Cost", f"€ {total_vc:.2f}", 
                  delta=f"{diff:.2f} € vs System Baseline",
                  delta_color="inverse")
    
    with c2:
        # Action button to push local calculation to global session state
        if st.button("🔄 Sync to Global Model", use_container_width=True, key="sync_vc_button"):
            st.session_state.variable_cost = total_vc
            st.success("System-wide Variable Cost updated.")
            st.rerun()

    # 4. STRUCTURE VISUALIZATION
    st.subheader("2. Cost Structure Profile")
    
    
    cost_data = {
        "Raw Materials": raw_materials,
        "Direct Labor": labor_cost,
        "Energy/Utilities": energy_cost,
        "Logistics/Pkg": packaging_shipping
    }

    if total_vc > 0:
        for label, value in cost_data.items():
            pct = value / total_vc
            st.write(f"**{label}:** € {value:.2f} ({pct:.1%})")
            st.progress(pct)
    else:
        st.warning("Input values to visualize cost structure.")

    # 5. NAVIGATION
    st.divider()
    if st.button("⬅️ Back to Library Hub", key="back_from_uc", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
