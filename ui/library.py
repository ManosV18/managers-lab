import streamlit as st
from core.sync import sync_global_state

# Imports - Βεβαιώσου ότι τα αρχεία υπάρχουν στο tools/
try:
    from tools.break_even_shift_calculator import show_break_even_shift_calculator
    from tools.pricing_power_radar import show_pricing_power_radar
    from tools.cash_fragility_index import show_cash_fragility_index
    from tools.clv_calculator import show_clv_calculator
    # Πρόσθεσε εδώ μελλοντικά imports
except ImportError as e:
    st.error(f"Missing Tool File: {e}")

def show_library():
    metrics = sync_global_state()
    s = st.session_state

    # 1. ΠΑΝΤΑ ΟΡΑΤΟ HEADER & METRICS
    st.title("📚 Strategic Tool Library")
    
    # Εδώ βλέπεις το WACC και τα βασικά σου νούμερα
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("WACC", f"{s.get('wacc', 0.15):.2%}")
    m2.metric("Unit Margin", f"{metrics.get('unit_contribution', 0.0):,.2f} €")
    m3.metric("Break-even", f"{metrics.get('survival_bep', 0):,.0f} u")
    m4.metric("Runway", f"{metrics.get('cash_runway', 0):,.0f} days")
    
    st.divider()

    # 2. ROUTER: ΕΙΤΕ ΔΕΙΧΝΟΥΜΕ ΤΙΣ ΚΑΤΗΓΟΡΙΕΣ ΕΙΤΕ ΤΟ ΕΡΓΑΛΕΙΟ
    if s.get('selected_tool') is None:
        # --- ΕΜΦΑΝΙΣΗ ΚΑΤΗΓΟΡΙΩΝ ---
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("### 🚀 Strategy")
            if st.button("⚖️ BEP Shift", use_container_width=True):
                s.selected_tool = "break_even"
                st.rerun()
            if st.button("🎯 Pricing Radar", use_container_width=True):
                s.selected_tool = "pricing"
                st.rerun()
            if st.button("👥 CLV Simulator", use_container_width=True):
                s.selected_tool = "clv"
                st.rerun()

        with col2:
            st.markdown("### 💰 Finance")
            if st.button("🛡️ Cash Fragility", use_container_width=True):
                s.selected_tool = "fragility"
                st.rerun()
            if st.button("📉 Debt Analysis", use_container_width=True, disabled=True):
                pass

        with col3:
            st.markdown("### ⚙️ Ops")
            if st.button("🔄 CCC Analyzer", use_container_width=True, disabled=True):
                pass
            if st.button("📦 Inventory Opti", use_container_width=True, disabled=True):
                pass

        with col4:
            st.markdown("### 📉 Risk")
            if st.button("🌪️ Stress Test", use_container_width=True, disabled=True):
                pass
            if st.button("📊 Monte Carlo", use_container_width=True, disabled=True):
                pass

    else:
        # --- ΕΜΦΑΝΙΣΗ ΕΡΓΑΛΕΙΟΥ & ΚΟΥΜΠΙ ΕΠΙΣΤΡΟΦΗΣ ---
        if st.button("⬅️ Back to All Categories", type="primary"):
            s.selected_tool = None
            st.rerun()
        
        st.divider()

        # Κλήση της αντίστοιχης συνάρτησης
        t = s.selected_tool
        if t == "break_even":
            show_break_even_shift_calculator()
        elif t == "pricing":
            show_pricing_power_radar()
        elif t == "clv":
            show_clv_calculator()
        elif t == "fragility":
            show_cash_fragility_index()

    # 3. SIDEBAR EXIT
    st.sidebar.divider()
    if st.sidebar.button("🚀 Exit Library", use_container_width=True):
        s.selected_tool = None # Καθαρίζουμε το εργαλείο πριν βγούμε
        s.mode = "path"
        st.rerun()
