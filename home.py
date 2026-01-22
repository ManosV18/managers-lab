import streamlit as st

def show_home():

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------

    st.title("🧪 Managers’ Lab")

    st.markdown("""
    A decision laboratory for managers.  

    Not a dashboard. Not a reporting or forecasting tool.  

    Managers’ Lab exists to test what must be true for a decision to work —  
    and what breaks when it doesn’t.  

    The tools are already built. Judgment is yours.
    """)

    st.divider()

    st.markdown("### Choose the type of decision you are trying to make.")

    # -------------------------------------------------
    # DECISION GROUPS
    # -------------------------------------------------

    st.subheader("Pricing & Viability")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Break-Even Shift Analysis"):
            st.session_state.selected_category = "📈 Break-Even & Pricing"
            st.session_state.selected_tool = "Break-Even Shift Analysis"

    with col2:
        if st.button("Loss Threshold Before Price Cut"):
            st.session_state.selected_category = "📈 Break-Even & Pricing"
            st.session_state.selected_tool = "Loss Threshold Before Price Cut"

    st.subheader("Customer Economics")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("CLV Analysis"):
            st.session_state.selected_category = "👥 Customer Value"
            st.session_state.selected_tool = "CLV Analysis"

    with col2:
        if st.button("Substitution Analysis"):
            st.session_state.selected_category = "👥 Customer Value"
            st.session_state.selected_tool = "Substitution Analysis"

    with col3:
        if st.button("Complementary Product Analysis"):
            st.session_state.selected_category = "👥 Customer Value"
            st.session_state.selected_tool = "Complementary Product Analysis"

    st.subheader("Cash Flow & Financing")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Cash Cycle Calculator"):
            st.session_state.selected_category = "💰 Finance & Cash Flow"
            st.session_state.selected_tool = "Cash Cycle Calculator"

    with col2:
        if st.button("Credit Policy Analysis"):
            st.session_state.selected_category = "💰 Finance & Cash Flow"
            st.session_state.selected_tool = "Credit Policy Analysis"

    with col3:
        if st.button("Supplier Payment Analysis"):
            st.session_state.selected_category = "💰 Finance & Cash Flow"
            st.session_state.selected_tool = "Supplier Payment Analysis"

    st.subheader("Cost Structure & Profitability")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Unit Cost Calculator"):
            st.session_state.selected_category = "📊 Cost & Profit"
            st.session_state.selected_tool = "Unit Cost Calculator"

    with col2:
        if st.button("Discount NPV Analysis"):
            st.session_state.selected_category = "📊 Cost & Profit"
            st.session_state.selected_tool = "Discount NPV Analysis"

    st.subheader("Inventory & Operations")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Inventory Turnover Analysis"):
            st.session_state.selected_category = "📦 Inventory & Operations"
            st.session_state.selected_tool = "Inventory Turnover Analysis"

    with col2:
        if st.button("Credit Days Calculator"):
            st.session_state.selected_category = "📦 Inventory & Operations"
            st.session_state.selected_tool = "Credit Days Calculator"

    st.subheader("Strategy & Decision")

    if st.button("QSPM – Strategy Comparison"):
        st.session_state.selected_category = "🧭 Strategy & Decision"
        st.session_state.selected_tool = "QSPM – Strategy Comparison"

    # -------------------------------------------------
    # HOW TO USE (AS REQUESTED — UNCHANGED)
    # -------------------------------------------------

    st.divider()

    st.subheader("How to use the Lab")
    st.markdown("""
    Use the sidebar to open a specific tool once you know which decision frame you are operating in.  

    Focus on tolerance, not forecasts. Small changes compound structurally.  

    If you need guidance, Getting Started explains the decision logic behind the Lab.
    """)

    # -------------------------------------------------
    # CONTACT (UNCHANGED)
    # -------------------------------------------------

    st.markdown("""
    **Contact**  
    For feedback, questions, or collaboration:  
    ✉️ brokeconomist@gmail.com
    """)
