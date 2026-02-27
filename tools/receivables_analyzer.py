import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, getcontext
from core.sync import sync_global_state # Η σύνδεση με την Engine

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

def show_receivables_analyzer_ui():
    # 1. SYNC WITH CORE ENGINE
    metrics = sync_global_state()
    s = st.session_state
    
    # Προετοιμασία τιμών από το σύστημα
    sys_revenue = float(metrics.get('revenue', 1000.0))
    sys_cogs = float(s.get('volume', 0)) * float(s.get('variable_cost', 0.0))
    sys_wacc = float(s.get('wacc', 0.15))
    sys_ar_days = float(s.get('ar_days', 45))
    sys_ap_days = float(s.get('ap_days', 30))

    st.title("📊 Strategic Receivables Analyzer (NPV Mode)")
    st.info("Aligned with Excel Model calculations (365-day basis).")

    with st.form("npv_form"):
        col1, col2 = st.columns(2)
        with col1:
            # Τραβάει το Revenue από το Stage 0
            c_sales = st.number_input("Current Sales (€)", value=sys_revenue)
            e_sales = st.number_input("Extra Sales (€)", value=sys_revenue * 0.25)
            d_trial = st.number_input("Discount %", value=2.0) / 100
            p_take = st.number_input("% Clients Take Discount", value=40.0) / 100
            # Τραβάει τις AR Days από το Stage 0 ή το CCC Tool
            d_take = st.number_input("Days (Current - for Take group)", value=int(sys_ar_days))
        with col2:
            d_no_take = st.number_input("Days (Current - for No-Take group)", value=int(sys_ar_days * 2.6))
            d_new = st.number_input("New Payment Days (Target)", value=10)
            # Τραβάει το COGS από το Stage 0
            cogs_val = st.number_input("COGS (€)", value=sys_cogs if sys_cogs > 0 else sys_revenue * 0.8)
            # Τραβάει το WACC
            wacc_val = st.number_input("WACC %", value=sys_wacc * 100) / 100
            # Τραβάει τις AP Days
            d_supps = st.number_input("Supplier Payment Days", value=int(sys_ap_days))
        
        submitted = st.form_submit_button("Run Analysis", use_container_width=True)

    if submitted:
        r = calculate_discount_npv(c_sales, e_sales, d_trial, p_take, d_take, d_no_take, d_new, cogs_val, wacc_val, d_supps)
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("NPV", f"€{r['npv']:,.2f}")
        c2.metric("Max Discount", f"{r['max_discount']:.2f}%")
        c3.metric("Optimum Discount", f"{r['optimum_discount']:.2f}%")
        
        with st.expander("View Full Calculations"):
            st.write(f"Current Receivables: €{r['current_receivables']:,.2f}")
            st.write(f"New Receivables: €{r['new_receivables']:,.2f}")
            st.write(f"Free Capital: €{r['free_capital']:,.2f}")
            st.write(f"Profit from Growth: €{r['profit_from_extra_sales']:,.2f}")
            st.write(f"Discount Cost: €{r['discount_cost']:,.2f}")

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()

# ΣΥΝΔΕΣΗ ΜΕ ΤΟ ΚΕΝΤΡΙΚΟ ΣΥΣΤΗΜΑ
        st.success("✅ Analysis Complete")
        if st.button("🚀 Apply this Policy to Global Baseline"):
            # 1. Ενημερώνουμε τις ημέρες είσπραξης στον Ταμειακό Κύκλο
            st.session_state.ar_days = d_new
            
            # 2. Ενημερώνουμε τον όγκο ή την τιμή στο Stage 0 
            # (Εδώ υποθέτουμε ότι οι 'Extra Sales' αυξάνουν το volume)
            current_vol = st.session_state.get('volume', 1000)
            extra_vol = float(e_sales) / float(st.session_state.get('price', 1.0))
            st.session_state.volume = current_vol + extra_vol
            
            st.info("Global Baseline Updated: AR Days and Volume synchronized.")
            st.rerun()
