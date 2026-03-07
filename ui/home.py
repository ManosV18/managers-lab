import streamlit as st
from core.sync import sync_global_state, lock_baseline
from core.tools_registry import TOOLS


def run_home():

    metrics = sync_global_state()
    is_locked = st.session_state.get("baseline_locked", False)

    # HERO
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0;">
            <h1 style="font-size:48px;">🛡️ Strategic Decision Room</h1>
            <h2 style="font-size:28px; font-weight:600;">
                Test your business decisions before risking real money
            </h2>
            <p style="font-size:18px; color:#555;">
                Change prices, costs or investments and instantly see the impact
                on profit, break-even and cash survival.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # STATUS
    if not is_locked:
        st.info("💡 Enter baseline numbers to activate the system.")
    else:
        st.success("✅ Baseline Active")

    st.divider()

    # KPI PANEL
    col1, col2, col3, col4 = st.columns(4)

    rev = metrics.get("revenue") if is_locked else None
    ebit = metrics.get("ebit") if is_locked else None
    bep = metrics.get("bep_units") if is_locked else None
    fcf = metrics.get("fcf") if is_locked else None

    def show(v, suffix=""):
        if v is None:
            return "—"
        return f"{v:,.0f}{suffix}"

    col1.metric("Revenue", show(rev, " €"))
    col2.metric("EBIT", show(ebit, " €"))
    col3.metric("Break-Even Units", show(bep))
    col4.metric("Free Cash Flow", show(fcf, " €"))

    st.divider()

    # MAIN AREA
    st.subheader("⚙️ Business Setup & Tools")

    left, right = st.columns([1, 2])

    # BASELINE
    with left:

        st.markdown("### 🏗️ Baseline Setup")

        if st.button("Lock Baseline / Start System", use_container_width=True):
            lock_baseline()
            st.session_state.flow_step = "stage1"
            st.rerun()

    # TOOLS
    with right:

        st.markdown("### 🛠️ Tools")

        cols = st.columns(3)

        for i, tool in enumerate(TOOLS):

            name = tool["name"]
            mod = tool["module"]
            func = tool["function"]

            with cols[i % 3]:

                if st.button(name, key=f"home_tool_{name}", use_container_width=True):

                    st.session_state.selected_tool = (mod, func)
                    st.session_state.flow_step = "library"
                    st.rerun()
