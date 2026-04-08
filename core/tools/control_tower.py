import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from core.engine import calculate_metrics

def _safe_get(key, default=0.0):
    """Safe session_state getter with float casting."""
    try:
        val = st.session_state.get(key, default)
        return float(val) if val is not None else float(default)
    except Exception:
        return float(default)

def show_control_tower():
    st.title("🕹️ Mission Control: Enterprise Tower")
    st.caption("Integrated Strategic & Financial Oversight")
    
    s = st.session_state
    
    # --- 1. LIVE SYNC ---
    m = calculate_metrics(
        price=_safe_get('price', 150.0),
        volume=_safe_get('volume', 15000.0),
        variable_cost=_safe_get('variable_cost', 90.0),
        fixed_cost=_safe_get('fixed_cost', 450000.0),
        ar_days=_safe_get('ar_days', 60),
        inv_days=_safe_get('inv_days', 45),
        ap_days=_safe_get('ap_days', 30),
        annual_debt_service=_safe_get('annual_debt_service', 70000.0),
        opening_cash=_safe_get('opening_cash', 150000.0),
        total_debt=_safe_get('total_debt', 500000.0),
        fixed_assets=_safe_get('fixed_assets', 800000.0)
    )
    s.metrics = m

    # --- 1.1 BASELINE CALCULATION (For Delta WC Logic) ---
    if 'baseline_nwc' not in s:
        b = calculate_metrics(
            price=150.0, 
            volume=15000.0, 
            variable_cost=90.0, 
            fixed_cost=450000.0,
            ar_days=60, 
            inv_days=45, 
            ap_days=30,
            annual_debt_service=_safe_get('annual_debt_service', 70000.0),
            opening_cash=_safe_get('opening_cash', 150000.0)
        )
        s.baseline_nwc = (b.get('ar_value', 0.0) + b.get('inv_value', 0.0)) - b.get('ap_value', 0.0)
    
    # --- 2. TOP LEVEL METRICS (Dynamic Strategic FCF) ---
    revenue = m.get("revenue", 0.0)
    net_profit = m.get("net_profit", 0.0)
    depreciation = _safe_get('depreciation', 0.0)
    debt_service = _safe_get('annual_debt_service', 0.0)
    
    current_nwc = (m.get('ar_value', 0.0) + m.get('inv_value', 0.0)) - m.get('ap_value', 0.0)
    wc_cash_impact = current_nwc - s.baseline_nwc 
    
    fcf = net_profit + depreciation - debt_service - wc_cash_impact
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual Revenue", f"${revenue:,.0f}")
    c2.metric("Net Profit (P&L)", f"${net_profit:,.0f}")
    
    fcf_color = "normal" if fcf > 0 else "inverse"
    c3.metric("Free Cash Flow", f"${fcf:,.0f}", delta=f"{fcf-net_profit:,.0f} vs Profit", delta_color=fcf_color)
    
    wacc_locked = s.get('wacc_locked', 15.0)
    c4.metric("WACC Target", f"{wacc_locked:.2f}%")
    
    st.divider()

    # --- 3. QUADRANTS ---
    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    with q1: # QUADRANT 1: BREAK-EVEN CHART
        st.subheader("🎯 Profitability Hub")
        p = _safe_get('price', 150.0)
        v = _safe_get('volume', 15000.0)
        vc = _safe_get('variable_cost', 90.0)
        fc = _safe_get('fixed_cost', 450000.0)
        
        upper_limit = int(v * 2) if v > 0 else 1000
        step = int(max(1, upper_limit / 10))
        v_range = list(range(0, upper_limit + step, step))
        
        df_be = pd.DataFrame({
            "Units": v_range,
            "Revenue": [vol * p for vol in v_range],
            "Total Costs": [fc + (vol * vc) for vol in v_range]
        })
        
        fig_be = go.Figure()
        fig_be.add_trace(go.Scatter(x=df_be["Units"], y=df_be["Revenue"], name="Revenue", line=dict(color='#10b981', width=3)))
        fig_be.add_trace(go.Scatter(x=df_be["Units"], y=df_be["Total Costs"], name="Total Costs", line=dict(color='#ef4444', width=3)))
        fig_be.add_vline(x=v, line_dash="dash", line_color="white", annotation_text="Current Volume")

        fig_be.update_layout(
            height=300, template="plotly_dark", margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", y=1.1), xaxis_title="Volume (Units)", yaxis_title="Value ($)"
        )
        st.plotly_chart(fig_be, use_container_width=True)

    with q2: # QUADRANT 2: LIQUIDITY (CCC)
        st.subheader("💧 Working Capital Velocity")
        ccc = m.get("ccc", 0.0)
        st.write(f"**CCC:** {ccc:.0f} Days")
        ar, inv, ap = _safe_get("ar_days", 30), _safe_get("inv_days", 60), _safe_get("ap_days", 45)
        
        fig_ccc = go.Figure(go.Bar(
            y=['Receivables', 'Inventory', 'Payables'], 
            x=[ar, inv, -ap], 
            orientation='h', 
            marker_color=['#3b82f6', '#f59e0b', '#ef4444']
        ))
        fig_ccc.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), template="plotly_dark")
        st.plotly_chart(fig_ccc, use_container_width=True)

    with q3: # QUADRANT 3: RISK RADAR
        st.subheader("🛡️ Risk Radar")
        cash = m.get('net_cash_position', 0.0)
        daily_burn = (fc + (v * vc)) / 365 
        survival_days = int(cash / daily_burn) if daily_burn > 0 else 0
        
        day_label = "Day" if survival_days == 1 else "Days"
        st.metric("Survival (Zero Income)", f"{survival_days} {day_label}")
        
        if survival_days < 30: st.error("🚨 Critical Runway: High Fragility Detected")
        elif survival_days < 90: st.warning("⚠️ Tight Runway: Monitor Cash Cycle")
        else: st.success("✅ Safe Runway: Structural Resilience")

    with q4: # QUADRANT 4: VALUE CREATION (ROIC)
        st.subheader("🚀 Value Creation")
        roic = m.get("roic", 0.0) * 100
        spread = roic - wacc_locked
        st.metric("ROIC", f"{roic:.2f}%", delta=f"{spread:.2f}% vs WACC")
        if spread > 0: st.success("Value Creation")
        else: st.error("Value Destruction")

    # --- 4. STRATEGIC INTELLIGENCE CHECKLIST ---
    st.markdown("### 🧠 Strategic Intelligence Checklist")
    col_ch1, col_ch2, col_ch3 = st.columns(3)
    
    with col_ch1:
        st.info("**Pricing Power**\n\nCan you raise prices by 2% without losing 5% volume? If not, your brand is fragile.")
    with col_ch2:
        st.info("**Cash Velocity**\n\nIf you increase AR Days by 10, how many thousands in FCF do you 'sacrifice'?")
    with col_ch3:
        st.info("**Survival Buffer**\n\nIs your survival runway (>90 days) enough to pivot your entire business model?")

    st.divider()

        # --- 5. STRATEGIC GAP ANALYSIS (The "Fix-it" Logic) ---
    st.subheader(f"🛠️ Strategic Gap Analysis: How to fix the ${abs(wc_cash_impact):,.0f} hole")
    
    current_v = _safe_get('volume', 15000.0)
    current_vc = _safe_get('variable_cost', 90.0)
    
    daily_cogs = (current_vc * current_v) / 365
    required_days = wc_cash_impact / daily_cogs if daily_cogs > 0 else 0

    col1, col2 = st.columns(2)

    # --- OPTION 1 ---
    with col1:
        st.write("#### Option 1: Pressure Suppliers")
        st.warning(f"To offset this, you must increase Payables by **{required_days:.1f} days**.")
        st.caption(f"Target AP Days: {_safe_get('ap_days', 30) + required_days:.0f} Days")

    # --- OPTION 2 ---
    with col2:
        st.write("#### Option 2: Lean Operations")
        inv_days_now = _safe_get('inv_days', 45)

        max_inventory_reduction = inv_days_now
        
        if required_days > max_inventory_reduction:
            st.error(
                f"Not enough: maximum inventory reduction only saves "
                f"**{max_inventory_reduction:.1f} days**."
            )
        else:
            st.success(f"Reduce Inventory by **{required_days:.1f} days** to break even on cash.")

    # --- STRATEGIC INSIGHT ---
    st.markdown("### 🧠 Strategic Insight")

    if required_days > inv_days_now:
        st.info(
            "No single lever closes the gap. "
            "A **combined strategy** is required:\n\n"
            "• Extend payables\n"
            "• Reduce inventory\n"
            "• Accelerate receivables"
        )
    else:
        st.success(
            "Gap can be closed with a single operational adjustment."
        )
