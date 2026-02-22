import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decimal import Decimal, getcontext
from core.engine import compute_core_metrics

# --- 1. CORE LOGIC ENGINES ---
def calculate_discount_npv(current_sales, extra_sales, discount_trial, prc_clients_take_disc, 
                           eff_take, eff_no_take, new_days_payment, cogs, wacc, supplier_days):
    getcontext().prec = 20
    i = wacc / 365
    
    avg_current_days = (prc_clients_take_disc * eff_take) + ((1 - prc_clients_take_disc) * eff_no_take)
    current_rec = current_sales * avg_current_days / 365
    
    total_sales = current_sales + extra_sales
    prcnt_new = ((current_sales * prc_clients_take_disc) + extra_sales) / total_sales
    
    new_avg_days = (prcnt_new * new_days_payment + (1 - prcnt_new) * eff_no_take)
    new_rec = total_sales * new_avg_days / 365
    
    free_cap = current_rec - new_rec
    profit_extra = extra_sales * (1 - cogs / current_sales)
    discount_cost = total_sales * prcnt_new * discount_trial
    
    # Financial Impact Breakdown
    yield_free_cap = free_cap * wacc
    npv = yield_free_cap + profit_extra - discount_cost
    
    # --- THRESHOLDS CALCULATION ---
    # Max Discount: Το σημείο όπου NPV = 0
    max_discount = (yield_free_cap + profit_extra) / (total_sales * prcnt_new) if (total_sales * prcnt_new) > 0 else 0
    
    # Optimum Discount: Θεωρητικό βέλτιστο βάσει επιτοκίου και χρόνου (Rule of thumb)
    optimum_discount = (1 - ((1 + i) ** (new_days_payment - avg_current_days))) / 2

    return {
        "avg_current_days": round(avg_current_days, 1),
        "new_avg_days": round(new_avg_days, 1),
        "free_capital": round(free_cap, 2),
        "npv": round(npv, 2),
        "discount_cost": round(discount_cost, 2),
        "yield_free_cap": round(yield_free_cap, 2),
        "profit_extra": round(profit_extra, 2),
        "max_discount": round(max_discount * 100, 2),
        "optimum_discount": round(abs(optimum_discount * 100), 2)
    }

# --- 2. UI FUNCTION ---
def show_receivables_manager():
    st.header("📊 Receivables Strategic Control")
    
    metrics = compute_core_metrics()
    base_sales = metrics['revenue']
    base_cogs = st.session_state.get('variable_cost', 0.0) * st.session_state.get('volume', 0)
    base_wacc = st.session_state.get('interest_rate', 0.10)

    tab1, tab2 = st.tabs(["🎯 Pareto Segmentation", "💳 Discount NPV Simulator"])
    
    with tab1:
        st.subheader("Customer Category Breakdown")
        num_cat = st.number_input("Categories", 1, 10, 3)
        data = []
        cols = st.columns([2, 2, 1])
        cols[0].write("Category Name")
        cols[1].write("Amount (€)")
        cols[2].write("Avg. Days")
        
        for i in range(num_cat):
            c = st.columns([2, 2, 1])
            name = c[0].text_input(f"Name {i}", f"Segment {i+1}", label_visibility="collapsed")
            amt = c[1].number_input(f"Amt {i}", 0.0, value=base_sales/num_cat if base_sales > 0 else 10000.0, label_visibility="collapsed")
            days = c[2].number_input(f"Days {i}", 0, value=60, label_visibility="collapsed")
            data.append({"Category": name, "Amount": amt, "Days": days})
        
        df = pd.DataFrame(data).sort_values(by="Amount", ascending=False)
        total_amt = df["Amount"].sum()
        weighted_avg_days = (df["Amount"] * df["Days"]).sum() / total_amt if total_amt > 0 else 0
        
        st.metric("Systemic Weighted DSO", f"{weighted_avg_days:.1f} Days")
        
        df["Cum%"] = (df["Amount"].cumsum() / total_amt) * 100
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["Category"], y=df["Amount"], name="Debt Amount", marker_color="#1f77b4"))
        fig.add_trace(go.Scatter(x=df["Category"], y=df["Cum%"], name="Cumulative %", yaxis="y2", line=dict(color="#d62728", width=3)))
        fig.update_layout(yaxis2=dict(overlaying='y', side='right', range=[0, 110]), template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("Push Weighted Days to Simulator", use_container_width=True):
            st.session_state['sim_dso'] = weighted_avg_days
            st.success("DSO synced with Simulator!")

    with tab2:
        st.subheader("Financial Trade-off Analysis")
        sim_dso = st.session_state.get('sim_dso', weighted_avg_days)
        
        col_l, col_r = st.columns(2)
        disc_val = col_l.slider("Proposed Discount %", 0.0, 5.0, 2.0, step=0.1) / 100
        take_rate = col_r.slider("% Customers Taking Discount", 0, 100, 40) / 100
        target_days = col_l.number_input("Target Discount Days (e.g. payment in 10 days)", value=10)
        extra_sales_pct = col_r.number_input("Est. Extra Sales from Policy (%)", value=5.0) / 100
        
        res = calculate_discount_npv(total_amt, total_amt * extra_sales_pct, disc_val, take_rate, 
                                     target_days, sim_dso, target_days, base_cogs, base_wacc, 30)
        
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("DSO Shift", f"{res['avg_current_days']} → {res['new_avg_days']}", f"{res['new_avg_days'] - res['avg_current_days']:.1f} days")
        m2.metric("Cash Released", f"{res['free_capital']:,.2f} €")
        m3.metric("Net NPV Impact", f"{res['npv']:,.2f} €", delta="Value Creation" if res['npv'] > 0 else "Value Destruction", delta_color="normal" if res['npv'] > 0 else "inverse")

        # --- ΤΑ ΟΡΙΑ ΠΟΥ ΖΗΤΗΣΕΣ ---
        st.subheader("🧠 Strategic Thresholds")
        st.info(f"""
        * **Max Sustainable Discount:** **{res['max_discount']}%** (Αν δώσεις παραπάνω από αυτό, χάνεις χρήματα ανεξάρτητα από το πόσο γρήγορα εισπράττεις).
        * **Recommended Optimum:** **{res['optimum_discount']}%** (Το μαθηματικό σημείο ισορροπίας μεταξύ κόστους κεφαλαίου και ταχύτητας χρήματος).
        """)
        
        with st.expander("🔍 Detailed Economic Breakdown"):
            st.write(f"✅ Yield from Released Capital: **{res['yield_free_cap']:,.2f} €**")
            st.write(f"✅ Margin from Extra Sales: **{res['profit_extra']:,.2f} €**")
            st.error(f"❌ Cost of Offering Discount: **{res['discount_cost']:,.2f} €**")
