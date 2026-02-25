import streamlit as st
from core.sync import sync_global_state

# Imports των εργαλείων (προσθέτεις όσα φτιάχνεις)
from tools.break_even_shift_calculator import show_break_even_shift_calculator
from tools.pricing_power_radar import show_pricing_power_radar
from tools.cash_fragility_index import show_cash_fragility_index
from tools.clv_calculator import show_clv_calculator

def show_library():
    metrics = sync_global_state()
    s = st.session_state

    st.title("📚 Strategic Tool Library")
    
    # --- TOP METRIC BAR (Εδώ βλέπεις τα πάντα) ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("WACC (Cost of Capital)", f"{s.get('wacc', 0.15):.2%}")
    m2.metric("Unit Contribution", f"{metrics.get('unit_contribution', 0.0):,.2f} €")
    m3.metric("Survival BEP", f"{metrics.get('survival_bep', 0):,.0f} units")
    m4.metric("Net Margin %", f"{(metrics.get('net_profit', 0)/metrics.get('revenue', 1)*100) if metrics.get('revenue',0)>0 else 0:.1f}%")
    
    st.divider()

    if s.get('selected_tool') is None:
        # Δημιουργία 4 στηλών για τις 4 βασικές κατηγορίες
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("### 🚀 Growth")
            if st.button("⚖️ Break-even Shift", use_container_width=True):
                s.selected_tool = "break_even"
                st.rerun()
            if st.button("🎯 Pricing Power", use_container_width=True):
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
            if st.button("📉 Debt Servicing", use_container_width=True, disabled=True):
                pass

        with col3:
            st.markdown("### ⚙️ Operations")
            if st.button("📦 Inventory Opti", use_container_width=True, disabled=True):
                pass
            if st.button("🔄 CCC Analyzer", use_container_width=True, disabled=True):
                pass

        with col4:
            st.markdown("### 📉 Risk")
            if st.button("🌪️ Stress Tester", use_container_width=True, disabled=True):
                pass
            if st.button("📊 Monte Carlo", use_container_width=True, disabled=True):
                pass

    # --- TOOL ROUTER ---
    else:
        if st.button("⬅️ Back to Library Hub"):
            s.selected_tool = None
            st.rerun()
        
        st.divider()
        
        # Εδώ καλούνται οι συναρτήσεις των εργαλείων
        if s.selected_tool == "break_even":
            show_break_even_shift_calculator()
        elif s.selected_tool == "pricing":
            show_pricing_power_radar()
        elif s.selected_tool == "clv":
            show_clv_calculator()
        elif s.selected_tool == "fragility":
            show_cash_fragility_index()

    # Sidebar Navigation
    st.sidebar.divider()
    if st.sidebar.button("🚀 Return to Strategic Path", use_container_width=True):
        s.mode = "path"
        st.rerun()
