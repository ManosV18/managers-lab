import streamlit as st

def show_about():
    # Ο τίτλος που ζήτησες
    st.title("🧪 System Architecture")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Framework Overview")
        st.write("""
        **Managers' Lab** is a structural decision system designed to model 
        the economic mechanics of a business before strategy is applied.
        
        It focuses on measurable fundamentals:
        revenue structure, cost behavior, cash timing, capital pressure, 
        and durability over a 365-day operating cycle.
        
        All analytical modules project stress onto the same shared baseline,
        ensuring consistency across simulations.
        """)
        
        st.subheader("What This System Is Not")
        st.write("""
        - Not accounting software  
        - Not KPI decoration  
        - Not optimism-based forecasting  

        The objective is structural clarity — not presentation.
        """)

    with col2:
        st.subheader("Contact")
        st.write("For methodology questions or technical feedback:")
        
        st.markdown("📧 **Email:** manosv@gmail.com")
        st.markdown("🌐 **Medium:** [https://medium.com/@ManosV_18]")
        
        st.divider()
        st.caption("Version: 2.0.1 (Stable Build)")
        st.caption("Architecture: Shared Core System")

    # Κουμπί επιστροφής με σωστό indentation
    st.divider()
    if st.button("⬅️ Back to Strategic Decision Room", use_container_width=True):
        st.session_state.flow_step = "home"
        st.rerun()
