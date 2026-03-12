import streamlit as st
import plotly.graph_objects as go

def show_growth_funding_needed():
    st.header("📈 Growth Funding Requirement (AFN)")
    st.info("Additional Funds Needed model: Calculating the gap between growth ambitions and organic capital generation.")

    # 1. FETCH CURRENT BASELINE
    s = st.session_state
    m = s.get("metrics", {})
    
    if not s.get('baseline_locked', False):
        st.warning("🔒 Access Denied: Please lock your Baseline in Home to enable Growth Modeling.")
        return

    # 2. FINANCIAL PARAMETERS (Interest & Tax Adjustment)
    st.subheader("📊 Profitability Adjustment")
    col_f1, col_f2 = st.columns(2)
    
    avg_interest_rate = col_f1.number_input("Average Interest Rate (%)", value=5.0, step=0.5, key="afn_int_rate") / 100
    tax_rate = float(s.get('tax_rate', 0.22))
    
    # Logic: EBIT - Interest - Taxes
    ebit = float(m.get('ebit', 0.0))
    # Approximation: 70% of debt service is interest expense
    interest_expense = float(s.get('annual_debt_service', 0.0)) * 0.7 
    
    ebt = ebit - interest_expense
    net_profit = ebt * (1 - tax_rate) if ebt > 0 else ebt
    
    current_sales = float(m.get('revenue', 0.0))
    net_profit_margin = net_profit / current_sales if current_sales > 0 else 0

    st.caption(f"Calculated Net Profit: **€ {net_profit:,.2f}** | Net Margin: **{net_profit_margin:.2%}**")

    # 3. GROWTH SCENARIO
    st.subheader("🚀 Growth Scenario")
    c_in1, c_in2 = st.columns(2)
    target_growth_pct = c_in1.slider("Target Sales Growth (%)", 0.0, 100.0, 20.0, key="afn_growth_sl") / 100
    retention_rate = c_in2.slider("Retention Rate (%)", 0, 100, 100, key="afn_retention_sl") / 100
    
    delta_sales = current_sales * target_growth_pct
    new_total_sales = current_sales + delta_sales

    # 4. AFN RATIOS (Standard Operating Benchmarks)
    assets_ratio = 0.65  # Capital Intensity
    liabilities_ratio = 0.15 # Spontaneous financing (AP/Accruals)

    # 5. AFN FORMULA: (Required Assets) - (Spontaneous Liabs) - (Internal Funding)
    required_assets = assets_ratio * delta_sales
    spontaneous_liabs = liabilities_ratio * delta_sales
    internal_funding = net_profit_margin * new_total_sales * retention_rate
    
    afn = required_assets - spontaneous_liabs - internal_funding

    # 6. RESULTS
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("New Sales Target", f"€ {new_total_sales:,.0f}")
    m2.metric("Internal Reinvestment", f"€ {internal_funding:,.0f}")
    
    afn_val = max(0, afn)
    m3.metric("AFN (External Capital)", f"€ {afn_val:,.0f}", 
              delta="Capital Needed" if afn > 0 else "Self-Funded", 
              delta_color="inverse" if afn > 0 else "normal")

    # 7. VISUALIZATION (Waterfall Chart)
    
    fig = go.Figure(go.Waterfall(
        measure = ["relative", "relative", "relative", "total"],
        x = ["New Asset Requirement", "Spontaneous Liabs", "Retained Profit", "External Funding Gap"],
        y = [required_assets, -spontaneous_liabs, -internal_funding, 0],
        text = [f"+{required_assets:,.0f}", f"-{spontaneous_liabs:,.0f}", f"-{internal_funding:,.0f}", f"{afn:,.0f}"],
        textposition = "outside",
        connector = {"line":{"color":"#64748b"}},
        decreasing = {"marker":{"color":"#00CC96"}},
        increasing = {"marker":{"color":"#EF553B"}},
        totals = {"marker":{"color":"#1E3A8A"}}
    ))
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # 8. VERDICT (Cold & Direct)
    st.subheader("💡 Strategic Verdict")
    if afn > 0:
        st.error(f"**Financing Gap Detected:** Organic cash flow (after tax & interest) is insufficient. You need **€ {afn:,.0f}** in external debt or equity to sustain this growth rate without depleting liquidity.")
    else:
        st.success(f"**Organic Sustainability:** The system generates enough net profit to self-fund this growth scenario. No external capital is required.")

    # Navigation (Ευθυγραμμισμένο με το νέο app.py)
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
    
