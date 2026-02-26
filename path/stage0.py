import streamlit as st
from core.sync import lock_baseline, sync_global_state

def run_stage0():
    st.header("🏗️ Stage 0: Strategic Baseline Setup")
    st.write("Changes made here update the system in real-time.")
    st.divider()

    # --- BLOCK 1: REVENUE & VOLUME ---
    st.subheader("📊 Sales & Pricing")
    c1, c2 = st.columns(2)
    
    # Χρησιμοποιούμε το 'key' για να γράφουμε ΑΠΕΥΘΕΙΑΣ στο session_state
    # που διαβάζει το Sidebar και η Engine.
    st.number_input(
        "Unit Sales Price (€)", 
        min_value=0.0,
        value=float(st.session_state.get('price', 100.0)),
        key='price'  # ΑΥΤΟ ΠΡΕΠΕΙ ΝΑ ΕΙΝΑΙ ΤΟ ΙΔΙΟ ΜΕ ΤΟ SIDEBAR
    )
    
    st.number_input(
        "Planned Annual Volume (Units)", 
        min_value=0,
        value=int(st.session_state.get('volume', 1000)),
        key='volume' # ΑΥΤΟ ΠΡΕΠΕΙ ΝΑ ΕΙΝΑΙ ΤΟ ΙΔΙΟ ΜΕ ΤΟ SIDEBAR
    )

    # --- BLOCK 2: COST ANALYSIS ---
    st.subheader("💰 Cost Structure")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Variable Costs Breakdown**")
        # Εδώ χρησιμοποιούμε προσωρινές μεταβλητές για τον υπολογισμό
        v1 = st.number_input("Raw Materials (€/unit)", value=30.0, key='tmp_raw')
        v2 = st.number_input("Direct Labor (€/unit)", value=15.0, key='tmp_labor')
        v3 = st.number_input("Shipping/Other (€/unit)", value=5.0, key='tmp_ship')
        
        # Ενημέρωση του κεντρικού variable_cost που βλέπει η Engine
        st.session_state.variable_cost = v1 + v2 + v3
        st.info(f"Calculated Variable Cost: **€{st.session_state.variable_cost:,.2f}**")

    with col_b:
        st.markdown("**Fixed Costs Breakdown**")
        f1 = st.number_input("Monthly Rent (€)", value=1000.0, key='tmp_rent') * 12
        f2 = st.number_input("Admin Salaries (Annual)", value=10000.0, key='tmp_sal')
        
        # Ενημέρωση του κεντρικού fixed_cost που βλέπει η Engine
        st.session_state.fixed_cost = f1 + f2
        st.info(f"Total Fixed Costs: **€{st.session_state.fixed_cost:,.2f}**")

    

    # --- BLOCK 3: ENGINE SYNC CHECK ---
    st.divider()
    st.subheader("🔄 Real-Time Engine Sync")
    
    # Καλούμε το sync_global_state ΓΙΑ ΝΑ ΔΟΥΜΕ αν η engine πήρε τα νέα νούμερα
    # Χωρίς να κλειδώσουμε ακόμα, απλά για preview
    try:
        from core.engine import calculate_metrics
        # Προσωρινός υπολογισμός για να βλέπει ο χρήστης ότι "δουλεύει"
        preview_metrics = calculate_metrics(
            st.session_state.price,
            st.session_state.volume,
            st.session_state.variable_cost,
            st.session_state.fixed_cost,
            st.session_state.get('wacc', 0.15),
            st.session_state.get('tax_rate', 0.22),
            st.session_state.get('ar_days', 45.0),
            st.session_state.get('inventory_days', 60.0),
            st.session_state.get('ap_days', 30.0),
            st.session_state.get('annual_debt_service', 0.0),
            st.session_state.get('opening_cash', 10000.0)
        )
        st.write(f"**Current EBIT Preview:** €{preview_metrics['ebit']:,.2f}")
    except:
        st.warning("Engine is waiting for valid data inputs...")

    # --- FINAL LOCK ---
    st.divider()
    if st.button("🔒 Lock & Update All Stages", use_container_width=True):
        # ΠΡΟΣΟΧΗ: Διαγράφουμε το παλιό baseline για να αναγκάσουμε την Engine 
        # να πάρει τα ΦΡΕΣΚΑ νούμερα
        if 'baseline' in st.session_state:
            del st.session_state.baseline
        
        lock_baseline() 
        st.success("System Updated! Metrics are now synced across all stages.")
        st.rerun()
