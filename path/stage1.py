import streamlit as st
from core.sync import sync_global_state

def run_stage1():
    st.title("⚖️ Stage 1: Operating Leverage & Break-Even")
    
    # 1. FETCH DATA
    m = sync_global_state()
    s = st.session_state

    st.markdown("""
    Ανάλυση του σημείου μηδέν (Break-Even) και της λειτουργικής μόχλευσης.
    """)

    # 2. KPIs με ασφαλή πρόσβαση (.get)
    c1, c2, c3 = st.columns(3)
    
    bep = m.get('survival_bep', 0)
    ebit = m.get('ebit', 0)
    c_margin = m.get('contribution_margin', 0)
    
    c1.metric("Break-Even Units", f"{bep:,.0f}")
    
    vol = s.get('volume', 0)
    safety_margin = ((vol - bep) / vol) if vol > 0 else 0
    c2.metric("Margin of Safety", f"{safety_margin:.1%}")
    
    c3.metric("Annual EBIT", f"{ebit:,.0f} €")

    # 3. Operating Leverage Logic
    st.divider()
    st.subheader("Operating Leverage Insights")
    
    # Ασφαλής υπολογισμός DOL
    dol = (c_margin / ebit) if ebit > 0 else 0
    
    st.write(f"**Degree of Operating Leverage (DOL):** {dol:.2f}")
    st.info(f"Για κάθε 1% μεταβολή στις πωλήσεις, το EBIT θα μεταβάλλεται κατά {dol:.2f}%.")

    

    # 4. NAVIGATION
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
