import streamlit as st
import pandas as pd
import plotly.express as px

def show_unit_cost_app():
    st.header("📊 Industrial Unit Cost Calculator")
    st.info("Analytical Breakdown: Deconstruct your Variable Cost components to identify efficiency gaps.")

    s = st.session_state
    
    # 1. LOAD & INITIALIZE STATE
    # Χρησιμοποιούμε το global variable_cost από το Home
    current_global_vc = float(s.get('variable_cost', 90.0))

    st.subheader("1. Variable Cost Decomposition")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠 Direct Production Costs")
        # Χρησιμοποιούμε δυναμικά ποσοστά επί του υπάρχοντος κόστους
        raw_materials = st.number_input("Raw Materials / unit ($)", min_value=0.0, 
                                        value=current_global_vc * 0.7)
        labor_cost = st.number_input("Direct Labor / unit ($)", min_value=0.0, 
                                     value=current_global_vc * 0.2)
        
    with col2:
        st.markdown("### ⚡ Variable Overheads")
        energy_cost = st.number_input("Energy & Utilities / unit ($)", min_value=0.0, 
                                      value=current_global_vc * 0.05)
        logistics = st.number_input("Logistics & Packaging ($)", min_value=0.0, 
                                    value=current_global_vc * 0.05)

    # 2. CALCULATION ENGINE
    total_vc = raw_materials + labor_cost + energy_cost + logistics
    
    st.divider()
    
    # 3. ANALYSIS & SYSTEM SYNC
    c1, c2 = st.columns([2, 1])
    
    with c1:
        diff = total_vc - current_global_vc
        color = "inverse" if diff > 0 else "normal" # Κόκκινο αν αυξήθηκε το κόστος
        st.metric("Calculated Variable Cost", f"$ {total_vc:.2f}", 
                  delta=f"{diff:.2f} $ vs System Baseline",
                  delta_color=color)
    
    with c2:
        if st.button("🔄 Sync to Global Model", use_container_width=True):
            s.variable_cost = total_vc
            st.success("System-wide Variable Cost updated.")
            st.rerun()

    # 4. VISUALIZATION (Professional Chart)
    st.subheader("2. Cost Structure Profile")
    
    cost_df = pd.DataFrame({
        "Component": ["Raw Materials", "Direct Labor", "Energy", "Logistics"],
        "Value": [raw_materials, labor_cost, energy_cost, logistics]
    })
    
    

    fig = px.pie(cost_df, values='Value', names='Component', 
                 hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
    st.plotly_chart(fig, use_container_width=True)

    # 5. NAVIGATION
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        s.flow_step = "home"
        s.selected_tool = None
        st.rerun()
