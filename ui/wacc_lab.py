import streamlit as st
from uuid import uuid4

from core.wacc_engine import WACCEngine
from core.decision import DecisionFactory


def render_wacc_lab(baseline_state):
    """
    WACC Decision Lab.

    Presentation layer only.

    Responsibilities:
    - Display current capital structure.
    - Collect WACC assumptions.
    - Call WACCEngine.
    - Display WACC analysis.

    Does NOT:
    - Calculate WACC directly.
    - Modify CompanyState.
    - Create scenarios.
    - Persist changes to the baseline.
    """

    st.title("📉 WACC Lab")

    st.caption(
        "Cost of Capital Analysis → Hurdle Rate → ROIC Spread"
    )

    st.info(
        "Calculate the company's Weighted Average Cost of Capital "
        "(WACC) and compare it with ROIC to assess value creation."
    )

    # =========================================================
    # BASELINE VALIDATION
    # =========================================================

    if baseline_state is None:
        st.error("No baseline CompanyState is available.")
        return

    # =========================================================
    # BASELINE CAPITAL STRUCTURE
    # =========================================================

    capital = baseline_state.capital_structure

    baseline_debt = float(capital.total_debt)
    baseline_tax_rate = float(capital.tax_rate)
    baseline_wacc = float(capital.wacc)

    # =========================================================
    # CAPITAL STRUCTURE
    # =========================================================

    st.subheader("🏦 Capital Structure")

    col1, col2 = st.columns(2)

    with col1:
        market_equity = st.number_input(
            "Market Value of Equity (€)",
            min_value=0.0,
            value=1_000_000.0,
            step=50_000.0,
            key="wacc_market_equity",
        )

    with col2:
        total_debt = st.number_input(
            "Total Debt (€)",
            min_value=0.0,
            value=baseline_debt,
            step=50_000.0,
            key="wacc_total_debt",
        )

    st.divider()

    # =========================================================
    # RISK / COST ASSUMPTIONS
    # =========================================================

    st.subheader("📈 Risk & Cost Components")

    col1, col2, col3 = st.columns(3)

    with col1:
        risk_free_rate_pct = st.number_input(
            "Risk-Free Rate (%)",
            min_value=0.0,
            value=3.5,
            step=0.1,
            key="wacc_risk_free",
        )

        beta = st.number_input(
            "Equity Beta",
            min_value=0.0,
            value=1.2,
            step=0.05,
            key="wacc_beta",
            help="1.0 = market risk. Above 1.0 = higher systematic risk.",
        )

    with col2:
        market_risk_premium_pct = st.number_input(
            "Market Risk Premium (%)",
            min_value=0.0,
            value=5.5,
            step=0.1,
            key="wacc_mrp",
        )

        interest_rate_pct = st.number_input(
            "Average Interest Rate on Debt (%)",
            min_value=0.0,
            value=6.0,
            step=0.1,
            key="wacc_interest_rate",
        )

    with col3:
        tax_rate_pct = st.number_input(
            "Corporate Tax Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=baseline_tax_rate * 100.0,
            step=0.5,
            key="wacc_tax_rate",
        )

        roic_pct = st.number_input(
            "ROIC (%)",
            min_value=0.0,
            value=0.0,
            step=0.5,
            key="wacc_roic",
            help="Optional. Used to calculate ROIC − WACC spread.",
        )

    # =========================================================
    # CALCULATION
    # =========================================================

    st.divider()

    try:
        result = WACCEngine.calculate_wacc(
            market_equity=market_equity,
            total_debt=total_debt,
            risk_free_rate=risk_free_rate_pct / 100.0,
            beta=beta,
            market_risk_premium=market_risk_premium_pct / 100.0,
            interest_rate=interest_rate_pct / 100.0,
            tax_rate=tax_rate_pct / 100.0,
        )

    except (ValueError, TypeError) as exc:
        st.error(f"WACC calculation error: {exc}")
        return

    # =========================================================
    # EXECUTIVE RESULTS
    # =========================================================

    st.subheader("📊 WACC Result")

    res1, res2, res3 = st.columns(3)

    res1.metric(
        "Cost of Equity (Ke)",
        f"{result['cost_of_equity_pct']:.2f}%",
    )

    res2.metric(
        "After-Tax Cost of Debt (Kd)",
        f"{result['after_tax_cost_of_debt_pct']:.2f}%",
    )

    res3.metric(
        "WACC",
        f"{result['wacc_pct']:.2f}%",
    )

    # =========================================================
    # CAPITAL MIX
    # =========================================================

    st.subheader("⚖️ Capital Mix")

    mix1, mix2 = st.columns(2)

    mix1.metric(
        "Equity Weight",
        f"{result['equity_weight_pct']:.1f}%",
    )

    mix2.metric(
        "Debt Weight",
        f"{result['debt_weight_pct']:.1f}%",
    )

    st.progress(
        min(
            max(result["equity_weight"], 0.0),
            1.0,
        )
    )

    st.caption(
        f"Total Capital: €{result['total_capital']:,.0f}"
    )

    # =========================================================
    # ROIC VS WACC
    # =========================================================

    st.divider()

    st.subheader("🎯 ROIC vs WACC")

    if roic_pct > 0.0:

        spread_result = WACCEngine.calculate_roic_spread(
            roic=roic_pct / 100.0,
            wacc=result["wacc"],
        )

        spread = spread_result["spread_pct"]

        if spread > 2.0:

            st.success(
                f"🎯 Value Creation: ROIC "
                f"({roic_pct:.2f}%) exceeds WACC "
                f"({result['wacc_pct']:.2f}%) by "
                f"{spread:.2f} percentage points."
            )

        elif spread > 0.0:

            st.warning(
                f"⚠️ Marginal Value Creation: ROIC "
                f"({roic_pct:.2f}%) exceeds WACC "
                f"({result['wacc_pct']:.2f}%) by only "
                f"{spread:.2f} percentage points."
            )

        else:

            st.error(
                f"🚨 Value Destruction: WACC "
                f"({result['wacc_pct']:.2f}%) exceeds ROIC "
                f"({roic_pct:.2f}%) by "
                f"{abs(spread):.2f} percentage points."
            )

    else:

        st.info(
            "Enter a ROIC above 0% to evaluate the "
            "ROIC − WACC value creation spread."
        )

    # =========================================================
    # BASELINE COMPARISON
    # =========================================================

    st.divider()

    st.subheader("🔎 Baseline Comparison")

    current_wacc = result["wacc_pct"]
    baseline_wacc_pct = baseline_wacc * 100.0

    delta_wacc = current_wacc - baseline_wacc_pct

    st.metric(
        "Calculated WACC",
        f"{current_wacc:.2f}%",
        delta=f"{delta_wacc:+.2f} pp vs Baseline",
        delta_color="inverse",
    )

    st.caption(
        f"Baseline WACC stored in CompanyState: "
        f"{baseline_wacc_pct:.2f}%"
    )

    # =========================================================
    # CREATE WACC DECISION (FIXED)
    # =========================================================

    if st.button("Create WACC Decision", use_container_width=True, key="create_wacc_decision"):
        # Βεβαιωνόμαστε ότι το target_wacc είναι σε δεκαδική μορφή (π.χ. 0.0896 αντί για 8.96)
        raw_wacc = result["wacc"]
        target_wacc_decimal = raw_wacc / 100.0 if raw_wacc > 1.0 else raw_wacc

        decision = DecisionFactory.wacc_change(
            decision_id=f"wacc_{uuid4().hex[:8]}",
            target_wacc=target_wacc_decimal,
        )

        # 1. Ενημέρωση λίστας decisions
        if "decisions" not in st.session_state:
            st.session_state.decisions = []
        if isinstance(st.session_state.decisions, list):
            st.session_state.decisions.append(decision)

        # 2. Ενημέρωση του DecisionPlan
        if "decision_plan" in st.session_state and st.session_state["decision_plan"] is not None:
            plan = st.session_state["decision_plan"]
            if hasattr(plan, "add_decision"):
                plan.add_decision(decision)
            elif hasattr(plan, "decisions") and isinstance(plan.decisions, list):
                if decision.id not in [d.id for d in plan.decisions]:
                    plan.decisions.append(decision)
            elif isinstance(plan, list):
                if decision.id not in [d.id for d in plan]:
                    plan.append(decision)

        st.session_state.selected_decision = decision
        st.success(f"Created Decision: {decision.name} (WACC: {target_wacc_decimal * 100:.2f}%)")
        st.rerun()
    
    # =========================================================
    # CURRENT WACC DECISIONS
    # =========================================================

    wacc_decisions = [
        decision
        for decision in st.session_state.get(
            "decisions",
            [],
        )
        if decision.category == "capital_structure"
        and "wacc" in decision.changes
    ]

    if wacc_decisions:

        st.divider()

        st.subheader(
            "Created WACC Decisions"
        )

        for decision in wacc_decisions:

            col1, col2 = st.columns(
                [4, 1]
            )

            with col1:

                st.write(
                    f"**{decision.name}**"
                )

                st.caption(
                    decision.description
                )

            with col2:

                selected_decision = (
                    st.session_state.get(
                        "selected_decision"
                    )
                )

                is_selected = (
                    selected_decision is not None
                    and selected_decision.id
                    == decision.id
                )

                if st.button(
                    "Selected"
                    if is_selected
                    else "Select",
                    key=(
                        f"select_wacc_"
                        f"{decision.id}"
                    ),
                ):

                    st.session_state.selected_decision = (
                        decision
                    )

                    st.rerun()


    # =========================================================
    # TRACE / DEBUG
    # =========================================================

    with st.expander("Calculation Details"):

        st.write(
            {
                "Risk-Free Rate": f"{risk_free_rate_pct:.2f}%",
                "Beta": beta,
                "Market Risk Premium": (
                    f"{market_risk_premium_pct:.2f}%"
                ),
                "Cost of Equity": (
                    f"{result['cost_of_equity_pct']:.2f}%"
                ),
                "Pre-Tax Cost of Debt": (
                    f"{result['pre_tax_cost_of_debt_pct']:.2f}%"
                ),
                "After-Tax Cost of Debt": (
                    f"{result['after_tax_cost_of_debt_pct']:.2f}%"
                ),
                "Equity Weight": (
                    f"{result['equity_weight_pct']:.2f}%"
                ),
                "Debt Weight": (
                    f"{result['debt_weight_pct']:.2f}%"
                ),
                "WACC": (
                    f"{result['wacc_pct']:.2f}%"
                ),
            }
        )
