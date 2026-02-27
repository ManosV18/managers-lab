import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.sync import sync_global_state

def show_growth_funding_needed():
    st.header("📈 Growth Funding Requirement (AFN)")
    st.info("Additional Funds Needed model based on Risk-Adjusted Net Profit.")

    # 1. FETCH CURRENT BASELINE
    metrics = sync_global_state()
    s = st.session_state
    
    if not metrics:
        st.warning("⚠️ Baseline not locked. Please return to Stage 0.")
        return

    # 2. FINANCIAL PARAMETERS (Interest & Tax Adjustment)
    st.subheader("📊 Profitability Adjustment")
    col_f1, col_f2 = st.columns(2)
    
    # Ο χρήστης ορίζει το μέσο επιτόκιο (Interest Rate) για το σύνολο του δανεισμού
    avg_interest_rate = col_f1.number_input("Average Interest Rate (%)", value=5.0, step=0.5, key="afn_int_rate") / 100
    tax_rate = float(s.get('tax_rate', 0.22))
    
    # Ανάκτηση EBIT και Debt Service από την Engine
    ebit = float(metrics.get('ebit', 0.0))
    # Υπολογίζουμε έναν εκτιμώμενο τόκο (Interest Expense) 
    # Αν δεν έχουμε το συνολικό κεφάλαιο δανείου, χρησιμοποιούμε το annual_debt_service ως προσέγγιση
    interest_expense = float(s.get('annual_debt_service', 0.0)) * 0.7 # Προσέγγιση: το 70% του service είναι τόκος
    
    # Υπολογισμός Net Profit: EBIT - Τόκοι - Φόροι
    ebt = ebit - interest_expense
    net_profit = ebt * (1 - tax_rate) if ebt > 0 else ebt
    
    current_sales = float(metrics.get('revenue', 0.0))
    # Νέο Net Profit Margin
    net_profit_margin = net_profit / current_sales if current_sales > 0 else 0

    st.caption(f"Calculated Net Profit: **€ {net_profit:,.2f}** | Net Margin: **{net_profit_margin:.2%}**")

    # 3. GROWTH SCENARIO
    st.subheader("🚀 Growth Scenario")
    c_in1, c_in2 = st.columns(2)
    target_growth_pct = c_in1.slider("Target Sales Growth (%)", 0.0, 100.0, 20.0, key="afn_growth_sl") / 100
    retention_rate = c_in2.slider("Retention Rate (%)", 0, 100, 100, key="afn_retention_sl") / 100
    
    delta_sales = current_sales * target_growth_pct
    new_total_sales = current_sales + delta_sales

    # 4. AFN RATIOS (Assets & Liabilities linkage)
    assets_ratio = 0.65  
    liabilities_ratio = 0.15 

    # 5. AFN FORMULA: (A*/S)ΔS - (L*/S)ΔS - (NetMargin * NewSales * Retention)
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

    # 7. VISUALIZATION
    fig = go.Figure(go.Waterfall(
        measure = ["relative", "relative", "relative", "total"],
        x = ["New Assets", "Spontaneous Liabs", "Net Profit Retained", "Funding Gap"],
        y = [required_assets, -spontaneous_liabs, -internal_funding, 0],
        text = [f"+{required_assets:,.0f}", f"-{spontaneous_liabs:,.0f}", f"-{internal_funding:,.0f}", f"{afn:,.0f}"],
        textposition = "outside",
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    

    # 8. VERDICT
    if afn > 0:
        st.error(f"🚨 **FINANCING GAP:** To support this growth, you must secure **€{afn:,.0f}** in new debt or equity. Organic cash flow is insufficient after interest and taxes.")
    else:
        st.success(f"✅ **ORGANIC SUSTAINABILITY:** The net profit (after tax & interest) is sufficient to fund the growth scenario.")

    if st.button("Back to Library Hub", use_container_width=True):
        st.session_state.selected_tool = None
        st.rerun()
