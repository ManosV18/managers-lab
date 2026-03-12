import streamlit as st
import matplotlib.pyplot as plt

def analyze_resilience(profit, assets, current_assets, current_liabilities):
    # Fixed division by zero by using a minimum epsilon or conditional check
    roa = (profit / assets) * 100 if assets > 0 else 0
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
    return round(roa, 2), round(current_ratio, 2)

def show_resilience_map():
    s = st.session_state
    m = s.get("metrics", {})
    
    st.header("🛡️ Financial Resilience & Shock Absorption Map")
    st.info("Strategic Mapping: Efficiency (ROA) vs. Liquidity (Current Ratio).")

    # 1. FETCH & ALIGN DATA
    net_profit = float(m.get('net_profit', 0.0))
    revenue = float(s.get('price', 0) * s.get('volume', 0))
    
    # Ensuring values are never zero for division
    sys_assets = float(s.get('total_assets', revenue * 0.8 if revenue > 0 else 1.0))
    if sys_assets <= 0: sys_assets = 1.0
    
    sys_c_assets = float(s.get('current_assets', s.get('opening_cash', 0.0) + m.get('wc_requirement', 0.0)))
    
    sys_c_liabilities = float(s.get('current_liabilities', s.get('fixed_cost', 0.0) / 4))
    if sys_c_liabilities <= 0: sys_c_liabilities = 1.0 # Avoid DivisionByZero

    # 2. CALCULATION
    roa, c_ratio = analyze_resilience(net_profit, sys_assets, sys_c_assets, sys_c_liabilities)

    # 3. VISUALIZATION (Strategic Matrix)
    st.subheader("📍 Strategic Position")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Matrix setup
    ax.set_xlim(0, 4)  
    ax.set_ylim(-10, 30) 
    ax.axhline(10, color='#64748b', linewidth=1, linestyle='--') 
    ax.axvline(1.5, color='#64748b', linewidth=1, linestyle='--') 
    
    # Quadrant Labels
    ax.text(0.2, 25, "GROWTH TRAP\n(Illiquid Profit)", fontsize=9, color='orange', fontweight='bold')
    ax.text(2.2, 25, "THE FORTRESS\n(Anti-Fragile)", fontsize=9, color='green', fontweight='bold')
    ax.text(0.2, -5, "DANGER ZONE\n(Insolvency Risk)", fontsize=9, color='red', fontweight='bold')
    ax.text(2.2, -5, "SAFE STORAGE\n(Underutilized)", fontsize=9, color='blue', fontweight='bold')

    # Current Position Plot
    ax.scatter(c_ratio, roa, color='#ef4444', s=300, edgecolors='black', zorder=5)
    ax.annotate(f"CURRENT STATE\n(CR: {c_ratio}, ROA: {roa}%)", (c_ratio, roa), 
                textcoords="offset points", xytext=(0,15), ha='center', fontweight='bold', 
                bbox=dict(boxstyle='round,pad=0.5', fc='#1E3A8A', alpha=0.8, color='white'))

    ax.set_xlabel("Liquidity Buffer (Current Ratio)")
    ax.set_ylabel("Efficiency (ROA %)")
    ax.grid(True, alpha=0.1)
    st.pyplot(fig)

    # 4. SHOCK ABSORPTION ANALYSIS
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧠 Liquidity Shock Profile")
        if c_ratio < 1.0:
            st.error("**Technical Insolvency:** System cannot absorb even minor delays in receivables.")
        elif c_ratio < 1.5:
            st.warning("**Lean Buffer:** Vulnerable to market volatility. Efficiency is high, but safety is low.")
        else:
            st.success("**High Buffer:** Anti-fragile state. Can withstand revenue shocks.")

    with col2:
        st.markdown("### 📈 Operational Strength")
        if roa > 15:
            st.success("**High Performance:** Strong internal capital generation.")
        elif roa > 5:
            st.info("**Moderate Stability:** Stable, but lacks 'escape velocity' for major disasters.")
        else:
            st.error("**Value Destruction:** Survival depends purely on cash depletion.")

    # 5. STRESS TEST SIMULATION
    st.divider()
    st.subheader("🌪️ Real-Time Stress Test")
    shock_pct = st.slider("Simulate Sudden Cash Inflow Drop (%)", 0, 80, 25)
    
    new_c_ratio = (sys_c_assets * (1 - shock_pct/100)) / sys_c_liabilities
    
    st.write(f"In a **{shock_pct}%** shock scenario, Current Ratio drops from **{c_ratio}** to **{new_c_ratio:.2f}**.")
    
    if new_c_ratio < 1:
        st.error(f"🚨 **SYSTEM COLLAPSE:** At {shock_pct}% shock, the entity fails to meet current obligations.")
    else:
        st.success(f"✅ **SURVIVAL:** The system remains solvent despite the {shock_pct}% shock.")

    # Navigation
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
