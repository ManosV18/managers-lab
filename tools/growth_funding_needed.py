import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.engine import compute_core_metrics

def show_growth_funding_needed():
    st.header("📈 Growth Funding Requirement (AFN)")
    st.info("Predict how much new external capital is required to support an increase in sales based on the Additional Funds Needed (AFN) model.")

    # 1. FETCH CURRENT BASELINE
    metrics = compute_core_metrics()
    s = st.session_state
    
    current_sales = metrics.get('revenue', 0.0)
    current_profit = metrics.get('net_profit', 0.0)
    
    # Αναλογία κέρδους (Profit Margin)
    current_profit_margin = current_profit / current_sales if current_sales > 0 else 0
    
    # Πόσο από το κέρδος μένει στην εταιρεία (Retention Rate)
    # Αν δεν υπάρχει στο state, ορίζουμε 100% (δεν δίνονται μερίσματα) για Cold Analysis
    retention_rate = s.get('retention_rate', 1.0)

    # 2. USER INPUT: GROWTH TARGET
    st.subheader("Growth Scenario")
    col_in1, col_in2 = st.columns(2)
    
    target_growth_pct = col_in1.slider("Target Sales Growth (%)", 0.0, 100.0, 20.0) / 100
    retention_rate = col_in2.slider("Retention Rate (%)", 0, 100, int(retention_rate * 100)) / 100
    
    delta_sales = current_sales * target_growth_pct
    new_total_sales = current_sales + delta_sales

    # 3. AFN RATIOS (Standard Industrial Benchmarks)
    # Assets that increase with sales (Inventory, AR, Cash)
    assets_ratio = 0.69  
    # Liabilities that increase spontaneously (Accounts Payable, Accruals)
    liabilities_ratio = 0.15 

    # 4. AFN FORMULA: AFN = (A*/S)ΔS - (L*/S)ΔS - (Margin * NewSales * Retention)
    required_increase_assets = assets_ratio * delta_sales
    spontaneous_increase_liabilities = liabilities_ratio * delta_sales
    internal_funding_from_profits = current_profit_margin * new_total_sales * retention_rate
    
    afn = required_increase_assets - spontaneous_increase_liabilities - internal_funding_from_profits

    # 5. RESULTS DASHBOARD
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    c1.metric("New Sales Target", f"€ {new_total_sales:,.0f}")
    c2.metric("Asset Funding Need", f"€ {required_increase_assets:,.0f}", help="The total amount of new assets required to support the new sales volume.")
    
    afn_val = max(0, afn)
    st.session_state['afn_result'] = afn_val
    
    c3.metric("AFN (External Capital)", f"€ {afn_val:,.0f}", 
              delta="Required Funds" if afn > 0 else "Surplus Cash", 
              delta_color="inverse" if afn > 0 else "normal")

    # 6. VISUALIZATION: WATERFALL OF FUNDING
    st.subheader("📊 Funding Gap Breakdown")
    
    fig = go.Figure(go.Waterfall(
        name = "AFN", orientation = "v",
        measure = ["relative", "relative", "relative", "total"],
        x = ["New Assets Needed", "Spontaneous Liabs", "Internal Profits", "Funding Gap (AFN)"],
        textposition = "outside",
        text = [f"+{required_increase_assets:,.0f}", f"-{spontaneous_increase_liabilities:,.0f}", f"-{internal_funding_from_profits:,.0f}", f"={afn:,.0f}"],
        y = [required_increase_assets, -spontaneous_increase_liabilities, -internal_funding_from_profits, 0],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))

    fig.update_layout(template="plotly_dark", height=450, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    

    # 7. COLD STRATEGIC VERDICT
    st.divider()
    if afn > 0:
        st.warning(f"⚠️ **Strategic Risk:** Για να επιτύχετε ανάπτυξη {target_growth_pct:.0%}, χρειάζεστε **€{afn:,.0f}** εξωτερικά κεφάλαια (Δάνεια ή Equity). Αν δεν τα βρείτε, η ανάπτυξη θα προκαλέσει ασφυξία στη ρευστότητα.")
    else:
        st.success(f"✅ **Organic Growth:** Η κερδοφορία σας είναι αρκετή για να χρηματοδοτήσει αυτό το σενάριο ανάπτυξης εσωτερικά. Δεν απαιτείται νέος δανεισμός.")

    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
