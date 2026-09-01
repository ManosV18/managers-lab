import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st

from diagnostics.complementary_products import (
    calculate_complementary_product_impact,
)


def _get_price(baseline_state):
    try:
        return float(baseline_state.drivers.price)
    except AttributeError:
        return float(getattr(baseline_state, "price", 150.0))


def _get_variable_cost(baseline_state):
    try:
        return float(
            baseline_state.drivers.variable_cost_per_unit
        )
    except AttributeError:
        return float(
            getattr(baseline_state, "variable_cost", 100.0)
        )


def _format_euro(value):
    return f"€{float(value):,.2f}"


def _format_pct(value):
    return f"{float(value):.1f}%"


def render_complementary_products_lab(baseline_state):
    """
    Diagnostic:
    Can complementary products offset the contribution lost
    from a price reduction on the main product?
    """

    st.title("🧩 Complementary Products Diagnostic")

    st.markdown(
        """
        **What happens if I reduce the price of my main product
        and customers also buy complementary products?**

        This diagnostic estimates how much of the contribution
        lost on the main product can be recovered through
        complementary-product purchases.
        """
    )

    price = _get_price(baseline_state)
    variable_cost = _get_variable_cost(baseline_state)
    main_profit = price - variable_cost

    st.subheader("Current Main Product")

    c1, c2, c3 = st.columns(3)

    c1.metric("Current Price", _format_euro(price))
    c2.metric("Variable Cost", _format_euro(variable_cost))
    c3.metric("Contribution / Unit", _format_euro(main_profit))

    st.divider()

    st.subheader("1. Price Decision")

    price_decrease_pct = st.number_input(
        "Price reduction (%)",
        min_value=0.0,
        max_value=99.0,
        value=10.0,
        step=1.0,
        key="complementary_price_decrease",
    )

    st.subheader("2. Complementary Products")

    st.caption(
        "Add the expected profit and probability of purchase "
        "for each complementary product."
    )

    product_count = st.number_input(
        "Number of complementary products",
        min_value=1,
        max_value=10,
        value=2,
        step=1,
        key="complementary_product_count",
    )

    complement_data = []

    for i in range(int(product_count)):
        c1, c2 = st.columns(2)

        with c1:
            profit = st.number_input(
                f"Complement {i + 1} — Profit per purchase (€)",
                min_value=0.0,
                value=20.0,
                step=5.0,
                key=f"complementary_profit_{i}",
            )

        with c2:
            probability_pct = st.number_input(
                f"Complement {i + 1} — Purchase probability (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=5.0,
                key=f"complementary_probability_{i}",
            )

        complement_data.append(
            (profit, probability_pct / 100.0)
        )

    st.divider()

    if st.button(
        "🔍 Analyze Complementary Products",
        use_container_width=True,
        key="analyze_complementary_products",
    ):
        result = calculate_complementary_product_impact(
            main_price=price,
            price_decrease_pct=price_decrease_pct,
            main_profit_per_unit=main_profit,
            complement_data=complement_data,
        )

        if result is None:
            st.error(
                "The diagnostic cannot be calculated with the "
                "current baseline assumptions."
            )
            return

        st.session_state[
            "complementary_products_result"
        ] = result

    result = st.session_state.get(
        "complementary_products_result"
    )

    if result is None:
        return

    st.divider()
    st.subheader("🏁 Result")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Price After Reduction",
        _format_euro(result["price_after_cut"]),
    )

    c2.metric(
        "Contribution Lost / Main Unit",
        _format_euro(
            result["main_profit_loss_per_unit"]
        ),
    )

    c3.metric(
        "Expected Complement Profit",
        _format_euro(
            result["expected_complement_profit"]
        ),
    )

    st.divider()

    coverage = result["recovery_coverage_pct"]

    if coverage >= 100:
        st.success(
            f"""
            **The complementary products can fully offset the
            contribution lost from the price reduction.**

            Expected complementary profit covers approximately
            **{coverage:.1f}%** of the contribution loss per main
            product.
            """
        )
    elif coverage > 0:
        st.warning(
            f"""
            The complementary products recover approximately
            **{coverage:.1f}%** of the contribution lost from the
            price reduction.

            The price reduction is therefore only partially
            compensated by cross-selling.
            """
        )
    else:
        st.info(
            "No meaningful complementary-product contribution "
            "was identified under the current assumptions."
        )

    c1, c2 = st.columns(2)

    c1.metric(
        "Expected Complement Profit / Main Unit",
        _format_euro(
            result["expected_complement_profit"]
        ),
    )

    c2.metric(
        "Combined Contribution / Main Unit",
        _format_euro(
            result["combined_profit_per_unit"]
        ),
    )

    with st.expander(
        "ℹ️ How this diagnostic works",
        expanded=False,
    ):
        st.markdown(
            """
            The diagnostic calculates:

            **1. Main-product contribution**

            Selling price minus variable cost.

            **2. Contribution lost**

            The selected price reduction is applied to the
            contribution generated by the main product.

            **3. Expected complementary profit**

            For each complementary product:

            `Profit per purchase × Purchase probability`

            The results are summed to obtain expected
            complementary profit per main-product customer/order.

            **4. Recovery**

            Expected complementary profit is compared with the
            contribution lost from the main product.
            """
        )
