import streamlit as st
from core.sync import sync_global_state  # Corrected Import

def show_loss_threshold_before_price_cut():
    st.header("📉 Loss Threshold Analysis")
    st.info("Calculate the maximum allowable price reduction or volume drop before the business enters a deficit.")

    # 1. FETCH BASELINE DATA (Institutional Sync)
    # Η sync_global_state αναλαμβάνει να καλέσει την engine με τα 11 positional arguments
    metrics = sync_global_state() 
    s = st.session_state
    
    # Ανάκτηση παραμέτρων από το session_state
    p = s.get('price', 0.0)
    vc = s.get('variable_cost', 0.0)
    q = s.get('volume', 0)
    
    # Ανάκτηση υπολογισμένων metrics από την engine
    current_margin_per_unit = metrics.get('unit_contribution', 0.0)
    
    # Χρήση των σταθερών υποχρεώσεων
    fixed_costs = s.get('fixed_cost', 0.0)
    # Βεβαιώσου ότι το key 'annual_debt' ταυτίζεται με αυτό που έχεις στο Sidebar
    debt_service = s.get('annual_debt', 0.0) 
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
              help="Η τιμή κάτω από την οποία η επιχείρηση μπαίνει σε ζημιά (Net Deficit), συνυπολογίζοντας σταθερά έξοδα και δάνεια.")
    
    # Cold Delta: Οπτική ένδειξη ασφαλείας
    c2.metric("Max Price Cut Allowed", 
              f"{max_price_cut:,.2f} €", 
              delta=f"-{max_price_cut_pct:.1f}%", 
              delta_color="inverse" if max_price_cut > 0 else "normal")
    
    st.divider()

    # 3. INTERACTIVE SIMULATOR
    st.subheader("What-If Scenario")
    new_price = st.slider("Simulated Price (€)", 
                          min_value=float(vc), 
                          max_value=float(p * 1.5), 
                          value=float(p))
    
    new_margin = new_price - vc
    new_ebitda = (new_margin * q) - fixed_costs
    new_tax = max(0, new_ebitda * s.get('tax_rate', 0.22))
    new_fcf = new_ebitda - new_tax - debt_service
    
    if new_fcf < 0:
        st.error(f"🚨 **Deficit Alert:** At a price of {new_price:,.2f} €, you will have an annual deficit of **{abs(new_fcf):,.2f} €**.")
    else:
        st.success(f"✅ **Safe Zone:** At this price, you still generate **{new_fcf:,.2f} €** in free cash flow.")

    # 4. COLD VERDICT
    st.subheader("🧠 Strategic Insight")
    st.markdown(f"""
    Your business model maintains a **pricing buffer of {max_price_cut_pct:.1f}%**. 
    
    * **Competition:** If competitors reduce their prices beyond this threshold, the business will require an immediate increase in Volume to remain viable.
    * **Costs:** If your Variable Cost (VC) increases by **{max_price_cut:,.2f} €** per unit, the current sales volume will no longer be sufficient to cover debt obligations and fixed expenses.
    """)

    # 5. NAVIGATION
    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
