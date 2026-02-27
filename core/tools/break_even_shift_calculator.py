import streamlit as st
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_break_even_shift_calculator():
    # 1. FETCH DATA (Σύνδεση με την κεντρική Engine)
    metrics = sync_global_state()
    s = st.session_state
    
    st.header("⚖️ Break-even Shift Analysis")
    st.info("Analyze how changes in fixed costs or unit margins shift your survival threshold.")

    # 2. SECURE VARIABLE RETRIEVAL (Συγχρονισμός με Stage 0)
    # Χρησιμοποιούμε το 'annual_debt_service' για να ταυτίζεται με το Stage 0
    current_fixed = float(s.get('fixed_cost', 0.0)) + float(s.get('annual_debt_service', 0.0))
    
    # Unit Contribution από την Engine (Price - Variable Cost)
    current_unit_cm = float(metrics.get('unit_contribution', 0.0))
    
    # Break-even Units από την Engine
    current_bep = float(metrics.get('bep_units', 0.0))

    # Error handling για μηδενικό περιθώριο
    if current_unit_cm <= 0:
        st.error("🚨 Unit Margin is zero or negative. Break-even cannot be calculated.")
        st.warning("Please check your Price and Variable Cost settings in Stage 0.")
        if st.button("Go to Stage 0"):
            st.session_state.flow_step = "stage0"
            st.rerun()
        return

    # 3. SHIFT PARAMETERS (Προσομοίωση μεταβολών)
    st.subheader("🛠️ Shift Scenarios")
    col1, col2 = st.columns(2)
    
    fixed_change_pct = col1.slider("Change in Fixed Costs (%)", -50, 50, 0, key="be_fixed_shift")
    margin_change_pct = col2.slider("Change in Unit Margin (%)", -50, 50, 0, key="be_margin_shift")

    # 4. CALCULATIONS (Cold Analysis Logic)
    new_fixed = current_fixed * (1 + fixed_change_pct / 100)
    new_unit_cm = current_unit_cm * (1 + margin_change_pct / 100)
    
    # Νέο Break-even Point
    new_bep = new_fixed / new_unit_cm if new_unit_cm > 0 else 0.0
    bep_shift = new_bep - current_bep
    bep_shift_pct = (bep_shift / current_bep * 100) if current_bep > 0 else 0.0

    # 5. RESULTS DASHBOARD
    st.divider()
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Current BEP (Units)", f"{current_bep:,.0f}")
    m2.metric("New BEP (Units)", f"{new_bep:,.0f}", 
              delta=f"{bep_shift:+.0f} units", 
              delta_color="inverse")
    m3.metric("Threshold Shift", f"{bep_shift_pct:+.1f}%", 
              delta="Risk Impact", 
              delta_color="inverse")

    # 6. VISUALIZATION
    st.subheader("📈 Break-even Sensitivity Graph")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Baseline BEP', 'Simulated BEP'],
        y=[current_bep, new_bep],
        marker_color=['#636EFA', '#EF553B'],
        text=[f"{current_bep:,.0f}", f"{new_bep:,.0f}"],
        textposition='auto',
    ))

    fig.update_layout(
        yaxis_title="Units for Survival",
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 7. ANALYST'S VERDICT (Based on User Preference: No Emotional Charge)
    st.subheader("🧠 Analyst's Verdict")
    if bep_shift_pct > 15:
        st.error(f"🚨 **STRUCTURAL FRAGILITY:** The survival threshold has increased by **{bep_shift_pct:.1f}%**. This indicates higher operational leverage risk.")
    elif bep_shift_pct < -5:
        st.success(f"✅ **RESILIENCE INCREASE:** The break-even point has dropped by **{abs(bep_shift_pct):.1f}%**. Margin of safety has expanded.")
    else:
        st.info("ℹ️ **STABLE:** Structural risk remains within baseline tolerance levels.")

    # 8. NAVIGATION
    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
