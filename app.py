import streamlit as st

# ----------------------------------------
# Imports of all tools
# ----------------------------------------
from home import show_home
from start_here import show_start_here
from break_even_shift_calculator import show_break_even_shift_calculator
from clv_calculator import show_clv_calculator
from substitution_analysis import show_substitution_analysis
from substitutes_sensitivity_tool import show_substitutes_sensitivity_tool
from complementary_analysis import show_complementary_analysis
from loss_threshold import show_loss_threshold_before_price_cut
from credit_policy_app import show_credit_policy_analysis
from supplier_credit_app import show_supplier_credit_analysis
from cash_cycle import run_cash_cycle_app
from loan_vs_leasing_calculator import loan_vs_leasing_ui
from unit_cost_app import show_unit_cost_app
from discount_npv_ui import show_discount_npv_ui
from credit_days_calculator import show_credit_days_calculator
from inventory_turnover_calculator import show_inventory_turnover_calculator
from qspm_two_strategies import show_qspm_tool

# ----------------------------------------
# Page config
# ----------------------------------------
st.set_page_config(
    page_title="Managers’ Lab",
    page_icon="🧪",
    layout="centered"
)

# ----------------------------------------
# Tool registry
# ----------------------------------------
tool_categories = {
    "🏠 Home": [("Home", show_home)],
    "💡 Getting Started": [("Start Here", show_start_here)],
    "📈 Break-Even & Pricing": [
        ("Break-Even Shift Analysis", show_break_even_shift_calculator),
        ("Loss Threshold Before Price Cut", show_loss_threshold_before_price_cut),
    ],
    "👥 Customer Value": [
        ("CLV Analysis", show_clv_calculator),
        ("Substitution Analysis", show_substitution_analysis),
        ("Substitutes Sensitivity Tool", show_substitutes_sensitivity_tool),
        ("Complementary Product Analysis", show_complementary_analysis),
    ],
    "💰 Finance & Cash Flow": [
        ("Cash Cycle Calculator", run_cash_cycle_app),
        ("Credit Policy Analysis", show_credit_policy_analysis),
        ("Supplier Payment Analysis", show_supplier_credit_analysis),
        ("Loan vs Leasing Analysis", loan_vs_leasing_ui),
    ],
    "📊 Cost & Profit": [
        ("Unit Cost Calculator", show_unit_cost_app),
        ("Discount NPV Analysis", show_discount_npv_ui),
    ],
    "📦 Inventory & Operations": [
        ("Credit Days Calculator", show_credit_days_calculator),
        ("Inventory Turnover Analysis", show_inventory_turnover_calculator),
    ],
    "🧭 Strategy & Decision": [
        ("QSPM – Strategy Comparison", show_qspm_tool),
    ],
}

# ----------------------------------------
# Session state initialization
# ----------------------------------------
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "🏠 Home"

if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = "Home"

# ----------------------------------------
# Sidebar
# ----------------------------------------
st.sidebar.title("🧪 Managers’ Lab - Tool Categories")

category_keys = list(tool_categories.keys())
selected_category = st.sidebar.selectbox(
    "Select category",
    category_keys,
    index=category_keys.index(st.session_state.selected_category)
)

# Reset tool to first in category if category changed
if selected_category != st.session_state.selected_category:
    st.session_state.selected_category = selected_category
    st.session_state.selected_tool = tool_categories[selected_category][0][0]

tools_in_category = tool_categories[st.session_state.selected_category]
tool_names = [t[0] for t in tools_in_category]

selected_tool = st.sidebar.radio(
    "Choose tool",
    tool_names,
    index=tool_names.index(st.session_state.selected_tool)
)

st.session_state.selected_tool = selected_tool

# ----------------------------------------
# Back to Home button
# ----------------------------------------
if not (st.session_state.selected_category == "🏠 Home" and st.session_state.selected_tool == "Home"):
    if st.button("← Back to Lab"):
        st.session_state.selected_category = "🏠 Home"
        st.session_state.selected_tool = "Home"
        st.rerun()

# ----------------------------------------
# Render selected tool
# ----------------------------------------
for name, func in tools_in_category:
    if name == st.session_state.selected_tool:
        func()
        break

# ----------------------------------------
# Footer
# ----------------------------------------
st.divider()
st.caption(
    "Managers’ Lab · Decision laboratory\n"
    "Exploration is open. Commitment may not be.\n"
)
