import streamlit as st
from core.sync import lock_baseline

def run_home():

    s = st.session_state

    # --- HERO SECTION ---
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
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ------------------------------------------------
    # TWO COLUMN LAYOUT
    # ------------------------------------------------
    left, right = st.columns([1,1])

    # =================================================
    # LEFT COLUMN - Business Setup
    # =================================================
    with left:

        st.header("🏗️ Business Setup")

        st.subheader("📊 Sales Parameters")
        c1, c2 = st.columns(2)

        s.price = c1.number_input(
            "Unit Price (€)",
            value=float(s.get("price",100.0))
        )

        s.volume = c2.number_input(
            "Annual Volume",
            value=int(s.get("volume",1000))
        )

        st.subheader("💰 Cost Structure")
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Variable Costs**")
            v1 = st.number_input(
                "Materials (€/unit)",
                value=float(s.get("in_mat",30.0)),
                key="in_mat"
            )
            v2 = st.number_input(
                "Labor (€/unit)",
                value=float(s.get("in_lab",15.0)),
                key="in_lab"
            )
            s.variable_cost = v1 + v2
            st.info(f"Total Variable Cost: €{s.variable_cost:,.2f}")

        with col_b:
            st.markdown("**Fixed Costs (Annual)**")
            f1 = st.number_input(
                "Rent & Utilities",
                value=float(s.get("in_rent",12000.0)),
                key="in_rent"
            )
            f2 = st.number_input(
                "Salaries & Admin",
                value=float(s.get("in_sal",8000.0)),
                key="in_sal"
            )
            s.fixed_cost = f1 + f2
            st.info(f"Total Fixed Cost: €{s.fixed_cost:,.2f}")

        st.divider()

        # ------------------------------------------------
        # ADVANCED FINANCIAL SETTINGS (Hidden)
        # ------------------------------------------------
        with st.expander("⚙️ Advanced Financial Settings"):

            c1, c2, c3 = st.columns(3)
            c1.number_input("Cost of Capital (WACC %)", value=float(s.get('wacc', 0.15)), key='wacc', format="%.4f")
            c2.number_input("Tax Rate (0.xx)", value=float(s.get('tax_rate', 0.22)), key='tax_rate', format="%.2f")
            c3.number_input("Annual Debt Service (€)", value=float(s.get('annual_debt_service', 0.0)), key='annual_debt_service')

            st.markdown("**Working Capital Assumptions (Days)**")
            d1, d2, d3 = st.columns(3)
            d1.number_input("AR Days", value=int(s.get('ar_days', 45)), key='ar_days')
            d2.number_input("Inventory Days", value=int(s.get('inventory_days', 60)), key='inventory_days')
            d3.number_input("AP Days", value=int(s.get('ap_days', 30)), key='ap_days')

        st.divider()

        # LOCK LOGIC
        if st.button("🔒 Lock Baseline & Initialize", use_container_width=True):
            if s.price > s.variable_cost:
                lock_baseline()
                s.flow_step = "stage1"
                st.rerun()
            else:
                st.error("Unit price must be higher than variable cost.")

    # =================================================
    # RIGHT COLUMN - Business Questions / Tools
    # =================================================
    with right:

        st.header("🧠 Business Questions")
        st.markdown("Select a business area to explore the available tools.")

        # ------------------------------------------------
        # CASH & LIQUIDITY
        # ------------------------------------------------
        with st.expander("💰 Cash & Liquidity", expanded=False):
            st.markdown("Understand how money moves through your business and how long you can survive during slow periods.")
            if st.button("Cash Survival Tool", key="cash_survival"):
                st.session_state.flow_step = "stage3"
                st.rerun()
            st.caption("Estimate how many days your business can operate without new revenue.")

        # ------------------------------------------------
        # PRICING & PROFIT
        # ------------------------------------------------
        with st.expander("💵 Pricing & Profit", expanded=False):
            st.markdown("Analyze how pricing and sales affect profitability and financial sustainability.")
            if st.button("Break-Even / Profit Analysis", key="break_even"):
                st.session_state.flow_step = "stage1"
                st.rerun()
            st.caption("Calculate the sales level required to cover all business costs.")

            if st.button("Profit Check Tool", key="profit_check"):
                st.session_state.flow_step = "stage2"
                st.rerun()
            st.caption("Evaluate profitability at a specific sales level.")

            if st.button("Required Price Estimator", key="price_required"):
                st.session_state.flow_step = "stage1"
                st.rerun()
            st.caption("Estimate the minimum price required to sustain the business.")

        # ------------------------------------------------
        # COSTS & OPERATIONS
        # ------------------------------------------------
        with st.expander("📦 Costs & Operations", expanded=False):
            st.markdown("Understand production costs and operational efficiency.")
            if st.button("Open cost analysis tools", key="cost_tools"):
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("Analyze the real cost behind your operations.")

        # ------------------------------------------------
        # GROWTH & INVESTMENT
        # ------------------------------------------------
        with st.expander("📈 Growth & Investment", expanded=False):
            st.markdown("Evaluate expansion decisions and funding requirements.")
            if st.button("Open growth planning tools", key="growth_tools"):
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("Estimate funding needs and investment options.")

        # ------------------------------------------------
        # STRATEGY & RISK
        # ------------------------------------------------
        with st.expander("🧠 Strategy & Risk", expanded=False):
            st.markdown("Simulate strategic decisions and stress-test your business.")
            if st.button("Open strategy simulation tools", key="strategy_tools"):
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("Compare strategic scenarios and evaluate business resilience.")

        # ------------------------------------------------
        # FULL TOOL LIBRARY
        # ------------------------------------------------
        with st.expander("🧰 Full Tools Library", expanded=False):
            st.markdown("Access the full set of advanced financial and strategic tools.")
            if st.button("Open tools library", key="tool_library"):
                st.session_state.flow_step = "library"
                st.rerun()
            st.caption("Browse all available analysis tools.")
