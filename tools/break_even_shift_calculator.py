import streamlit as st
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_break_even_shift_calculator():
    # 1. FETCH DATA (Η κρίσιμη σύνδεση)
    metrics = sync_global_state()
    s = st.session_state
    
    st.header("⚖️ Break-even Shift Analysis")
    st.info("Analyze how changes in fixed costs or unit margins shift your survival threshold.")

    # 2. SECURE VARIABLE RETRIEVAL (Διορθωμένα Keys)
    # Προσθήκη loan payment αν υπάρχει, αλλιώς 0.0
    current_fixed = float(s.get('fixed_cost', 0.0)) + float(s.get('annual_loan_payment', 0.0))
    
    # Τραβάμε το Unit Contribution που υπολογίζει η Engine
    current_unit_cm = float(metrics.get('unit_contribution', 0.0))
    
    # Τραβάμε το BEP Units (το σωστό key από το Stage 5)
    current_bep = float(metrics.get('bep_units', 0.0))

    # Έλεγχος αν υπάρχουν δεδομένα για να προχωρήσουμε
    if current_unit_cm <= 0:
        st.error("🚨 Unit Margin is zero or negative. Break-even cannot be calculated.")
        return

    # 3. SHIFT PARAMETERS
    st.subheader("🛠️ Shift Scenarios")
    col1, col2 = st.columns(2)
    
    # Μεταβολές +/- (όπως στο Stage 4)
    fixed_change_pct = col1.slider("Change in Fixed Costs (%)", -50, 50, 0)
    margin_change_pct = col2.slider("Change in Unit Margin (%)", -50, 50, 0)

    # 4. CALCULATIONS (Cold Analysis)
    new_fixed = current_fixed * (1 + fixed_change_pct / 100)
    new_unit_cm = current_unit_cm * (1 + margin_change_pct / 100)
    
    new_bep = new_fixed / new_unit_cm if new_unit_cm > 0 else 0.0
    bep_shift = new_bep - current_bep
    # Αποφυγή διαίρεσης με το μηδέν
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

    # 7. COLD ANALYSIS VERDICT
    st.subheader("🧠 Analyst's Verdict")
    if bep_shift_pct > 15:
        st.error(f"🚨 **STRUCTURAL FRAGILITY:** The survival threshold has moved up by **{bep_shift_pct:.1f}%**. This requires a radical increase in sales volume or immediate cost-cutting.")
    elif bep_shift_pct < -5:
        st.success(f"✅ **RESILIENCE INCREASE:** The system's break-even dropped by **{abs(bep_shift_pct):.1f}%**. Your safety buffer is expanding.")
    else:
        st.info("ℹ️ **STABLE:** The structural risk remains within historical baseline parameters.")

    # 8. NAVIGATION
    st.divider()
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
