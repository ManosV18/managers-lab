import streamlit as st
import plotly.graph_objects as go

# =========================================================
# CASH BREAK-EVEN CALCULATION
# =========================================================

def calculate_cash_break_even(
    *,
    price: float,
    variable_cost: float,
    fixed_cash_costs: float,
    cash_interest: float,
    principal_payments: float,
    target_cash_profit: float,
) -> dict:
    """
    Calculate cash-based break-even requirements.

    Cash requirement consists of:

        Fixed cash operating costs
        + Cash interest
        + Principal repayments
        + Target cash profit

    Non-cash accounting charges such as depreciation
    are deliberately excluded.
    """

    cash_contribution_per_unit = (
        price - variable_cost
    )

    cash_requirement = (
        fixed_cash_costs
        + cash_interest
        + principal_payments
        + target_cash_profit
    )

    if cash_contribution_per_unit <= 0:

        required_volume = None

    else:

        required_volume = (
            cash_requirement
            / cash_contribution_per_unit
        )

    return {
        "cash_contribution_per_unit": (
            cash_contribution_per_unit
        ),
        "cash_requirement": cash_requirement,
        "required_volume": required_volume,
    }


# =========================================================
# STATE EXTRACTION
# =========================================================

def _extract_cash_inputs(state):
    """
    Extract the inputs required by the cash break-even model
    from a CompanyState.

    This function works for both:

        - locked baseline state
        - projected state

    Therefore the Lab can compare:

        Baseline
            vs
        DecisionPlan Projection
    """

    drivers = state.drivers
    capital = state.capital_structure

    return {
        "price": float(
            drivers.price
        ),

        "variable_cost": float(
            drivers.variable_cost_per_unit
        ),

        "volume": float(
            drivers.volume
        ),

        "fixed_opex": float(
            drivers.fixed_opex
        ),

        "interest": float(
            capital.annual_cash_interest_paid
        ),

        "principal": float(
            capital.principal_payments
        ),

        "target_cash_profit": float(
            drivers.target_profit_goal
        ),
    }


# =========================================================
# CASH BREAK-EVEN LAB
# =========================================================

def render_cash_break_even_lab(
    baseline_state,
    projected_state,
    financial_projection=None,
) -> None:
    """
    Cash Break-Even Decision Lab.

    Architecture:

        Locked Baseline
              ↓
        DecisionPlan
              ↓
        DecisionEvaluator
              ↓
        Projected CompanyState
              ↓
        Cash Break-Even Lab

    Important:

        The Lab does NOT execute Decisions.

        If projected_state is supplied, it represents the
        already evaluated DecisionPlan projection.

        The Lab therefore remains an analytical layer.
    """

    st.title("💧 Cash Break-Even Lab")

    st.info(
        """
        Cash break-even looks at the business from a cash perspective.

        It asks a practical management question:

        **How much must the business sell to cover its cash commitments
        and achieve the desired cash profit?**

        Unlike an accounting break-even calculation, this view excludes
        non-cash charges such as depreciation and includes actual cash
        financing payments such as interest and principal repayments.
        """
    )

    # =====================================================
    # BASELINE INPUTS
    # =====================================================

    baseline = _extract_cash_inputs(
        baseline_state
    )

    # =====================================================
    # PROJECTED INPUTS
    # =====================================================
    #
    # If a DecisionPlan has been evaluated, projected_state
    # contains the resulting business state.
    #
    # Example:
    #
    # Baseline price      = €150
    # Decision            = Price → €160
    # Projected price     = €160
    #
    # If there is no projection, projected_state defaults
    # to baseline.
    # =====================================================

    if projected_state is not None:

        projected = _extract_cash_inputs(
            projected_state
        )

    else:

        projected = dict(
            baseline
        )

    # =====================================================
    # BASELINE CALCULATION
    # =====================================================

    baseline_result = calculate_cash_break_even(
        price=baseline["price"],
        variable_cost=baseline["variable_cost"],
        fixed_cash_costs=baseline["fixed_opex"],
        cash_interest=baseline["interest"],
        principal_payments=baseline["principal"],
        target_cash_profit=baseline["target_cash_profit"],
    )

    baseline_cash_bep = (
        baseline_result["required_volume"]
    )

    if baseline_cash_bep is not None:

        baseline_buffer = (
            baseline["volume"]
            - baseline_cash_bep
        )

    else:

        baseline_buffer = None

    # =====================================================
    # PROJECTED CALCULATION
    # =====================================================

    projected_result = calculate_cash_break_even(
        price=projected["price"],
        variable_cost=projected["variable_cost"],
        fixed_cash_costs=projected["fixed_opex"],
        cash_interest=projected["interest"],
        principal_payments=projected["principal"],
        target_cash_profit=projected["target_cash_profit"],
    )

    projected_cash_bep = (
        projected_result["required_volume"]
    )

    if projected_cash_bep is not None:

        projected_buffer = (
            projected["volume"]
            - projected_cash_bep
        )

    else:

        projected_buffer = None

    # =====================================================
    # CURRENT / PROJECTED POSITION
    # =====================================================

    st.subheader(
        "📌 Baseline Cash Position"
    )

    current_col1, current_col2, current_col3 = (
        st.columns(3)
    )

    with current_col1:

        st.metric(
            "Sales Volume",
            f"{baseline['volume']:,.0f} units",
        )

    with current_col2:

        if baseline_cash_bep is not None:

            st.metric(
                "Cash Break-Even",
                f"{baseline_cash_bep:,.0f} units",
            )

        else:

            st.metric(
                "Cash Break-Even",
                "N/A",
            )

    with current_col3:

        if baseline_buffer is not None:

            st.metric(
                "Cash Sales Buffer",
                f"{baseline_buffer:,.0f} units",
            )

        else:

            st.metric(
                "Cash Sales Buffer",
                "N/A",
            )

    # =====================================================
    # DECISION PROJECTION STATUS
    # =====================================================

    if projected_state is not None:

        st.success(
            """
            🔄 **Decision projection detected**

            The scenario below reflects the currently evaluated
            DecisionPlan rather than the locked baseline.
            """
        )

    else:

        st.info(
            """
            No DecisionPlan projection is currently available.

            The scenario therefore starts from the locked baseline.
            """
        )

    # =====================================================
    # TEST A CASH DECISION
    # =====================================================

    st.divider()

    st.subheader(
        "🔄 What-If Cash Scenario"
    )

    st.caption(
        """
        Change the assumptions below and see how the cash
        break-even requirement changes.

        These controls are a what-if analysis.
        The locked baseline and DecisionPlan are not modified.
        """
    )

    col1, col2, col3 = st.columns(3)

    # =====================================================
    # OPERATING DRIVERS
    # =====================================================

    with col1:

        scenario_price = st.number_input(
            "Selling Price (€)",
            min_value=0.01,
            value=float(
                projected["price"]
            ),
            step=1.0,
            key="cash_be_price",
        )

        scenario_variable_cost = st.number_input(
            "Variable Cash Cost / Unit (€)",
            min_value=0.0,
            value=float(
                projected["variable_cost"]
            ),
            step=1.0,
            key="cash_be_variable_cost",
        )

    # =====================================================
    # CASH OPERATING / FINANCING COSTS
    # =====================================================

    with col2:

        scenario_fixed_opex = st.number_input(
            "Fixed Cash Operating Costs (€)",
            min_value=0.0,
            value=float(
                projected["fixed_opex"]
            ),
            step=1_000.0,
            key="cash_be_fixed_opex",
        )

        scenario_interest = st.number_input(
            "Cash Interest (€)",
            min_value=0.0,
            value=float(
                projected["interest"]
            ),
            step=1_000.0,
            key="cash_be_interest",
        )

    # =====================================================
    # PRINCIPAL / TARGET
    # =====================================================

    with col3:

        scenario_principal = st.number_input(
            "Principal Repayment (€)",
            min_value=0.0,
            value=float(
                projected["principal"]
            ),
            step=1_000.0,
            key="cash_be_principal",
        )

        scenario_target_cash_profit = st.number_input(
            "Target Cash Profit (€)",
            min_value=0.0,
            value=float(
                projected["target_cash_profit"]
            ),
            step=1_000.0,
            key="cash_be_target_profit",
        )

    # =====================================================
    # SALES VOLUME
    # =====================================================

    st.subheader(
        "Sales Volume"
    )

    scenario_volume = st.number_input(
        "Expected Sales Volume (units)",
        min_value=0.0,
        value=float(
            projected["volume"]
        ),
        step=500.0,
        key="cash_be_volume",
    )

    # =====================================================
    # WHAT-IF CALCULATION
    # =====================================================

    scenario_result = calculate_cash_break_even(
        price=scenario_price,
        variable_cost=scenario_variable_cost,
        fixed_cash_costs=scenario_fixed_opex,
        cash_interest=scenario_interest,
        principal_payments=scenario_principal,
        target_cash_profit=scenario_target_cash_profit,
    )

    scenario_cash_bep = (
        scenario_result["required_volume"]
    )

    scenario_contribution = (
        scenario_result[
            "cash_contribution_per_unit"
        ]
    )

    scenario_requirement = (
        scenario_result[
            "cash_requirement"
        ]
    )

    if scenario_cash_bep is not None:

        cash_sales_buffer = (
            scenario_volume
            - scenario_cash_bep
        )

    else:

        cash_sales_buffer = None

    # =====================================================
    # BASELINE VS DECISION PROJECTION
    # =====================================================

    st.divider()

    st.subheader(
        "📊 Baseline vs Decision Projection"
    )

    projection_overview = {
        "Metric": [
            "Selling Price",
            "Variable Cash Cost",
            "Sales Volume",
            "Fixed Cash Operating Costs",
            "Cash Interest",
            "Principal Repayment",
            "Target Cash Profit",
            "Cash Break-Even",
            "Cash Sales Buffer",
        ],

        "Baseline": [
            f"€ {baseline['price']:,.0f}",
            f"€ {baseline['variable_cost']:,.0f}",
            f"{baseline['volume']:,.0f}",
            f"€ {baseline['fixed_opex']:,.0f}",
            f"€ {baseline['interest']:,.0f}",
            f"€ {baseline['principal']:,.0f}",
            f"€ {baseline['target_cash_profit']:,.0f}",
            (
                f"{baseline_cash_bep:,.0f}"
                if baseline_cash_bep is not None
                else "N/A"
            ),
            (
                f"{baseline_buffer:,.0f}"
                if baseline_buffer is not None
                else "N/A"
            ),
        ],

        "Decision Projection": [
            f"€ {projected['price']:,.0f}",
            f"€ {projected['variable_cost']:,.0f}",
            f"{projected['volume']:,.0f}",
            f"€ {projected['fixed_opex']:,.0f}",
            f"€ {projected['interest']:,.0f}",
            f"€ {projected['principal']:,.0f}",
            f"€ {projected['target_cash_profit']:,.0f}",
            (
                f"{projected_cash_bep:,.0f}"
                if projected_cash_bep is not None
                else "N/A"
            ),
            (
                f"{projected_buffer:,.0f}"
                if projected_buffer is not None
                else "N/A"
            ),
        ],
    }

    st.table(
        projection_overview
    )

    # =====================================================
    # WHAT-IF SCENARIO
    # =====================================================

    st.divider()

    st.subheader(
        "📊 What-If Scenario"
    )

    what_if_overview = {
        "Metric": [
            "Selling Price",
            "Variable Cash Cost",
            "Expected Sales Volume",
            "Fixed Cash Operating Costs",
            "Cash Interest",
            "Principal Repayment",
            "Target Cash Profit",
            "Cash Contribution / Unit",
            "Total Cash Requirement",
        ],

        "Decision Projection": [
            f"€ {projected['price']:,.0f}",
            f"€ {projected['variable_cost']:,.0f}",
            f"{projected['volume']:,.0f}",
            f"€ {projected['fixed_opex']:,.0f}",
            f"€ {projected['interest']:,.0f}",
            f"€ {projected['principal']:,.0f}",
            f"€ {projected['target_cash_profit']:,.0f}",
            (
                f"€ "
                f"{projected_result['cash_contribution_per_unit']:,.2f}"
            ),
            (
                f"€ "
                f"{projected_result['cash_requirement']:,.0f}"
            ),
        ],

        "What-If": [
            f"€ {scenario_price:,.0f}",
            f"€ {scenario_variable_cost:,.0f}",
            f"{scenario_volume:,.0f}",
            f"€ {scenario_fixed_opex:,.0f}",
            f"€ {scenario_interest:,.0f}",
            f"€ {scenario_principal:,.0f}",
            f"€ {scenario_target_cash_profit:,.0f}",
            f"€ {scenario_contribution:,.2f}",
            f"€ {scenario_requirement:,.0f}",
        ],
    }

    st.table(
        what_if_overview
    )

    # =====================================================
    # RESULTS
    # =====================================================

    st.divider()

    c1, c2, c3 = st.columns(3)

    if scenario_cash_bep is not None:

        c1.metric(
            "What-If Cash Break-Even",
            f"{scenario_cash_bep:,.0f} units",
            delta=(
                f"{scenario_cash_bep - baseline_cash_bep:,.0f}"
                if baseline_cash_bep is not None
                else None
            ),
            delta_color="inverse",
        )

        c2.metric(
            "Cash Contribution / Unit",
            f"€ {scenario_contribution:,.2f}",
        )

        c3.metric(
            "What-If Cash Sales Buffer",
            f"{cash_sales_buffer:,.0f} units",
            delta=f"{cash_sales_buffer:,.0f}",
            delta_color=(
                "normal"
                if cash_sales_buffer >= 0
                else "inverse"
            ),
        )

    else:

        c1.metric(
            "Cash Break-Even Volume",
            "N/A",
        )

        c2.metric(
            "Cash Contribution / Unit",
            f"€ {scenario_contribution:,.2f}",
        )

        c3.metric(
            "What-If Cash Sales Buffer",
            "N/A",
        )

        st.error(
            """
            The selling price is not sufficient to cover
            the variable cash cost per unit.

            There is therefore no meaningful cash
            break-even volume under these assumptions.
            """
        )

    # =====================================================
    # INTERPRETATION
    # =====================================================

    if scenario_cash_bep is not None:

        if scenario_volume < scenario_cash_bep:

            st.warning(
                f"""
                ⚠️ The expected sales volume of
                **{scenario_volume:,.0f} units**
                is below the cash break-even requirement of
                **{scenario_cash_bep:,.0f} units**.

                The business would need approximately
                **{scenario_cash_bep - scenario_volume:,.0f}**
                additional units to achieve the selected cash target.
                """
            )

        else:

            st.success(
                f"""
                🟢 The expected sales volume of
                **{scenario_volume:,.0f} units**
                is above the cash break-even requirement of
                **{scenario_cash_bep:,.0f} units**.

                The scenario provides a cash sales buffer of
                **{cash_sales_buffer:,.0f} units**.
                """
            )

    # =====================================================
    # CHART
    # =====================================================

    if scenario_cash_bep is not None:

        st.divider()

        st.subheader(
            "📈 Cash Break-Even vs Expected Sales"
        )

        fig = go.Figure()

        fig.add_bar(
            name="Cash Break-Even",
            x=["What-If"],
            y=[scenario_cash_bep],
        )

        fig.add_bar(
            name="Expected Sales",
            x=["What-If"],
            y=[scenario_volume],
        )

        fig.update_layout(
            barmode="group",
            height=400,
            title=(
                "Cash Break-Even Requirement "
                "vs Expected Sales Volume"
            ),
            margin=dict(
                t=50,
                b=30,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # =====================================================
    # MANAGEMENT VIEW
    # =====================================================

    st.divider()

    st.subheader(
        "🧭 Management View"
    )

    st.markdown(
        """
        **This is not an accounting break-even calculation.**

        Managers Lab uses a cash perspective to answer a practical
        management question:

        > **How much must the business sell to cover its cash commitments
        > and achieve the desired cash profit?**
        """
    )

    st.markdown(
        """
        The calculation therefore focuses on:

        - cash variable costs
        - fixed cash operating costs
        - cash interest
        - principal repayments
        - target cash profit

        Non-cash accounting charges such as depreciation are excluded.
        """
    )

    st.caption(
        """
        Managers Lab does not tell management what decision to make.
        It shows the cash consequences of the assumptions selected.
        """
    )
