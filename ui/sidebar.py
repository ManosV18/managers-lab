import streamlit as st

def show_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='color:#1E3A8A;'>🧠 Managers Lab</h2>", unsafe_allow_html=True)
        st.divider()
        
        # Επιστροφή στην κεντρική οθόνη
        if st.button("🏠 Control Tower", use_container_width=True):
            st.session_state.flow_step = "home"
            st.session_state.selected_tool = None
            st.rerun()

        # --- ΠΡΟΣΘΗΚΗ: ΚΟΥΜΠΙ ΓΙΑ ΤΟ ABOUT ---
        if st.button("🧪 System Architecture", use_container_width=True):
            st.session_state.flow_step = "about" # Αυτό θα καλεί τη show_about() στο main
            st.rerun()
            
        st.divider()
        
        # Κατάσταση Συστήματος
        if st.session_state.get('baseline_locked', False):
            st.success("✅ Baseline: LOCKED")
        else:
            st.warning("🔓 Baseline: OPEN")

        if st.button("🔄 Global Reset", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
