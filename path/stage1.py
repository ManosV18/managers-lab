import streamlit as st
from core.engine import compute_core_metrics

def run_stage1():
    st.header("🧱 Stage 1: Static Survival Threshold")
    st.caption("Analytical Focus: The 'Cash Wall' vs. Unit Contribution.")

    # 1. Single Source of Truth από τον Engine
    metrics = compute_core_metrics()
    s = st.session_state

    # 2. Viability Guardrail (Διορθωμένο Indentation)
    if metrics['is_non_viable']:
        st.error("🚨 **SYSTEMIC COLLAPSE:** Your Variable Cost exceeds your Price. The business loses money with every unit sold. Survival is mathematically impossible at any volume.")
        if st.button("⬅️ Return to Setup", use_container_width=True):
            st.session_state.flow_step = 0
            st.rerun()
        return # Σταματάμε την εκτέλεση εδώ αν δεν είναι βιώσιμο

    # 3. Ανάκτηση τιμών από τον Engine
    cash_wall = metrics['cash_wall']
    unit_cont = metrics['unit_contribution']
    survival_bep = metrics['survival_bep']
    current_volume = s.volume

    # 4. Visualizing the Challenge
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    c1.metric("The Cash Wall", f"{cash_wall:,.0f} €", help="Fixed Costs + Debt Service + Working Capital Requirement")
    c2.metric("Unit Ladder", f"{unit_cont:,.2f} €", help="Contribution per unit")
    c3.metric("Survival BEP", f"{survival_bep:,.0f} Units")

    # 5. Gap Analysis
    gap = survival_bep - current_volume
    st.subheader("📏 The Survival Gap")
    
    if gap > 0:
        st.error(f"🚨 **Structural Deficit:** You are {gap:,.0f} units below the Cash Survival Wall.")
        # Πρόοδος προς το BEP
        progress_val = min(current_volume / survival_bep, 1.0) if survival_bep > 0 else 0
        st.progress(progress_val)
    else:
        st.success(f"🟢 **Structural Surplus:** You are {abs(gap):,.0f} units above the Survival Wall.")
        st.progress(1.0)

    # 6. Cold Insight
    st.info(f"""
    **Cold Reality Insight:** Για να καλύψεις τις σταθερές σου υποχρεώσεις και το κεφάλαιο κίνησης που 'δεσμεύεται' στις λειτουργίες, 
    χρειάζεσαι **{survival_bep:,.0f} μονάδες**. Αυτή τη στιγμή παράγεις **{current_volume:,.0f}**.
    """)

    

    # Navigation
    if st.button("Next: Volume Shock Simulation 📉", type="primary", use_container_width=True):
        st.session_state.flow_step = 2
        st.rerun()
