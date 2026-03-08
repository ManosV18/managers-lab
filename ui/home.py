import streamlit as st
from core.sync import lock_baseline


def run_home():

    s = st.session_state

    # ------------------------------------------------
    # HERO SECTION
    # ------------------------------------------------

    st.title("🛡️ Strategic Decision Room")

    st.subheader(
        "See the real impact on your cash and survival before committing"
    )

    st.write(
        "Change prices, costs, or volumes and instantly see the effect on "
        "profit, break-even, and cash survival."
    )

    st.caption("Know the outcome before you spend a euro.")

    st.divider()

    # ------------------------------------------------
    # TWO COLUMN LAYOUT
    # ------------------------------------------------

    left, right = st.columns([1, 1])

    # =================================================
    # LEFT COLUMN
    # =================================================

    with left:

        st.header("🏗️ Business Setup")

        st.subheader("📊 Sales Parameters")

        c1, c2 = st.columns(2)

        c1.number_input(
            "Unit Price (€)",
            value=float(s.get("price", 100.0)),
            key="price"
        )

        c2.number_input(
            "Annual Volume",
            value=int(s.get("volume", 1000)),
            key="volume"
        )

        st.subheader("💰 Cost Structure")

        col_a, col_b = st.columns(2)

        with col_a:

            st.markdown("**Variable Costs**")

            st.number_input(
                "Materials (€/unit)",
                value=float(s.get("in_mat", 30.0)),
                key="in_mat"
            )

            st.number_input(
                "Labor (€/unit)",
                value=float(s.get("in_lab", 15.0)),
                key="in_lab"
            )

            variable_cost = s.in_mat + s.in_lab

            st.info(f"Total Variable Cost: €{variable_cost:,.2f}")

        with col_b:

            st.markdown("**Fixed Costs (Annual)**")

            st.number_input(
                "Rent & Utilities",
                value=float(s.get("in_rent", 12000.0)),
                key="in_rent"
            )

            st.number_input(
                "Salaries & Admin",
                value=float(s.get("in_sal", 8000.0)),
                key="in_sal"
            )

            fixed_cost = s.in_rent + s.in_sal

            st.info(f"Total Fixed Cost: €{fixed_cost:,.2f}")

        st.divider()

        if st.button("🔒 Lock Baseline & Initialize", use_container_width=True):

            if s.price > variable_cost:

                s.variable_cost = variable_cost
                s.fixed_cost = fixed_cost

                lock_baseline()

                s.flow_step = "stage1"

                st.rerun()

            else:

                st.error("Unit price must be higher than variable cost.")

    # =================================================
    # RIGHT COLUMN
    # =================================================

    with right:

        st.header("🧠 Business Questions")

        question = st.selectbox(

            "What do you want to know?",

            [

                "How much do I need to sell to not lose money?",
                "If I sell this many units will the business make money?",
                "What price should I charge so the business works?",
                "With the cash I have how long can I survive?",
                "Open tools library"

            ]
        )

        st.markdown("")

        if st.button("Run Analysis", use_container_width=True):

            if question == "How much do I need to sell to not lose money?":
                s.flow_step = "stage1"

            elif question == "If I sell this many units will the business make money?":
                s.flow_step = "stage2"

            elif question == "What price should I charge so the business works?":
                s.flow_step = "stage1"

            elif question == "With the cash I have how long can I survive?":
                s.flow_step = "stage3"

            elif question == "Open tools library":
                s.flow_step = "library"

            st.rerun()
