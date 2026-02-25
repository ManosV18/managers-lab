import streamlit as st
from core.engine import refresh_global_metrics

def show_library():
    st.title("📚 Strategic Tool Library")
    
    # 1. ENFORCE REFRESH BEFORE LOADING TOOLS
    refresh_global_metrics()
    
    # 2. TOOL CATALOG
    categories = {
        "💰 Finance & Capital": [
            ("Capital Structure Control", "wacc_optimizer", "show_wacc_optimizer"),
            ("Executive Dashboard", "executive_dashboard", "show_executive_dashboard"),
            ("Cash Cycle Calculator", "cash_cycle", "run_cash_cycle_app"),
            ("Receivables Strategic Control", "receivables_analyzer", "show_receivables_analyzer_ui"), 
            ("Inventory Strategic Control", "inventory_manager", "show_inventory_manager"),
            ("Cash Fragility Index", "cash_fragility_index", "show_cash_fragility_index"),
        ],
        "📈 Strategy & Growth": [
            ("Break-Even Shift Analysis", "break_even_shift_calculator", "show_break_even_shift_calculator"),
            ("Pricing Power Radar", "pricing_power_radar", "show_pricing_power_radar"),
            ("CLV Analysis", "clv_calculator", "show_clv_calculator"),
        ]
    }

    cat_names = list(categories.keys())
    selected_cat = st.sidebar.selectbox("Select Category", cat_names)
    
    tool_list = categories[selected_cat]
    tool_names = [t[0] for t in tool_list]
    selected_tool_name = st.radio("Select Tool", tool_names, horizontal=True)

    # 3. DYNAMIC LOADING
    tool_data = next(t for t in tool_list if t[0] == selected_tool_name)
    file_name, function_name = tool_data[1], tool_data[2]

    st.divider()

    try:
        module = __import__(f"tools.{file_name}", fromlist=[function_name])
        func = getattr(module, function_name)
        func()
    except Exception as e:
        st.error(f"Execution Error: {e}")
