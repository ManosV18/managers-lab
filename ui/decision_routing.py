import streamlit as st
import sys
import os

# Ασφάλεια για να βρίσκει πάντα τον φάκελο core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.decision_router import DecisionRouter


def render_decision_routing(diagnostic_name: str, diagnostic_result: dict):
    """
    Renders routing buttons for relevant Decision Labs based on diagnostic output.
    """
    if diagnostic_name == "cash_fragility":
        routes = DecisionRouter.routes_for_cash_fragility(diagnostic_result)
    else:
        routes = []

    if not routes:
        return

    st.markdown("### 🎯 Recommended Decision Labs")
    
    cols = st.columns(len(routes))
    
    for idx, route in enumerate(routes):
        with cols[idx]:
            st.subheader(route["label"])
            st.write(route["description"])
            
            # Όταν πατηθεί το κουμπί, αλλάζει η σελίδα στο session_state
            if st.button(f"Go to {route['decision_area']}", key=f"route_{route['driver']}"):
                st.session_state["current_page"] = route["page"]
                st.rerun()
