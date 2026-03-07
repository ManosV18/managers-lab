import streamlit as st

def show_sidebar():
    # Defaults
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = "home"

    with st.sidebar:
        st.title("🚀 Navigation")
        
        nav_options = {
            "🏠 Home / Global Setup": "home",
            "📊 Stage 1: Survival & BEP": "stage1",
            "🏁 Stage 2: Dashboard": "stage2",
            "💧 Stage 3: Liquidity Physics": "stage3",
            "🌪️ Stage 4: Stress Testing": "stage4",
            "⚖️ Stage 5: Strategic Decision": "stage5",
            "📚 Tools Library": "library"
        }
        
        current_step = st.session_state.flow_step
        selection = st.selectbox("Go to Module:", list(nav_options.keys()), 
                                 index=list(nav_options.values()).index(current_step) if current_step in nav_options.values() else 0)
        
        if nav_options[selection] != current_step:
            st.session_state.flow_step = nav_options[selection]
            st.rerun()
            
        st.divider()
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.session_state.flow_step = "home"
            st.rerun()
