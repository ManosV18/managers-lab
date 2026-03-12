import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, getcontext
import numpy as np

# --- CALCULATION ENGINE (Analytical Precision - NO LOGIC CHANGES) ---
def calculate_discount_npv(
    current_sales, extra_sales, discount_trial, prc_clients_take_disc,
    days_curently_paying_clients_take_discount, days_curently_paying_clients_not_take_discount,
    new_days_payment_clients_take_disc, cogs, wacc, avg_days_pay_suppliers
):
    getcontext().prec = 50 
    
    cs = Decimal(str(current_sales))
    es = Decimal(str(extra_sales))
    dt = Decimal(str(discount_trial))
    pct_take = Decimal(str(prc_clients_take_disc))
    d_take_old = Decimal(str(days_curently_paying_clients_take_discount))
    d_no_take_old = Decimal(str(days_curently_paying_clients_not_take_discount))
    d_new_policy = Decimal(str(new_days_payment_clients_take_disc))
    cg = Decimal(str(cogs))
    wc = Decimal(str(wacc))
    d_supp = Decimal(str(avg_days_pay_suppliers))
    
    pct_no_take = 1 - pct_take
    avg_curr_days = (pct_take * d_take_old) + (pct_no_take * d_no_take_old)
    curr_rec = (cs * avg_curr_days) / 365
    
    total_sales = cs + es
    prcnt_new_policy = ((cs * pct_take) + es) / total_sales
    prcnt_old_policy = 1 - prcnt_new_policy
    
    new_avg_period = (prcnt_new_policy * d_new_policy) + (prcnt_old_policy * d_no_take_old)
    new_rec = (total_sales * new_avg_period) / 365
    free_cap = curr_rec - new_rec
    
    prof_extra = es * (1 - (cg / cs))
    prof_free_cap = free_cap * wc
    dist_cost = total_sales * prcnt_new_policy * dt
    
    i = wc / 365
    term1 = (total_sales * prcnt_new_policy * (1 - dt)) / ((1 + i) ** d_new_policy)
    term2 = (total_sales * prcnt_old_policy) / ((1 + i) ** d_no_take_old)
    inflow = term1 + term2
    
    term3 = (cg / cs) * (es / cs) * cs / ((1 + i) ** d_supp)
    term4 = cs / ((1 + i) ** avg_curr_days)
    outflow = term3 + term4
    
    npv = inflow - outflow

    max_d = 1 - (
        (1 + i)**(d_new_policy - d_no_take_old) * (
            (1 - 1/prcnt_new_policy) + (
                (1 + i)**(d_no_take_old - avg_curr_days) + 
                (cg/cs)*(es/cs)*(1 + i)**(d_no_take_old - d_supp)
            ) / (prcnt_new_policy * (1 + es/cs))
        )
    )
    
    opt_d = (1 - ((1 + i)**(d_new_policy - avg_curr_days))) / 2

    return {
        "avg_current_collection_days": float(avg_curr_days),
        "current_receivables": float(curr_rec),
        "new_avg_collection_period": float(new_avg_period),
        "new_receivables": float(new_rec),
        "free_capital": float(free_cap),
        "profit_from_extra_sales": float(prof_extra),
        "profit_from_free_capital": float(prof_free_cap),
        "discount_cost": float(dist_cost),
        "npv": float(npv),
        "max_discount": float(max_d * 100),
        "optimum_discount": float(opt_d * 100),
        "pct_new_policy": float(prcnt_new_policy * 100)
    }

# --- UI LAYER ---
def show_receivables_analyzer_ui():
    s = st.session_state
    
    # 🔗 DYNAMIC GLOBAL INPUTS
    if 'wacc_locked' in s:
        sys_wacc = float(s['wacc_locked']) / 100
        wacc_label = f"Locked WACC: {s['wacc_locked']:.2f}%"
    else:
        sys_wacc = 0.15
        wacc_label = "Default WACC: 15.00%"

    sys_revenue = float(s.get('price', 100.0) * s.get('volume', 1000))
    sys_cogs = float(s.get('variable_cost', 60.0) * s.get('volume', 1000))
    sys_ar_days = float(s.get('ar_days', 45.0))
    sys_ap_days = float(s.get('ap_days', 30.0))

    st.header("📊 Strategic Receivables Analyzer (NPV)")
    st.info(f"Analytical Value Assessment using {wacc_label}.")

    with st.form("npv_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Market Assumptions**")
            c_sales = st.number_input("Current Sales (€)", value=sys_revenue)
            e_sales = st.number_input("Projected Extra Sales (€)", value=sys_revenue * 0.10)
            d_trial = st.number_input("Proposed Discount (%)", value=2.0, step=0.1) / 100
            p_take = st.number_input("% Clients Expected to Adopt", value=40.0, step=1.0) / 100
            d_take_current = st.number_input("Current Collection (Take Group) - Days", value=int(sys_ar_days))
            
        with col2:
            st.markdown("**Timeline & Capital Cost**")
            d_new_target = st.number_input("New Payment Target (Days)", value=10, step=1)
            cogs_val = st.number_input("COGS (€)", value=sys_cogs)
            wacc_val = st.number_input("Cost of Capital - WACC (%)", value=sys_wacc * 100, step=0.1) / 100
            d_supps = st.number_input("DPO (Supplier Days)", value=int(sys_ap_days))
            d_no_take = st.number_input("Collection for Non-Adopters (Days)", value=int(sys_ar_days * 1.5))

        submitted = st.form_submit_button("Execute NPV Simulation", use_container_width=True)

    if submitted:
        r = calculate_discount_npv(c_sales, e_sales, d_trial, p_take, d_take_current, d_no_take, d_new_target, cogs_val, wacc_val, d_supps)
        
        st.divider()
        
        # --- TOP LEVEL VERDICT ---
        st.subheader("🏁 Financial Verdict")
        c1, c2, c3 = st.columns(3)
        c1.metric("Strategy NPV", f"€{r['npv']:,.2f}", 
                  delta="Value Creator" if r['npv'] > 0 else "Value Destroyer", 
                  delta_color="normal" if r['npv'] > 0 else "inverse")
        c2.metric("Break-even Discount", f"{r['max_discount']:.2f}%")
        c3.metric("Mathematical Optimum", f"{r['optimum_discount']:.2f}%")

        # --- DETAILED ANALYTICAL BREAKDOWN ---
        st.write("---")
        st.subheader("🔍 Detailed Operational Impact")
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.write("**Collection Profile:**")
            st.write(f"• Current Weighted Avg Days: **{r['avg_current_collection_days']:.1f} days**")
            st.write(f"• New Weighted Avg Days: **{r['new_avg_collection_period']:.1f} days**")
            st.write(f"• Total Client Adoption: **{r['pct_new_policy']:.1f}%** of total sales")
            
        with col_right:
            st.write("**Liquidity Profile:**")
            st.write(f"• Current Receivables: **€{r['current_receivables']:,.2f}**")
            st.write(f"• New Projected Receivables: **€{r['new_receivables']:,.2f}**")
            st.metric("Capital Liberated", f"€{r['free_capital']:,.2f}")

        # --- SENSITIVITY MATRIX ---
        st.divider()
        st.subheader("🔬 Sensitivity Analysis: Stress Testing the Strategy")
        st.write("Analyzing NPV stability across variations in Adoption Rate and Sales Growth.")

        # Adoption range (x-axis): 10% to 90%
        # Sales Growth range (y-axis): 0% to 20%
        adoption_range = [0.1, 0.25, 0.4, 0.6, 0.8]
        growth_range = [0.0, 0.05, 0.1, 0.15, 0.2]
        
        matrix_data = []
        for g in growth_range:
            row = []
            for a in adoption_range:
                temp = calculate_discount_npv(
                    c_sales, c_sales * Decimal(str(g)), d_trial, Decimal(str(a)), 
                    d_take_current, d_no_take, d_new_target, cogs_val, wacc_val, d_supps
                )
                row.append(temp['npv'])
            matrix_data.append(row)

        

        fig_sens = go.Figure(data=go.Heatmap(
            z=matrix_data,
            x=[f"{a*100:.0f}% Adoption" for a in adoption_range],
            y=[f"+{g*100:.0f}% Growth" for g in growth_range],
            colorscale='RdYlGn',
            zmid=0,
            text=[[f"€{val:,.0f}" for val in row] for row in matrix_data],
            texttemplate="%{text}",
            hoverongaps=False
        ))
        fig_sens.update_layout(
            template="plotly_dark",
            height=450,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_sens, use_container_width=True)
        st.caption("Analytical Note: Green zones represent viable execution parameters where the discount creates shareholder value.")

    # Navigation
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
