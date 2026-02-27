import streamlit as st

# Import all the tools we finalized today
from tools.receivables_analyzer import show_receivables_analyzer_ui
from tools.inventory_manager import show_inventory_manager
from tools.resilience_map import show_resilience_map
from tools.payables_manager import show_payables_manager
from tools.cash_fragility import show_cash_fragility_index
from tools.clv_calculator import show_clv_calculator
from tools.unit_cost_analyzer import show_unit_cost_app

# Define the library structure
TOOLS_LIBRARY = {
    "Operations & CCC": {
        "Strategic Receivables (NPV)": {
            "function": show_receivables_analyzer_ui,
            "icon": "📊",
            "description": "Optimize credit policy using NPV logic."
        },
        "Inventory Optimizer (EOQ)": {
            "function": show_inventory_manager,
            "icon": "📦",
            "description": "Find the perfect balance between ordering and holding costs."
        },
        "Payables Manager": {
            "function": show_payables_manager,
            "icon": "🤝",
            "description": "Analyze Cash Discounts vs. Supplier Credit value."
        },
        "Unit Cost Deconstruction": {
            "function": show_unit_cost_app,
            "icon": "⚙️",
            "description": "Break down and sync variable cost components."
        }
    },
    "Risk & Survival": {
        "Resilience & Shock Map": {
            "function": show_resilience_map,
            "icon": "🛡️",
            "description": "Map structural integrity using ROA vs Liquidity."
        },
        "Cash Fragility Index": {
            "function": show_cash_fragility_index,
            "icon": "📉",
            "description": "Compare your Cash Runway against your CCC cycle."
        }
    },
    "Strategy & Growth": {
        "Executive CLV Simulator": {
            "function": show_clv_calculator,
            "icon": "👥",
            "description": "Calculate Risk-Adjusted Customer Lifetime Value (NPV)."
        }
    }
}

def render_library_hub():
    st.title("🏛️ Strategic Tools Library")
    st.markdown("Select an advanced analytical module to stress-test your baseline.")
    st.divider()

    # Create columns for the main categories
    cols = st.columns(len(TOOLS_LIBRARY))
    
    for i, (category, tools) in enumerate(TOOLS_LIBRARY.items()):
        with cols[i]:
            st.subheader(category)
            for tool_name, info in tools.items():
                if st.button(f"{info['icon']} {tool_name}", 
                             key=f"btn_{tool_name}", 
                             use_container_width=True,
                             help=info['description']):
                    st.session_state.selected_tool = tool_name
                    st.rerun()

    st.divider()
    st.caption("All tools are hard-linked to the Global Baseline (Stage 0).")
