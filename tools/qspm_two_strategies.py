import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_qspm_tool():
    st.header("🧭 QSPM – Strategy Comparison")
    st.info("Quantitative Strategic Planning Matrix: Evaluate which strategy best fits your current business reality based on weighted Success Factors.")

    # 1. LOAD SYSTEM CONTEXT (Analytical Grounding)
    # Χρήση του sync_global_state για ομοιομορφία με την υπόλοιπη εφαρμογή
    m = sync_global_state()
    
    # Υπολογισμός Survival Margin & Cash Cycle από τα κεντρικά δεδομένα
    revenue = m.get('revenue', 0)
    cash_wall = m.get('cash_wall', 0)
    survival_margin = (revenue / cash_wall) - 1 if cash_wall > 0 else 0
    cash_cycle = m.get('ccc', 0)

    st.write(f"**Current Strategic Context:** Survival Margin: {survival_margin:.1%} | Cash Conversion Cycle: {int(cash_cycle)} Days")

    st.divider()

    # 2. DEFINE STRATEGIES
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        strat1_name = st.text_input("Strategy A", value="Operational Optimization")
    with col_s2:
        strat2_name = st.text_input("Strategy B", value="Aggressive Market Expansion")

    # 3. CRITICAL SUCCESS FACTORS (CSFs)
    factors = [
        ("Financial Stability (Cash Flow)", 0.30),
        ("Profitability (Margin)", 0.25),
        ("Market Share / Growth", 0.20),
        ("Execution Simplicity", 0.15),
        ("Resource Availability", 0.10)
    ]

    st.subheader("Attractiveness Scoring (1-4)")
    st.caption("1: Not attractive | 2: Somewhat attractive | 3: Reasonably attractive | 4: Highly attractive")

    scores_a = []
    scores_b = []
    raw_a = []
    raw_b = []

    # Δημιουργία των Sliders για κάθε παράγοντα
    for factor, weight in factors:
        st.markdown(f"**{factor}** (Weight: {weight:.0%})")
        c1, c2 = st.columns(2)
        with c1:
            s_a = st.slider(f"Score A", 1, 4, 2, key=f"q_a_{factor}")
            raw_a.append(s_a)
            scores_a.append(s_a * weight)
        with c2:
            s_b = st.slider(f"Score B", 1, 4, 2, key=f"q_b_{factor}")
            raw_b.append(s_b)
            scores_b.append(s_b * weight)

    # 4. FINAL CALCULATION
    total_a = sum(scores_a)
    total_b = sum(scores_b)

    st.divider()

    # 5. RESULTS DISPLAY
    res_a, res_b = st.columns(2)
    with res_a:
        st.metric(f"Total Score: {strat1_name}", f"{total_a:.2f}")
    with res_b:
        delta_val = total_b - total_a
        st.metric(f"Total Score: {strat2_name}", f"{total_b:.2f}", 
                  delta=f"{delta_val:.2f}" if total_b != total_a else None)

    # 6. VISUAL RADAR CHART
    st.subheader("📊 Strategic Alignment Radar")
    
    categories = [f[0] for f in factors]
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(r=raw_a, theta=categories, fill='toself', name=strat1_name))
    fig.add_trace(go.Scatterpolar(r=raw_b, theta=categories, fill='toself', name=strat2_name))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 4])),
        showlegend=True,
        template="plotly_dark",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    # 7. STRATEGIC VERDICT
    st.subheader("🧠 Analyst's Verdict")
    if abs(total_a - total_b) < 0.2:
        st.warning("**Strategic Stalemate:** The options are very close. Reassess the weights or consider a Phased Execution approach.")
    elif total_a > total_b:
        st.success(f"**Winner: {strat1_name}** – This choice aligns better with current constraints and the business risk profile.")
    else:
        st.success(f"**Winner: {strat2_name}** – This strategy quantitatively outperforms, potentially offering higher ROI despite risk.")

    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
