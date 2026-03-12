import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, getcontext
import numpy as np

# --- CALCULATION ENGINE (ΑΠΑΡΑΛΛΑΚΤΟΣ) ---
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
    
    pct_no_take = Decimal('1') - pct_take
    avg_curr_days = (pct_take * d_take_old) + (pct_no_take * d_no_take_old)
    curr_rec = (cs * avg_curr_days) / Decimal('365')
    
    total_sales = cs + es
    prcnt_new_policy = ((cs * pct_take) + es) / total_sales
    prcnt_old_policy = Decimal('1') - prcnt_new_policy
    
    new_avg_period = (prcnt_new_policy * d_new_policy) + (prcnt_old_policy * d_no_take_old)
    new_rec = (total_sales * new_avg_period) / Decimal('365')
    free_cap = curr_rec - new_rec
    
    prof_extra = es * (Decimal('1') - (cg / cs))
    prof_free_cap = free_cap * wc
    dist_cost = total_sales * prcnt_new_policy * dt
    
    i = wc / Decimal('365')
    term1 = (total_sales * prcnt_new_policy * (Decimal('1') - dt)) / ((Decimal('1') + i) ** d_new_policy)
    term2 = (total_sales * prcnt_old_policy) / ((Decimal('1') + i) ** d_no_take_old)
    inflow = term1 + term2
    
    term3 = (cg / cs) * (es / cs) * cs / ((Decimal('1') + i) ** d_supp)
    term4 = cs / ((Decimal('1') + i) ** avg_curr_days)
    outflow = term3 + term4
    
    npv = inflow - outflow

    max_d = Decimal('1') - (
        (Decimal('1') + i)**(d_new_policy - d_no_take_old) * (
            (Decimal('1') - Decimal('1')/prcnt_new_policy) + (
                (Decimal('1') + i)**(d_no_take_old - avg_curr_days) + 
                (cg/cs)*(es/cs)*(Decimal('1') + i)**(d_no_take_old - d_supp)
            ) / (prcnt_new_policy * (Decimal('1') + es/cs))
        )
    )
    
    opt_d = (Decimal('1') - ((Decimal('1') + i)**(d_new_policy - avg_curr_days))) / Decimal('2')

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
    
    sys_wacc = float(s.get('wacc_locked', 15.0)) / 100
    sys_revenue = float(s.get('price', 100.0) * s.get('volume', 1000))
    sys_cogs = float(s.get('variable_cost', 60.0) * s.get('volume', 1000))
    sys_ar_days = float(s.get('ar_days', 45.0))
    sys_ap_days = float(s.get('ap_days', 30.0))
    sys_cash = float(s.get('cash_position', 100000.0))
    sys_fixed_costs = float(s.get('fixed_costs', 500000.0))

    st.header("📊 Strategic Receivables Analyzer (NPV)")

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
        
        # Financial Verdict Cards
        st.divider()
        st.subheader("🏁 Financial Verdict")
        c1, c2, c3 = st.columns(3)
        c1.metric("Strategy NPV", f"€{r['npv']:,.2f}", delta="Value Creator" if r['npv'] > 0 else "Value Destroyer")
        c2.metric("Break-even Discount", f"{r['max_discount']:.2f}%")
        c3.metric("Mathematical Optimum", f"{r['optimum_discount']:.2f}%")

        # Detailed Impact
        st.write("---")
        col_left, col_right = st.columns(2)
        with col_left:
            st.write("**Collection Profile:**")
            st.write(f"• New Weighted Avg Days: **{r['new_avg_collection_period']:.1f} days**")
        with col_right:
            st.write("**Liquidity Profile:**")
            st.metric("Capital Liberated", f"€{r['free_capital']:,.2f}")

        # Sensitivity Matrix
        st.divider()
        st.subheader("🔬 Sensitivity Analysis")
        # [Κώδικας Heatmap εδώ - Παραλείπεται για συντομία αλλά παραμένει στο αρχείο σου]

        # --- SURVIVAL SHIELD & LIQUIDITY GAP CHART ---
        st.divider()
        st.subheader("🛡️ Strategic Survival Monitor")

        daily_burn = sys_fixed_costs / 365
        survival_days = sys_cash / daily_burn if daily_burn > 0 else 999
        new_dso = r['new_avg_collection_period']
        l_gap = new_dso - survival_days

        # Visual Alerts (Όπως τα ορίσαμε)
        if new_dso > survival_days:
            st.error(f"🚨 **CRITICAL FRAGILITY**: Gap of {l_gap:.1f} days. You run out of cash before you get paid.")
        elif (survival_days - new_dso) < 15:
            st.warning(f"⚠️ **LOW BUFFER**: Safety margin is only {(survival_days - new_dso):.1f} days.")
        else:
            st.success(f"✅ **ROBUST**: Cash arrives {abs(l_gap):.1f} days before depletion.")

        # --- NEW: LIQUIDITY GAP LINE CHART ---
        st.write("**Liquidity Gap vs. Discount Rate**")
        discounts = np.linspace(0, 0.05, 11) # 0% to 5%
        gaps = []
        for d in discounts:
            temp_r = calculate_discount_npv(c_sales, e_sales, d, p_take, d_take_current, d_no_take, d_new_target, cogs_val, wacc_val, d_supps)
            gaps.append(temp_r['new_avg_collection_period'] - survival_days)

        fig_gap = go.Figure()
        fig_gap.add_trace(go.Scatter(x=discounts*100, y=gaps, mode='lines+markers', name='Liquidity Gap', line=dict(color='#ff4b4b')))
        fig_gap.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Survival Threshold")
        fig_gap.update_layout(title="Liquidity Gap (Days) by Discount level", xaxis_title="Discount %", yaxis_title="Days (Positive = Danger)", template="plotly_dark")
        st.plotly_chart(fig_gap, use_container_width=True)

    st.divider()
    if st.button("⬅️ Back to Control Tower"):
        st.session_state.flow_step = "home"
        st.rerun()
        
