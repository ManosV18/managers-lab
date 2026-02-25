import streamlit as st

def show_library():
    # Έλεγχος αν έχει επιλεγεί κάποιο εργαλείο, αλλιώς εμφάνιση του Hub
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = None

    # UI του Hub (Βιβλιοθήκη)
    st.title("📚 Strategy & Operations Library")
    st.markdown("---")
    
    # Οργάνωση σε Tabs για ευκολία πλοήγησης
    tabs = st.tabs(["🎯 Strategy", "📈 Sales & Pricing", "⚙️ Operations"])

    with tabs[0]: # Strategy
        st.subheader("Strategic Decision Support")
        if st.button("🧭 QSPM Strategy Comparison", use_container_width=True):
            st.session_state.selected_tool = ("qspm_analyzer", "show_qspm_tool")
            st.rerun()

    with tabs[1]: # Sales & Pricing
        st.subheader("Revenue Optimization")
        if st.button("📉 Sales Loss Threshold Analyzer", use_container_width=True):
            st.session_state.selected_tool = ("loss_threshold", "show_loss_threshold_before_price_cut")
            st.rerun()
        
        if st.button("🎯 Pricing Strategy & Elasticity", use_container_width=True):
            st.session_state.selected_tool = ("pricing_elasticity", "show_pricing_strategy_tool")
            st.rerun()

    with tabs[2]: # Operations
        st.subheader("Working Capital Tools")
        if st.button("📊 Receivables NPV Analyzer", use_container_width=True):
            st.session_state.selected_tool = ("receivables_analyzer", "show_receivables_analyzer_ui")
            st.rerun()
            
    # Σημείωση: Ο κώδικας που φορτώνει τα εργαλεία βρίσκεται στην app.py 
    # ή στο κεντρικό UI component που καλεί την show_library()
