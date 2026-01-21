import streamlit as st

def show_home():
    # --- Page title ---
    st.title("🧪 Managers’ Lab")

    # --- Core positioning ---
    st.markdown(
        """
        An interactive environment for **financial decision testing**.

        Not a dashboard.  
        Not a reporting or forecasting tool.

        **Managers’ Lab is a decision laboratory.**

        You test assumptions, constraints, and breakpoints behind managerial choices —
        pricing, growth, financing, customer value, and cost structure.

        The tools are already built.  
        **Judgment is yours.**

        Managers’ Lab does not tell you what to do.  
        It shows what must be true for a decision to work —  
        and what breaks when it doesn’t.
        """
    )

    # --- Tool categories ---
    st.subheader("Tool Categories")

    st.markdown("""
    - **Getting Started** — Core decision logic used across the Lab  
    - **Break-Even & Pricing** — Costs, margins, pricing pressure  
    - **Customer Value** — CLV, substitution, complementary effects  
    - **Finance & Cash Flow** — Cash cycles, credit, financing structure  
    - **Cost & Profit** — Unit economics, profitability, investment impact  
    - **Inventory & Operations** — Turnover, EOQ, working capital
    """)

    # --- Usage philosophy ---
    st.subheader("How to Use the Lab")

    st.markdown(
        """
        Select a category and tool from the sidebar.

        Each tool tests **what must be true** for a decision to hold.

        Focus on **tolerance**, not forecasts.  
        Small changes compound structurally.
        """
    )

    # --- Divider ---
    st.markdown("---")

    # --- Optional orientation hint (kept minimal) ---
    st.caption("First time here? Start with **Getting Started** to align with the Lab’s decision logic.")

    # --- Contact ---
    st.markdown(
        """
        <br><br>
        **Contact**  
        Feedback, questions, or collaboration:  
        ✉️ <a href="mailto:brokeconomist@gmail.com">brokeconomist@gmail.com
