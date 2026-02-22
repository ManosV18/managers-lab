import streamlit as st

def show_break_even_shift_calculator():
    st.header("⚖️ Break-Even Shift Analysis")
    st.caption("Stage 1: Establishing the Survival Anchor and Global Data.")

    # 1. INITIALIZE GLOBAL STATE (Αν δεν υπάρχουν ήδη, βάζουμε default τιμές)
    if "global_units" not in st.session_state: st.session_state.global_units = 10000
    if "global_price" not in st.session_state: st.session_state.global_price = 20.0
    if "global_vc" not in st.session_state: st.session_state.global_vc = 15.0
    if "global_fc" not in st.session_state: st.session_state.global_fc = 75000.0

    st.info("💡 Data entered here will automatically populate other tools in the path.")

    # 2. INPUTS (Διαβάζουν από το Session State)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Status")
        # Χρησιμοποιούμε το 'value' για να δείξουμε την τρέχουσα τιμή του state
        units = st.number_input("Current Sales Units", value=st.session_state.global_units, step=100)
        price = st.number_input("Current Selling Price (€)", value=st.session_state.global_price, step=1.0)
        
    with col2:
        st.subheader("Cost Structure")
        vc = st.number_input("Variable Cost per Unit (€)", value=st.session_state.global_vc, step=1.0)
        fc = st.number_input("Total Fixed Costs (€)", value=st.session_state.global_fc, step=500.0)

    # 3. UPDATE GLOBAL STATE (Αποθηκεύουμε ό,τι άλλαξε ο χρήστης)
    st.session_state.global_units = units
    st.session_state.global_price = price
    st.session_state.global_vc = vc
    st.session_state.global_fc = fc

    # 4. CALCULATIONS
    current_revenue = units * price
    current_variable_total = units * vc
    current_contribution = current_revenue - current_variable_total
    current_profit = current_contribution - fc
    
    bep_units = fc / (price - vc) if (price - vc) > 0 else 0
    bep_revenue = bep_units * price

    # 5. DISPLAY RESULTS
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Profit", f"{current_profit:,.2f} €")
    c2.metric("Break-Even Units", f"{int(bep_units)} units")
    c3.metric("Survival Margin", f"{((units/bep_units)-1)*100:.1f}%" if bep_units > 0 else "N/A")

    # Προσθήκη γραφήματος για οπτική επιβεβαίωση
    # 

    st.success("✅ Data saved. When you move to Unit Cost or Cash Cycle, these values will be pre-filled.")
