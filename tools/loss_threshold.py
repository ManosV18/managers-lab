import streamlit as st
from core.sync import sync_global_state  # Η μοναδική πηγή δεδομένων

def show_loss_threshold_before_price_cut():
    st.header("📉 Loss Threshold Analysis")
    st.info("Calculate the maximum allowable price reduction or volume drop before the business enters a deficit.")

    # 1. FETCH DATA VIA SYNC (Αυτό γεμίζει τα 11 ορίσματα αυτόματα)
    metrics = sync_global_state() 
    s = st.session_state
    
    # Ανάκτηση παραμέτρων από το state
    p = s.get('price', 0.0)
    vc = s.get('variable_cost', 0.0)
    q = s.get('volume', 0)
    
    # Ανάκτηση αποτελεσμάτων από την engine
    current_margin_per_unit = metrics.get('unit_contribution', 0.0)
    
    # Σταθερές υποχρεώσεις (Fixed Costs + Debt)
    fixed_costs = s.get('fixed_cost', 0.0)
    debt_service = s.get('annual_debt', 0.0) 
    fixed_obligations = fixed_costs + debt_service

    # 2. ANALYSIS
    be_price = (fixed_obligations / q) + vc if q > 0 else 0
    max_price_cut = p - be_price
    max_price_cut_pct = (max_price_cut / p) * 100 if p > 0 else 0

    # UI Metrics
    st.subheader("Current Structural Resistance")
    c1, c2 = st.columns(2)
    c1.metric("Current Unit Margin", f"{current_margin_per_unit:,.2f} €")
    c1.metric("Break-even Price", f"{be_price:,.2f} €")
    
    c2.metric("Max Price Cut Allowed", 
              f"{max_price_cut:,.2f} €", 
              delta=f"-{max_price_cut_pct:.1f}%", 
              delta_color="inverse" if max_price_cut > 0 else "normal")
    
    st.divider()

    # 3. INTERACTIVE SLIDER
    new_price = st.slider("Simulated Price (€)", float(vc), float(p * 1.5), float(p))
    
    new_margin = new_price - vc
    new_ebitda = (new_margin * q) - fixed_costs
    new_tax = max(0, new_ebitda * s.get('tax_rate', 0.22))
    new_fcf = new_ebitda - new_tax - debt_service
    
    if new_fcf < 0:
        st.error(f"🚨 **Deficit Alert:** Annual deficit of **{abs(new_fcf):,.2f} €**.")
    else:
        st.success(f"✅ **Safe Zone:** Surplus of **{new_fcf:,.2f} €**.")

    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
