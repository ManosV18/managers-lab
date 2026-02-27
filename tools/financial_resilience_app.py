import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from core.sync import sync_global_state

def analyze_resilience(profit, assets, current_assets, current_liabilities):
    roa = (profit / assets) * 100 if assets > 0 else 0
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
    return round(roa, 2), round(current_ratio, 2)

def show_resilience_map():
    # 1. SYNC WITH GLOBAL BASELINE
    metrics = sync_global_state()
    s = st.session_state
    
    # Auto-fetch from Global Engine
    sys_net_profit = float(metrics.get('net_profit', 0.0))
    # Note: Assets and Liabilities are pulled from your Stage 0 setup
    sys_assets = float(s.get('total_assets', 100000.0)) 
    sys_c_assets = float(s.get('current_assets', 50000.0))
    sys_c_liabilities = float(s.get('current_liabilities', 40000.0))

    st.header("🛡️ Financial Resilience & Shock Absorption Map")
    st.caption("Strategic assessment of the system's structural integrity and survival capacity.")

    # 2. CALCULATION
    roa, c_ratio = analyze_resilience(sys_net_profit, sys_assets, sys_c_assets, sys_c_liabilities)

    # 3. VISUALIZATION (2x2 Resilience Matrix)
    st.subheader("📍 Strategic Positioning")
    fig, ax = plt.subplots(figsize=(8, 7))
    
    # Standardized axis for comparative analysis
    ax.set_xlim(0, 4)  
    ax.set_ylim(-10, 30) 
    
    # Critical Thresholds
    ax.axhline(10, color='black', linewidth=1, linestyle='--') # Profitability Floor
    ax.axvline(1.5, color='black', linewidth=1, linestyle='--') # Liquidity Floor
    
    # Quadrant Definitions
    ax.text(0.2, 25, "Growth Trap\n(Illiquid / Over-leveraged)", fontsize=10, color='orange', fontweight='bold')
    ax.text(2.2, 25, "The Fortress\n(Anti-Fragile / Efficient)", fontsize=10, color='green', fontweight='bold')
    ax.text(0.2, -5, "Danger Zone\n(High Insolvency Risk)", fontsize=10, color='red', fontweight='bold')
    ax.text(2.2, -5, "Safe Storage\n(Low Capital Efficiency)", fontsize=10, color='blue', fontweight='bold')

    # Plot Current Position
    ax.scatter(c_ratio, roa, color='red', s=300, edgecolors='black', zorder=5)
    ax.annotate(f"CURRENT STATE\n(CR: {c_ratio}, ROA: {roa}%)", (c_ratio, roa), 
                textcoords="offset points", xytext=(0,20), ha='center', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))

    ax.set_xlabel("Liquidity Buffer (Current Ratio)")
    ax.set_ylabel("Operational Efficiency (ROA %)")
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)

    

    # 4. ANALYTICAL VERDICT
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧠 Liquidity Shock Profile")
        if c_ratio < 1.0:
            st.error("**Insolvency Threshold:** The system cannot survive a 10% delay in receivables. Immediate capital injection or credit restructuring required.")
        elif c_ratio < 1.5:
            st.warning("**Lean Operating Model:** High efficiency but zero room for error. A single 'Black Swan' event will trigger a liquidity crisis.")
        else:
            st.success("**Strategic Buffer:** High shock absorption. The system can withstand major market contractions.")

    with col2:
        st.markdown("### 📈 Efficiency Audit")
        if roa > 15:
            st.success("**High Engine Output:** The system generates sufficient internal alpha to fund its own survival and growth.")
        elif roa > 5:
            st.info("**Stable Output:** Steady performance. System remains viable but depends on consistent market conditions.")
        else:
            st.error("**Value Attrition:** Operating below the cost of capital. The system is consuming itself to stay alive.")

    # 5. DYNAMIC STRESS TEST
    st.divider()
    st.subheader("🌪️ Shock Scenario Simulation")
    shock_pct = st.slider("Simulate Sudden Cash/Asset Haircut (%)", 0, 80, 25)
    
    # The math of a sudden shock to current assets
    new_c_ratio = (sys_c_assets * (1 - shock_pct/100)) / sys_c_liabilities
    
    st.write(f"After a **{shock_pct}%** sudden shock, your Current Ratio would shift from **{c_ratio}** to **{new_c_ratio:.2f}**.")
    
    if new_c_ratio < 1:
        st.error(f"💀 **SYSTEM FAILURE:** At {shock_pct}% shock, the entity loses the ability to pay its workers and suppliers.")
    elif new_c_ratio < 1.2:
        st.warning(f"⚠️ **CRITICAL STRESS:** Survival is possible but requires emergency liquidation of assets.")
    else:
        st.success(f"🛡️ **STRUCTURAL SURVIVAL:** The system absorbs the {shock_pct}% shock and remains functional.")

    if st.button("⬅️ Return to Library Hub"):
        st.session_state.selected_tool = None
        st.rerun()
