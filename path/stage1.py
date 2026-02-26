import streamlit as st
from core.sync import sync_global_state

def run_stage1():
    st.header("⚖️ Stage 1: Operating Leverage & Break-Even Analysis")
    
    # 1. FETCH DATA (Συγχρονισμός με Engine & Sidebar)
    m = sync_global_state()
    s = st.session_state

    st.caption("Analyzing the structural sensitivity of EBIT relative to volume fluctuations.")
    st.divider()

    # =====================================================
    # 2. KPIs (Ευθυγράμμιση ονομάτων με την Engine)
    # =====================================================
    c1, c2, c3 = st.columns(3)
    
    # Τα ονόματα αυτά πρέπει να υπάρχουν στο λεξικό που επιστρέφει η calculate_metrics
    bep = float(m.get('bep_units', 0.0))
    ebit = float(m.get('ebit', 0.0))
    vol = float(s.get('volume', 0.0))
    
    c1.metric("Survival BEP", f"{bep:,.0f} Units", help="Volume required to cover all fixed costs and debt.")
    
    # Υπολογισμός Margin of Safety
    safety_margin = ((vol - bep) / vol) if vol > 0 else 0
    c2.metric("Margin of Safety", f"{safety_margin:.1%}", 
              delta="Secure" if safety_margin > 0.2 else "Risk",
              delta_color="normal" if safety_margin > 0.2 else "inverse")
    
    c3.metric("Annual EBIT", f"€ {ebit:,.0f}")

    # =====================================================
    # 3. LEVERAGE INSIGHTS (DOL)
    # =====================================================
    st.subheader("Leverage Metrics")
    
    # Το Total Contribution Margin από την Engine
    total_contribution = float(m.get('total_contribution', 0.0))
    
    # DOL = Total Contribution / EBIT
    dol = (total_contribution / ebit) if ebit > 0 else 0
    
    st.write(f"**Degree of Operating Leverage (DOL):** {dol:.2f}")
    
    if dol > 0:
        st.info(f"Analytical Mandate: A 1% change in sales will result in a {dol:.2f}% change in EBIT.")
    else:
        st.warning("⚠️ Operating Leverage cannot be calculated with zero or negative EBIT.")

    # 

    # =====================================================
    # 4. CAPITAL ALLOCATION PREVIEW
    # =====================================================
    st.subheader("💰 Capital Allocation Potential")
    fcf = float(m.get('fcf', 0.0))
    st.write(f"Current Free Cash Flow (Post-Tax/Debt): **€ {fcf:,.2f}**")
    st.caption("Αυτό είναι το ποσό που είναι διαθέσιμο για επανεπένδυση ή αποπληρωμή κεφαλαίου.")

    # =====================================================
    # 5. NAVIGATION
    # =====================================================
    st.divider()
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Back to Stage 0"):
            st.session_state.flow_step = "stage0"
            st.rerun()
    with col_next:
        if st.button("Proceed to Stage 2 ➡️"):
            st.session_state.flow_step = "stage2"
            st.rerun()
