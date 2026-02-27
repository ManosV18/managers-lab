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
    
    # Auto-fetch from Stage 0 and Engine
    sys_net_profit = float(metrics.get('net_profit', 0.0))
    sys_assets = float(s.get('total_assets', 1.0)) # Needs to be defined in Stage 0
    sys_c_assets = float(s.get('current_assets', 0.0))
    sys_c_liabilities = float(s.get('current_liabilities', 1.0))

    st.header("🛡️ Financial Resilience & Shock Absorption Map")
    st.caption("Real-time mapping of the system's ability to withstand economic volatility.")

    # 2. CALCULATION
    roa, c_ratio = analyze_resilience(sys_net_profit, sys_assets, sys_c_assets, sys_c_liabilities)

    # 3. VISUALIZATION (2x2 Matrix)
    st.subheader("📍 Strategic Position")
    fig, ax = plt.subplots(figsize=(8, 7))
    
    ax.set_xlim(0, 4)  
    ax.set_ylim(-10, 30) 
    
    # Thresholds
    ax.axhline(10, color='black', linewidth=1, linestyle='--') 
    ax.axvline(1.5, color='black', linewidth=1, linestyle='--') 
    
    # Labels
    ax.text(0.2, 25, "Growth Trap\n(Illiquid Profit)", fontsize=10, color='orange', fontweight='bold')
    ax.text(2.2, 25, "The Fortress\n(Anti-Fragile)", fontsize=10, color='green', fontweight='bold')
    ax.text(0.2, -5, "Danger Zone\n(High Risk)", fontsize=10, color='red', fontweight='bold')
    ax.text(2.2, -5, "Safe Storage\n(Inefficient)", fontsize=10, color='blue', fontweight='bold')

    # Current Position
    ax.scatter(c_ratio, roa, color='red', s=250, edgecolors='black', zorder=5)
    ax.annotate(f"CURRENT STATE\n(CR: {c_ratio}, ROA: {roa}%)", (c_ratio, roa), 
                textcoords="offset points", xytext=(0,15), ha='center', fontweight='bold', 
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))

    ax.set_xlabel("Liquidity Buffer (Current Ratio)")
    ax.set_ylabel("Efficiency (ROA %)")
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)

    # 4. SHOCK ABSORPTION ANALYSIS (Analytical Verdict)
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧠 Liquidity Shock Profile")
        if c_ratio < 1.0:
            st.error("**Technical Insolvency:** System cannot absorb even minor delays in receivables.")
        elif c_ratio < 1.5:
            st.warning("**Lean Buffer:** Vulnerable to market volatility. Efficiency is high, but safety is low.")
        else:
            st.success("**High Buffer:** Anti-fragile state. Can lose major revenue streams and remain standing.")

    with col2:
        st.markdown("### 📈 Operational Strength")
        if roa > 15:
            st.success("**High Performance:** Strong internal capital generation. Survival is self-funded.")
        elif roa > 5:
            st.info("**Moderate Stability:** Stable operations, but lacks 'escape velocity' for major shocks.")
        else:
            st.error("**Value Destruction:** Stagnant system. Survival depends purely on cash depletion.")

    # 5. STRESS TEST SIMULATION
    st.divider()
    st.subheader("🌪️ Real-Time Stress Test")
    shock_pct = st.slider("Simulate Sudden Revenue/Cash Drop (%)", 0, 70, 25)
    
    new_c_ratio = (sys_c_assets * (1 - shock_pct/100)) / sys_c_liabilities
    
    st.write(f"In a **{shock_pct}%** shock scenario, Liquidity drops from **{c_ratio}** to **{new_c_ratio:.2f}**.")
    
    if new_c_ratio < 1:
        st.error(f"🚨 **SYSTEM COLLAPSE:** At {shock_pct}% shock, the entity fails to meet current obligations.")
    else:
        st.success(f"✅ **SURVIVAL:** The system remains solvent despite the {shock_pct}% shock.")

    if st.button("⬅️ Back to Library"):
        st.session_state.selected_tool = None
        st.rerun()
