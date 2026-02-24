# =========================================
# Stage 0: System Calibration
# =========================================
import streamlit as st
from core.engine import compute_core_metrics

def run_stage0():
    st.header("⚙️ Stage 0: System Calibration")
    st.caption("Establish the core economic parameters of the enterprise.")

    # Ορισμός βασικών columns για το layout
    col1, col2 = st.columns(2)

    # =============================
    # Revenue Structure
    # =============================
    with col1:
        st.subheader("Revenue Structure")
        st.session_state.price = st.number_input(
            "Price per Unit (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('price', 50.0))
        )
        st.session_state.volume = st.number_input(
            "Annual Volume (Units)", 
            min_value=0, 
            value=int(st.session_state.get('volume', 15000))
        )
        revenue = st.session_state.price * st.session_state.volume
        st.metric("Annual Revenue", f"{revenue:,.0f} €")

    # =============================
    # Cost Structure
    # =============================
    with col2:
        st.subheader("Cost Structure")
        st.session_state.variable_cost = st.number_input(
            "Variable Cost per Unit (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('variable_cost', 25.0))
        )
        st.session_state.fixed_cost = st.number_input(
            "Annual Fixed Costs (€)", 
            min_value=0.0, 
            value=float(st.session_state.get('fixed_cost', 200000.0))
        )

        p = st.session_state.price
        vc = st.session_state.variable_cost
        margin = (p - vc) / p if p > 0 else 0
        
        if p <= 0:
            st.error("❌ Price must be greater than zero.")
        elif p <= vc:
            st.error(f"❌ Critical: Negative/Zero Margin ({margin:.1%}).", 
                     help="Value destruction: You are losing money on every unit produced before fixed costs.")
        elif margin < 0.20:
            st.warning(f"⚠️ Low structural buffer ({margin:.1%}). High sensitivity to volume shifts.")
        else:
            st.success(f"✅ Healthy Margin: {margin:.1%}")

    # =============================
    # Core Metrics Preview (Live)
    # =============================
    st.divider()
    metrics = compute_core_metrics()
    col_b1, col_b2 = st.columns(2)
    col_b1.metric("Operating Break-Even (Units)", f"{metrics.get('operating_bep',0):,.0f}")
    col_b2.metric("Unit Contribution", f"{metrics.get('unit_contribution',0):,.2f} €")

    # =============================
    # Working Capital Cycle
    # =============================
    st.divider()
    st.subheader("⏳ Cash Timing & Durability")
    with st.expander("Configure Working Capital Cycle", expanded=False):
        st.caption("Adjust operational cash timing and inventory friction.")
        c1, c2, c3, c4 = st.columns(4)
        
        st.session_state.ar_days = c1.number_input("Receivables (DSO)", min_value=0, value=int(st.session_state.get('ar_days', 45)))
        st.session_state.inventory_days = c2.number_input("Inventory (DIO)", min_value=0, value=int(st.session_state.get('inventory_days', 60)))
        st.session_state.payables (DPO) = c3.number_input("Payables (DPO)", min_value=0, value=int(st.session_state.get('payables_days', 30)))
        
        # Προσθήκη Slow Moving Factor βάσει παρατηρήσεων
        slow_pct = c4.number_input("Slow-Stock (%)", min_value=0, max_value=100, value=int(st.session_state.get('slow_moving_factor', 0.2)*100))
        st.session_state.slow_moving_factor = slow_pct / 100

    # Αναλυτικός υπολογισμός Liquidity Drain (365 days)
    # Inventory & Payables υπολογίζονται επί του COGS, Receivables επί του Revenue
    cogs_annual = st.session_state.variable_cost * st.session_state.volume
    revenue_annual = st.session_state.price * st.session_state.volume
    
    ccc = st.session_state.ar_days + st.session_state.inventory_days - st.session_state.payables_days
    st.session_state.ccc = ccc
    
    ar_funding = revenue_annual * (st.session_state.ar_days / 365)
    inv_funding = cogs_annual * (st.session_state.inventory_days / 365)
    pay_offset = cogs_annual * (st.session_state.payables_days / 365)
    
    # Προσθήκη friction από αργοκίνητο απόθεμα
    inventory_friction = inv_funding * st.session_state.slow_moving_factor
    
    total_wc_req = ar_funding + inv_funding - pay_offset + inventory_friction
    st.session_state.working_capital_req = total_wc_req
    st.session_state.liquidity_drain_annual = total_wc_req

    col_c1, col_c2 = st.columns(2)
    col_c1.metric("Cash Conversion Cycle", f"{ccc} Days")
    col_c2.metric("Total Liquidity Drain", f"{total_wc_req:,.0f} €", help="Cash tied up in operations.")

    # =============================
    # Financial Structure
    # =============================
    st.divider()
    st.subheader("🏦 Financial Structure")
    f1, f2, f3 = st.columns(3)
    
    tax_in = f1.number_input("Tax Rate (%)", 0.0, 100.0, float(st.session_state.get('tax_input_field', 22.0)), 0.5, key="tax_input_field")
    int_in = f2.number_input("Cost of Debt (%)", 0.0, 100.0, float(st.session_state.get('interest_input_field', 5.0)), 0.5, key="interest_input_field")
    wacc_in = f3.number_input("WACC (%)", 0.0, 100.0, float(st.session_state.get('wacc_input_field', 12.0)), 0.5, key="wacc_input_field")
    
    st.session_state.tax_rate = tax_in / 100
    st.session_state.interest_rate = int_in / 100
    st.session_state.wacc = wacc_in / 100

    # =============================
    # Navigation
    # =============================
    st.divider()
    if st.button("Lock Baseline & Continue ➡️", use_container_width=True, type="primary"):
        if st.session_state.price > st.session_state.variable_cost:
            st.session_state.baseline_locked = True
            st.session_state.flow_step = 1
            st.session_state.mode = "path"
            st.toast("Baseline Locked ✅ Moving to Break-Even Analysis.")
            st.rerun()
        else:
            st.error("Cannot lock: Unit economics are non-viable (Negative Margin).")
