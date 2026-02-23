def initialize_system_state():
    """Single Source of Truth for the entire system"""

    # UI State
    defaults_ui = {
        "mode": "home",
        "flow_step": 0,
        "baseline_locked": False,
        "selected_tool": None
    }

    # 1️⃣ Revenue Engine
    defaults_revenue = {
        "price": 30.0,
        "volume": 10000
    }

    # 2️⃣ Cost Structure
    defaults_cost = {
        "variable_cost": 15.0,
        "fixed_cost": 50000.0
    }

    # 3️⃣ Working Capital
    defaults_cash = {
        "ar_days": 45,
        "inventory_days": 60,
        "payables_days": 30,
        "ccc": 0,
        "working_capital_req": 0.0,
        "liquidity_drain_annual": 0.0
    }

    # 4️⃣ Capital & Financing (ΔΙΑΧΩΡΙΣΜΟΣ RATE vs WACC)
    defaults_capital = {
        "debt": 20000.0,
        "interest_rate": 0.05,        # Κόστος Δανεισμού (π.χ. Τράπεζα)
        "wacc": 0.12,                 # Συνολικό Κόστος Κεφαλαίου (για NPV/CLV)
        "annual_loan_payment": 12000.0
    }

    # 5️⃣ Customer Durability
    defaults_customer = {
        "retention_rate": 0.85,
        "cac": 150.0,
        "purch_per_year": 4.0
    }

    all_defaults = {
        **defaults_ui,
        **defaults_revenue,
        **defaults_cost,
        **defaults_cash,
        **defaults_capital,
        **defaults_customer
    }

    for key, value in all_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
