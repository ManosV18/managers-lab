import streamlit as st
from core.sync import sync_global_state

def show_receivables_optimizer():
    st.header("🎯 Receivables Strategic Optimizer")
    st.info("Ανάλυση NPV για την προσφορά έκπτωσης σε πελάτες με σκοπό την επιτάχυνση των εισπράξεων.")

    # 1. FETCH GLOBAL DATA
    metrics = sync_global_state()
    s = st.session_state

    # INPUTS (Από το πάνω μέρος της εικόνας σου)
    col1, col2 = st.columns(2)
    
    with col1:
        current_sales = st.number_input("Current Sales (€)", value=float(s.get('sales', 1000.0)))
        extra_sales = st.number_input("Extra Sales from Policy (€)", value=250.0)
        discount_trial = st.number_input("Discount Offered (%)", value=2.0, step=0.1) / 100
        prc_take_disc = st.number_input("% Clients Taking Discount", value=40.0) / 100
        wacc = metrics.get('wacc', 0.20)
        st.write(f"**WACC (Cost of Capital):** {wacc:.1%}")

    with col2:
        days_take_disc = st.number_input("Days (Clients taking discount)", value=60)
        days_not_take_disc = st.number_input("Days (Clients NOT taking discount)", value=120)
        new_days_take_disc = st.number_input("New Payment Term for Discount (Days)", value=10)
        cogs_val = st.number_input("COGS (€)", value=800.0)

    # 2. CALCULATIONS (ΑΚΡΙΒΩΣ ΟΠΩΣ ΣΤΗΝ ΕΙΚΟΝΑ ΣΟΥ)
    # ---------------------------------------------------------
    prc_not_take_disc = 1 - prc_take_disc
    
    # Current State
    avg_collection_days = (days_take_disc * prc_take_disc) + (days_not_take_disc * prc_not_take_disc)
    current_receivables = (current_sales * avg_collection_days) / 365 # 365 βάσει οδηγίας σας

    # New Policy State
    total_new_sales = current_sales + extra_sales
    prcnt_new_clients_in_new_policy = ((current_sales * prc_take_disc) + extra_sales) / total_new_sales
    prcnt_new_clients_in_old_policy = 1 - prcnt_new_clients_in_new_policy
    
    new_avg_collection_period = (prcnt_new_clients_in_new_policy * new_days_take_disc) + (prcnt_new_clients_in_old_policy * days_not_take_disc)
    new_receivables = (total_new_sales * new_avg_collection_period) / 365
    
    # Financial Impacts
    free_capital = current_receivables - new_receivables
    profit_from_extra_sales = extra_sales * (1 - (cogs_val / current_sales))
    profit_from_free_capital = free_capital * wacc
    discount_cost = total_new_sales * prcnt_new_clients_in_new_policy * discount_trial
    
    # FINAL NPV
    npv = profit_from_extra_sales + profit_from_free_capital - discount_cost

    # 3. DISPLAY RESULTS (Yellow Box in your Image)
    st.divider()
    st.subheader("📊 Strategic Analysis Results")
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Current Receivables", f"€ {current_receivables:,.2f}")
    res1.metric("New Receivables", f"€ {new_receivables:,.2f}")
    res1.metric("Free Capital", f"€ {free_capital:,.2f}")

    res2.metric("Profit from Extra Sales", f"€ {profit_from_extra_sales:,.2f}")
    res2.metric("Profit from Free Capital", f"€ {profit_from_free_capital:,.2f}")
    res2.metric("Discount Cost (Loss)", f"€ {discount_cost:,.2f}", delta_color="inverse")

    st.info(f"### 💎 NPV of New Policy: € {npv:,.2f}")

    # 4. OPTIMUM DISCOUNT (NPV Break Even logic)
    st.divider()
    # Σύμφωνα με την εικόνα σας για το Break Even
    max_disc = 1 - (1 / (1 + (wacc/365))**(avg_collection_days - new_days_take_disc)) # Προσέγγιση
    
    st.write(f"**Maximum Allowable Discount (Break Even):** {max_disc:.2%}")

    # ACTIONS
    if st.button("Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
