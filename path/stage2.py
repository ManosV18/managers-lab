import streamlit as st
from core.engine import compute_core_metrics

def run_stage2():
    st.header("📉 Stage 2: Volume Shock Simulation")
    st.caption("Sensitivity Analysis: Assessing how sales volatility impacts Free Cash Flow.")

    # 1. ΚΡΑΤΑΜΕ ΤΟ BASELINE (Πριν το Shock)
    # Παίρνουμε τα metrics με το τρέχον volume (π.χ. 5000 μονάδες)
    baseline_metrics = compute_core_metrics()
    baseline_fcf = baseline_metrics['fcf']
    original_vol = st.session_state.volume

    # 2. ΡΥΘΜΙΣΗ ΤΟΥ SHOCK
    st.subheader("Apply Stress Test")
    shock_pct = st.slider("Simulated Volume Drop (%)", 0, 80, 25, help="How much will sales drop in a bad scenario?")
    
    # Προσωρινός υπολογισμός του νέου όγκου
    stressed_vol = original_vol * (1 - shock_pct/100)
    
    # Ενημερώνουμε προσωρινά το state για να υπολογίσει ο Engine τα νέα metrics
    st.session_state.volume = stressed_vol
    stressed_metrics = compute_core_metrics()
    fcf_shocked = stressed_metrics['fcf']

    # 3. ΥΠΟΛΟΓΙΣΜΟΣ ΕΛΑΣΤΙΚΟΤΗΤΑΣ (Elasticity)
    if baseline_fcf != 0:
        delta_pct = (fcf_shocked - baseline_fcf) / abs(baseline_fcf)
    else:
        delta_pct = 0.0

    # 4. ΕΜΦΑΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ
    st.divider()
    c1, c2 = st.columns(2)
    
    c1.metric("Original Annual FCF", f"{baseline_fcf:,.0f} €")
    
    # Το "Cold" Delta δείχνει την % επιδείνωση
    st.metric(
        label="Stressed Annual FCF", 
        value=f"{fcf_shocked:,.0f} €", 
        delta=f"{delta_pct:.1%} vs Baseline", 
        delta_color="inverse"
    )

    

    # 5. COLD INSIGHT
    st.subheader("🔬 Manager's Assessment")
    if fcf_shocked < 0:
        st.error(f"""
        **Terminal Shock:** Μια πτώση {shock_pct}% στις πωλήσεις εξαφανίζει όλο το FCF και δημιουργεί 
        τρύπα {abs(fcf_shocked):,.0f}€. Το μοντέλο σου δεν έχει 'λίπος' για να απορροφήσει κραδασμούς.
        """)
    else:
        st.success(f"""
        **Resilient Structure:** Παρά την πτώση, το FCF παραμένει θετικό ({fcf_shocked:,.0f}€). 
        Έχεις επαρκές 'Safety Buffer'.
        """)

    # 6. ΕΠΑΝΑΦΟΡΑ VOLUME & NAVIGATION
    # Επαναφέρουμε το volume στην αρχική του τιμή για να μην επηρεαστούν τα επόμενα Stages
    st.session_state.volume = original_vol

    st.divider()
    if st.button("Next: Liquidity Collapse (Stage 3) 🫁", type="primary", use_container_width=True):
        st.session_state.flow_step = 3
        st.rerun()
