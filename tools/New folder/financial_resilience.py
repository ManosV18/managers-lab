import streamlit as st
import plotly.graph_objects as go

def show_resilience_map():
    s = st.session_state
    m = s.get("metrics", {})

    st.header("🛡️ Can Your Business Survive a Financial Shock?")
    st.info("See how profitability and liquidity work together to determine whether your business can absorb unexpected shocks.")

    # --- 1. BUILD BALANCE SHEET FROM ENGINE VALUES ---
    opening_cash    = float(s.get('opening_cash', 150000.0))
    fixed_assets    = float(s.get('fixed_assets', 800000.0))
    annual_ds       = float(s.get('annual_debt_service', 70000.0))

    ar_value        = float(m.get('ar_value', 0.0))
    inv_value       = float(m.get('inv_value', 0.0))
    ap_value        = float(m.get('ap_value', 0.0))
    net_profit      = float(m.get('net_profit', 0.0))

    current_assets  = opening_cash + ar_value + inv_value
    current_liabs   = ap_value + (annual_ds / 4)   # quarterly debt service approximation
    total_assets    = fixed_assets + current_assets

    if total_assets <= 0:   total_assets = 1.0
    if current_liabs <= 0:  current_liabs = 1.0

    roa       = round((net_profit / total_assets) * 100, 2)
    c_ratio   = round(current_assets / current_liabs, 2)

    # --- 2. STRATEGIC MATRIX (Plotly) ---
    st.subheader("📍 Your Current Position")

    fig = go.Figure()

    # Quadrant backgrounds
    fig.add_shape(type="rect", x0=0, x1=1.5, y0=10, y1=30,  fillcolor="rgba(239,68,68,0.08)",   line_width=0)
    fig.add_shape(type="rect", x0=1.5, x1=4,  y0=10, y1=30,  fillcolor="rgba(16,185,129,0.08)",  line_width=0)
    fig.add_shape(type="rect", x0=0, x1=1.5, y0=-10, y1=10,  fillcolor="rgba(239,68,68,0.15)",   line_width=0)
    fig.add_shape(type="rect", x0=1.5, x1=4,  y0=-10, y1=10, fillcolor="rgba(59,130,246,0.08)",  line_width=0)

    # Quadrant dividers
    fig.add_shape(type="line", x0=1.5, x1=1.5, y0=-10, y1=30, line=dict(color="#64748b", dash="dash", width=1))
    fig.add_shape(type="line", x0=0,   x1=4,   y0=10,  y1=10, line=dict(color="#64748b", dash="dash", width=1))

    # Quadrant labels
    labels = [
        (0.2,  25, "GROWTH TRAP<br>(Illiquid Profit)",   "orange"),
        (2.2,  25, "THE FORTRESS<br>(Financially Resilient)",      "green"),
        (0.2,  -5, "DANGER ZONE<br>(Insolvency Risk)",    "red"),
        (2.2,  -5, "UNDERUTILIZED CAPITAL<br>(Low Returns)",     "royalblue"),
    ]
    for x, y, text, color in labels:
        fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                           font=dict(size=10, color=color), align="left")

    # Current position
    fig.add_trace(go.Scatter(
        x=[c_ratio], y=[roa],
        mode="markers+text",
        marker=dict(size=18, color="#ef4444", line=dict(color="white", width=2)),
        text=[f"  CR: {c_ratio} | ROA: {roa}%"],
        textposition="middle right",
        textfont=dict(color="white", size=11),
        name="Current State"
    ))

    fig.update_layout(
        height=450,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(title="Liquidity Buffer (Current Ratio)", range=[0, 4]),
        yaxis=dict(title="Efficiency (ROA %)", range=[-10, 30]),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 3. SHOCK ABSORPTION ANALYSIS ---
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧠 Liquidity Shock Profile")
        if c_ratio < 1.0:
            st.error("**Technical Insolvency:** Cannot absorb even minor delays in receivables.")
        elif c_ratio < 1.5:
            st.warning("**Lean Buffer:** Vulnerable to volatility. Efficiency is high, safety is low.")
        else:
            st.success("**High Buffer:** Strong liquidity buffer. The business can absorb temporary cash flow disruptions.")

    with col2:
        st.markdown("### 📈 Operational Strength")
        if roa > 15:
            st.success("**High Performance:** Strong internal capital generation.")
        elif roa > 5:
            st.info("**Moderate Stability:** Stable performance, but limited capacity to absorb major shocks.")
        else:
            st.error("**Value Destruction:** The business is not generating sufficient returns to sustain itself over time.")

    # --- 4. LIQUIDITY SHOCK TEST ---
    st.divider()
    st.subheader("🌪️ Liquidity Shock Test")
    st.caption(
        "Simulate events such as delayed customer payments, inventory write-downs, "
        "bad debts, or restricted cash, and see how your liquidity position changes."
    )

    shock_pct = st.slider(
        "Simulate an Unexpected Loss of Liquid Assets (%)",
        min_value=0,
        max_value=80,
        value=25,
        step=5
    )

    # Impact on current assets
    shocked_assets = current_assets * (1 - shock_pct / 100)
    new_c_ratio = round(shocked_assets / current_liabs, 2)
    liquidity_lost = current_assets - shocked_assets

    # Dashboard
    col_s1, col_s2, col_s3 = st.columns(3)

    col_s1.metric(
        "Baseline Current Ratio",
        f"{c_ratio:.2f}"
    )

    col_s2.metric(
        "Post-Shock Current Ratio",
        f"{new_c_ratio:.2f}",
        delta=f"{new_c_ratio - c_ratio:.2f}",
        delta_color="inverse"
    )

    col_s3.metric(
    "Liquid Assets Lost",
    f"${liquidity_lost:,.0f}",
    delta=f"{shock_pct}%"
    )

    st.divider()

    if new_c_ratio < 1.0:
        st.error(
            f"🚨 **Critical Liquidity Risk:** "
            f"After a {shock_pct}% liquidity shock, your Current Ratio falls to "
            f"**{new_c_ratio:.2f}**, below the minimum level generally considered "
            f"adequate to meet short-term obligations."
        )

    elif new_c_ratio < 1.5:
        st.warning(
            f"⚠️ **Reduced Financial Flexibility:** "
            f"A {shock_pct}% liquidity shock reduces your Current Ratio to "
            f"**{new_c_ratio:.2f}**. The business remains solvent, but its ability "
            f"to absorb additional disruptions becomes limited."
        )

    else:
        st.success(
            f"✅ **Business Remains Financially Resilient:** "
            f"Even after a {shock_pct}% liquidity shock, your Current Ratio remains "
            f"at **{new_c_ratio:.2f}**, indicating that the business should still be "
            f"able to meet its short-term obligations."
        )
    
    st.divider()
    if st.button("⬅️ Back to Hub", use_container_width=True):
        st.session_state.flow_step = "home"
        st.session_state.selected_tool = None
        st.rerun()

