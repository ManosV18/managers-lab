import streamlit as st
import importlib.util
import os
import sys
from core.sync import lock_baseline

# --- INTERNAL TOOL: PAYABLES MANAGER ---
def show_payables_manager_internal():
    st.header("🤝 Payables Manager: Supplier Credit Analysis")
    st.info("Evaluate cash discounts vs. supplier credit terms (365-day basis).")
    
    col1, col2 = st.columns(2)
    with col1:
        cred_days = st.number_input("Supplier Credit Period (Days)", value=60, key="int_cred_days")
        disc_prc = st.number_input("Cash Discount Offered (%)", value=2.0, key="int_disc_prc") / 100
        cash_take = st.number_input("% of Purchases for Discount", value=50.0, key="int_cash_prc") / 100
    with col2:
        annual_purch = st.number_input("Annual Purchase Volume (€)", value=1000000, key="int_ann_purch")
        wacc = st.number_input("Cost of Capital / Interest (%)", value=10.0, key="int_wacc") / 100

    disc_gain = annual_purch * disc_prc * cash_take
    opp_cost = (annual_purch * cash_take * (cred_days / 365)) * wacc
    net_benefit = disc_gain - opp_cost

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Discount Gain", f"€{disc_gain:,.0f}")
    c2.metric("Credit Opp. Cost", f"-€{opp_cost:,.0f}")
    c3.metric("Net Benefit", f"€{net_benefit:,.0f}", delta=f"{net_benefit:,.0f}")

# -------------------
# HOME FUNCTION
# -------------------
def run_home():
    s = st.session_state

    # HERO
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <h1 style="font-size:48px;">🛡️ Strategic Decision Room</h1>
            <h2 style="font-size:28px; font-weight:600; margin-top:10px;">
                See the real impact on your cash and survival before committing
            </h2>
            <h3 style="font-size:20px; font-weight:normal; color:#555; margin-top:10px;">
                Change prices, costs, or volumes and instantly see the effect on profit, break-even, and cash survival.
            </h3>
            <p style="font-size:18px; color:#777; margin-top:15px;">
                Know the outcome before you spend a euro.
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    st.divider()
    left, right = st.columns([1,1])

    # =================================================
    # LEFT: Business Setup
    # =================================================
    with left:
        st.header("🏗️ Business Setup")
        c1, c2 = st.columns(2)
        s.price = c1.number_input("Unit Price (€)", value=float(s.get("price",100.0)))
        s.volume = c2.number_input("Annual Volume", value=int(s.get("volume",1000)))

        st.subheader("💰 Cost Structure")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Variable Costs**")
            v1 = st.number_input("Materials (€/unit)", value=float(s.get("in_mat",30.0)), key="in_mat")
            v2 = st.number_input("Labor (€/unit)", value=float(s.get("in_lab",15.0)), key="in_lab")
            s.variable_cost = v1 + v2
            st.info(f"Total Variable Cost: €{s.variable_cost:,.2f}")
        with col_b:
            st.markdown("**Fixed Costs (Annual)**")
            f1 = st.number_input("Rent & Utilities", value=float(s.get("in_rent",12000.0)), key="in_rent")
            f2 = st.number_input("Salaries & Admin", value=float(s.get("in_sal",8000.0)), key="in_sal")
            s.fixed_cost = f1 + f2
            st.info(f"Total Fixed Cost: €{s.fixed_cost:,.2f}")

        st.divider()
        with st.expander("⚙️ Advanced Financial Settings"):
            c1, c2, c3 = st.columns(3)
            c1.number_input("Cost of Capital (WACC %)", value=float(s.get('wacc',0.15)), key='wacc', format="%.4f")
            c2.number_input("Tax Rate (0.xx)", value=float(s.get('tax_rate',0.22)), key='tax_rate', format="%.2f")
            c3.number_input("Annual Debt Service (€)", value=float(s.get('annual_debt_service',0.0)), key='annual_debt_service')

        if st.button("🔒 Lock Baseline & Initialize", use_container_width=True):
            if s.price > s.variable_cost:
                lock_baseline()
                st.success("✅ Baseline Locked")
            else:
                st.error("Unit price must be higher than variable cost.")

    # =================================================
    # RIGHT: Tools Categories
    # =================================================
    with right:
        st.header("🧠 Business Tools")
        st.markdown("Select a category to explore the tools:")

        tools_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "core",
    "tools"
)
        
        # ---------- 1️⃣ Strategy & Pricing ----------
        with st.expander("🚀 Strategy & Pricing", expanded=False):
            st.markdown("Analyze pricing, profitability, and growth strategy impacts.")
            # List of (button_label, module, func)
            buttons = [
                ("🎯 Pricing Strategy & Elasticity", "pricing_strategy", "show_pricing_strategy_tool"),
                ("📡 Pricing Radar Matrix", "pricing_radar", "show_pricing_radar"),
                ("📉 Loss Threshold (Price Cut)", "loss_threshold", "show_loss_threshold_before_price_cut"),
                ("⚖️ BEP Shift Analysis", "break_even_shift_calculator", "show_break_even_shift_calculator"),
                ("🧭 QSPM Strategy Matrix", "qspm_analyzer", "show_qspm_tool"),
                ("👥 CLV Simulator", "clv_calculator", "show_clv_calculator")
            ]
            for label, mod, func in buttons:
                if st.button(label, key=label):
                    if mod == "INTERNAL":
                        globals()[func]()
                    else:
                        try:
                            file_path = os.path.join(tools_dir, f"{mod}.py")
                            spec = importlib.util.spec_from_file_location(mod, file_path)
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[mod] = module
                            spec.loader.exec_module(module)
                            getattr(module, func)()
                        except Exception as e:
                            st.error(f"Error loading '{mod}': {e}")

        # ---------- 2️⃣ Capital & Finance ----------
        with st.expander("💰 Capital & Finance", expanded=False):
            st.markdown("Manage cash, WACC, funding, and financial optimization.")
            buttons = [
                ("📉 WACC Optimizer", "wacc_optimizer", "show_wacc_optimizer"),
                ("📈 Growth Funding (AFN)", "growth_funding", "show_growth_funding_needed"),
                ("⚖️ Loan vs Leasing Analyzer", "loan_vs_leasing", "loan_vs_leasing_ui")
            ]
            for label, mod, func in buttons:
                if st.button(label, key=label):
                    try:
                        file_path = os.path.join(tools_dir, f"{mod}.py")
                        spec = importlib.util.spec_from_file_location(mod, file_path)
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[mod] = module
                        spec.loader.exec_module(module)
                        getattr(module, func)()
                    except Exception as e:
                        st.error(f"Error loading '{mod}': {e}")

        # ---------- 3️⃣ Operations & CCC ----------
        with st.expander("⚙️ Operations & CCC", expanded=False):
            st.markdown("Analyze costs, operational efficiency, inventory, payables, and CCC.")
            buttons = [
                ("🔄 Cash Conversion Cycle (CCC)", "cash_cycle", "run_cash_cycle_app"),
                ("📊 Receivables Analyzer (NPV)", "receivables_analyzer", "show_receivables_analyzer_ui"),
                ("📦 Inventory Optimizer (EOQ)", "inventory_manager", "show_inventory_manager"),
                ("🤝 Payables Manager", "INTERNAL", "show_payables_manager_internal"),
                ("🔢 Unit Cost Analyzer", "unit_cost_analyzer", "show_unit_cost_app")
            ]
            for label, mod, func in buttons:
                if st.button(label, key=label):
                    if mod == "INTERNAL":
                        globals()[func]()
                    else:
                        try:
                            file_path = os.path.join(tools_dir, f"{mod}.py")
                            spec = importlib.util.spec_from_file_location(mod, file_path)
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[mod] = module
                            spec.loader.exec_module(module)
                            getattr(module, func)()
                        except Exception as e:
                            st.error(f"Error loading '{mod}': {e}")

        # ---------- 4️⃣ Risk & Control ----------
        with st.expander("🛡️ Risk & Control", expanded=False):
            st.markdown("Simulate resilience, stress-tests, and monitor executive risks.")
            buttons = [
                ("🏁 Executive Command Center", "executive_dashboard", "show_executive_dashboard"),
                ("🚨 Cash Fragility Index", "cash_fragility_index", "show_cash_fragility_index"),
                ("🛡️ Resilience & Shock Map", "financial_resilience_app", "show_resilience_map"),
                ("📉 Stress Test Simulator", "stress_test_simulator", "show_stress_test_tool")
            ]
            for label, mod, func in buttons:
                if st.button(label, key=label):
                    try:
                        file_path = os.path.join(tools_dir, f"{mod}.py")
                        spec = importlib.util.spec_from_file_location(mod, file_path)
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[mod] = module
                        spec.loader.exec_module(module)
                        getattr(module, func)()
                    except Exception as e:
                        st.error(f"Error loading '{mod}': {e}")
