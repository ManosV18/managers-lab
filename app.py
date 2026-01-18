import streamlit as st

# --- Import των modules ---
from home import show_home
from start_here import show_start_here
from break_even_shift_calculator import show_break_even_calculator
from clv_calculator import show_clv_calculator
from substitution_analysis import show_substitution_analysis
from complementary_analysis import show_complementary_analysis
from loss_threshold import show_loss_threshold_before_price_cut
from credit_policy_app import show_credit_policy_analysis
from supplier_credit_app import show_supplier_credit_analysis
from cash_cycle import run_cash_cycle_app
from loan_vs_leasing_calculator import loan_vs_leasing_ui
from gross_profit_analysis import show_gross_profit_analysis
from unit_cost_app import show_unit_cost_app
from discount_npv_ui import show_discount_npv_ui
from economic_order_quantity import show_economic_order_quantity
from credit_days_calculator import show_credit_days_calculator
from inventory_turnover_calculator import show_inventory_turnover_calculator

# --- Page config ---
st.set_page_config(page_title="Managers’ Lab", page_icon="🧪", layout="centered")

# --- Tool categories ---
tool_categories = {
    "🏠 Lab Home": [("Home", show_home)],
    "💡 Getting Started": [("Start Here", show_start_here)],
    "📈 Break-Even & Pricing": [
        ("Break-Even Calculator", show_break_even_calculator),
        ("Loss Threshold Before Price Cut", show_loss_threshold_before_price_cut),
    ],
    "👥 Customer Value": [
        ("CLV Analysis", show_clv_calculator),
        ("Substitution Analysis", show_substitution_analysis),
        ("Complementary Product Analysis", show_complementary_analysis),
    ],
    "💰 Finance & Cash Flow": [
        ("Cash Cycle Calculator", run_cash_cycle_app),
        ("Credit Policy Analysis", show_credit_policy_analysis),
        ("Supplier Payment Analysis", show_supplier_credit_analysis),
        ("Loan vs Leasing Analysis", loan_vs_leasing_ui),
    ],
    "📊 Cost & Profit": [
        ("Gross Profit Estimation", show_gross_profit_analysis),
        ("Unit Cost Calculator", show_unit_cost_app),
        ("Discount NPV Analysis", show_discount_npv_ui),
        ("Economic Order Quantity (EOQ)", show_economic_order_quantity),
    ],
    "📦 Inventory & Operations": [
        ("Credit Days Calculator", show_credit_days_calculator),
        ("Inventory Turnover Analysis", show_inventory_turnover_calculator),
    ],
}

# --- Sidebar ---
st.sidebar.title("🧪 Managers’ Lab - Tool Categories")
selected_category = st.sidebar.selectbox("Select a Category", list(tool_categories.keys()))

tools_in_category = tool_categories[selected_category]
tool_names = [t[0] for t in tools_in_category]
selected_tool_name = st.sidebar.radio("Choose a Tool", tool_names)

# --- Show selected tool ---
for name, func in tools_in_category:
    if name == selected_tool_name:
        func()
        break
