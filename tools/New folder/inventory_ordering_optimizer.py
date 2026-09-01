import math
import plotly.graph_objects as go
import streamlit as st

# ===========================================================
# EOQ & INVENTORY ENGINE (Based on Excel Logic)
# ===========================================================


def calculate_inventory_metrics(
    unit_price,
    annual_demand,
    ordering_cost,
    discount_pct,
    insurance_pm,
    annual_interest_rate,
    months,
    maintenance_pm,
):
    """Calculates EOQ and inventory costs based on the provided logic.

    - unit_price (q): Initial Unit Price
    - annual_demand (M): Period Demand / Annual Demand
    - ordering_cost (kf): Fixed Cost per Order
    - discount_pct (r): Percentage Discount
    - insurance_pm: Monthly Insurance & Handling
    - annual_interest_rate: Annual Interest Rate / Cost of Capital
    - months: Period duration in months
    - maintenance_pm: Monthly Warehouse Maintenance (Rent, Utilities, etc.)
    """
    if annual_demand <= 0 or unit_price <= 0 or ordering_cost < 0:
        return None

    # Price after discount
    discounted_price = unit_price * (1 - discount_pct)

    # 1. Interest Rate for the Period % 
    i = annual_interest_rate * (months / 12.0)

    # 2. Purchase Cost of Goods
    kv = discounted_price * annual_demand

    # 3. Total Storage & Maintenance Expenses
    maintenance_total = maintenance_pm * months
    insurance_total = insurance_pm * months

    # 4. Storage Cost Rate %
    # j = (Total Storage Expenses) / (Base Purchase Cost)
    base_kv = unit_price * annual_demand
    j = (
        (maintenance_total / base_kv) + (insurance_total / base_kv)
        if base_kv > 0
        else 0
    )

    # 5. Economic Order Quantity B (EOQ Formula)
    # Excel Formula: IF(r==0, SQRT((2*M*kf)/(q*(i+j))), SQRT((2*M*kf)/(q*(j + (1-r)*i))))
    carrying_rate = (j + (1 - discount_pct) * i) if discount_pct > 0 else (i + j)

    if carrying_rate <= 0:
        return None

    eoq = math.sqrt((2 * annual_demand * ordering_cost) / (unit_price * carrying_rate))

    # 6. Number of Orders for the Period
    orders = annual_demand / eoq if eoq > 0 else 0

    # 7. Total Fixed Ordering Cost (KF)
    kf_total = orders * ordering_cost

    # 8. Total Storage & Interest Holding Cost (KL)
    kl_total = carrying_rate * (eoq / 2) * unit_price

    # 9. Total Operating Cost (KF + KL)
    total_operating_cost = kf_total + kl_total

    # 10. Total Inventory Cost (K = KV + KF + KL)
    total_cost = kv + total_operating_cost

    # 11. Tied-up Working Capital (Average Inventory Value)
    capital_tied_up = (eoq / 2) * discounted_price

    return {
        "eoq": eoq,
        "orders": orders,
        "purchase_cost": kv,
        "ordering_cost": kf_total,
        "holding_cost": kl_total,
        "operating_cost": total_operating_cost,
        "total_cost": total_cost,
        "interest_pct": i,
        "storage_pct": j,
        "carrying_rate": carrying_rate,
        "capital_tied_up": capital_tied_up,
        "discounted_price": discounted_price,
    }


# ===========================================================
# STREAMLIT UI MODULE
# ===========================================================


def show_inventory_ordering_optimizer():
    # Back to Hub Navigation Button
    if st.button("⬅ Back to Hub"):
        st.session_state["current_page"] = "hub"
        st.rerun()

    st.title("📦 How Much Inventory Should I Order?")
    st.caption("Managers Lab — Operational Decision Support")

    st.info("""
        Determine the order quantity that minimizes your total inventory cost by balancing:

        • Ordering costs
        • Inventory carrying costs
        • Cost of capital

        This tool analyzes one inventory item (SKU) at a time.

        For businesses with multiple products, repeat the analysis for each major product or product family.
        """)

    st.subheader("🛠️ Inventory & Cost Assumptions")

    col_a, col_b = st.columns(2)

    with col_a:
        annual_demand = st.number_input(
            "Annual Demand (Units)",
            value=10000.0,
            step=500.0,
            help="Total required units for the selected period.",
        )
        unit_price = st.number_input(
            "Purchase Price per Unit ($)",
            value=30.0,
            step=1.0,
            help="Purchase price per unit before discounts.",
        )
        ordering_cost = st.number_input(
            "Ordering Cost per Order ($)",
            value=600.0,
            step=50.0,
            help="Shipping, admin, handling, and processing fees per purchase order.",
        )
        discount_pct = 0.0
    
    with col_b:
        months = 12
        
        annual_interest_rate = (
            st.number_input(
                "Annual Cost of Capital / Interest Rate %",
                value=5.0,
                step=0.5,
                help="Used to estimate the financing cost of holding inventory."
            )
            / 100.0
        )
        maintenance_pm = st.number_input(
            "Warehouse Operating Cost ($/Month)",
            value=600.0,
            step=50.0,
        )
        insurance_pm = 0.0
        
    st.divider()

    # Calculation Execution
    res = calculate_inventory_metrics(
        unit_price=unit_price,
        annual_demand=annual_demand,
        ordering_cost=ordering_cost,
        discount_pct=discount_pct,
        insurance_pm=insurance_pm,
        annual_interest_rate=annual_interest_rate,
        months=months,
        maintenance_pm=maintenance_pm,
    )

    if res is None:
        st.error(
            "Please review your inputs. Demand and unit price must be positive numbers."
        )
        return

    # -------------------------------------------------------
    # EXECUTIVE SUMMARY & METRICS
    # -------------------------------------------------------
    st.subheader("📊 Recommended Ordering Policy")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        label="Optimal Order Quantity (EOQ)",
        value=f"{res['eoq']:,.0f} units",
        help="The cost-minimizing order quantity per batch.",
    )

    m2.metric(
        label="Orders per Period",
        value=f"{res['orders']:.2f}",
        help="How many purchase orders you need to place.",
    )

    m3.metric(
        label="Avg. Tied-up Cash",
        value=f"${res['capital_tied_up']:,.0f}",
        help="Average cash locked in working capital stock.",
    )

    m4.metric(
        label="Total Cost of Inventory",
        value=f"${res['total_cost']:,.0f}",
        help="Purchase cost + Fixed ordering cost + Holding costs.",
    )

    # -------------------------------------------------------
    # COST BREAKDOWN METRICS
    # -------------------------------------------------------
    st.subheader("📦Cost Components Breakdown")
    c1, c2, c3 = st.columns(3)
    c1.metric("Purchase Cost", f"${res['purchase_cost']:,.0f}")
    c2.metric("Fixed Ordering Cost", f"${res['ordering_cost']:,.0f}")
    c3.metric("Holding & Interest Cost", f"${res['holding_cost']:,.0f}")

    st.divider()

    # -------------------------------------------------------
    # VISUALIZATIONS & CHARTS
    # -------------------------------------------------------
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📈 Total Cost vs Order Size")

        # Range of order sizes (from 20% to 250% of EOQ)
        q_min = max(10, int(res["eoq"] * 0.2))
        q_max = int(res["eoq"] * 2.5)
        q_range = list(range(q_min, q_max, max(1, (q_max - q_min) // 50)))

        ordering_costs = [
            (annual_demand / q_val) * ordering_cost for q_val in q_range
        ]
        holding_costs = [
            res["carrying_rate"] * (q_val / 2) * unit_price for q_val in q_range
        ]
        total_ops = [oc + hc for oc, hc in zip(ordering_costs, holding_costs)]

        fig_curve = go.Figure()
        fig_curve.add_trace(
            go.Scatter(
                x=q_range,
                y=ordering_costs,
                mode="lines",
                name="Ordering Cost",
                line=dict(dash="dash", color="#FFA15A"),
            )
        )
        fig_curve.add_trace(
            go.Scatter(
                x=q_range,
                y=holding_costs,
                mode="lines",
                name="Holding Cost",
                line=dict(dash="dash", color="#19D3F3"),
            )
        )
        fig_curve.add_trace(
            go.Scatter(
                x=q_range,
                y=total_ops,
                mode="lines",
                name="Total Operating Cost",
                line=dict(color="#636EFA", width=3),
            )
        )

        # Highlight EOQ point
        fig_curve.add_vline(
            x=res["eoq"],
            line_width=2,
            line_dash="dot",
            line_color="green",
            annotation_text=f"EOQ: {res['eoq']:.0f}",
        )

        fig_curve.update_layout(
            xaxis_title="Order Quantity (Units)",
            yaxis_title="Cost ($)",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            template="plotly_dark",
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig_curve, use_container_width=True)

    with col_chart2:
        st.subheader("📊 Where Your Inventory Money Goes")
        fig_bar = go.Figure(
            data=[
                go.Bar(
                    x=["Purchase", "Ordering", "Holding"],
                    y=[
                        res["purchase_cost"],
                        res["ordering_cost"],
                        res["holding_cost"],
                    ],
                    marker_color=["#2CA02C", "#FF7F0E", "#1F77B4"],
                    text=[
                        f"${res['purchase_cost']:,.0f}",
                        f"${res['ordering_cost']:,.0f}",
                        f"${res['holding_cost']:,.0f}",
                    ],
                    textposition="auto",
                )
            ]
        )
        fig_bar.update_layout(
            yaxis_title="Amount ($)",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            template="plotly_dark",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # -------------------------------------------------------
    # DECISION INTELLIGENCE & INSIGHTS
    # -------------------------------------------------------
    st.subheader("💡 Operational Insights")

    days_between_orders = (
        (months * 30) / res["orders"] if res["orders"] > 0 else 0
    )

    col_diag1, col_diag2 = st.columns(2)

    with col_diag1:
        st.markdown("#### 🔍 Operational Dynamics")
        st.write(
            f"• **Ordering Cadence:** You need to reorder approximately every **{days_between_orders:.1f} days**."
        )
        st.write(
            f"• **Carrying Drag Rate:** Annual carrying & capital holding expenses equal **{res['carrying_rate']*100:.2f}%** of inventory value."
        )

        if res["ordering_cost"] > res["holding_cost"] * 1.3:
            st.warning(
                "⚠️ **High Reordering Friction:** Ordering costs dominate holding costs. Consider increasing order sizes to reduce administrative and shipping overhead."
            )
        elif res["holding_cost"] > res["ordering_cost"] * 1.3:
            st.warning(
                "⚠️ **Excess Inventory Drag:** Holding costs significantly exceed reordering costs. You are holding too much stock, tying up liquidity and incurring excess facility drag."
            )
        else:
            st.success(
                "✅ **Balanced Inventory Strategy:** Reordering costs and carrying costs are in equilibrium (EOQ Optimum)."
            )

    with col_diag2:
        st.markdown("#### 💰 Working Capital Impact")
        st.write(
            f"• **Capital Tied Up:** An average of **${res['capital_tied_up']:,.0f}** remains locked in warehouse stock."
        )

        st.write(
            f"• **Average Cash Tied Up in Inventory:** **${res['capital_tied_up']:,.0f}**"
        )

        st.write(
            f"• **Reducing inventory by 10% could release approximately "
            f"**${res['capital_tied_up']*0.10:,.0f}** of working capital."
        )
        
    # -------------------------------------------------------
    # EXECUTIVE RECOMMENDATION (Full-width Section)
    # -------------------------------------------------------
    st.divider()
    st.subheader("📝 Executive Recommendation")

    if res["ordering_cost"] > res["holding_cost"] * 1.3:
        recommendation = f"""
        Your current ordering policy creates **too many purchase orders**.

        Based on your assumptions, the optimal order quantity is
        **{res['eoq']:,.0f} units**.

        This means placing approximately **{res['orders']:.1f} orders**
        during the period (roughly every **{days_between_orders:.0f} days**).

        Increasing the order size would reduce procurement and administration
        costs without creating excessive inventory carrying costs.
        """
    elif res["holding_cost"] > res["ordering_cost"] * 1.3:
        recommendation = f"""
        Your business is carrying **more inventory than is economically justified**.

        Although larger orders reduce procurement costs, they also lock
        approximately **${res['capital_tied_up']:,.0f}** in working capital.

        Reducing order size would release cash while keeping total operating
        costs close to their optimum level.

        The recommended economic order quantity is
        **{res['eoq']:,.0f} units**.
        """
    else:
        recommendation = f"""
        Your inventory policy is already **very close to the economic optimum**.

        The recommended order quantity is **{res['eoq']:,.0f} units**,
        which means placing approximately **{res['orders']:.1f} orders**
        during the planning period (about every **{days_between_orders:.0f} days**).

        Under your current assumptions, this ordering policy minimizes
        the combined cost of procurement and inventory holding while
        maintaining an efficient use of working capital.
        """

    st.info("### 📌 Executive Recommendation")

    st.write(recommendation)

    st.divider()

    st.markdown("#### Key Takeaways")

    st.markdown(f"""
    - **Recommended Order Quantity:** **{res['eoq']:,.0f} units**
    - **Orders During the Period:** **{res['orders']:.1f}**
    - **Average Time Between Orders:** **{days_between_orders:.0f} days**
    - **Average Cash Locked in Inventory:** **${res['capital_tied_up']:,.0f}**
    - **Total Inventory Cost:** **${res['total_cost']:,.0f}**
    """)


    st.divider()

    st.subheader("🎯 Management Interpretation")

    if res["orders"] < 3:
        st.warning(
            "You place very few orders each year. "
            "This reduces procurement costs but increases inventory levels and cash tied up."
        )

    elif res["orders"] > 12:
        st.warning(
            "You reorder very frequently. "
            "Inventory remains lean, but purchasing and logistics costs become significant."
        )

    else:
        st.success(
            "Your replenishment frequency is well balanced between procurement efficiency and inventory investment."
        )
# Autonomous testing execution
if __name__ == "__main__":
    st.set_page_config(page_title="Inventory Optimizer", layout="wide")
    
