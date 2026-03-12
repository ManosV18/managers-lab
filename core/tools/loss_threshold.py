import streamlit as st

def calculate_sales_loss_threshold(comp_old, comp_new, our_p, u_cost):
    try:
        # Numerator: % change in competitor price
        top = (comp_new - comp_old) / comp_old
        # Denominator: (Unit Cost - Our Price) / Our Price
        # This represents the contribution margin ratio context
        bottom = (u_cost - our_p) / our_p
        if bottom == 0: return None
        return (top / bottom) * 100
    except ZeroDivisionError:
        return None

def show_loss_threshold_before_price_cut():
    st.header("📉 Sales Loss Threshold Analysis")
    st.info("Strategic Pricing: Calculate the maximum volume loss you can absorb before a price match becomes necessary.")

    s = st.session_state
    
    # 1. INPUT SECTION
    st.subheader("1. Market & Cost Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        comp_old = st.number_input("Competitor Original Price (€)", value=8.00, step=0.10)
        our_price = st.number_input("Our Current Selling Price (€)", value=float(s.get('price', 8.00)), step=0.10)
    
    with col2:
        comp_new = st.number_input("Competitor New Price (€)", value=7.20, step=0.10)
        unit_cost = st.number_input("Our Unit Cost (VC) (€)", value=float(s.get('variable_cost', 4.50)), step=0.10)

    # 2. CALCULATION
    threshold = calculate_sales_loss_threshold(comp_old, comp_new, our_price, unit_cost)
    price_cut_pct = ((comp_new - comp_old) / comp_old) * 100

    st.divider()

    # 3. ANALYST'S VERDICT
    if threshold is not None:
        if threshold <= 0:
            st.error("🚨 **Systemic Vulnerability:** Your current price/cost structure provides no buffer. Any price match will result in immediate value destruction.")
        else:
            # Executive Display
            st.subheader("2. Strategic Indifference Point")
            
            
            
            st.markdown(f"""
            <div style="background-color:#1E3A8A; padding:25px; border-radius:10px; color: white;">
                <h4 style="margin:0; color:#cbd5e1;">Maximum Allowable Volume Loss</h4>
                <p style="font-size:42px; font-weight:bold; margin:10px 0;">{threshold:.2f}%</p>
                <p style="font-size:14px; color:#94a3b8; line-height:1.4;">
                    If the competitor's <b>{abs(price_cut_pct):.1f}%</b> price cut results in a sales drop of <b>less than {threshold:.2f}%</b>, 
                    holding your price is mathematically more profitable than matching them.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.write("---")
            st.subheader("💡 Decision Matrix")
            if abs(price_cut_pct) > threshold:
                st.warning("⚠️ **High Risk:** The competitor's cut is aggressive. If customer loyalty is low, matching may be required to prevent market share collapse.")
            else:
                st.success("✅ **Hold Position:** Your margins are robust enough to absorb the projected volume shift. Do not trigger a margin-depleting price war.")

    # Navigation (Ευθυγραμμισμένο με το νέο app.py)
    st.divider()
    if st.button("⬅️ Back to Control Tower", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()
    
