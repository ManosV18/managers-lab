import streamlit as st
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_cash_fragility_index():
    st.header("🛡️ Cash Fragility & Survival Analysis")
    st.info("Αυτός ο δείκτης αναλύει την αντοχή της επιχείρησης σε ταμειακά σοκ, συνδέοντας τα διαθέσιμα με τον Ταμειακό Κύκλο.")

    # 1. FETCH DATA FROM ENGINE & SESSION STATE
    metrics = compute_core_metrics()
    revenue = metrics['revenue']
    total_costs = metrics['total_costs']
    
    # Τραβάμε τον Ταμειακό Κύκλο (CCC) από το Executive Dashboard (ή βάζουμε default)
    ccc_days = st.session_state.get('ar_days', 60.0) + \
               st.session_state.get('global_inventory_dsi', 45.0) - \
               st.session_state.get('payables_days', 30.0)

    # 2. USER INPUTS FOR CASH RESERVES
    st.subheader("1. Current Liquidity Position")
    col1, col2 = st.columns(2)
    
    cash_on_hand = col1.number_input("Current Cash & Equivalents (€)", value=max(10000.0, total_costs * 0.1), step=5000.0)
    unused_credit = col2.number_input("Unused Credit Lines / Overdraft (€)", value=0.0, step=5000.0)
    
    total_liquidity = cash_on_hand + unused_credit
    daily_burn_rate = total_costs / 365

    # 3. CALCULATE FRAGILITY METRICS
    # Cash Runway: Πόσες μέρες αντέχουμε χωρίς εισπράξεις
    cash_runway = total_liquidity / daily_burn_rate if daily_burn_rate > 0 else 0
    
    # Fragility Ratio: Σχέση Cash Runway προς Cash Conversion Cycle
    # Αν ο κύκλος είναι μεγαλύτερος από το runway, η επιχείρηση είναι "Fragile"
    fragility_score = (ccc_days / cash_runway) if cash_runway > 0 else 999

    st.divider()

    # 4. DASHBOARD METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Cash Runway", f"{cash_runway:.1f} Days", help="Days of operations covered by current cash.")
    m2.metric("Cash Conversion Cycle", f"{ccc_days:.1f} Days", delta="Needs Financing", delta_color="inverse")
    
    # Χρωματισμός Fragility Score
    status = "SAFE"
    color = "green"
    if fragility_score > 1.2:
        status = "CRITICAL"
        color = "red"
    elif fragility_score > 0.8:
        status = "WARNING"
        color = "orange"
        
    m3.metric("Fragility Status", status, delta=f"Score: {fragility_score:.2f}", delta_color="inverse")

    # 5. VISUAL SURVIVAL GAUGE
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = cash_runway,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Survival Days (Runway)"},
        gauge = {
            'axis': {'range': [None, max(180, ccc_days * 1.5)]},
            'steps': [
                {'range': [0, ccc_days], 'color': "red"},
                {'range': [ccc_days, ccc_days * 1.5], 'color': "orange"},
                {'range': [ccc_days * 1.5, 1000], 'color': "lightgreen"}],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'value': ccc_days} # Το όριο ασφαλείας είναι ο ταμειακός κύκλος
        }
    ))
    fig.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig, use_container_width=True)

    # 6. ANALYTICAL VERDICT (Cold & Analytical)
    st.subheader("2. Strategic Verdict")
    
    if fragility_score > 1:
        st.error(f"""
        **Ανάλυση:** Η επιχείρηση βρίσκεται σε **Ταμειακή Ασφυξία**. 
        Ο Ταμειακός Κύκλος ({ccc_days:.1f} ημέρες) είναι μεγαλύτερος από τα αποθέματα ρευστότητας ({cash_runway:.1f} ημέρες). 
        **Κίνδυνος:** Αν σταματήσουν οι πωλήσεις ή καθυστερήσει ένας μεγάλος πελάτης, η επιχείρηση δεν θα μπορεί να καλύψει τις υποχρεώσεις της σε {cash_runway:.0f} ημέρες.
        """)
        st.markdown("👉 **Action:** Χρειάζεται άμεση μείωση του Inventory ή χρήση του Receivables Analyzer για επιτάχυνση εισπράξεων.")
    else:
        st.success(f"""
        **Ανάλυση:** Η επιχείρηση διαθέτει **Ταμειακό Μαξιλάρι**. 
        Τα διαθέσιμα καλύπτουν πλήρως τον Ταμειακό Κύκλο. Έχετε ένα περιθώριο ασφαλείας {(cash_runway - ccc_days):.1f} ημερών πέρα από τη συνήθη λειτουργία σας.
        """)

    # 7. STRESS TEST SCENARIO
    st.subheader("3. Shock Resistance Test")
    drop_pct = st.slider("Scenario: Sudden Increase in Operating Costs (%)", 0, 50, 20)
    new_burn = daily_burn_rate * (1 + drop_pct/100)
    new_runway = total_liquidity / new_burn
    
    st.write(f"Σε περίπτωση αύξησης εξόδων κατά {drop_pct}%, το Runway μειώνεται στις **{new_runway:.1f} ημέρες**.")

if __name__ == "__main__":
    show_cash_fragility_index()
