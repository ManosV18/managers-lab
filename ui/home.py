import streamlit as st
from core.sync import lock_baseline


def run_home():

    s = st.session_state

    # ------------------------------------------------
    # HERO SECTION
    # ------------------------------------------------

    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <h1 style="font-size:44px;">🛡️ Strategic Decision Room</h1>

            <h2 style="font-size:26px; font-weight:600;">
            See the real impact on your cash and survival before committing
            </h2>

            <h3 style="font-size:19px; font-weight:normal; color:#555;">
            Change prices, costs, or volumes and instantly see the effect on profit,
            break-even, and cash survival.
            </h3>

            <p style="font-size:18px; color:#777;">
            Know the outcome before you spend a euro.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ------------------------------------------------
    # TWO COLUMN LAYOUT
    # ------------------------------------------------

    left, right = st.columns([1,1])

    # =================================================
    # LEFT COLUMN
    # BUSINESS SETUP
    # =================================================

    with left:

        st.header("🏗️ Business Setup")

        st.subheader("📊 Sales Parameters")

        c1, c2 = st.columns(2)

        s.price = c1.number_input(
            "Unit Price (€)",
            value=float(s.get("price",100.0))
        )

        s.volume = c2.number_input(
            "Annual Volume",
            value=int(s.get("volume",1000))
        )

        st.subheader("💰 Cost Structure")

        col_a, col_b = st.columns(2)

        with col_a:

            st.markdown("**Variable Costs**")

            v1 = st.number_input(
                "Materials (€/unit)",
                value=float(s.get("in_mat",30.0)),
                key="in_mat"
            )

            v2 = st.number_input(
                "Labor (€/unit)",
                value=float(s.get("in_lab",15.0)),
                key="in_lab"
            )

            s.variable_cost = v1 + v2

            st.info(f"Total Variable Cost: €{s.variable_cost:,.2f}")

        with col_b:

            st.markdown("**Fixed Costs (Annual)**")

            f1 = st.number_input(
                "Rent & Utilities",
                value=float(s.get("in_rent",12000.0)),
                key="in_rent"
            )

            f2 = st.number_input(
                "Salaries & Admin",
                value=float(s.get("in_sal",8000.0)),
                key="in_sal"
            )

            s.fixed_cost = f1 + f2

            st.info(f"Total Fixed Cost: €{s.fixed_cost:,.2f}")

        st.divider()

        if st.button("🔒 Lock Baseline & Initialize", use_container_width=True):

            if s.price > s.variable_cost:

                lock_baseline()
                s.flow_step = "stage1"
                st.rerun()

            else:

                st.error("Unit price must be higher than variable cost.")

    # =================================================
    # RIGHT COLUMN
    # QUESTIONS / TOOLS
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
                st.session_state.flow_step = "stage1"

            elif question == "If I sell this many units will the business make money?":
                st.session_state.flow_step = "stage2"

            elif question == "What price should I charge so the business works?":
                st.session_state.flow_step = "stage1"

            elif question == "With the cash I have how long can I survive?":
                st.session_state.flow_step = "stage3"

            elif question == "Open tools library":
                st.session_state.flow_step = "library"

            st.rerun()
