import streamlit as st
import pandas as pd
from core.sync import sync_global_state

def run_stage5():
    st.header("🏁 Stage 5: Strategic Decision & Synthesis")
    
    # 1. DATA SYNC (Η γέφυρα με την Engine)
    m = sync_global_state()
    s = st.session_state

    if not m:
        st.warning("⚠️ Baseline not locked. Please return to Stage 0.")
        return

    st.caption("Final strategic evaluation: Balancing operational stability with growth potential.")
    st.divider()

    # 2. OPERATIONAL VITAL SIGNS (Τα νούμερα που βγήκαν από την ανάλυση)
    st.subheader("Operational Vital Signs")
    c1, c2, c3 = st.columns(3)
    
    fcf = float(m.get('fcf', 0.0))
    bep = float(m.get('bep_units', 0.0))
    runway = float(m.get('runway_months', 0.0))

    c1.metric("Final Annual FCF", f"€ {fcf:,.0f}")
    c2.metric("Survival BEP", f"{bep:,.0f} Units")
    
    # Runway Labeling
    runway_label = "Stable (∞)" if (runway >= 100 or runway < 0) else f"{runway:.1f} Mo"
    c3.metric("Runway Status", runway_label)

    st.divider()

    # 3. STRATEGIC QSPM (Το εργαλείο λήψης αποφάσεων)
    st.subheader("⚖️ Strategic Decision Matrix (QSPM)")
    st.write("Score each strategy (1-4) based on its impact on the key Success Factors below:")

    # Ορισμός των 2 δρόμων
    strat_a = "Efficiency (Margin Focus)"
    strat_b = "Growth (Volume Focus)"

    # Success Factors & Weights (Συντελεστές Βαρύτητας)
    factors = [
        {"Factor": "FCF Impact", "Weight": 0.50},
        {"Factor": "Implementation Speed", "Weight": 0.30},
        {"Factor": "Risk Resilience", "Weight": 0.20}
    ]

    scores = []
    for f in factors:
        st.markdown(f"**{f['Factor']}** (Importance: {f['Weight']:.0%})")
        col_a, col_b = st.columns(2)
        
        # Sliders για βαθμολόγηση
        s_a = col_a.slider(f"{strat_a} Score", 1, 4, 2, key=f"a_{f['Factor']}")
        s_b = col_b.slider(f"{strat_b} Score", 1, 4, 2, key=f"b_{f['Factor']}")
        
        scores.append({
            "Factor": f['Factor'],
            "Weight": f['Weight'],
            "A_Weighted": s_a * f['Weight'],
            "B_Weighted": s_b * f['Weight']
        })

    # Υπολογισμός Τελικών Score
    total_a = sum(item['A_Weighted'] for item in scores)
    total_b = sum(item['B_Weighted'] for item in scores)

    st.divider()

    # 4. FINAL VERDICT (Το Τελικό Συμπέρασμα)
    st.subheader("🏆 Analytical Verdict")
    res_a, res_b = st.columns(2)
    
    res_a.metric(strat_a, f"{total_a:.2f}")
    res_b.metric(strat_b, f"{total_b:.2f}")

    

    if total_a > total_b:
        st.success(f"**Recommendation:** The system prioritizes **{strat_a}**. Under current liquidity conditions, focus on cost-cutting and margin protection.")
    elif total_b > total_a:
        st.info(f"**Recommendation:** The system prioritizes **{strat_b}**. The data suggests an aggressive stance: Focus on scale and market share expansion.")
    else:
        st.warning("Both strategies are balanced. Professional judgment required for final selection.")

    # 5. DETAILED METRICS REVIEW (Clean Table Format)
    with st.expander("🔍 Full Engine Output Review", expanded=False):
        st.write("Comprehensive analysis of all system variables with 2-decimal precision:")
        
        # Λίστα για τη συλλογή των δεδομένων
        data_rows = []
        
        # Λογική αντιστοίχισης τεχνικών ονομάτων με επίσημους οικονομικούς όρους
        friendly_names = {
            'ebit': 'EBIT',
            'fcf': 'Free Cash Flow',
            'ocf': 'Operating Cash Flow',
            'ccc': 'Cash Conversion Cycle',
            'bep_units': 'Break-Even Point (Units)',
            'wc_requirement': 'Working Capital Requirements',
            'net_cash_position': 'Net Cash Position',
            'runway_months': 'Cash Runway (Months)',
            'cash_wall': 'Annual Cash Wall',
            'revenue': 'Projected Revenue',
            'unit_contribution': 'Unit Contribution',
            'contribution_margin': 'Total Contribution Margin',
            'contribution_ratio': 'Contribution Margin Ratio'
        }

        for key, value in m.items():
            # Χρήση του friendly name αν υπάρχει, αλλιώς μετατροπή του key
            label = friendly_names.get(key, key.replace('_', ' ').title())
            
            # Μορφοποίηση ανάλογα με τον τύπο του metric
            if any(word in key for word in ['revenue', 'ebit', 'fcf', 'ocf', 'position', 'requirement', 'contribution', 'wall']):
                formatted_value = f"€ {value:,.2f}"
            elif 'ratio' in key or 'pct' in key:
                formatted_value = f"{value:.2%}"
            elif 'days' in key or 'ccc' in key:
                formatted_value = f"{value:,.2f} Days"
            else:
                formatted_value = f"{value:,.2f}"
            
            data_rows.append({"Financial Metric": label, "Value": formatted_value})

        # Δημιουργία και εμφάνιση του πίνακα
        df_metrics = pd.DataFrame(data_rows)
        st.table(df_metrics)

    # 6. SYSTEM RESET
    st.divider()
    col_back, col_reset = st.columns([1, 1])
    
    with col_back:
        if st.button("⬅️ Back to Stress Testing", use_container_width=True):
            st.session_state.flow_step = "stage4"
            st.rerun()

    with col_reset:
        if st.button("🔄 Restart War Room Analysis", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.rerun()
