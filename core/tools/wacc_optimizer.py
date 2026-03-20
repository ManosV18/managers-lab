import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_wacc_optimizer_ui():
    st.header("📉 WACC Optimizer (Cost of Capital)")
    st.info("Calculate the Weighted Average Cost of Capital (Hurdle Rate) to benchmark your ROIC.")

    s = st.session_state
    
    # 1. DATA SYNC (The McKinsey Connection)
    # Τραβάμε τα 16-20 βασικά νούμερα από το Home/Engine
    baseline_debt = float(s.get("total_debt", 500000.0))
    metrics = s.get("metrics", {})
    total_inv_capital = float(metrics.get("invested_capital", 1300000.0))
    current_roic = float(metrics.get("roic", 0.0)) # Παίρνουμε το ROIC για σύγκριση
    
    # Το Equity προκύπτει από το Invested Capital (Net of Cash)
    baseline_equity = max(total_inv_capital - baseline_debt, 1000.0)

    # 2. INPUT SECTION
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏦 Capital Structure")
        market_equity = st.number_input("Market Value of Equity ($)", value=baseline_equity, step=50000.0)
        total_debt = st.number_input("Total Debt ($)", value=baseline_debt, step=50000.0)
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=22.0) / 100
        
        actual_total_cap = market_equity + total_debt
        e_weight = market_equity / actual_total_cap if actual_total_cap > 0 else 0
        d_weight = total_debt / actual_total_cap if actual_total_cap > 0 else 0

    with col2:
        st.subheader("📈 Risk & Cost Components")
        risk_free = st.number_input("Risk-Free Rate (%)", value=3.5, help="e.g., 10Y Govt Bond Yield") / 100
        beta = st.number_input("Equity Beta (Sector Risk)", value=1.2, help="1.0 = Market Avg, >1.0 = Aggressive")
        mkt_premium = st.number_input("Market Risk Premium (%)", value=5.5) / 100
        
        # CAPM Formula
        cost_of_equity = risk_free + (beta * mkt_premium)
        
        avg_interest_rate = st.number_input("Avg. Interest Rate on Debt (%)", value=6.0) / 100
        cost_of_debt = avg_interest_rate * (1 - tax_rate) # Tax Shield Logic

    # 3. CALCULATIONS
    wacc = (e_weight * cost_of_equity) + (d_weight * cost_of_debt)
    wacc_pct = wacc * 100

    st.divider()

    # 4. EXECUTIVE DASHBOARD (Economic Spread)
    res1, res2, res3 = st.columns(3)
    res1.metric("Cost of Equity (Ke)", f"{cost_of_equity*100:.2f}%")
    res2.metric("After-Tax Cost of Debt (Kd)", f"{cost_of_debt*100:.2f}%")
    
    # Το Economic Spread: ROIC - WACC
    spread = current_roic - wacc_pct
    res3.metric("Final WACC", f"{wacc_pct:.2f}%", delta=f"{spread:.2f}% Spread", 
                delta_color="normal" if spread > 0 else "inverse")

    # 5. VISUALIZATION (Capital Mix Waterfall)
    
    
    st.write(f"**Capital Mix:** Equity {e_weight*100:.1f}% | Debt {d_weight*100:.1f}%")
    st.progress(e_weight)

    # 6. STRATEGIC ANALYSIS
    st.subheader("💡 Strategic Verdict")
    if spread > 2:
        st.success(f"🎯 **Value Creation:** Your ROIC ({current_roic:.1f}%) comfortably exceeds your WACC ({wacc_pct:.1f}%). The business is creating shareholder wealth.")
    elif spread > 0:
        st.warning(f"⚠️ **Marginal Performance:** You are barely covering the cost of capital. Any increase in interest rates will destroy value.")
    else:
        st.error(f"🚨 **Value Destruction:** Your WACC is higher than your ROIC. You are essentially burning capital to stay in business.")

    # 7. GLOBAL SYNC & NAVIGATION
    st.divider()
    c_nav1, c_nav2 = st.columns(2)
    
    if c_nav1.button("🔐 Lock WACC for Strategy", use_container_width=True):
        st.session_state.wacc_locked = round(wacc_pct, 2)
        st.success(f"WACC locked at {wacc_pct:.2f}%. NPV & CLV tools updated.")

    if c_nav2.button("⬅️ Return to Hub", use_container_width=True):
        st.session_state.flow_step = "home"
        st.rerun()
