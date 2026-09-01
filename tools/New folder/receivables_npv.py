import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, getcontext, InvalidOperation, Overflow
import numpy as np

# --- CALCULATION ENGINE
def calculate_discount_npv(
    current_sales, extra_sales, discount_trial, prc_clients_take_disc,
    days_curently_paying_clients_take_discount, days_curently_paying_clients_not_take_discount,
    new_days_payment_clients_take_disc, cogs, wacc, avg_days_pay_suppliers
):
    getcontext().prec = 50

    try:
        cs = Decimal(str(current_sales))
        es = Decimal(str(extra_sales))
        dt = Decimal(str(discount_trial))
        pct_take = Decimal(str(prc_clients_take_disc))
        d_take_old = Decimal(str(days_curently_paying_clients_take_discount))
        d_no_take_old = Decimal(str(days_curently_paying_clients_not_take_discount))
        d_new_policy = Decimal(str(new_days_payment_clients_take_disc))
        cg = Decimal(str(cogs))
        wc = Decimal(str(wacc))
        d_supp = Decimal(str(avg_days_pay_suppliers))

        if cs == 0 or pct_take == 0:
            return None

        pct_no_take   = Decimal('1') - pct_take
        avg_curr_days = (pct_take * d_take_old) + (pct_no_take * d_no_take_old)
        curr_rec      = (cs * avg_curr_days) / Decimal('365')

        total_sales      = cs + es
        prcnt_new_policy = ((cs * pct_take) + es) / total_sales
        prcnt_old_policy = Decimal('1') - prcnt_new_policy

        new_avg_period = (prcnt_new_policy * d_new_policy) + (prcnt_old_policy * d_no_take_old)
        new_rec        = (total_sales * new_avg_period) / Decimal('365')
        free_cap       = curr_rec - new_rec

        prof_extra    = es * (Decimal('1') - (cg / cs))
        prof_free_cap = free_cap * wc
        dist_cost     = total_sales * prcnt_new_policy * dt

        i = wc / Decimal('365')

        MAX_EXP     = Decimal('500')
        exp_new     = min(d_new_policy,   MAX_EXP)
        exp_no_take = min(d_no_take_old,  MAX_EXP)
        exp_curr    = min(avg_curr_days,  MAX_EXP)
        exp_supp    = min(d_supp,         MAX_EXP)

        term1   = (total_sales * prcnt_new_policy * (Decimal('1') - dt)) / ((Decimal('1') + i) ** exp_new)
        term2   = (total_sales * prcnt_old_policy) / ((Decimal('1') + i) ** exp_no_take)
        inflow  = term1 + term2

        term3   = (cg / cs) * (es / cs) * cs / ((Decimal('1') + i) ** exp_supp)
        term4   = cs / ((Decimal('1') + i) ** exp_curr)
        outflow = term3 + term4

        npv = inflow - outflow

        max_d = Decimal('1') - (
            (Decimal('1') + i)**(exp_new - exp_no_take) * (
                (Decimal('1') - Decimal('1')/prcnt_new_policy) + (
                    (Decimal('1') + i)**(exp_no_take - exp_curr) +
                    (cg/cs)*(es/cs)*(Decimal('1') + i)**(exp_no_take - exp_supp)
                ) / (prcnt_new_policy * (Decimal('1') + es/cs))
            )
        )

        opt_d = (Decimal('1') - ((Decimal('1') + i)**(exp_new - exp_curr))) / Decimal('2')

        return {
            "avg_current_collection_days": float(avg_curr_days),
            "current_receivables":         float(curr_rec),
            "new_avg_collection_period":   float(new_avg_period),
            "new_receivables":             float(new_rec),
            "free_capital":                float(free_cap),
            "profit_from_extra_sales":     float(prof_extra),
            "profit_from_free_capital":    float(prof_free_cap),
            "discount_cost":               float(dist_cost),
            "npv":                         float(npv),
            "max_discount":                float(max_d * 100),
            "optimum_discount":            float(opt_d * 100),
            "pct_new_policy":              float(prcnt_new_policy * 100)
        }

    except (InvalidOperation, Overflow, ZeroDivisionError):
        return None


# --- UI LAYER ---
def show_receivables_analyzer_ui():
    s = st.session_state

    sys_wacc         = float(s.get('wacc_locked', 15.0)) / 100
    sys_revenue      = float(s.get('price', 150.0)) * float(s.get('volume', 12000))
    sys_cogs         = float(s.get('variable_cost', 100.0)) * float(s.get('volume', 12000))
    sys_ar_days      = float(s.get('ar_days', 90.0))
    sys_ap_days      = float(s.get('ap_days', 45.0))
    sys_opening_cash = float(s.get('opening_cash', 150000.0))
    sys_fixed_cost   = float(s.get('fixed_cost', 450000.0))

    st.header("💳 Early Payment Discount Decision")

    st.caption(
        "Should you sacrifice margin to collect cash sooner? "
        "Evaluate whether faster collections create more value than the discount you offer."
    )
    # ── WHAT DOES THIS TOOL ACTUALLY DO? ──────────────────
    with st.expander("💡 What decision does this tool evaluate?", expanded=True):
        st.markdown(
            "Customers often ask for a discount in exchange for paying earlier.\n\n"

            "The real business question is not:\n"
            "**'How much discount should I give?'**\n\n"

            "The real question is:\n"
            "**'Will earlier cash collection create more value than the margin I give away?'**\n\n"

            "This Decision Lab compares two alternatives:\n\n"

            "- **Option A — Keep current payment terms.**\n"
            "- **Option B — Offer an early payment discount.**\n\n"

            "It measures the financial impact of both choices using Net Present Value (NPV).\n\n"

            "A positive NPV means the cash you recover sooner is worth more than the discount you offer.\n"
            "A negative NPV means the discount destroys value."
        )

    with st.form("npv_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📈 Current Business**")
            c_sales        = st.number_input("Current Sales ($)", value=sys_revenue)
            e_sales        = st.number_input("Expected Additional Sales ($)", value=sys_revenue * 0.10)
            d_trial        = st.number_input("Discount Offered (%)", value=2.0, step=0.1) / 100
            p_take         = st.number_input("Expected Customer Adoption (%)", value=40.0, step=1.0) / 100
            d_take_current = st.number_input("Current Collection Days (Customers Taking Discount)",
                                             value=int(sys_ar_days))

        with col2:
            st.markdown("**⚙️ Proposed Discount Policy**")
            d_new_target = st.number_input("Target Payment Days After Discount", value=10, step=1,
                                           min_value=1, max_value=365)
            cogs_val     = st.number_input("COGS ($)", value=sys_cogs)
            wacc_val     = st.number_input("Company Cost of Capital (WACC) (%)",
                                           value=sys_wacc * 100, step=0.1) / 100
            d_supps      = st.number_input("DPO (Supplier Days)", value=int(sys_ap_days),
                                           min_value=1, max_value=365)
            d_no_take    = st.number_input("Collection Days (Customers Not Taking Discount)",
                                           value=int(sys_ar_days * 1.5),
                                           min_value=1, max_value=365)

        submitted = st.form_submit_button("Analyze Decision", use_container_width=True)

    if submitted:
        r = calculate_discount_npv(
            c_sales, e_sales, d_trial, p_take,
            d_take_current, d_no_take, d_new_target,
            cogs_val, wacc_val, d_supps
        )

        if r is None:
            st.error("🚨 Calculation error: check your inputs. Days values may be too large or margins too thin.")
            st.stop()

        st.divider()
        st.subheader("🏁 Decision Outcome")
        c1, c2, c3 = st.columns(3)
        c1.metric("Decision NPV", f"${r['npv']:,.2f}",
                  delta="Creates Value" if r['npv'] > 0 else "Destroys Value")
        c2.metric("Maximum Sustainable Discount", f"{r['max_discount']:.2f}%")
        c3.metric("Optimal Discount", f"{r['optimum_discount']:.2f}%")

        # ── WHAT DO THESE THREE NUMBERS MEAN? ─────────────
        with st.expander("🔍 What do these three numbers mean?"):
            npv_sign = "positive" if r['npv'] > 0 else "negative"
            st.markdown(
                f"**Decision NPV (${r['npv']:,.2f}) — is the discount worth it?**\n"
                f"This is {npv_sign}. "
                + (
                    "The discount policy creates value — the cash you unlock by collecting faster "
                    "is worth more than the margin you sacrifice."
                    if r['npv'] > 0 else
                    "The discount policy destroys value — you are giving away more in margin "
                    "than you gain from faster cash collection."
                ) + "\n\n"
                f"**Break-even Discount ({r['max_discount']:.2f}%) — your ceiling:**\n"
                f"Never offer a discount above this rate. Above {r['max_discount']:.2f}%, "
                f"the policy loses money regardless of adoption rate or collection improvement.\n\n"
                f"**Value Maximizing Discount ({r['optimum_discount']:.2f}%) — the sweet spot:**\n"
                f"This is the exact rate that maximizes your NPV given your cost of capital "
                f"and collection days. It balances incentive for early payment "
                f"against margin sacrifice."
            )

        st.write("---")
        col_left, col_right = st.columns(2)
        with col_left:
            st.write("**Collection Performance:**")
            st.write(f"New Weighted Avg Days: **{r['new_avg_collection_period']:.1f} days**")
        with col_right:
            st.write("**Cash Released:**")
            st.metric("Cash Unlocked", f"${r['free_capital']:,.2f}")

        # --- SURVIVAL MONITOR ---
        st.divider()
        st.subheader("🛡️ Liquidity Safety Check")

        var_cost_val  = float(s.get('variable_cost', 100.0))
        volume_val    = float(s.get('volume', 12000))
        annual_burn   = sys_fixed_cost + (var_cost_val * volume_val)
        daily_burn    = annual_burn / 365
        survival_days = sys_opening_cash / daily_burn if daily_burn > 0 else 999

        new_dso = r['new_avg_collection_period']
        l_gap   = new_dso - survival_days

        if new_dso > survival_days:
            st.error(
                f"🚨 CRITICAL FRAGILITY: Gap of {l_gap:.1f} days. "
                f"You run out of cash before you get paid."
            )
        elif (survival_days - new_dso) < 15:
            st.warning(
                f"LOW BUFFER: Safety margin is only {(survival_days - new_dso):.1f} days."
            )
        else:
            st.success(
                f"ROBUST: Cash arrives {abs(l_gap):.1f} days before depletion."
            )

        # ── WHY DOES THE SURVIVAL GAP MATTER? ─────────────
        with st.expander("🔍 Why does the survival gap matter here?"):
            st.markdown(
                f"Your survival runway is **{survival_days:.0f} days** — "
                "how long you can operate if all revenue stopped today "
                "(opening cash divided by daily operational burn).\n\n"
                f"Your new weighted collection period is **{new_dso:.1f} days** — "
                "how long until cash actually arrives under this discount policy.\n\n"
                "If collection days exceed survival days, you run out of cash "
                "before the discount policy pays back. "
                "This is the hidden risk most businesses miss: "
                "a mathematically positive NPV policy can still create a cash crisis "
                "if your liquidity buffer is too thin to bridge the gap."
            )
            if new_dso > survival_days:
                shortfall = (new_dso - survival_days) * daily_burn
                st.markdown(
                    f"To close this gap you need an additional "
                    f"**${shortfall:,.0f}** in liquid reserves, "
                    f"or reduce collection days below {survival_days:.0f}."
                )

        # ── NPV SENSITIVITY CHART ─────────────────────────
        st.write("**NPV Sensitivity vs. Discount Rate**")

        # Range: 0% to 2x the break-even discount, capped at 10%
        max_d_pct = min(r['max_discount'] * 2, 10.0) / 100
        discounts = np.linspace(0, max_d_pct, 21)
        npvs = []
        for d in discounts:
            temp_r = calculate_discount_npv(
                c_sales, e_sales, d, p_take,
                d_take_current, d_no_take, d_new_target,
                cogs_val, wacc_val, d_supps
            )
            npvs.append(temp_r['npv'] if temp_r else None)

        # Color each segment: green above zero, red below
        fig_npv = go.Figure()
        fig_npv.add_trace(go.Scatter(
            x=discounts * 100, y=npvs,
            mode='lines+markers',
            name='Decision NPV',
            line=dict(color='#10b981', width=3),
            marker=dict(size=6)
        ))

        # Mark current discount
        current_d_pct = d_trial * 100
        fig_npv.add_vline(
            x=current_d_pct,
            line_dash="dash", line_color="white",
            annotation_text=f"Your discount ({current_d_pct:.1f}%)",
            annotation_position="top right"
        )

        # Mark break-even
        fig_npv.add_vline(
            x=r['max_discount'],
            line_dash="dot", line_color="#ef4444",
            annotation_text=f"Break-even ({r['max_discount']:.2f}%)",
            annotation_position="top left"
        )

        # Mark optimum
        fig_npv.add_vline(
            x=r['optimum_discount'],
            line_dash="dot", line_color="#f59e0b",
            annotation_text=f"Optimum ({r['optimum_discount']:.2f}%)",
            annotation_position="bottom right"
        )

        fig_npv.add_hline(y=0, line_dash="dash", line_color="#64748b")

        fig_npv.update_layout(
            title="How the Discount Changes Value",
            xaxis_title="Discount Rate (%)",
            yaxis_title="Decision NPV ($)",
            template="plotly_dark",
            height=350
        )
        st.plotly_chart(fig_npv, use_container_width=True)

        with st.expander("🔍 How should I interpret this chart?"):
            st.markdown(
                "This shows how the value of your discount policy changes "
                "as you increase the discount rate.\n\n"
                "- The **green line** is your NPV at each discount level\n"
                "- The **white dashed line** is your current proposed discount\n"
                "- The **yellow dotted line** is the mathematically optimal discount\n"
                "- The **red dotted line** is the break-even point — cross it and the policy loses money\n\n"
                "A steep downward slope means your policy is highly sensitive to discount rate changes. "
                "A flat slope means you have more room to adjust without major NPV impact."
            )

    st.divider()
    if st.button("⬅️ Back to Hub"):
        st.session_state.flow_step = "home"
        st.rerun()
