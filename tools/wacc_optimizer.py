import streamlit as st

from core.wacc_engine import WACCEngine


def show_wacc_optimizer_ui():
    st.header("📉 WACC Optimizer (Cost of Capital)")

    st.info(
        "Calculate the Weighted Average Cost of Capital (Hurdle Rate) "
        "to benchmark your ROIC."
    )

    s = st.session_state

    # =========================================================
    # BASELINE DATA
    # =========================================================

    baseline_debt = float(
        s.get("total_debt", 500000.0)
    )

    metrics = s.get("metrics", {})

    total_invested_capital = float(
        metrics.get(
            "invested_capital",
            1300000.0,
        )
    )

    current_roic = float(
        metrics.get(
            "roic",
            0.0,
        )
    )

    current_roic_pct = current_roic * 100.0

    baseline_equity = max(
        total_invested_capital - baseline_debt,
        1000.0,
    )

    # =========================================================
    # INPUTS
    # =========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏦 Capital Structure")

        market_equity = st.number_input(
            "Market Value of Equity (€)",
            value=baseline_equity,
            step=50000.0,
        )

        total_debt = st.number_input(
            "Total Debt (€)",
            value=baseline_debt,
            step=50000.0,
        )

        tax_rate = (
            st.number_input(
                "Corporate Tax Rate (%)",
                value=22.0,
            )
            / 100.0
        )

    with col2:

        st.subheader("📈 Risk & Cost Components")

        risk_free_rate = (
            st.number_input(
                "Risk-Free Rate (%)",
                value=3.5,
                help="e.g. 10Y Government Bond Yield",
            )
            / 100.0
        )

        beta = st.number_input(
            "Equity Beta (Sector Risk)",
            value=1.2,
            help="1.0 = Market Average, >1.0 = Higher Risk",
        )

        market_risk_premium = (
            st.number_input(
                "Market Risk Premium (%)",
                value=5.5,
            )
            / 100.0
        )

        interest_rate = (
            st.number_input(
                "Average Interest Rate on Debt (%)",
                value=6.0,
            )
            / 100.0
        )

    # =========================================================
    # WACC CALCULATION
    # =========================================================

    try:

        result = WACCEngine.calculate_wacc(
            market_equity=market_equity,
            total_debt=total_debt,
            risk_free_rate=risk_free_rate,
            beta=beta,
            market_risk_premium=market_risk_premium,
            interest_rate=interest_rate,
            tax_rate=tax_rate,
        )

    except (ValueError, TypeError) as e:

        st.error(
            f"Unable to calculate WACC: {e}"
        )
        return

    # =========================================================
    # RESULTS
    # =========================================================

    wacc_pct = result["wacc_pct"]
    cost_of_equity_pct = result["cost_of_equity_pct"]
    after_tax_cost_of_debt_pct = (
        result["after_tax_cost_of_debt_pct"]
    )

    spread = (
        current_roic_pct
        - wacc_pct
    )

    st.divider()

    res1, res2, res3 = st.columns(3)

    res1.metric(
        "Cost of Equity (Ke)",
        f"{cost_of_equity_pct:.2f}%",
    )

    res2.metric(
        "After-Tax Cost of Debt (Kd)",
        f"{after_tax_cost_of_debt_pct:.2f}%",
    )

    res3.metric(
        "WACC",
        f"{wacc_pct:.2f}%",
        delta=f"{spread:.2f}% Spread vs ROIC",
        delta_color=(
            "normal"
            if spread > 0
            else "inverse"
        ),
    )

    # =========================================================
    # CAPITAL MIX
    # =========================================================

    st.subheader("Capital Mix")

    st.write(
        f"**Equity:** "
        f"{result['equity_weight_pct']:.1f}%"
        f"  |  "
        f"**Debt:** "
        f"{result['debt_weight_pct']:.1f}%"
    )

    st.progress(
        result["equity_weight"]
    )

    # =========================================================
    # STRATEGIC VERDICT
    # =========================================================

    st.subheader("💡 Strategic Verdict")

    if spread > 2.0:

        st.success(
            f"🎯 **Value Creation:** "
            f"ROIC ({current_roic_pct:.1f}%) "
            f"comfortably exceeds WACC "
            f"({wacc_pct:.1f}%)."
        )

    elif spread > 0.0:

        st.warning(
            f"⚠️ **Marginal Performance:** "
            f"ROIC ({current_roic_pct:.1f}%) "
            f"is only slightly above WACC "
            f"({wacc_pct:.1f}%)."
        )

    else:

        st.error(
            f"🚨 **Value Destruction:** "
            f"WACC ({wacc_pct:.1f}%) "
            f"exceeds ROIC "
            f"({current_roic_pct:.1f}%)."
        )

    # =========================================================
    # OPTIONAL REFERENCE
    # =========================================================

    st.divider()

    st.caption(
        "This tool calculates WACC as an analytical reference. "
        "It does not modify the locked CompanyState."
    )

    # =========================================================
    # LOCK / STORE RESULT
    # =========================================================

    if st.button(
        "🔐 Use WACC for Strategy",
        type="primary",
        use_container_width=True,
    ):

        st.session_state.wacc_calculation = result

        st.success(
            f"WACC calculated at {wacc_pct:.2f}%. "
            "The result is available for strategic analysis."
        )
