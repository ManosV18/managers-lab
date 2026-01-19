# == FILE: product_mix_logic.py ==
"""
Product Mix Optimization logic (PuLP)
Functions:
 - optimize_product_mix(products, capacity=None, budget=None)

Product data structure (list of dicts):
[{
  'name': 'Prod A',
  'price': 10.0,
  'cost': 6.0,
  'max_demand': 1000.0,
  'capacity_required': 0.5,
  'current_qty': 200.0  # optional
}, ...]

Returns dict with product_mix, total_profit, capacity_usage, status, details (pulp status)
"""

from typing import List, Dict, Optional
import pulp


def optimize_product_mix(products: List[Dict], capacity: Optional[float] = None, budget: Optional[float] = None):
    # Create LP problem
    prob = pulp.LpProblem("Product_Mix_Optimization", pulp.LpMaximize)

    # Decision variables: quantity for each product (continuous, >=0)
    qty_vars = {}
    for p in products:
        name = p.get("name")
        # upper bound is max_demand
        ub = None
        if p.get("max_demand") is not None:
            try:
                ub = float(p.get("max_demand"))
            except Exception:
                ub = None
        var = pulp.LpVariable(f"qty_{name}", lowBound=0, upBound=ub)
        qty_vars[name] = var

    # Objective: maximize profit = sum((price-cost) * qty)
    profit_terms = []
    for p in products:
        name = p["name"]
        margin = float(p.get("price", 0.0)) - float(p.get("cost", 0.0))
        profit_terms.append(margin * qty_vars[name])
    prob += pulp.lpSum(profit_terms)

    # Capacity constraint: sum(qty * capacity_required) <= capacity
    if capacity is not None:
        cap_terms = []
        for p in products:
            name = p["name"]
            cap_req = float(p.get("capacity_required", 0.0))
            cap_terms.append(cap_req * qty_vars[name])
        prob += pulp.lpSum(cap_terms) <= float(capacity)

    # Budget constraint: sum(qty * cost) <= budget
    if budget is not None:
        cost_terms = []
        for p in products:
            name = p["name"]
            cost = float(p.get("cost", 0.0))
            cost_terms.append(cost * qty_vars[name])
        prob += pulp.lpSum(cost_terms) <= float(budget)

    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # Prepare results
    product_mix = {}
    for p in products:
        name = p["name"]
        qty = qty_vars[name].varValue if qty_vars[name].varValue is not None else 0.0
        product_mix[name] = float(qty)

    total_profit = 0.0
    total_capacity_used = 0.0
    total_cost_used = 0.0
    for p in products:
        name = p["name"]
        qty = product_mix[name]
        margin = float(p.get("price", 0.0)) - float(p.get("cost", 0.0))
        total_profit += margin * qty
        total_capacity_used += float(p.get("capacity_required", 0.0)) * qty
        total_cost_used += float(p.get("cost", 0.0)) * qty

    capacity_usage = None
    if capacity is not None and float(capacity) > 0:
        capacity_usage = total_capacity_used / float(capacity)

    status = pulp.LpStatus.get(pulp.value(prob.status), pulp.LpStatus[prob.status]) if False else pulp.LpStatus[prob.status]

    return {
        "product_mix": product_mix,
        "total_profit": float(total_profit),
        "capacity_used": float(total_capacity_used),
        "capacity": float(capacity) if capacity is not None else None,
        "capacity_usage": float(capacity_usage) if capacity_usage is not None else None,
        "total_cost_used": float(total_cost_used),
        "status": status,
        "pulp_status_code": int(prob.status)
    }


# == FILE: product_mix_calculator.py ==
"""
Streamlit UI to drive the product mix optimizer.
This file exposes a function `run()` that you can import from your main `app.py` and call
or run directly with `streamlit run product_mix_calculator.py`.

Dependencies: streamlit, pandas, numpy, pulp, matplotlib
"""

import streamlit as st
import pandas as pd
import numpy as np
from product_mix_logic import optimize_product_mix

# Optional: try to import Greek-format helpers from your utils if present
try:
    from utils import format_number_gr
except Exception:
    def format_number_gr(x):
        try:
            # simple fallback: use comma as decimal separator
            return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return str(x)


def run():
    st.title("Managers' Club — Product Mix Optimization")
    st.write("Εργαλείο: Βελτιστοποίηση προϊοντικού μείγματος (linear programming)")

    st.markdown("**1) Εισαγωγή προϊόντων** — επεξεργάσου τον πίνακα ή κάνε paste από Excel.")

    # Default example products
    default_data = [
        {"name": "Προϊόν Α", "price": 10.0, "cost": 6.0, "max_demand": 1000.0, "capacity_required": 0.5, "current_qty": 200.0},
        {"name": "Προϊόν Β", "price": 8.0, "cost": 4.5, "max_demand": 800.0, "capacity_required": 0.3, "current_qty": 150.0},
        {"name": "Προϊόν Γ", "price": 12.0, "cost": 9.0, "max_demand": 400.0, "capacity_required": 0.8, "current_qty": 80.0},
    ]

    df = pd.DataFrame(default_data)

    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    st.markdown("**2) Συνολικοί περιορισμοί**")
    capacity = st.number_input("Συνολική διαθέσιμη capacity (ώρες ή μονάδα) - άφησέ κενό για no-limit", value=100.0, min_value=0.0)
    budget = st.number_input("Προϋπολογισμός κόστους (προαιρετικό) - άφησέ κενό για no-limit", value=0.0, min_value=0.0)
    if budget == 0.0:
        budget = None

    st.write("---")
    if st.button("Υπολόγισε Optimal Mix"):
        # build products list
        products = []
        for _, row in edited.iterrows():
            try:
                products.append({
                    "name": str(row.get("name", "")),
                    "price": float(row.get("price", 0.0)),
                    "cost": float(row.get("cost", 0.0)),
                    "max_demand": float(row.get("max_demand", 0.0)),
                    "capacity_required": float(row.get("capacity_required", 0.0)),
                    "current_qty": float(row.get("current_qty", 0.0)) if not np.isnan(row.get("current_qty", np.nan)) else 0.0
                })
            except Exception as e:
                st.error(f"Σφάλμα στην ανάγνωση των προϊόντων: {e}")
                st.stop()

        result = optimize_product_mix(products, capacity=capacity, budget=budget)

        # Show results
        st.subheader("Αποτέλεσμα — Optimal Mix")
        mix = result["product_mix"]
        out_rows = []
        for p in products:
            name = p["name"]
            out_rows.append({
                "name": name,
                "optimal_qty": mix.get(name, 0.0),
                "current_qty": p.get("current_qty", 0.0),
                "price": p.get("price"),
                "cost": p.get("cost"),
                "margin": p.get("price") - p.get("cost")
            })
        out_df = pd.DataFrame(out_rows)
        out_df["optimal_value"] = out_df.optimal_qty * out_df.price
        out_df["optimal_profit"] = out_df.optimal_qty * out_df.margin

        # KPIs
        st.metric("Συνολικά Προβλεπόμενα Κέρδη", format_number_gr(result["total_profit"]))
        if result["capacity"] is not None:
            st.metric("Χρήση capacity", f"{result['capacity_usage']*100:.1f}%")
        st.write(out_df)

        # Charts
        st.markdown("**Γράφημα: Optimal Qty ανά Προϊόν**")
        chart_df = out_df.set_index("name")[ ["optimal_qty", "current_qty"] ]
        st.bar_chart(chart_df)

        st.markdown("**Προτεινόμενη Κατανομή Κέρδους ανά Προϊόν**")
        profit_chart = out_df.set_index("name")["optimal_profit"]
        st.area_chart(profit_chart)

        st.write("---")
        st.write("Raw solver status:", result.get("status"))


if __name__ == '__main__':
    run()


# == FILE: README INSTRUCTIONS (below as comment) ==
"""
Installation / Usage:
1. Create a folder in your Streamlit app repo, e.g. `product_mix_module/`.
2. Save the two sections above as separate files:
   - product_mix_logic.py
   - product_mix_calculator.py
3. Install dependencies (recommended in a virtualenv):
   pip install streamlit pandas numpy pulp matplotlib

4. Run locally for testing:
   streamlit run product_mix_calculator.py

5. To integrate into your existing `app.py` (Streamlit main), import and add to sidebar:

   from product_mix_calculator import run as product_mix_run

   # inside your navigation logic:
   if page == 'Product Mix':
       product_mix_run()

Notes / Extensions:
- You can replace the LP solver (PuLP default CBC) with any solver PuLP supports if you have it installed.
- To add elasticity-based pricing, create a separate module that uses SciPy minimize and plug into a combined advanced module.
- I kept the UI simple so you can match style with your other modules (Greek formatting helper used if present in `utils.py`).

If you want, I can now:
 - adapt the UI to use your exact `utils.format_number_gr` and styling,
 - export results to Excel (pandas .to_excel) for download,
 - add a "What-if" slider panel that recomputes on-the-fly for capacity/budget changes,
 - add sensitivity analysis (shadow prices) using dual values from PuLP.

Πες μου ποιο από τα παραπάνω να προσθέσω αμέσως.
"""

