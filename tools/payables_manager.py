# tools/payables_manager.py
"""
Payables Strategic Control
Optimize supplier payment strategies using WACC and NPV analysis
"""

import streamlit as st
from core.engine import compute_core_metrics


def show_payables_manager():
    st.header("🤝 Payables Strategic Control")
    st.info("Using Corporate WACC as the hurdle rate to optimize supplier payment strategies and cash retention.")
    
    # ═══════════════════════════════════════════════════════════
    # 1. FETCH GLOBAL DATA
    # ═══════════════════════════════════════════════════════════
    metrics = compute_core_metrics()
    
    q = st.session_state.get('volume', 0)
    vc = st.session_state.get('variable_cost', 0.0)
    
    # Annual purchases estimated based on Variable Cost
    annual_purchases = q * vc
    current_ap_days = st.session_state.get('payables_days', 30)
    
    # Using WACC as the opportunity cost of cash
    hurdle_rate = metrics['wacc'] 
    
    st.write(f"**🔗 Opportunity Cost (WACC):** {hurdle_rate:.1%}")
    
    # ═══════════════════════════════════════════════════════════
    # 2. TABS
    # ═══════════════════════════════════════════════════════════
    tab1, tab2 = st.tabs(["💰 Cash Flow Impact", "⚖️ NPV Optimizer (Excel View)"])
    
    # ───────────────────────────────────────────────────────────
    # TAB 1: Cash Flow Impact
    # ───────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Liquidity Optimization")
        
        new_ap_days = st.slider(
            "Target Payment Terms (Days)", 
            0, 150, 
            int(current_ap_days), 
            key="ap_slider"
        )
        
        # Calculation of cash released/trapped
        cash_impact = ((new_ap_days - current_ap_days) / 365) * annual_purchases
        value_benefit = cash_impact * hurdle_rate
        
        c1, c2 = st.columns(2)
        
        c1.metric(
            "Net Cash Impact", 
            f"€ {cash_impact:,.2f}", 
            delta=f"{new_ap_days - current_ap_days} Days Shift"
        )
        
        c2.metric(
            "Annual Value Benefit", 
            f"€ {max(0.0, value_benefit):,.2f}"
        )
    
    # ───────────────────────────────────────────────────────────
    # TAB 2: NPV Optimizer (Excel Logic)
    # ───────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Early Payment Discount Analysis")
        st.caption("NPV-based evaluation of early payment discount strategies")
        
        # Current sales from system
        current_sales = st.session_state.get('price', 0) * st.session_state.get('volume', 0)
        cogs = annual_purchases  # COGS = annual purchases
        
        # Input columns
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**📊 Strategic Parameters**")
            e_sales = st.number_input(
                "Extra Sales (€)", 
                value=250.0, 
                step=10.0,
                help="Additional sales from taking early payment discount"
            )
            disc_trial = st.number_input(
                "Discount Offered (%)", 
                value=2.0,
                min_value=0.0,
                max_value=10.0,
                step=0.1
            ) / 100
            prc_take = st.number_input(
                "% Clients Taking Discount", 
                value=40.0,
                min_value=0.0,
                max_value=100.0,
                step=1.0
            ) / 100
        
        with col_b:
            st.markdown("**📅 Payment Timing**")
            d_take = st.number_input(
                "Days if Taking Discount", 
                value=10,
                min_value=0,
                max_value=365
            )
            d_not = st.number_input(
                "Days if NOT Taking Discount", 
                value=30,
                min_value=0,
                max_value=365
            )
            n_days = st.number_input(
                "New Policy Days Limit", 
                value=10,
                min_value=0,
                max_value=365
            )
        
        # ═══════════════════════════════════════════════════════════
        # EXCEL FORMULAS (One-to-One)
        # ═══════════════════════════════════════════════════════════
        prc_not_take = 1.0 - prc_take
        
        # Current average collection period
        avg_curr_days = (d_take * prc_take) + (d_not * prc_not_take)
        curr_receiv = (current_sales * avg_curr_days) / 365
        
        # New scenario
        total_sales = current_sales + e_sales
        prc_new_pol = ((current_sales * prc_take) + e_sales) / total_sales if total_sales > 0 else 0
        prc_old_pol = 1.0 - prc_new_pol
        
        new_avg_period = (prc_new_pol * n_days) + (prc_old_pol * d_not)
        new_receiv = (total_sales * new_avg_period) / 365
        
        free_cap = curr_receiv - new_receiv
        
        # Yellow Fields (Profit components)
        gross_margin = 1.0 - (cogs / current_sales) if current_sales > 0 else 0
        prof_extra = e_sales * gross_margin
        prof_free_cap = free_cap * hurdle_rate
        cost_disc = total_sales * prc_new_pol * disc_trial
        
        final_npv = prof_extra + prof_free_cap - cost_disc
        
        # Thresholds
        daily_wacc = 1.0 + (hurdle_rate / 365)
        max_d = 1.0 - (daily_wacc ** (n_days - avg_curr_days))
        opt_d = 1.0 - (daily_wacc ** (n_days - d_not))
        
        # ═══════════════════════════════════════════════════════════
        # RESULTS DISPLAY
        # ═══════════════════════════════════════════════════════════
        st.divider()
        st.subheader("📈 NPV Analysis Results")
        
        # Metrics display
        res1, res2, res3 = st.columns(3)
        
        res1.metric("Free Capital", f"€ {free_cap:,.2f}")
        res2.metric("Profit from Extra Sales", f"€ {prof_extra:,.2f}")
        res3.metric("Profit from Free Capital", f"€ {prof_free_cap:,.2f}")
        
        st.divider()
        
        col_npv1, col_npv2 = st.columns(2)
        
        with col_npv1:
            st.metric(
                "💰 Net Present Value (NPV)",
                f"€ {final_npv:,.2f}",
                delta="Total Value Created"
            )
            st.metric("Discount Cost", f"€ {cost_disc:,.2f}")
        
        with col_npv2:
            st.metric("Maximum Discount", f"{max_d:.2%}")
            st.metric("Optimum Discount", f"{opt_d:.2%}")
        
        # Strategic verdict
        st.divider()
        
        if final_npv > 0:
            st.success(f"✅ **Verdict: ACCEPT STRATEGY.** NPV is positive (€{final_npv:,.2f}). The discount strategy creates value.")
        else:
            st.error(f"🚨 **Verdict: REJECT STRATEGY.** NPV is negative (€{final_npv:,.2f}). The discount cost exceeds the benefits.")
    
    # ═══════════════════════════════════════════════════════════
    # 3. SYNC BUTTON
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    if st.button("Sync Target Days to Global Strategy", type="primary"):
        st.session_state.payables_days = new_ap_days
        st.success(f"✅ Global Payables Days updated to {new_ap_days} days.")
        st.rerun()
