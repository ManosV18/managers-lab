import streamlit as st
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_break_even_shift_calculator():
    st.header("⚖️ Break-even Shift Analysis")
    st.info("Analyze how changes in fixed costs or unit margins shift your survival threshold.")

    # 1. FETCH BASELINE DATA
    metrics = compute_core_metrics()
    s = st.session_state
    
    current_fixed = s.get('fixed_cost', 0.0) + s.get('annual_loan_payment', 0.0)
    current_unit_cm = metrics['unit_contribution']
    current_bep = metrics['survival_bep']

    # 2. SHIFT PARAMETERS
    st.subheader("🛠️ Shift Scenarios")
    col1, col2 = st.columns(2)
    
    fixed_change_pct = col1.slider("Change in Fixed Costs (%)", -30, 50, 0)
    margin_change_pct = col2.slider("Change in Unit Margin (%)", -30, 50, 0)

    # 3. CALCULATIONS
    new_fixed = current_fixed * (1 + fixed_change_pct / 100)
    new_unit_cm = current_unit_cm * (1 + margin_change_pct / 100)
    
    # New Break-even Point (Volume)
    new_bep = new_fixed / new_unit_cm if new_unit_cm > 0 else float('inf')
    bep_shift = new_bep - current_bep
    bep_shift_pct = (bep_shift / current_bep * 100) if current_bep > 0 else 0

    # 4. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Current BEP (Units)", f"{current_bep:,.0f}")
    m2.metric("New BEP (Units)", f"{new_bep:,.0f}", 
              delta=f"{bep_shift:+.0f} units", 
              delta_color="inverse")
    m3.metric("Threshold Shift", f"{bep_shift_pct:+.1f}%", 
              delta="Risk Impact", 
              delta_color="inverse")

    # 5. VISUALIZATION: BEP SHIFT CHART
    st.subheader("📈 Break-even Sensitivity")
    
    fig = go.Figure()
    # Baseline Bar
    fig.add_trace(go.Bar(
        x=['Current', 'Scenario'],
        y=[current_bep, new_bep],
        marker_color=['#636EFA', '#EF553B'],
        text=[f"{current_bep:,.0f}", f"{new_bep:,.0f}"],
        textposition='auto',
    ))

    fig.update_layout(
        yaxis_title="Units needed to Break-even",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    

    # 6. COLD ANALYSIS
    st.subheader("🧠 Analyst's Verdict")
    if bep_shift_pct > 20:
        st.error(f"🚨 **DANGER:** Your break-even point has increased by **{bep_shift_pct:.1f}%**. Your business is becoming significantly more fragile. You need a massive volume increase to justify these new costs.")
    elif bep_shift_pct < 0:
        st.success(f"✅ **EFFICIENCY GAIN:** Your break-even point dropped by **{abs(bep_shift_pct):.1f}%**. Your 'Safety Margin' has expanded.")
    else:
        st.info("ℹ️ **NEUTRAL:** No significant shift in structural risk.")

    # 7. NAVIGATION
    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
