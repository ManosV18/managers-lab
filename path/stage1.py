import streamlit as st
from core.sync import sync_global_state

def run_stage1():
    st.title("⚖️ Stage 1: Operating Leverage & Break-Even")
    
    # 1. FETCH DATA (Συγχρονισμός με τον νέο κινητήρα)
    m = sync_global_state()
    s = st.session_state

    st.markdown("""
    Ανάλυση του σημείου μηδέν (Break-Even) και της λειτουργικής μόχλευσης. 
    Εδώ εξετάζουμε πόσο "ευαίσθητο" είναι το EBIT στις μεταβολές του όγκου πωλήσεων.
    """)

    # 2. KEY PERFORMANCE INDICATORS (KPIs)
    c1, c2, c3 = st.columns(3)
    
    # Χρησιμοποιούμε τα ονόματα μεταβλητών από τον νέο κινητήρα
    c1.metric("Break-Even Units", f"{m['survival_bep']:,.0f}", help="Units to cover Fixed Costs + Debt")
    
    safety_margin = ((s.volume - m['survival_bep']) / s.volume) if s.volume > 0 else 0
    c2.metric("Margin of Safety", f"{safety_margin:.1%}", delta=None)
    
    c3.metric("Annual EBIT", f"{m['ebit']:,.0f} €")

    # 3. VISUAL ANALYSIS (Optional Placeholder for Chart)
    st.divider()
    st.subheader("Operating Leverage Insights")
    
    # Cold Analytical Logic: 
    # Υπολογίζουμε τη μόχλευση: Contribution Margin / EBIT
    dol = (m['contribution_margin'] / m['ebit']) if m['ebit'] > 0 else 0
    
    st.write(f"**Degree of Operating Leverage (DOL):** {dol:.2f}")
    st.info(f"Για κάθε 1% μεταβολή στις πωλήσεις, το λειτουργικό κέρδος (EBIT) θα μεταβάλλεται κατά {dol:.2f}%.")

    # 4. NAVIGATION
    st.divider()
    col_prev, col_next = st.columns(2)
    
    with col_prev:
        if st.button("⬅️ Back to Stage 0"):
            st.session_state.flow_step = "stage0"
            st.rerun()
            
    with col_next:
        # Επιτρέπουμε τη μετάβαση μόνο αν η επιχείρηση είναι κερδοφόρα (ή αν το επιλέξει ο χρήστης)
        if st.button("Proceed to Stage 2 ➡️"):
            st.session_state.flow_step = "stage2"
            st.rerun()
