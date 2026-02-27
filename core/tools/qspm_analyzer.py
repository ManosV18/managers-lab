import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_qspm_tool():
    st.header("🧭 QSPM – Strategy Comparison")
    st.info("Quantitative Strategic Planning Matrix: Evaluate which strategy best fits your current business reality.")

    # 1. LOAD SYSTEM CONTEXT
    m = sync_global_state()
    revenue = m.get('revenue', 0)
    cash_wall = m.get('cash_wall', 0)
    survival_margin = (revenue / cash_wall) - 1 if cash_wall > 0 else 0
    cash_cycle = m.get('ccc', 0)

    st.write(f"**Context:** Survival Margin: {survival_margin:.1%} | CCC: {int(cash_cycle)} Days")
    st.divider()

    # 2. DEFINE STRATEGIES
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        strat1_name = st.text_input("Strategy A", value="Operational Optimization", key="qspm_s1")
    with col_s2:
        strat2_name = st.text_input("Strategy B", value="Aggressive Expansion", key="qspm_s2")

    # 3. FACTORS
    factors = [
        ("Financial Stability", 0.30),
        ("Profitability", 0.25),
        ("Market Growth", 0.20),
        ("Execution Simplicity", 0.15),
        ("Resource Availability", 0.10)
    ]

    scores_a, scores_b, raw_a, raw_b = [], [], [], []

    for factor, weight in factors:
        st.markdown(f"**{factor}** ({weight:.0%})")
        c1, c2 = st.columns(2)
        with c1:
            s_a = st.slider(f"Score A: {factor}", 1, 4, 2, key=f"sa_{factor}")
            raw_a.append(s_a)
            scores_a.append(s_a * weight)
        with c2:
            s_b = st.slider(f"Score B: {factor}", 1, 4, 2, key=f"sb_{factor}")
            raw_b.append(s_b)
            scores_b.append(s_b * weight)

    total_a, total_b = sum(scores_a), sum(scores_b)
    st.divider()

    # 4. RESULTS
    res_a, res_b = st.columns(2)
    res_a.metric(strat1_name, f"{total_a:.2f}")
    res_b.metric(strat2_name, f"{total_b:.2f}", delta=f"{total_b - total_a:.2f}" if total_b != total_a else None)

    # 5. RADAR CHART
    categories = [f[0] for f in factors]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=raw_a, theta=categories, fill='toself', name=strat1_name))
    fig.add_trace(go.Scatterpolar(r=raw_b, theta=categories, fill='toself', name=strat2_name))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 4])), template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    

    # 6. VERDICT
    st.subheader("🧠 Analyst's Verdict")
    if abs(total_a - total_b) < 0.2:
        st.warning("Strategic Stalemate: Options are too close. Reassess weights.")
    elif total_a > total_b:
        st.success(f"Winner: {strat1_name} - Better alignment with current constraints.")
    else:
        st.success(f"Winner: {strat2_name} - Quantitatively superior ROI potential.")

    st.divider()
    if st.button("⬅️ Back to Library Hub", key="qspm_back_btn"):
        st.session_state.selected_tool = None
        st.rerun()
