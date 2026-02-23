import streamlit as st
import pandas as pd
from core.engine import compute_core_metrics

def show_growth_funding_needed():
    st.header("📈 Growth Funding Requirement (AFN)")
    st.info("Predict how much new capital is required to support an increase in sales.")

    # 1. FETCH CURRENT BASELINE
    metrics = compute_core_metrics()
    s = st.session_state
    
    current_sales = metrics.get('revenue', 0)
    current_profit = metrics.get('net_profit', 0)
    
    # Safe calculation of profit margin to avoid KeyError
    current_profit_margin = current_profit / current_sales if current_sales > 0 else 0
    
    # Retention rate (how much profit stays in the company)
    # Default 0.5 (50%) if not set
    retention_rate = s.get('retention_rate', 0.5)

    # 2. USER INPUT: GROWTH TARGET
    st.subheader("Growth Scenario")
    target_growth_pct = st.slider("Target Sales Growth (%)", 0.0, 100.0, 20.0) / 100
    
    delta_sales = current_sales * target_growth_pct
    new_total_sales = current_sales + delta_sales

    # 3. AFN RATIOS (Based on your uploaded image)
    # Assets that increase with sales (69%)
    # Liabilities that increase spontaneously (15%)
    assets_ratio = 0.69  
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
    c2.metric("Total Funding Needed", f"€ {required_increase_assets:,.0f}")
    c3.metric("AFN (External Capital)", f"€ {max(0, afn):,.0f}", 
              delta="Required Funds" if afn > 0 else "Surplus", 
              delta_color="inverse")

    # 6. ANALYTICAL BREAKDOWN
    st.subheader("Financial Gap Analysis")
    
    breakdown_data = {
        "Component": ["Asset Expansion (+)", "Spontaneous Liabs (-)", "Retained Earnings (-)"],
        "Amount (€)": [
            f"€ {required_increase_assets:,.0f}",
            f"€ {spontaneous_increase_liabilities:,.0f}",
            f"€ {internal_funding_from_profits:,.0f}"
        ],
        "Description": ["New equipment/inventory", "Credit from suppliers", "Internal cash from sales"]
    }
    st.table(pd.DataFrame(breakdown_data))

    # 7. STRATEGIC VERDICT
    if afn > 0:
        st.warning(f"⚠️ **Gap identified:** To grow by {target_growth_pct:.0%}, you must secure **€{afn:,.0f}** from banks or investors.")
    else:
        st.success(f"✅ **Self-Sufficient:** Current margins allow for {target_growth_pct:.0%} growth without external debt.")
