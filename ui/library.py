import streamlit as st

def show_library():
    st.title("📚 Tool Library")
    st.caption("Direct access to all analytical modules.")

    categories = {
        "📈 Pricing & Break-Even": [
            # (Όνομα στην οθόνη, Όνομα αρχείου .py, Όνομα συνάρτησης)
            ("Break-Even Shift Analysis", "break_even_shift_calculator", "show_break_even_shift_calculator"),
            ("Loss Threshold Analysis",  "loss_threshold",              "show_loss_threshold_before_price_cut"),
            ("Pricing Power Radar",        "pricing_power_radar",          "show_pricing_power_radar"),
        ],
      
        "💰 Finance & Cash Flow": [
            ("Cash Cycle Calculator",      "cash_cycle",                  "run_cash_cycle_app"),
            ("Cash Fragility Index",       "cash_fragility_index",        "show_cash_fragility_index"),
            ("Credit Policy Analysis",     "credit_policy_app",           "show_credit_policy_analysis"),
            ("Supplier Credit Analysis",   "supplier_credit_app",         "show_supplier_credit_analysis"),
            ("Loan vs Leasing",            "loan_vs_leasing_calculator",  "loan_vs_leasing_ui"),
        ],
        "👥 Customer & Strategy": [
            ("CLV Analysis",               "clv_calculator",              "show_clv_calculator"),
            ("QSPM Strategy Tool",         "qspm_two_strategies",         "show_qspm_tool"),
            ("Substitutes Sensitivity",    "substitution_analysis_tool",  "show_substitutes_sensitivity_tool"),
            ("Complementary Analysis",     "complementary_analysis",      "show_complementary_analysis"),
        ],
        "📦 Operations": [
            ("Unit Cost Calculator",       "unit_cost_app",               "show_unit_cost_app"),
            ("Inventory Turnover",         "inventory_turnover_calculator","show_inventory_turnover_calculator"),
            ("Credit Days Calculator",     "credit_days_calculator",      "show_credit_days_calculator"),
            ("Discount NPV Analysis",      "discount_npv_ui",             "show_discount_npv_ui"),
        ],
    }

    cat_names  = list(categories.keys())
    all_tools  = {t[0]: (cat_idx, t_idx)
                  for cat_idx, (_, tools) in enumerate(categories.items())
                  for t_idx, t in enumerate(tools)}

    # ── FIX 3: Resolve default indexes BEFORE widgets are drawn,
    #    and clear selected_tool immediately so subsequent rerenders don't re-apply it ──
    selected_tool = st.session_state.get("selected_tool")

    if selected_tool and selected_tool in all_tools:
        default_cat_index, default_tool_index = all_tools[selected_tool]
    else:
        default_cat_index, default_tool_index = 0, 0

    # Clear NOW (before widgets) so future rerenders start fresh
    st.session_state.selected_tool = None

    # ── Widget: Category ──
    selected_cat = st.selectbox(
        "Choose Category",
        cat_names,
        index=default_cat_index,
    )

    tool_list  = categories[selected_cat]
    tool_names = [t[0] for t in tool_list]

    # ── FIX 4: If the user manually picked a different category via the selectbox,
    #    the default_tool_index from the previous category is no longer valid ──
    current_cat_index = cat_names.index(selected_cat)
    if current_cat_index != default_cat_index:
        default_tool_index = 0                     # reset to first tool in new category
    elif default_tool_index >= len(tool_names):    # safety clamp (shouldn't happen, but just in case)
        default_tool_index = 0

    # ── Widget: Tool ──
    selected_tool_name = st.radio("Select Tool", tool_names, index=default_tool_index)

    tool_data     = next(t for t in tool_list if t[0] == selected_tool_name)
    file_name     = tool_data[1]
    function_name = tool_data[2]

    st.divider()

    # ── FIX 5: Show the real exception so developers can debug ──
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
        st.exception(e)   # shows full traceback in dev mode
