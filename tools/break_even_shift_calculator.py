import streamlit as st
from core.sync import sync_global_state

def show_break_even_shift_calculator():
    metrics = sync_global_state()
    st.header("⚖️ Break-even Shift Analysis")
    st.info("Analyze how changes in fixed costs or unit margins shift your survival threshold.")

    # 1. FETCH BASELINE DATA SAFELY
    # Η sync_global_state καλεί τον κινητήρα με τα 11 ορίσματα εσωτερικά
    metrics = sync_global_state()
    s = st.session_state
    
    # Secure variable retrieval
    current_fixed = s.get('fixed_cost', 0.0) + s.get('annual_loan_payment', 0.0)
    current_unit_cm = metrics.get('unit_contribution', 0.0)
    current_bep = metrics.get('survival_bep', 0.0)

    # 2. SHIFT PARAMETERS
    st.subheader("🛠️ Shift Scenarios")
    col1, col2 = st.columns(2)
    
    fixed_change_pct = col1.slider("Change in Fixed Costs (%)", -30, 50, 0)
    margin_change_pct = col2.slider("Change in Unit Margin (%)", -30, 50, 0)

    # 3. CALCULATIONS
    new_fixed = current_fixed * (1 + fixed_change_pct / 100)
    new_unit_cm = current_unit_cm * (1 + margin_change_pct / 100)
    
    # New Break-even Point calculation
    new_bep = new_fixed / new_unit_cm if new_unit_cm > 0 else 0.0
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

    # 5. VISUALIZATION
    
    st.subheader("📈 Break-even Sensitivity")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Current Baseline', 'Future Scenario'],
        y=[current_bep, new_bep],
        marker_color=['#636EFA', '#EF553B'],
        text=[f"{current_bep:,.0f}", f"{new_bep:,.0f}"],
        textposition='auto',
    ))

    fig.update_layout(
        yaxis_title="Units to Break-even",
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 6. COLD ANALYSIS
    st.subheader("🧠 Analyst's Verdict")
    if bep_shift_pct > 20:
        st.error(f"🚨 **DANGER:** Break-even increased by **{bep_shift_pct:.1f}%**. Business fragility is escalating. Volume must increase significantly to offset this shift.")
    elif bep_shift_pct < 0:
        st.success(f"✅ **EFFICIENCY GAIN:** Break-even dropped by **{abs(bep_shift_pct):.1f}%**. Your safety margin has expanded.")
    else:
        st.info("ℹ️ **NEUTRAL:** No significant structural risk shift detected.")

    # 7. NAVIGATION
    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
