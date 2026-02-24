import streamlit as st
from core.engine import compute_core_metrics

def show_loss_threshold_before_price_cut():
    st.header("📉 Loss Threshold Analysis")
    st.info("Calculate the maximum allowable price reduction or volume drop before the business enters a deficit.")

    # 1. FETCH BASELINE DATA (Institutional Sync)
    metrics = compute_core_metrics()
    p = st.session_state.get('price', 0.0)
    vc = st.session_state.get('variable_cost', 0.0)
    q = st.session_state.get('volume', 0)
    
    current_margin_per_unit = metrics['unit_contribution']
    
    # Χρήση των παγκόσμιων σταθερών υποχρεώσεων από το Sidebar
    fixed_costs = st.session_state.get('fixed_cost', 0.0)
    debt_service = st.session_state.get('annual_loan_payment', 0.0)
    fixed_obligations = fixed_costs + debt_service

    # 2. ANALYSIS: Structural Resistance
    # Break-even Price = (Fixed Obligations / Q) + VC
    be_price = (fixed_obligations / q) + vc if q > 0 else 0
    max_price_cut = p - be_price
    max_price_cut_pct = (max_price_cut / p) * 100 if p > 0 else 0

    st.subheader("Current Structural Resistance")
    c1, c2 = st.columns(2)
    
    c1.metric("Current Unit Margin", f"{current_margin_per_unit:,.2f} €")
    c1.metric("Break-even Price", f"{be_price:,.2f} €", 
              help="Η τιμή κάτω από την οποία η επιχείρηση μπαίνει σε ζημιά, συνυπολογίζοντας σταθερά έξοδα και δάνεια.")
    
    # Cold Delta: Αν η τιμή πέσει κάτω από το BE, το χρώμα αλλάζει αυτόματα
    c2.metric("Max Price Cut Allowed", 
              f"{max_price_cut:,.2f} €", 
              delta=f"-{max_price_cut_pct:.1f}%", 
              delta_color="inverse" if max_price_cut > 0 else "normal")
    
    st.divider()

    # 3. INTERACTIVE SIMULATOR
    st.subheader("What-If Scenario")
    # Ο slider ξεκινά από το Variable Cost (το απόλυτο πάτωμα)
    new_price = st.slider("Simulated Price (€)", 
                          min_value=float(vc), 
                          max_value=float(p * 1.5), 
                          value=float(p))
    
    new_margin = new_price - vc
    # Νέο Net Profit (OCF/FCF logic)
    new_ebitda = (new_margin * q) - fixed_costs
    new_tax = max(0, new_ebitda * st.session_state.get('tax_rate', 0.22))
    new_fcf = new_ebitda - new_tax - debt_service
    
    if new_fcf < 0:
        st.error(f"🚨 **Deficit Alert:** At a price of {new_price:,.2f} €, you will have an annual deficit of **{abs(new_fcf):,.2f} €**.")
    else:
        st.success(f"✅ **Safe Zone:** At this price, you still generate **{new_fcf:,.2f} €** in free cash flow.")

    # 4. COLD VERDICT
    st.subheader("🧠 Strategic Insight")
    st.markdown(f"""
    Το επιχειρηματικό σου μοντέλο διαθέτει ένα **pricing buffer της τάξης του {max_price_cut_pct:.1f}%**. 
    
    * **Ανταγωνισμός:** Αν οι ανταγωνιστές μειώσουν τις τιμές τους περισσότερο από αυτό το όριο, η επιχείρηση θα χρειαστεί άμεση αύξηση του Volume για να επιβιώσει.
    * **Κόστος:** Αν το μεταβλητό σου κόστος (VC) αυξηθεί κατά **{max_price_cut:,.2f} €** ανά μονάδα, ο τρέχων όγκος πωλήσεων δεν θα επαρκεί πλέον για την κάλυψη των δανείων και των σταθερών εξόδων.
    """)

    

    # 5. NAVIGATION
    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
