import streamlit as st
from core.sync import sync_global_state

# --- 1. IMPORT ALL TOOLS ---
try:
    from tools.break_even_shift_calculator import show_break_even_shift_calculator
    from tools.cash_cycle import run_cash_cycle_app
    from tools.cash_fragility_index import show_cash_fragility_index
    from tools.clv_calculator import show_clv_calculator
    from tools.executive_dashboard import show_executive_dashboard
    from tools.financial_resilience_app import show_financial_resilience
    from tools.growth_funding_needed import show_growth_funding
    from tools.inventory_manager import show_inventory_manager
    from tools.loan_vs_leasing_calculator import show_loan_leasing
    from tools.loss_threshold import show_loss_threshold
    from tools.payables_manager import show_payables_manager
    from tools.pricing_power_radar import show_pricing_power_radar
    from tools.pricing_strategy import show_pricing_strategy
    from tools.qspm_two_strategies import show_qspm
    from tools.receivables_analyzer import show_receivables_analyzer
    from tools.stress_test_simulator import show_stress_test
    from tools.unit_cost_app import show_unit_cost_analyzer
    from tools.wacc_optimizer import show_wacc_optimizer
except ImportError as e:
    st.error(f"⚠️ Σφάλμα εισαγωγής εργαλείου: {e}")

def show_library():
    metrics = sync_global_state()
    s = st.session_state

    # 2. HEADER & METRICS
    st.title("🏛️ Strategic Tool Library")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("WACC", f"{s.get('wacc', 0.15):.2%}")
    m2.metric("Unit Margin", f"{metrics.get('unit_contribution', 0.0):,.2f} €")
    m3.metric("Survival BEP", f"{metrics.get('survival_bep', 0):,.0f} u")
    m4.metric("Net Profit", f"{metrics.get('net_profit', 0):,.2f} €")
    st.divider()

    # 3. ROUTER
    if s.get('selected_tool') is None:
        # Οργάνωση σε 4 Στήλες
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown("### 🚀 Strategy & Growth")
            if st.button("📊 Executive Dashboard", use_container_width=True): s.selected_tool = "dash"
            if st.button("🎯 Pricing Strategy", use_container_width=True): s.selected_tool = "price_strat"
            if st.button("📡 Pricing Power Radar", use_container_width=True): s.selected_tool = "price_radar"
            if st.button("⚖️ BEP Shift Analysis", use_container_width=True): s.selected_tool = "bep"
            if st.button("👥 CLV Simulator", use_container_width=True): s.selected_tool = "clv"
            if st.button("📈 Growth Funding", use_container_width=True): s.selected_tool = "funding"

        with c2:
            st.markdown("### 💰 Finance & Capital")
            if st.button("📉 WACC Optimizer", use_container_width=True): s.selected_tool = "wacc"
            if st.button("🏦 Loan vs Leasing", use_container_width=True): s.selected_tool = "loan"
            if st.button("🛡️ Cash Fragility", use_container_width=True): s.selected_tool = "fragility"
            if st.button("💎 Financial Resilience", use_container_width=True): s.selected_tool = "resilience"
            if st.button("🛑 Loss Threshold", use_container_width=True): s.selected_tool = "loss"

        with c3:
            st.markdown("### ⚙️ Operations")
            if st.button("🔄 Cash Cycle (CCC)", use_container_width=True): s.selected_tool = "ccc"
            if st.button("📦 Inventory Manager", use_container_width=True): s.selected_tool = "inv"
            if st.button("💳 Receivables Analyzer", use_container_width=True): s.selected_tool = "ar"
            if st.button("💸 Payables Manager", use_container_width=True): s.selected_tool = "ap"
            if st.button("🧪 Unit Cost Analyzer", use_container_width=True): s.selected_tool = "unit"

        with c4:
            st.markdown("### 📉 Risk & Decisions")
            if st.button("🌪️ Stress Test Sim", use_container_width=True): s.selected_tool = "stress"
            if st.button("📋 QSPM Analysis", use_container_width=True): s.selected_tool = "qspm"
        
        st.rerun() if any(s.get('selected_tool') == x for x in ["dash", "bep"]) else None # Trigger rerun on click

    else:
        # 4. ΕΜΦΑΝΙΣΗ ΕΡΓΑΛΕΙΟΥ
        if st.button("⬅️ Back to Categories", type="primary"):
            s.selected_tool = None
            st.rerun()
        
        st.divider()
        t = s.selected_tool
        
        # Mapping επιλογών με συναρτήσεις
        if t == "dash": show_executive_dashboard()
        elif t == "price_strat": show_pricing_strategy()
        elif t == "price_radar": show_pricing_power_radar()
        elif t == "bep": show_break_even_shift_calculator()
        elif t == "clv": show_clv_calculator()
        elif t == "funding": show_growth_funding()
        elif t == "wacc": show_wacc_optimizer()
        elif t == "loan": show_loan_leasing()
        elif t == "fragility": show_cash_fragility_index()
        elif t == "resilience": show_financial_resilience()
        elif t == "loss": show_loss_threshold()
        elif t == "ccc": run_cash_cycle_app()
        elif t == "inv": show_inventory_manager()
        elif t == "ar": show_receivables_analyzer()
        elif t == "ap": show_payables_manager()
        elif t == "unit": show_unit_cost_analyzer()
        elif t == "stress": show_stress_test()
        elif t == "qspm": show_qspm()

    st.sidebar.divider()
    if st.sidebar.button("🚀 Exit Library"):
        s.selected_tool = None
        s.mode = "path"
        st.rerun()
