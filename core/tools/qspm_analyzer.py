import streamlit as st
import plotly.graph_objects as go

def show_qspm_tool():
    st.header("🧭 QSPM – Strategy Comparison")
    st.info("Quantitative Strategic Planning Matrix: A logic-driven framework to evaluate the feasibility of divergent strategies.")

    # 1. LOAD SYSTEM CONTEXT (Analytical Baseline)
    s = st.session_state
    m = s.get('metrics', {})
    
    # Contextual data to guide the scoring logic
    revenue = float(m.get('revenue', 0.0))
    cash_wall = float(m.get('cash_wall', 0.0))
    survival_margin = (revenue / cash_wall) - 1 if cash_wall > 0 else 0
    cash_cycle = m.get('ccc', 0)

    st.write(f"**Current System Context:** Survival Margin: {survival_margin:.1%} | Cash Conversion Cycle: {int(cash_cycle)} Days")
    st.divider()

    # 2. DEFINE STRATEGIES
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        strat1_name = st.text_input("Strategy A", value="Operational Optimization", key="qspm_s1")
    with col_s2:
        strat2_name = st.text_input("Strategy B", value="Aggressive Expansion", key="qspm_s2")

    # 3. STRATEGIC FACTORS & WEIGHTS
    # These factors represent the pillars of the business model
    factors = [
        ("Financial Stability", 0.30),
        ("Profitability", 0.25),
        ("Market Growth", 0.20),
        ("Execution Simplicity", 0.15),
        ("Resource Availability", 0.10)
    ]

    scores_a, scores_b, raw_a, raw_b = [], [], [], []

    st.subheader("📊 Attractiveness Scoring (1-4)")
    st.caption("1 = Not Attractive | 2 = Somewhat Attractive | 3 = Highly Attractive | 4 = Ideally Attractive")

    for factor, weight in factors:
        with st.container():
            st.markdown(f"**{factor}** (Weight: {weight:.0%})")
            c1, c2 = st.columns(2)
            with c1:
                s_a = st.slider(f"{strat1_name} Score", 1, 4, 2, key=f"sa_{factor}")
                raw_a.append(s_a)
                scores_a.append(s_a * weight)
            with c2:
                s_b = st.slider(f"{strat2_name} Score", 1, 4, 2, key=f"sb_{factor}")
                raw_b.append(s_b)
                scores_b.append(s_b * weight)
        st.write("")

    total_a, total_b = sum(scores_a), sum(scores_b)
    st.divider()

    # 4. RESULTS DASHBOARD
    res_a, res_b = st.columns(2)
    res_a.metric(f"Total Score: {strat1_name}", f"{total_a:.2f}")
    res_b.metric(f"Total Score: {strat2_name}", f"{total_b:.2f}", 
                 delta=f"{total_b - total_a:.2f}" if total_b != total_a else None)

    # 5. STRATEGIC RADAR (Visualizing Alignment)
    
    categories = [f[0] for f in factors]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=raw_a, theta=categories, fill='toself', name=strat1_name, line_color='#EF553B'))
    fig.add_trace(go.Scatterpolar(r=raw_b, theta=categories, fill='toself', name=strat2_name, line_color='#636EFA'))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 4])),
        template="plotly_dark",
        height=450,
        margin=dict(l=80, r=80, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 6. ANALYST'S VERDICT
    st.subheader("🧠 Strategic Verdict")
    diff = abs(total_a - total_b)
    
    if diff < 0.2:
        st.warning("⚖️ **Strategic Stalemate:** The quantitative scores are too close to provide a definitive direction. Re-evaluate the weights of the factors or the scoring of 'Execution Simplicity'.")
    elif total_a > total_b:
        st.success(f"🏆 **Winner: {strat1_name}.** This strategy demonstrates superior alignment with your current financial constraints and resource availability.")
    else:
        st.success(f"🏆 **Winner: {strat2_name}.** This path offers higher expected returns and better capitalizes on market opportunities, despite potentially higher risk.")

    # Navigation (Ευθυγραμμισμένο με το νέο app.py)
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
