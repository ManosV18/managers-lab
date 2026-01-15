import streamlit as st

def show_home():
    # --- Page title ---
    st.title("🧪 Managers’ Lab")
    
    # --- Short description ---
    st.markdown(
        """
        Welcome to **Managers’ Lab** — an interactive environment for financial analysis,
        decision testing, and business modeling.

        This is not a dashboard or a reporting tool.  
        It is a lab for exploring assumptions, constraints, and breakpoints behind everyday
        managerial decisions.
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
