import streamlit as st

def show_unit_cost_app():
    st.header("📊 Industrial Unit Cost Calculator")
    st.info("Analyze the components of your Variable Cost. Use 'Sync' to update the global financial model.")

    # 1. LOAD CURRENT STATE
    if 'variable_cost' not in st.session_state:
        st.session_state.variable_cost = 50.0

    st.subheader("Cost Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠 Direct Costs")
        raw_materials = st.number_input("Raw Materials per unit (€)", min_value=0.0, 
                                        value=float(st.session_state.variable_cost * 0.7),
                                        key="uc_raw_mat")
        labor_cost = st.number_input("Direct Labor per unit (€)", min_value=0.0, 
                                     value=float(st.session_state.variable_cost * 0.2),
                                     key="uc_labor")
        
    with col2:
        st.markdown("### ⚡ Variable Overheads")
        energy_cost = st.number_input("Energy/Utilities per unit (€)", min_value=0.0, 
                                      value=float(st.session_state.variable_cost * 0.05),
                                      key="uc_energy")
        packaging_shipping = st.number_input("Packaging & Shipping (€)", min_value=0.0, 
                                             value=float(st.session_state.variable_cost * 0.05),
                                             key="uc_shipping")

    # 2. CALCULATE TOTAL VC
    total_vc = raw_materials + labor_cost + energy_cost + packaging_shipping
    
    st.divider()
    
    # 3. ANALYSIS & SYNC
    c1, c2 = st.columns([2, 1])
    
    with c1:
        diff = total_vc - st.session_state.get('variable_cost', 0.0)
        st.metric("Calculated Variable Cost", f"{total_vc:.2f} €", 
                  delta=f"{diff:.2f} € vs Global",
                  delta_color="inverse")
    
    with c2:
        # Προσθήκη μοναδικού key="sync_vc_button"
        if st.button("🔄 Sync to Global State", use_container_width=True, key="sync_vc_button"):
            st.session_state.variable_cost = total_vc
            st.success("Global Variable Cost Updated!")
            st.rerun()

    # 4. VISUALIZATION
    st.write("### Cost Structure Analysis")
    cost_data = {
        "Raw Materials": raw_materials,
        "Labor": labor_cost,
        "Energy": energy_cost,
        "Logistics": packaging_shipping
    }
    
    

    if total_vc > 0:
        for label, value in cost_data.items():
            pct = value / total_vc
            st.write(f"**{label}:** {value:.2f}€ ({pct:.1%})")
            st.progress(pct)

    st.divider()
    # Προσθήκη μοναδικού key="back_from_uc"
    if st.button("⬅️ Back to Library Hub", key="back_from_uc"):
        st.session_state.selected_tool = None
        st.rerun()
