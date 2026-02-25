import streamlit as st

def show_library():
    st.title("📚 Strategic Tool Library")
    
    # 1. ΔΥΝΑΜΙΚΟΣ ΚΑΤΑΛΟΓΟΣ ΕΡΓΑΛΕΙΩΝ (Dictionary-based)
    categories = {
        "📈 Pricing & Break-Even": [
            ("Break-Even Shift Analysis", "break_even_shift_calculator", "show_break_even_shift_calculator"),
            ("Loss Threshold Analysis", "loss_threshold", "show_loss_threshold_before_price_cut"),
            ("Pricing Power Radar", "pricing_power_radar", "show_pricing_power_radar"),
        ],
        "💰 Finance & Cash Flow": [
            ("Cash Cycle Calculator", "cash_cycle", "run_cash_cycle_app"),
            ("Receivables Strategic Control", "receivables_manager", "show_receivables_manager"),
            ("Inventory Strategic Control", "inventory_manager", "show_inventory_manager"),
            ("Loan vs Leasing Analysis", "loan_vs_leasing_calculator", "loan_vs_leasing_ui"),
            # Τα παρακάτω χρειάζονται τα αντίστοιχα .py αρχεία για να μην βγάλουν Error
            ("Cash Fragility Index", "cash_fragility_index", "show_cash_fragility_index"),
            ("Payables Strategic Control", "payables_manager", "show_payables_manager"),
        ],  
        "👥 Customer & Strategy": [
            ("CLV Analysis", "clv_calculator", "show_clv_calculator"),
            ("QSPM Strategy Tool", "qspm_two_strategies", "show_qspm_tool"),
        ],
        "📦 Operations": [
            ("Unit Cost Calculator", "unit_cost_app", "show_unit_cost_app"),
        ],
        "🛡️ Risk Management": [
            ("Stress Test Simulator", "stress_test_simulator", "show_stress_test_simulator"),
        ],       
    }

    # 2. UI ΓΙΑ ΕΠΙΛΟΓΗ ΚΑΤΗΓΟΡΙΑΣ & ΕΡΓΑΛΕΙΟΥ
    cat_names = list(categories.keys())
    
    # Διαχείριση Session State για να θυμάται πού ήμασταν
    if "lib_cat" not in st.session_state:
        st.session_state.lib_cat = cat_names[0]

    c1, c2 = st.columns([1, 2])
    
    selected_cat = c1.selectbox("Category", cat_names, key="lib_cat")
    
    tool_list = categories[selected_cat]
    tool_names = [t[0] for t in tool_list]
    
    selected_tool_name = c2.radio("Select Tool", tool_names, horizontal=True)

    # 3. DYNAMIC LOADING LOGIC
    tool_data = next(t for t in tool_list if t[0] == selected_tool_name)
    file_name = tool_data[1]
    function_name = tool_data[2]

    st.divider()

    # ΕΚΤΕΛΕΣΗ ΤΟΥ ΕΡΓΑΛΕΙΟΥ
    try:
        # Dynamic import
        module = __import__(f"tools.{file_name}", fromlist=[function_name])
        func = getattr(module, function_name)
        func()
    except ModuleNotFoundError:
        st.error(f"❌ Το αρχείο `tools/{file_name}.py` δεν βρέθηκε.")
    except AttributeError:
        st.error(f"❌ Η συνάρτηση `{function_name}` δεν υπάρχει στο `tools/{file_name}.py`.")
    except Exception as e:
        st.error(f"❌ Σφάλμα κατά την εκτέλεση: {e}")
        st.exception(e)

    # 4. GLOBAL ACTION
    st.sidebar.divider()
    if st.sidebar.button("🔄 Clear Library Cache"):
        st.rerun()
