import streamlit as st

def show_library():
    st.title("📚 Tool Library")
    
    if st.button("🔄 Refresh Global Data"):
        st.rerun()
    
    st.caption("Direct access to all analytical modules.")

    categories = {
        "📈 Pricing & Break-Even": [
            ("Break-Even Shift Analysis", "break_even_shift_calculator", "show_break_even_shift_calculator"),
            ("Loss Threshold Analysis",  "loss_threshold",              "show_loss_threshold_before_price_cut"),
            ("Pricing Power Radar",        "pricing_power_radar",          "show_pricing_power_radar"),
        ],
      
        "💰 Finance & Cash Flow": [
            ("Cash Cycle Calculator",      "cash_cycle",           "run_cash_cycle_app"),
            ("Cash Fragility Index",       "cash_fragility_index", "show_cash_fragility_index"),
            ("Receivables Strategic Control", "receivables_manager", "show_receivables_manager"),
            ("Payables Strategic Control",  "payables_manager",    "show_payables_manager"),
            ("Loan vs Leasing",            "loan_vs_leasing_calculator", "loan_vs_leasing_ui"),
            ("growth funding needed",            "growth_funding_needed_calculator", "show_growth_funding_needed"),
        ],  
        
        "👥 Customer & Strategy": [
            ("CLV Analysis",               "clv_calculator",               "show_clv_calculator"),
            ("QSPM Strategy Tool",          "qspm_two_strategies",          "show_qspm_tool"),
            ("Pricing & Elasticity Strategy", "pricing_strategy", "show_pricing_strategy_tool"), # <-- Η ΔΙΟΡΘΩΣΗ ΕΔΩ
        ],
        
        "📦 Operations": [
            ("Unit Cost Calculator",       "unit_cost_app",                "show_unit_cost_app"),
            ("Inventory Strategic Control", "inventory_manager",            "show_inventory_manager"),
        ],

        "🛡️ Risk Management": [
            ("stress test simulator",    "stress_test_simulator",            "show_stress_test_simulator"),
        ],       
    }
         
    cat_names  = list(categories.keys())
    all_tools  = {t[0]: (cat_idx, t_idx)
                  for cat_idx, (_, tools) in enumerate(categories.items())
                  for t_idx, t in enumerate(tools)}

    selected_tool = st.session_state.get("selected_tool")

    if selected_tool and selected_tool in all_tools:
        default_cat_index, default_tool_index = all_tools[selected_tool]
    else:
        default_cat_index, default_tool_index = 0, 0

    st.session_state.selected_tool = None

    selected_cat = st.selectbox(
        "Choose Category",
        cat_names,
        index=default_cat_index,
    )

    tool_list  = categories[selected_cat]
    tool_names = [t[0] for t in tool_list]

    current_cat_index = cat_names.index(selected_cat)
    if current_cat_index != default_cat_index:
        default_tool_index = 0 
    elif default_tool_index >= len(tool_names):
        default_tool_index = 0

    selected_tool_name = st.radio("Select Tool", tool_names, index=default_tool_index)

    tool_data     = next(t for t in tool_list if t[0] == selected_tool_name)
    file_name     = tool_data[1]
    function_name = tool_data[2]

    st.divider()

    try:
        module = __import__(f"tools.{file_name}", fromlist=[function_name])
        func   = getattr(module, function_name)
        func()
    except ModuleNotFoundError:
        st.error(f"❌ Module not found: `tools/{file_name}.py`")
    except AttributeError:
        st.error(f"❌ Function `{function_name}` not found in `tools/{file_name}.py`")
    except Exception as e:
        st.error(f"❌ Error while running `{function_name}`: {e}")
        st.exception(e)
