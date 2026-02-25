import streamlit as st
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_executive_dashboard():
    st.header("🏁 Executive Liquidity Command Center")
    st.info("Compare your Current Operations with an Optimized Strategic Scenario.")

    # 1. FETCH CURRENT DATA (Synced from other tools)
    curr_ar = st.session_state.get('ar_days', 60.0)
    curr_inv = st.session_state.get('global_inventory_dsi', 45.0)
    curr_ap = st.session_state.get('payables_days', 30.0)
    
    metrics = compute_core_metrics()
    wacc = metrics.get('wacc', 0.15)
    daily_sales = metrics['revenue'] / 365

    # 2. SCENARIO BUILDER (Optimized Inputs)
    st.subheader("🚀 Strategy Optimization Scenario")
    with st.expander("Adjust Optimization Targets", expanded=True):
        c1, c2, c3 = st.columns(3)
        opt_ar = c1.slider("Target AR Days (via Discounts)", 5, 120, int(curr_ar * 0.8))
        opt_inv = c2.slider("Target Inv. Days (via Lean Mgmt)", 5, 120, int(curr_inv * 0.8))
        opt_ap = c3.slider("Target AP Days (via Negotiation)", 5, 150, int(curr_ap * 1.2))

    # 3. CALCULATIONS
    curr_ccc = curr_ar + curr_inv - curr_ap
    opt_ccc = opt_ar + opt_inv - opt_ap
    
    curr_gap = curr_ccc * daily_sales
    opt_gap = opt_ccc * daily_sales
    
    cash_released = curr_gap - opt_gap
    annual_savings = cash_released * wacc

    # 4. COMPARISON DASHBOARD
    st.divider()
    st.subheader("📈 Scenario Comparison")
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.write("**Current State**")
        st.metric("Cash Cycle", f"{curr_ccc:.1f} Days")
        st.metric("Capital Tied Up", f"€ {curr_gap:,.0f}")
        
    with res_col2:
        st.write("**Optimized State**")
        st.metric("Cash Cycle", f"{opt_ccc:.1f} Days", delta=f"{opt_ccc - curr_ccc:.1f} Days", delta_color="inverse")
        st.metric("Capital Required", f"€ {opt_gap:,.0f}", delta=f"€ {-cash_released:,.0f}", delta_color="inverse")

    

    # 5. THE "BIG PRIZE" METRICS
    st.subheader("💰 Financial Upside of Optimization")
    m1, m2 = st.columns(2)
    
    m1.metric("Potential Cash Release", f"€ {cash_released:,.2f}", 
              help="Instant liquidity injection into the bank account.")
    m2.metric("Annual WACC Savings", f"€ {annual_savings:,.2f}", 
              help="Permanent annual reduction in cost of capital.")

    # 6. VISUAL GAP ANALYSIS
    fig = go.Figure()
    # Current
    fig.add_trace(go.Bar(
        name='Current Cycle', 
        x=['Inventory', 'Receivables', 'Payables (Offset)'], 
        y=[curr_inv, curr_ar, -curr_ap],
        marker_color='#636EFA', opacity=0.6
    ))
    # Optimized
    fig.add_trace(go.Bar(
        name='Optimized Cycle', 
        x=['Inventory', 'Receivables', 'Payables (Offset)'], 
        y=[opt_inv, opt_ar, -opt_ap],
        marker_color='#00CC96'
    ))

    fig.update_layout(
        barmode='group',
        title="Current vs. Optimized Component Breakdown (Days)",
        template="plotly_dark",
        yaxis_title="Days"
    )
    st.plotly_chart(fig, use_container_width=True)

    

    # 7. ANALYTICAL CONCLUSION
    st.subheader("💡 Cold Analytical Verdict")
    if cash_released > 0:
        st.success(f"""
        **The Verdict:** Executing this optimization strategy will liberate **€ {cash_released:,.2f}** in stagnant cash. 
        At a **{wacc:.1%} WACC**, this move is equivalent to a permanent profit increase of **€ {annual_savings:,.2f}** per year, 
        without increasing sales by a single Euro.
        """)
    else:
        st.warning("Your current settings suggest a shorter cycle than your target. Ensure your 'Optimized' targets are realistic and more efficient than current performance.")

    if st.button("Finalize Strategy & Update Global Dials"):
        st.session_state.ar_days = opt_ar
        st.session_state.global_inventory_dsi = opt_inv
        st.session_state.payables_days = opt_ap
        st.success("All strategic targets have been synced to the global model.")
import streamlit as st
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_executive_dashboard():
    st.header("🏁 Executive Liquidity Command Center")
    st.info("Compare your Current Operations with an Optimized Strategic Scenario.")

    # 1. FETCH CURRENT DATA (Synced from other tools)
    curr_ar = st.session_state.get('ar_days', 60.0)
    curr_inv = st.session_state.get('global_inventory_dsi', 45.0)
    curr_ap = st.session_state.get('payables_days', 30.0)
    
    metrics = compute_core_metrics()
    wacc = metrics.get('wacc', 0.15)
    daily_sales = metrics['revenue'] / 365

    # 2. SCENARIO BUILDER (Optimized Inputs)
    st.subheader("🚀 Strategy Optimization Scenario")
    with st.expander("Adjust Optimization Targets", expanded=True):
        c1, c2, c3 = st.columns(3)
        opt_ar = c1.slider("Target AR Days (via Discounts)", 5, 120, int(curr_ar * 0.8))
        opt_inv = c2.slider("Target Inv. Days (via Lean Mgmt)", 5, 120, int(curr_inv * 0.8))
        opt_ap = c3.slider("Target AP Days (via Negotiation)", 5, 150, int(curr_ap * 1.2))

    # 3. CALCULATIONS
    curr_ccc = curr_ar + curr_inv - curr_ap
    opt_ccc = opt_ar + opt_inv - opt_ap
    
    curr_gap = curr_ccc * daily_sales
    opt_gap = opt_ccc * daily_sales
    
    cash_released = curr_gap - opt_gap
    annual_savings = cash_released * wacc

    # 4. COMPARISON DASHBOARD
    st.divider()
    st.subheader("📈 Scenario Comparison")
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.write("**Current State**")
        st.metric("Cash Cycle", f"{curr_ccc:.1f} Days")
        st.metric("Capital Tied Up", f"€ {curr_gap:,.0f}")
        
    with res_col2:
        st.write("**Optimized State**")
        st.metric("Cash Cycle", f"{opt_ccc:.1f} Days", delta=f"{opt_ccc - curr_ccc:.1f} Days", delta_color="inverse")
        st.metric("Capital Required", f"€ {opt_gap:,.0f}", delta=f"€ {-cash_released:,.0f}", delta_color="inverse")

    

    # 5. THE "BIG PRIZE" METRICS
    st.subheader("💰 Financial Upside of Optimization")
    m1, m2 = st.columns(2)
    
    m1.metric("Potential Cash Release", f"€ {cash_released:,.2f}", 
              help="Instant liquidity injection into the bank account.")
    m2.metric("Annual WACC Savings", f"€ {annual_savings:,.2f}", 
              help="Permanent annual reduction in cost of capital.")

    # 6. VISUAL GAP ANALYSIS
    fig = go.Figure()
    # Current
    fig.add_trace(go.Bar(
        name='Current Cycle', 
        x=['Inventory', 'Receivables', 'Payables (Offset)'], 
        y=[curr_inv, curr_ar, -curr_ap],
        marker_color='#636EFA', opacity=0.6
    ))
    # Optimized
    fig.add_trace(go.Bar(
        name='Optimized Cycle', 
        x=['Inventory', 'Receivables', 'Payables (Offset)'], 
        y=[opt_inv, opt_ar, -opt_ap],
        marker_color='#00CC96'
    ))

    fig.update_layout(
        barmode='group',
        title="Current vs. Optimized Component Breakdown (Days)",
        template="plotly_dark",
        yaxis_title="Days"
    )
    st.plotly_chart(fig, use_container_width=True)

    

    # 7. ANALYTICAL CONCLUSION
    st.subheader("💡 Cold Analytical Verdict")
    if cash_released > 0:
        st.success(f"""
        **The Verdict:** Executing this optimization strategy will liberate **€ {cash_released:,.2f}** in stagnant cash. 
        At a **{wacc:.1%} WACC**, this move is equivalent to a permanent profit increase of **€ {annual_savings:,.2f}** per year, 
        without increasing sales by a single Euro.
        """)
    else:
        st.warning("Your current settings suggest a shorter cycle than your target. Ensure your 'Optimized' targets are realistic and more efficient than current performance.")

    if st.button("Finalize Strategy & Update Global Dials"):
        st.session_state.ar_days = opt_ar
        st.session_state.global_inventory_dsi = opt_inv
        st.session_state.payables_days = opt_ap
        st.success("All strategic targets have been synced to the global model.")
