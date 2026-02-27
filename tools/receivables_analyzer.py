import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, getcontext
from core.sync import sync_global_state

def calculate_discount_npv(
    current_sales, extra_sales, discount_trial, prc_clients_take_disc,
    days_curently_paying_clients_take_discount, days_curently_paying_clients_not_take_discount,
    new_days_payment_clients_take_disc, cogs, wacc, avg_days_pay_suppliers
):
    getcontext().prec = 50 # High precision to match Excel
    
    # Convert to Decimal for absolute accuracy
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
    
    # Intermediate Calculations (Base: 365)
    pct_no_take = 1 - pct_take
    avg_curr_days = (pct_take * d_take_old) + (pct_no_take * d_no_take_old)
    curr_rec = (cs * avg_curr_days) / 365
    
    total_sales = cs + es
    prcnt_new_policy = ((cs * pct_take) + es) / total_sales
    prcnt_old_policy = 1 - prcnt_new_policy
    
    new_avg_period = (prcnt_new_policy * d_new_policy) + (prcnt_old_policy * d_no_take_old)
    new_rec = (total_sales * new_avg_period) / 365
    free_cap = curr_rec - new_rec
    
    # Profit metrics
    prof_extra = es * (1 - (cg / cs))
    prof_free_cap = free_cap * wc
    dist_cost = total_sales * prcnt_new_policy * dt
    
    # NPV Calculation - Strict Excel Logic
    i = wc / 365
    
    # Inflow 1 & 2
    term1 = (total_sales * prcnt_new_policy * (1 - dt)) / ((1 + i) ** d_new_policy)
    term2 = (total_sales * prcnt_old_policy) / ((1 + i) ** d_no_take_old)
    inflow = term1 + term2
    
    # Outflow 1 & 2 (Excel Cell 25 formula)
    term3 = (cg / cs) * (es / cs) * cs / ((1 + i) ** d_supp)
    term4 = cs / ((1 + i) ** avg_curr_days)
    outflow = term3 + term4
    
    npv = inflow - outflow

    # Limits (Excel Formulas)
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

def show_receivables_analyzer_ui():
    # 1. SYNC WITH CORE ENGINE
    metrics = sync_global_state()
    s = st.session_state
    
    # Fetch Baseline (Stage 0 Constants)
    sys_revenue = float(metrics.get('revenue', 0.0))
    sys_cogs = float(s.get('volume', 0)) * float(s.get('variable_cost', 0.0))
    sys_wacc = float(s.get('wacc', 0.15))
    sys_ar_days = float(s.get('ar_days', 45))
    sys_ap_days = float(s.get('ap_days', 30))

    st.title("📊 Strategic Receivables Analyzer (NPV Mode)")
    st.info("Locked parameters are sourced from your Global Baseline (Stage 0).")

    with st.form("npv_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Market Assumptions")
            c_sales = st.number_input("Current Sales (€)", value=sys_revenue, disabled=True)
            e_sales = st.number_input("Extra Sales Expected (€)", value=sys_revenue * 0.10)
            d_trial = st.number_input("Proposed Discount %", value=2.0, step=0.1) / 100
            p_take = st.number_input("% Clients who will take the Discount", value=40.0, step=1.0) / 100
            d_take = st.number_input("Days (Current - Take group)", value=int(sys_ar_days))
            
        with col2:
            st.markdown("### ⏱️ Timeline & Logic")
            d_new = st.number_input("New Payment Target (Days)", value=10, step=1)
            cogs_val = st.number_input("Cost of Goods Sold (COGS €)", value=sys_cogs, disabled=True)
            wacc_val = st.number_input("WACC % (Cost of Capital)", value=sys_wacc * 100, disabled=True) / 100
            d_supps = st.number_input("Supplier Payment Days (DPO)", value=int(sys_ap_days), disabled=True)
            d_no_take = st.number_input("Days (Current - No-Take group)", value=int(sys_ar_days * 2))

        submitted = st.form_submit_button("Execute Strategy Simulation", use_container_width=True)

    if submitted:
        r = calculate_discount_npv(c_sales, e_sales, d_trial, p_take, d_take, d_no_take, d_new, cogs_val, wacc_val, d_supps)
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Strategy NPV", f"€{r['npv']:,.2f}", delta="Profitable" if r['npv'] > 0 else "Loss", delta_color="normal" if r['npv'] > 0 else "inverse")
        c2.metric("Max Discount", f"{r['max_discount']:.2f}%")
        c3.metric("Optimum Discount", f"{r['optimum_discount']:.2f}%")

        

        if r['npv'] > 0:
            st.success("🎯 Positive NPV detected. You can apply this strategy to the Global Baseline.")
            if st.button("🚀 Apply & Sync with Global Baseline", type="primary", use_container_width=True):
                st.session_state.ar_days = d_new
                growth_factor = 1 + (e_sales / c_sales) if c_sales > 0 else 1
                st.session_state.volume = float(s.get('volume', 0)) * float(growth_factor)
                st.success("Baseline Updated. Rerunning Engine...")
                st.rerun()
        else:
            st.error("⚠️ Value Destruction: This policy results in a negative NPV. Strategy not recommended.")

        with st.expander("Detailed Calculation Audit"):
            st.write(f"Current Receivables: €{r['current_receivables']:,.2f}")
            st.write(f"New Receivables Post-Policy: €{r['new_receivables']:,.2f}")
            st.write(f"Free Capital Released: €{r['free_capital']:,.2f}")
            st.write(f"Profit from Expansion: €{r['profit_from_extra_sales']:,.2f}")

    if st.button("⬅️ Return to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
