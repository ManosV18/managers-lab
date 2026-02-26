import streamlit as st
import pandas as pd
from core.sync import sync_global_state

def run_stage5():
    st.header("🏁 Stage 5: Strategic Decision & Synthesis")
    
    # 1. DATA SYNC
    m = sync_global_state()
    s = st.session_state
    st.divider()

    fcf = float(m.get('fcf', 0.0))
    bep = float(m.get('bep_units', 0.0))
    runway = float(m.get('runway_months', 0.0))

    # 2. OPERATIONAL VITAL SIGNS
    st.subheader("Operational Vital Signs")
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Annual FCF", f"€ {fcf:,.0f}")
    c2.metric("Survival BEP", f"{bep:,.0f} Units")
    
    runway_label = "Stable (∞)" if (runway >= 100 or runway < 0) else f"{runway:.1f} Mo"
    c3.metric("Runway Status", runway_label)

    st.divider()

    # 3. STRATEGIC QSPM (Two Different Strategies)
    st.subheader("⚖️ Strategic Decision Matrix (QSPM)")
    st.write("Score each strategy (1-4) based on its impact on the key Success Factors below:")

    # Define the 2 paths
    strat_a = "Efficiency (Margin Focus)"
    strat_b = "Growth (Volume Focus)"

    # Success Factors & Weights
    factors = [
        {"Factor": "FCF Impact", "Weight": 0.50},
        {"Factor": "Implementation Speed", "Weight": 0.30},
        {"Factor": "Risk Resilience", "Weight": 0.20}
    ]

    scores = []
    for f in factors:
        st.markdown(f"**{f['Factor']}** (Importance: {f['Weight']:.0%})")
        col_a, col_b = st.columns(2)
        s_a = col_a.slider(f"{strat_a} Score", 1, 4, 2, key=f"a_{f['Factor']}")
        s_b = col_b.slider(f"{strat_b} Score", 1, 4, 2, key=f"b_{f['Factor']}")
        
        scores.append({
            "Factor": f['Factor'],
            "Weight": f['Weight'],
            "A_Score": s_a * f['Weight'],
            "B_Score": s_b * f['Weight']
        })

    # Calculation
    total_a = sum(item['A_Score'] for item in scores)
    total_b = sum(item['B_Score'] for item in scores)

    st.divider()

    # 4. FINAL VERDICT
    st.subheader("🏆 Analytical Verdict")
    res_a, res_b = st.columns(2)
    
    res_a.metric(strat_a, f"{total_a:.2f}")
    res_b.metric(strat_b, f"{total_b:.2f}")

    

    if total_a > total_b:
        st.success(f"**Recommendation:** The system prioritizes **{strat_a}**. Focus on cost-cutting and margin optimization.")
    elif total_b > total_a:
        st.info(f"**Recommendation:** The system prioritizes **{strat_b}**. Focus on scale, volume, and market share.")
    else:
        st.warning("Both strategies are balanced. Professional judgment required for final selection.")

    # 5. SYSTEM RESET
    st.divider()
    if st.button("🔄 Restart War Room Analysis", use_container_width=True):
        st.session_state.clear()
        st.rerun()
