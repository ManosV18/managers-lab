import streamlit as st

def run_home():

    s = st.session_state
    m = s.get("metrics", {})

    # --------------------------------------------------
    # BASELINE STATE
    # --------------------------------------------------

    p = s.get("price", 100.0)
    vc = s.get("variable_cost", 60.0)
    v = s.get("volume", 1000)
    fc = s.get("fixed_cost", 20000.0)
    ads = s.get("annual_debt_service", 0.0)
    cash = s.get("opening_cash", 10000.0)
    tp = s.get("target_profit_goal", 0.0)

    net_cash = m.get("net_cash_position", cash)
    bep_units = m.get("bep_units", 0)
    margin = p - vc
    roic = m.get("roic", 0.0)

    # --------------------------------------------------
    # SNAPSHOT LOGIC
    # --------------------------------------------------

    if margin > 0 and bep_units:

        margin_of_safety = v - bep_units
        buffer_pct = (margin_of_safety / v * 100) if v > 0 else 0

        bep_display = f"{bep_units:,.0f} units"

        delta_val = (
            f"{margin_of_safety:,.0f} surplus"
            if margin_of_safety >= 0
            else f"{abs(margin_of_safety):,.0f} deficit"
        )

        delta_col = "normal" if margin_of_safety >= 0 else "inverse"

    else:

        buffer_pct = -100.0
        bep_display = "N/A"
        delta_val = "⚠ Not viable"
        delta_col = "inverse"

    # --------------------------------------------------
    # HERO SECTION
    # --------------------------------------------------

    st.markdown(
        """
        <div style='text-align:center; padding: 10px 0 30px 0;'>

        <h1 style='font-size:
