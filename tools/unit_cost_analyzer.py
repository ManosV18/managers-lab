import streamlit as st
from core.sync import sync_global_state

def show_unit_cost_app():
    st.header("📊 Industrial Unit Cost Calculator")
    st.info("Deconstruct Variable Costs into operational components. Use 'Sync' to push changes to the Global Financial Engine.")

    # 1. LOAD & SYNC GLOBAL STATE
    # Ensuring we have the latest global variable cost
    metrics = sync_global_state()
    s = st.session_state
    
    current_global_vc = float(s.get('variable_cost', 50.0))

    st.subheader("Operational Cost Breakdown")
    st.caption(f"Current Global Baseline Variable Cost: **{current_global_vc:.2f} €**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠 Direct Costs")
        # Defaulting values to represent a standard industrial split (70/20/5/5)
        raw_materials = st.number_input("Raw Materials per unit (€)", min_value=0.0, 
                                        value=float(current_global_vc * 0.7),
                                        key="uc_raw_mat")
        labor_cost = st.number_input("Direct Labor per unit (€)", min_value=0.0, 
                                     value=float(current_global_vc * 0.2),
                                     key="uc_labor")
        
    with col2:
        st.markdown("### ⚡ Variable Overheads")
        energy_cost = st.number_input("Energy/Utilities per unit (€)", min_value=0.0, 
                                      value=float(current_global_vc * 0.05),
                                      key="uc_energy")
        packaging_shipping = st.number_input("Packaging & Shipping (€)", min_value=0.0, 
                                             value=float(current_global_vc * 0.05),
                                             key="uc_shipping")

    # 2. CALCULATION ENGINE
    total_vc = raw_materials + labor_cost + energy_cost + packaging_shipping
    
    st.divider()
    
    # 3. ANALYSIS & SYNC BLOCK
    c1, c2 = st.columns([2, 1])
    
    with c1:
        diff = total_vc - current_global_vc
        st.metric("New Calculated Variable Cost", f"{total_vc:.2f} €", 
                  delta=f"{diff:.2f} € vs Baseline",
                  delta_color="inverse") # Red if cost increases
    
    with c2:
        if st.button("🔄 Sync to Global Engine", use_container_width=True, key="sync_vc_button", type="primary"):
            # Update the core session state
            st.session_state.variable_cost = total_vc
            # Force re-sync to update metrics like Contribution Margin and Break-even
            sync_global_state()
            st.success("Global Financial Engine Updated!")
            st.rerun()

    # 4. VISUAL STRUCTURE ANALYSIS
    
    st.write("### Cost Structure Analysis")
    cost_data = {
        "Raw Materials": raw_materials,
        "Direct Labor": labor_cost,
        "Energy & Utilities": energy_cost,
        "Logistics & Packaging": packaging_shipping
    }
    
    if total_vc > 0:
        for label, value in cost_data.items():
            pct = value / total_vc
            st.write(f"**{label}:** {value:.2f}€ ({pct:.1%})")
            st.progress(pct)

    st.divider()
    if st.button("⬅️ Back to Library Hub", key="back_from_uc"):
        st.session_state.selected_tool = None
        st.rerun()
