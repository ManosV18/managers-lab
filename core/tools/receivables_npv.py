import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, getcontext

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
        "optimum_discount": float(opt_d * 100)
    }

# --- UI LAYER ---
def show_receivables_analyzer_ui():
    s = st.session_state
    m = s.get("metrics", {})
    
    # LINKED DATA FROM GLOBAL ENGINE
    sys_revenue = float(s.get('price', 100.0) * s.get('volume', 1000))
    sys_cogs = float(s.get('variable_cost', 60.0) * s.get('volume', 1000))
    
    # 🔗 DYNAMIC WACC LINKAGE
    if 'wacc_locked' in s:
        sys_wacc = float(s['wacc_locked']) / 100
        wacc_label = f"Locked WACC: {s['wacc_locked']:.2f}%"
    else:
        sys_wacc = 0.15
        wacc_label = "Default WACC: 15.00%"

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
            p_take = st.number_input("% Clients Adopting Discount", value=40.0, step=1.0) / 100
            d_take = st.number_input("Current Collection (Take Group) - Days", value=int(sys_ar_days))
            
        with col2:
            st.markdown("**Timeline & Capital Cost**")
            d_new = st.number_input("New Payment Target (Days)", value=10, step=1)
            cogs_val = st.number_input("COGS (€)", value=sys_cogs)
            # Displaying the linked WACC but allowing slight adjustment for sensitivity analysis
            wacc_val = st.number_input("Cost of Capital - WACC (%)", value=sys_wacc * 100, step=0.1) / 100
            d_supps = st.number_input("DPO (Supplier Days)", value=int(sys_ap_days))
            d_no_take = st.number_input("Current Collection (No-Take) - Days", value=int(sys_ar_days * 1.5))

        submitted = st.form_submit_button("Execute NPV Simulation", use_container_width=True)

    if submitted:
        r = calculate_discount_npv(c_sales, e_sales, d_trial, p_take, d_take, d_no_take, d_new, cogs_val, wacc_val, d_supps)
        
        st.divider()
        st.subheader("🏁 Financial Verdict")

        c1, c2, c3 = st.columns(3)
        c1.metric("Strategy NPV", f"€{r['npv']:,.2f}", 
                  delta="Value Creator" if r['npv'] > 0 else "Value Destroyer", 
                  delta_color="normal" if r['npv'] > 0 else "inverse")
        c2.metric("Break-even Discount", f"{r['max_discount']:.2f}%")
        c3.metric("Mathematical Optimum", f"{r['optimum_discount']:.2f}%")

        

        st.write("---")
        st.subheader("🔍 Liquidity & Efficiency Impact")
        l1, l2 = st.columns(2)
        l1.metric("Capital to be Liberated", f"€{r['free_capital']:,.2f}")
        l2.metric("New Avg. Collection Period", f"{r['new_avg_collection_period']:.1f} Days", 
                  delta=f"{r['new_avg_collection_period'] - r['avg_current_collection_days']:.1f} Days", delta_color="inverse")

        if r['npv'] > 0:
            st.success(f"🎯 **Decision: EXECUTE.** The strategy creates €{r['npv']:,.2f} in value. Cash acceleration exceeds discount cost.")
        else:
            st.error(f"🚨 **Decision: REJECT.** The discount is too expensive. This move destroys shareholder value.")
    
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
