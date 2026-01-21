import streamlit as st

def show_home():
    # --- Page title ---
    st.title("🧪 Managers’ Lab")
    
    # --- Short description ---
    st.markdown(
        """
        An interactive environment for financial decision testing.

        Not a dashboard.
        Not a reporting or forecasting tool.

        Managers’ Lab is a decision laboratory.

        Here, you test assumptions, constraints, and breakpoints behind managerial choices:
        pricing, growth, financing, customer value, and cost structure.

        The tools are already built.
        Judgment is yours.

        Managers’ Lab does not tell you what to do.
        It shows what must be true for a decision to work — and what breaks when it doesn’t.
        """
    )

    # --- Main categories overview ---
    st.subheader("Tool Categories")
    
    st.markdown("""
    - **Getting Started** — Understand the logic behind the Lab  
    - **Break-Even & Pricing** — Costs, margins, and pricing pressure  
    - **Customer Value** — CLV, substitution, and complementary products  
    - **Finance & Cash Flow** — Cash cycles, credit policy, and financing  
    - **Cost & Profit** — Unit cost, gross profit, and NPV analysis  
    - **Inventory & Operations** — EOQ, turnover, and working capital
    """)

    # --- How to use ---
    st.subheader("How to Use the Lab")
    st.markdown(
        """
        Use the sidebar to select a category and a tool.  
        Each tool is designed to test *what must be true* for a decision to work.

        Focus on **tolerance**, not forecasts.  
        Small changes compound structurally.
        """
    )

    # --- Divider ---
    st.markdown("---")

    # --- Tip ---
    st.info("Tip: If this is your first visit, start with **Getting Started** to understand the decision logic.")

    # --- Footer / Contact ---
    st.markdown(
        """
        <br><br>
        **Contact**  
        For feedback, questions, or collaboration:  
        ✉️ <a href="mailto:brokeconomist@gmail.com">brokeconomist@gmail.com</a>
        """,
        unsafe_allow_html=True
    )
