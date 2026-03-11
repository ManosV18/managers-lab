import streamlit as st
import plotly.graph_objects as go

def calculate_cross_sell_impact(main_price, price_decrease_pct, profit_main, complement_data):
    # complement_data: list of (profit, attach_rate)
    expected_complement_profit = sum(p * r for p, r in complement_data)
    total_profit_per_main_unit = profit_main + expected_complement_profit

    try:
        # Indifference point formula for discounts considering bundle profit
        # Image of pricing indifference point formula
        required_increase = -price_decrease_pct / ((total_profit_per_main_unit / main_price) + price_decrease_pct)
        return required_increase * 100, expected_complement_profit
    except ZeroDivisionError:
        return None, 0

def calculate_max_drop(old_price, price_inc_pct, profit_A, sub_data):
    # sub_data: list of (profit_sub, switch_prob)
    weighted_sub_profit = sum(p * r for p, r in sub_data)
    
    numerator = -price_inc_pct
    denominator = ((profit_A - weighted_sub_profit) / old_price) + price_inc_pct
    
    if denominator == 0: return 0.0
    return (numerator / denominator) * 100

def show_pricing_strategy_tool():
    s = st.session_state
    st.header("🎯 Strategic Pricing & Elasticity")
    st.info("Advanced Modeling: Cross-Sell Dynamics and Cannibalization Risks.")

    mode = st.tabs(["🛒 Cross-Sell / Complements", "🔁 Substitution Risk"])

    # --- TAB 1: CROSS-SELL ANALYSIS ---
    with mode[0]:
        st.subheader("Complementary Product Ecosystem")
        
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Core Asset**")
            # Σύνδεση με το κεντρικό μοντέλο
            current_p = float(s.get('price', 200.0))
            current_vc = float(s.get('variable_cost', 140.0))
            
            main_p = st.number_input("Main Product Price (€)", value=current_p)
            main_prof = st.number_input("Main Product Profit (€)", value=current_p - current_vc)
            discount = st.slider("Proposed Discount on Main (%)", 0.0, 40.0, 10.0) / 100
        
        with c2:
            st.markdown("**Complements (Profit & Attach Rate)**")
            comp_list = []
            for i in range(1, 4):
                col_a, col_b = st.columns(2)
                p = col_a.number_input(f"Profit Item {i}", value=20.0, key=f"p_{i}")
                r = col_b.slider(f"Attach Rate %", 0, 100, 40, key=f"r_{i}") / 100
                comp_list.append((p, r))

        if st.button("Analyze Bundle Impact", use_container_width=True):
            res, avg_extra = calculate_cross_sell_impact(main_p, -discount, main_prof, comp_list)
            
            st.divider()
            if res and res > 0:
                m1, m2, m3 = st.columns(3)
                m1.metric("Required Vol. Growth", f"{res:.2f}%")
                m2.metric("Weighted Attach Profit", f"€{avg_extra:.2f}")
                m3.metric("New Effective Margin", f"€{(main_prof + avg_extra - (main_p * discount)):.2f}")
                
                if res > 25:
                    st.warning(f"⚠️ High Volume Dependency: You need a {res:.1f}% jump in sales to justify the discount.")
                else:
                    st.success("🟢 Low Risk: The bundle margin absorbs the discount effectively.")
            else:
                st.error("🚨 Strategic Deficit: The discount is larger than the total profit potential.")

    # --- TAB 2: SUBSTITUTION RISK ---
    with mode[1]:
        st.subheader("Cannibalization Matrix")
        
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Target Product (Price Hike)**")
            old_p = st.number_input("Current Price (€)", value=float(s.get('price', 100.0)), key="sub_old_p")
            p_A = st.number_input("Unit Profit (€)", value=float(s.get('price', 100.0) - s.get('variable_cost', 70.0)), key="sub_prof_a")
            p_inc = st.slider("Price Increase (%)", 0.0, 50.0, 10.0) / 100
        
        with col2:
            st.markdown("**Substitution Logic**")
            sub_list = []
            for i in range(1, 3):
                col_sub_a, col_sub_b = st.columns(2)
                sp = col_sub_a.number_input(f"Profit Sub {i}", value=20.0, key=f"sp_{i}")
                sr = col_sub_b.slider(f"Switch Rate to Sub {i} %", 0, 100, 30, key=f"sr_{i}") / 100
                sub_list.append((sp, sr))

        if st.button("Calculate Substitution Threshold", use_container_width=True):
            total_switch = sum(x[1] for x in sub_list)
            if total_switch > 1.0:
                st.error("Total switch probabilities cannot exceed 100%.")
            else:
                max_drop = calculate_max_drop(old_p, p_inc, p_A, sub_list)
                st.divider()
                st.metric("Max Allowed Volume Drop", f"{max_drop:.2f}%")
                
                fig = go.Figure(data=[go.Pie(labels=['Captured by Subs', 'Pure Market Loss'], 
                                           values=[total_switch, 1-total_switch], hole=.4)])
                fig.update_layout(height=350, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

    # --- NAVIGATION ---
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
