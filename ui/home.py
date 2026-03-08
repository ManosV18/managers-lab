import streamlit as st
from core.sync import sync_global_state

def run_home():
    st.title("🛡️ Strategic Decision Room")
    st.markdown("---")

    # Δημιουργούμε δύο κύριες κολώνες στην κεντρική οθόνη
    col_input, col_nav = st.columns([0.6, 0.4], gap="large")

    with col_input:
        st.subheader("⚙️ Global Parameters")
        st.info("Εδώ ορίζεις τη βάση της επιχείρησής σου.")
        
        # Ομαδοποίηση παραμέτρων σε Expanders για να είναι μαζεμένα
        with st.expander("1. Core Business Units", expanded=True):
            st.session_state.price = st.number_input("Unit Price (€)", value=float(st.session_state.get('price', 100.0)))
            st.session_state.variable_cost = st.number_input("Variable Cost (€)", value=float(st.session_state.get('variable_cost', 60.0)))
            st.session_state.volume = st.number_input("Annual Volume", value=int(st.session_state.get('volume', 1000)))
            st.session_state.fixed_cost = st.number_input("Annual Fixed Costs", value=float(st.session_state.get('fixed_cost', 20000.0)))

        with st.expander("2. Financials & Liquidity"):
            st.session_state.opening_cash = st.number_input("Opening Cash (€)", value=float(st.session_state.get('opening_cash', 10000.0)))
            st.session_state.annual_debt_service = st.number_input("Annual Debt Service (€)", value=float(st.session_state.get('annual_debt_service', 0.0)))
            tax_p = st.number_input("Tax Rate (%)", value=float(st.session_state.get('tax_rate', 0.22)) * 100)
            st.session_state.tax_rate = tax_p / 100

        with st.expander("3. Operating Cycle (Days)"):
            st.session_state.ar_days = st.number_input("AR Days (Collection)", value=float(st.session_state.get('ar_days', 45.0)))
            st.session_state.inventory_days = st.number_input("Inventory Days", value=float(st.session_state.get('inventory_days', 60.0)))
            st.session_state.ap_days = st.number_input("AP Days (Payment)", value=float(st.session_state.get('ap_days', 30.0)))

        if st.button("🔄 Reset All Data", type="secondary"):
            st.session_state.clear()
            st.rerun()

    with col_nav:
        st.subheader("📊 Analysis Hub")
        st.write("Επίλεξε τι θέλεις να αναλύσεις:")
        
        # Dropdown Navigation
        nav_options = {
            "Select Analysis...": "home",
            "📊 Stage 1: Survival & BEP": "stage1",
            "🏁 Stage 2: Dashboard": "stage2",
            "💧 Stage 3: Liquidity Physics": "stage3",
            "🌪️ Stage 4: Stress Testing": "stage4",
            "⚖️ Stage 5: Strategic Decision": "stage5",
            "📚 Full Tools Library": "library"
        }
        
        selection = st.selectbox("Μετάβαση σε:", list(nav_options.keys()))
        
        if nav_options[selection] != "home":
            # Έλεγχος αν υπάρχουν τα βασικά νούμερα πριν φύγει
            if st.session_state.get('price', 0) > 0:
                st.session_state.flow_step = nav_options[selection]
                st.rerun()
            else:
                st.error("⚠️ Πρέπει να συμπληρώσεις τουλάχιστον την Τιμή στο Stage 0.")

        st.divider()
        
        # QUICK LINKS ΣΤΑ ΕΡΓΑΛΕΙΑ (Απευθείας πρόσβαση)
        st.caption("Quick Tools Access")
        tool_cols = st.columns(1)
        if st.button("🎯 Break-Even Shift Calculator"):
            st.session_state.selected_tool = ("break_even_shift_calculator", "show_break_even_shift_calculator")
            st.session_state.flow_step = "library"
            st.rerun()
        if st.button("🚨 Cash Fragility Index"):
            st.session_state.selected_tool = ("cash_fragility_index", "show_cash_fragility_index")
            st.session_state.flow_step = "library"
            st.rerun()

    # ΤΟ "ZERO-BASE" ΣΕΝΑΡΙΟ ΠΟΥ ΖΗΤΗΣΕΣ
    # Αν ο χρήστης επιλέξει να "κλειδώσει" ένα σενάριο, μηδενίζουμε τα πάντα και κρατάμε μόνο τα νέα.
    st.sidebar.markdown("### 🛠️ Scenario Mode")
    if st.sidebar.button("🆕 Start New Scenario (Zero-Base)"):
        # Κρατάμε μόνο το navigation, σβήνουμε τα δεδομένα
        current_step = st.session_state.flow_step
        st.session_state.clear()
        st.session_state.flow_step = current_step
        st.success("Όλες οι τιμές μηδενίστηκαν. Είσαι σε Zero-Base mode.")
        st.rerun()
