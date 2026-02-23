import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# -----------------------
# CORE CALCULATIONS
# -----------------------

def calculate_cross_sell_impact(suit_price, price_decrease_pct, profit_suit, complement_data):
    # complement_data: list of tuples (profit, attach_rate)
    expected_complement_profit = sum(p * r for p, r in complement_data)
    total_profit_per_main_unit = profit_suit + expected_complement_profit

    try:
        # Indifference point formula
        required_increase = -price_decrease_pct / ((total_profit_per_main_unit / suit_price) + price_decrease_pct)
        return required_increase * 100, expected_complement_profit
    except ZeroDivisionError:
        return None, 0

def calculate_max_drop(old_price, price_inc_pct, profit_A, sub_data):
    # sub_data: list of tuples (profit_sub, switch_prob)
    weighted_sub_profit = sum(p * r for p, r in sub_data)
    
    numerator = -price_inc_pct
    denominator = ((profit_A - weighted_sub_profit) / old_price) + price_inc_pct
    
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100

# -----------------------
# UI INTERFACE
# -----------------------

def show_pricing_strategy_tool():
    st.header("🎯 Strategic Pricing & Elasticity")
    st.info("Choose a model to evaluate the impact of pricing changes on volume and total profitability.")

    mode = st.tabs(["🛒 Cross-Sell / Complements", "🔁 Substitution Risk"])

    # --- TAB 1: CROSS-SELL ANALYSIS ---
    with mode[0]:
        st.subheader("Complementary Products Analysis")
        st.write("Does the margin from accessories justify a discount on the main product?")
        
        c1, c2 = st.columns(2)
        with c1:
            main_price = st.number_input("Main Product Price (€)", value=200.0)
            main_profit = st.number_input("Main Product Profit (€)", value=60.0)
            discount = st.slider("Proposed Discount (%)", 0.0, 40.0, 10.0) / 100
        
        with c2:
            st.write("**Complements (Profit & Attach Rate)**")
            comp_list = []
            for item in ["Item 1", "Item 2", "Item 3", "Item 4"]:
                col_a, col_b = st.columns(2)
                p = col_a.number_input(f"Profit {item}", value=15.0, key=f"p_{item}")
                r = col_b.slider(f"Attach Rate %", 0, 100, 50, key=f"r_{item}") / 100
                comp_list.append((p, r))

        if st.button("Calculate Cross-Sell Impact", use_container_width=True):
            res, avg_extra = calculate_cross_sell_impact(main_price, -discount, main_profit, comp_list)
            
            if res and res > 0:
                st.divider()
                m1, m2, m3 = st.columns(3)
                m1.metric("Required Vol. Growth", f"{res:.2f}%")
                m2.metric("Avg. Extra Profit", f"€{avg_extra:.2f}")
                m3.metric("New Bundle Margin", f"€{(main_profit + avg_extra - (main_price * discount)):.2f}")
                
                if res > 30:
                    st.warning(f"⚠️ High risk: Need {res:.1f}% more volume to break even.")
                else:
                    st.success(f"🟢 Viable: Growth of {res:.1f}% is manageable.")
            else:
                st.error("🔴 Strategic Deficit: Discount exceeds total bundle margin.")

    # --- TAB 2: SUBSTITUTION RISK ---
    with mode[1]:
        st.subheader("Cannibalization & Substitution Matrix")
        st.write("If you raise prices, how much volume can you afford to lose to your other products?")
        
        col1, col2 = st.columns(2)
        with col1:
            old_p = st.number_input("Current Price Product A (€)", value=1.50)
            p_A = st.number_input("Unit Profit Product A (€)", value=0.30)
            p_inc = st.slider("Price Increase (%)", 0.0, 50.0, 10.0) / 100
        
        with col2:
            st.write("**Substitution Logic**")
            sub_list = []
            for i in range(3):
                col_a, col_b = st.columns(2)
                sp = col_a.number_input(f"Profit Sub {i+1}", value=0.20, key=f"sp_{i}")
                sr = col_b.slider(f"Switch Rate to {i+1} %", 0, 100, 20, key=f"sr_{i}") / 100
                sub_list.append((sp, sr))

        if st.button("Calculate Substitution Limit", use_container_width=True):
            total_switch = sum(x[1] for x in sub_list)
            if total_switch > 1.0:
                st.error("Total probabilities cannot exceed 100%")
            else:
                max_drop = calculate_max_drop(old_p, p_inc, p_A, sub_list)
                
                st.divider()
                st.subheader("Analytical Verdict")
                st.metric("Max Allowed Volume Drop", f"{max_drop:.2f}%")
                
                # Visual Pie Chart
                fig = go.Figure(data=[go.Pie(labels=['Switching', 'Lost Market'], 
                                            values=[total_switch, 1-total_switch], hole=.4)])
                st.plotly_chart(fig, use_container_width=True)

                if abs(max_drop) > 15:
                    st.success("🟢 Strong Pricing Power: High buffer for volume loss.")
                else:
                    st.error("🔴 Fragile Margin: Minimal room for volume loss.")
