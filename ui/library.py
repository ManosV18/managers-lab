import streamlit as st
from core.sync import sync_global_state

# Import των εργαλείων σου (Βεβαιώσου ότι τα ονόματα αρχείων/συναρτήσεων συμπίπτουν)
from tools.break_even_shift_calculator import show_break_even_shift_calculator
from tools.pricing_power_radar import show_pricing_power_radar
from tools.cash_fragility_index import show_cash_fragility_index
from tools.clv_calculator import show_clv_calculator

def show_library():
    # 1. ΣΥΓΧΡΟΝΙΣΜΟΣ & METRICS
    metrics = sync_global_state()
    s = st.session_state

    # 2. HEADER ΜΕ ΤΑ ΒΑΣΙΚΑ METRICS (Εδώ θα δεις το WACC)
    st.title("📚 Strategic Tool Library")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current WACC", f"{s.get('wacc', 0.15):.2%}")
    m2.metric("Unit Margin", f"{metrics.get('unit_contribution', 0.0):,.2f} €")
    m3.metric("Break-even", f"{metrics.get('survival_bep', 0):,.0f} units")
    m4.metric("Cash Runway", f"{metrics.get('cash_runway', 0):,.0f} days")
    
    st.divider()

    # 3. ΕΠΙΛΟΓΗ ΕΡΓΑΛΕΙΟΥ (Αν δεν έχει επιλεγεί ήδη κάποιο)
    if s.get('selected_tool') is None:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚀 Strategy & Growth")
            if st.button("⚖️ Break-even Shift Analysis", use_container_width=True):
                s.selected_tool = "break_even"
                st.rerun()
            if st.button("🎯 Pricing Power Radar", use_container_width=True):
                s.selected_tool = "pricing"
                st.rerun()
            if st.button("👥 CLV Simulator", use_container_width=True):
                s.selected_tool = "clv"
                st.rerun()

        with col2:
            st.subheader("💰 Finance & Capital")
            if st.button("🛡️ Cash Fragility Index", use_container_width=True):
                s.selected_tool = "fragility"
                st.rerun()
            # Πρόσθεσε εδώ μελλοντικά εργαλεία Finance

    # 4. ROUTER ΕΡΓΑΛΕΙΩΝ
    else:
        tool = s.selected_tool
        
        if st.button("⬅️ Back to Library"):
            s.selected_tool = None
            st.rerun()
            
        st.divider()

        if tool == "break_even":
            show_break_even_shift_calculator()
        elif tool == "pricing":
            show_pricing_power_radar()
        elif tool == "clv":
            show_clv_calculator()
        elif tool == "fragility":
            show_cash_fragility_index()

    # 5. ΕΠΙΣΤΡΟΦΗ ΣΤΟ PATH
    st.sidebar.divider()
    if st.sidebar.button("🚀 Return to Strategic Path", use_container_width=True):
        s.mode = "path"
        st.rerun()
