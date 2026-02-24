import streamlit as st
from core.engine import compute_core_metrics

def show_cash_fragility_index():
    st.header("🛡️ Cash Fragility Index")
    st.info("Stress Test: How many days can the business survive if all inflows (collections) stop today?")

    # 1. READ FROM CORE & ENGINE (Shared Data)
    metrics = compute_core_metrics()
    
    # Use 'cash_wall' from Engine (Fixed Costs + Debt Service)
    # This represents the true structural "Burn" for survival.
    total_survival_burn_annual = metrics.get('cash_wall', 0.0)
    daily_burn_rate = total_survival_burn_annual / 365

    st.write(f"**Annual Cash Obligations (Fixed Costs + Debt Service):** {total_survival_burn_annual:,.2f} €/year")
    st.write(f"**Calculated Daily Burn Rate:** {daily_burn_rate:,.2f} €/day")

    st.divider()

    # 2. USER INPUTS (Liquidity Assessment)
    col1, col2 = st.columns(2)
    with col1:
        current_cash = st.number_input("Current Cash in Bank (€)", min_value=0.0, value=10000.0)
    with col2:
        unused_credit_lines = st.number_input("Available Credit Lines / Overdraft (€)", min_value=0.0, value=5000.0)

    total_liquidity = current_cash + unused_credit_lines

    # 3. CALCULATIONS
    if daily_burn_rate > 0:
        days_to_zero = total_liquidity / daily_burn_rate
    else:
        days_to_zero = float('inf')

    # 4. RESULTS & VISUALS
    st.subheader("Survival Runway")
    
    if days_to_zero < 30:
        status = "CRITICAL FRAGILITY"
        st.error(f"🚨 {status}")
    elif days_to_zero < 60:
        status = "LOW BUFFER"
        st.warning(f"⚠️ {status}")
    else:
        status = "STABLE"
        st.success(f"✅ {status}")

    st.metric("Days of Survival", f"{int(days_to_zero)} Days", delta=f"{status}")
    
    # Progress bar mapped to a 120-day ideal buffer
    progress_val = min(days_to_zero / 120, 1.0)
    st.progress(progress_val)
    st.caption("Safety threshold: 60-90 days of fixed obligations. Target: 120 days.")

    

    st.divider()

    # 5. COLD INSIGHT & STRATEGIC VERDICT
    st.subheader("🧠 Strategic Verdict")
    
    safe_liquidity = daily_burn_rate * 90
    gap = max(0.0, safe_liquidity - total_liquidity)
    
    if gap > 0:
        st.markdown(f"""
        To achieve a 'Safe' status (90 days of autonomy), you require a total liquidity of **{safe_liquidity:,.2f} €**.
        
        **Liquidity Gap:** **{gap:,.2f} €**.
        
        **Recommended Actions:**
        1. **Accelerate Collections:** Reduce DSO using the Receivables Manager.
        2. **Inventory Liquidation:** Release cash from slow-moving stock using the Inventory Manager.
        3. **Debt Restructuring:** Negotiate lower installments to reduce the Daily Burn rate.
        """)
    else:
        st.markdown(f"""
        The business is in a **Position of Strength**. You possess sufficient liquidity to absorb significant market shocks without jeopardizing operational continuity.
        """)

    if st.button("Back to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
