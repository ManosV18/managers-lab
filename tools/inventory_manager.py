import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_inventory_manager():
    st.header("📦 Inventory Strategic Control")
    st.info("Analyze inventory efficiency and the financial cost of trapped capital.")

    # 1. FETCH GLOBAL METRICS
    metrics = compute_core_metrics()
    wacc = metrics['wacc']
    annual_revenue = metrics['revenue']
    
    # Get COGS safely
    v = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    annual_cogs = v * vc

    # 2. SECTIONS: ANALYSIS & OPTIMIZATION
    tab1, tab2 = st.tabs(["📊 Turnover & Efficiency", "💰 Carrying Cost Analysis"])

    with tab1:
        st.subheader("Inventory Health Metrics")
        
        col1, col2 = st.columns(2)
        avg_inventory = col1.number_input("Average Inventory Value (€)", value=annual_cogs * 0.15 if annual_cogs > 0 else 50000.0)
        
        # Calculations
        inventory_turnover = annual_cogs / avg_inventory if avg_inventory > 0 else 0
        days_sales_inv = (avg_inventory / annual_cogs) * 365 if annual_cogs > 0 else 0
        
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Inventory Turnover", f"{inventory_turnover:.2f}x")
        m2.metric("Days Sales in Inv. (DSI)", f"{days_sales_inv:.1f} Days")
        m3.metric("Inv. to Revenue Ratio", f"{(avg_inventory / annual_revenue * 100 if annual_revenue > 0 else 0):.1f}%")

        # Visual Chart: DSI vs Industry Benchmarks (Simulated)
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = days_sales_inv,
            title = {'text': "Days Sales in Inventory (DSI)"},
            gauge = {
                'axis': {'range': [None, 180]},
                'steps': [
                    {'range': [0, 45], 'color': "lightgreen"},
                    {'range': [45, 90], 'color': "yellow"},
                    {'range': [90, 180], 'color': "red"}],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': 60}
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("The Cost of Dead Capital")
        st.write(f"Using Corporate WACC (**{wacc:.1%}**) as the base for carrying costs.")
        
        col_l, col_r = st.columns(2)
        other_costs = col_l.slider("Additional Holding Costs % (Storage, Insurance, Obsolescence)", 0.0, 15.0, 5.0) / 100
        total_carrying_rate = wacc + other_costs
        
        annual_carrying_cost = avg_inventory * total_carrying_rate
        daily_cost = annual_carrying_cost / 365

        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Total Annual Carrying Cost", f"€ {annual_carrying_cost:,.2f}")
        c2.metric("Daily Bleed Rate", f"€ {daily_cost:,.2f}", delta="Cost of Holding", delta_color="inverse")

        st.subheader("💡 Optimization Impact")
        reduction_pct = st.slider("Target Inventory Reduction (%)", 0, 50, 10)
        cash_released = avg_inventory * (reduction_pct / 100)
        annual_savings = cash_released * total_carrying_rate
        
        st.success(f"**Action Plan:** Reducing inventory by {reduction_pct}% will release **€ {cash_released:,.2f}** in cash and save **€ {annual_savings:,.2f}** in annual costs.")
