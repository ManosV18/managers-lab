import streamlit as st

# --- Import των modules σου ---
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
"from qspm_two_strategies import show_qspm_tool"


# Προαιρετικά άρθρα σαν “tools”
#from articles import show_article_clv, show_article_banks  # Υποθέτω έχεις άρθρα σε ένα module

# --- Page config ---
st.set_page_config(page_title="Managers’ Club", page_icon="📊", layout="centered")

# --- Κατηγοριοποίηση ---
tool_categories = {
    "🏠 Home": [
        ("Home", show_home),
    ],
    "💡 Getting Started": [
        ("Start Here", show_start_here),
    ],
    "📈 Break-Even & Pricing": [
        ("Break-Even Shift Analysis", show_break_even_shift_calculator),
        ("Loss Threshold Before Price Cut", show_loss_threshold_before_price_cut),
    ],
    "👥 Customer Value": [
        ("CLV Analysis", show_clv_calculator),
        ("Substitution Analysis", show_substitution_analysis),
        ("Substitutes sensitivity tool", show_substitutes_sensitivity_tool),
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

# --- Sidebar ---
st.sidebar.title("📊 Managers’ Club - Tool Categories")
selected_category = st.sidebar.selectbox("Select a Category", list(tool_categories.keys()))

tools_in_category = tool_categories[selected_category]
tool_names = [t[0] for t in tools_in_category]
selected_tool_name = st.sidebar.radio("Choose a Tool", tool_names)

# --- Show selected tool ---
for name, func in tools_in_category:
    if name == selected_tool_name:
        func()
        break

