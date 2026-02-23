import streamlit as st
from core.engine import compute_core_metrics

def show_growth_funding_needed():
    st.header("📈 Growth Funding Requirement (AFN)")
    st.info("Predict how much new capital is required to support an increase in sales.")

    # 1. FETCH CURRENT BASELINE
    metrics = compute_core_metrics()
    s = st.session_state
    
    current_sales = metrics['revenue']
    current_profit_margin = metrics['net_profit_margin']
    # Αν δεν υπάρχει retention_rate, υποθέτουμε 50% (επαναπένδυση κερδών)
    retention_rate = s.get('retention_rate', 0.5)

    # 2. USER INPUT: GROWTH TARGET
    st.subheader("Growth Scenario")
    target_growth_pct = st.slider("Target Sales Growth (%)", 0.0, 100.0, 20.0) / 100
    
    delta_sales = current_sales * target_growth_pct
    new_total_sales = current_sales + delta_sales

    # 3. SPONTANEOUS ASSETS & LIABILITIES (Based on your image logic)
    # Χρησιμοποιούμε placeholders ή τραβάμε από το session αν υπάρχουν
    assets_ratio = 0.69  # Από την εικόνα σου (Σύνολο Ενεργητικού 69%)
    liabilities_ratio = 0.15 # Από την εικόνα σου (Σύνολο Παθητικού 15%)

    # 4. AFN FORMULA
    # AFN = (A*/S)ΔS - (L*/S)ΔS - MS1(RR)
    required_increase_assets = assets_ratio * delta_sales
    spontaneous_increase_liabilities = liabilities_ratio * delta_sales
    internal_funding_from_profits = current_profit_margin * new_total_sales * retention_rate
    
    afn = required_increase_assets - spontaneous_increase_liabilities - internal_funding_from_profits

    # 5. RESULTS DASHBOARD
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    c1.metric("New Sales Target", f"€ {new_total_sales:,.0f}")
    c2.metric("Total Funding Needed", f"€ {required_increase_assets:,.0f}")
    c3.metric("AFN (New Capital)", f"€ {max(0, afn):,.0f}", delta="External Funds", delta_color="inverse")

    # 6. ANALYTICAL BREAKDOWN
    st.subheader("Financial Gap Breakdown")
    
    breakdown_data = {
        "Requirement": ["Asset Expansion", "Spontaneous Financing", "Retained Earnings", "External Funding (AFN)"],
        "Amount (€)": [
            f"€ {required_increase_assets:,.0f}",
            f"€ {spontaneous_increase_liabilities:,.0f}",
            f"€ {internal_funding_from_profits:,.0f}",
            f"€ {max(0, afn):,.0f}"
        ]
    }
    st.table(pd.DataFrame(breakdown_data))

    # 7. STRATEGIC VERDICT
    if afn > 0:
        st.warning(f"⚠️ **Funding Gap:** To achieve {target_growth_pct:.0%} growth, you need **€{afn:,.0f}** in new loans or equity.")
    else:
        st.success(f"✅ **Self-Funded:** Your profit margins are high enough to support this growth internally.")
