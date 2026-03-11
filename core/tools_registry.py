import streamlit as st

def show_library():
    s = st.session_state
    
    if s.get("selected_tool") is None:
        s.flow_step = "home"
        st.rerun()

    if st.button("⬅️ Back to Control Tower"):
        s.selected_tool = None
        s.flow_step = "home"
        st.rerun()

    st.divider()

    # Λήψη του ονόματος του εργαλείου
    mod_name, func_name = s.selected_tool

    # Αν ο χρήστης πάτησε το Payables Manager, τρέξε τον παρακάτω κώδικα απευθείας
    if mod_name == "payables_manager" or mod_name == "INTERNAL":
        run_payables_manager_logic()
    else:
        # Για τα υπόλοιπα εργαλεία που θα φτιάξεις στο μέλλον
        st.info(f"Tool '{mod_name}' is being prepared. Diagnostic mode active.")
        run_payables_manager_logic()

def run_payables_manager_logic():
    """Ο κώδικας του Payables Manager ενσωματωμένος για να μην βγάζει File Not Found"""
    st.header("🤝 Payables Manager: Supplier Credit Analysis")
    
    s = st.session_state
    
    # Αυτόματος υπολογισμός από τα Global Parameters του Home
    v = s.get("volume", 1000)
    vc = s.get("variable_cost", 60.0)
    calculated_purchases = float(v) * float(vc)
    
    col1, col2 = st.columns(2)
    with col1:
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="p_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="p_disc") / 100
    with col2:
        annual_purch = st.number_input("Annual Purchase Volume (€)", value=calculated_purchases, key="p_purch")
        wacc = st.number_input("Cost of Capital - WACC (%)", value=15.0, key="p_wacc") / 100

    # Υπολογισμός με βάση 365 ημέρες [2026-02-18]
    disc_gain = annual_purch * (s.get("int_cash_prc", 50) / 100 if "int_cash_prc" in s else 0.5) * disc_prc
    opp_cost = (annual_purch * 0.5 * (cred_days / 365)) * wacc
    net_benefit = disc_gain - opp_cost

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Discount Gain", f"€{disc_gain:,.0f}")
    c2.metric("Opportunity Cost", f"-€{opp_cost:,.0f}")
    c3.metric("Net Benefit", f"€{net_benefit:,.0f}")
    
    if net_benefit > 0:
        st.success("Analysis: Taking the discount is financially optimal.")
    else:
        st.warning("Analysis: Utilizing the full credit period is better.")
