import streamlit as st
from core.sync import sync_global_state

def run_home():
    metrics = sync_global_state()
    is_locked = st.session_state.get('baseline_locked', False)
    
    # --- KPI DASHBOARD VISUAL ---
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

# Τιμές μόνο αν έχει κλειδωθεί το baseline
rev_val = metrics.get('revenue') if is_locked else None
ebit_val = metrics.get('ebit') if is_locked else None
bep_val = metrics.get('bep_units') if is_locked else None
fcf_val = metrics.get('fcf') if is_locked else None

# --- Χρωματισμός ανάλογα με το μέγεθος / κριτήριο ---
def colorize(value, thresholds):
    if value is None:
        return "—"
    low, high = thresholds
    if value < low:
        return f"🔴 {value:,.0f}"
    elif value < high:
        return f"🟠 {value:,.0f}"
    else:
        return f"🟢 {value:,.0f}"

c1.metric("Projected Revenue", colorize(rev_val, (20000, 50000)), "€")
c2.metric("EBIT", colorize(ebit_val, (5000, 20000)), "€")
c3.metric("Break-Even (Units)", colorize(bep_val, (50, 200)), "units")
c4.metric("Free Cash Flow", colorize(fcf_val, (5000, 15000)), "€")

# Προσθήκη progress bars για πιο visual αίσθηση
st.markdown("### Performance Overview")
st.progress(min(rev_val / 50000, 1) if rev_val else 0)
st.progress(min(ebit_val / 20000, 1) if ebit_val else 0)
st.progress(min(fcf_val / 15000, 1) if fcf_val else 0)

st.divider()

    # --- QUICK ACTIONS ---
    st.subheader("Quick Start")
    st.write("Lock your baseline parameters or explore tools to guide your strategic decisions.")

    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🚀 Getting Started", expanded=True):
            st.write("Define your unit economics and fixed costs.")
            if st.button("Go to Stage 0", key="h_btn_s0", use_container_width=True):
                st.session_state.flow_step = "stage0"
                st.rerun()

    with col2:
        with st.expander("📚 Library & Tools", expanded=True):
            st.write("Access specialized calculators and strategic tools.")
            if st.button("Open Library", key="h_btn_lib", use_container_width=True):
                st.session_state.flow_step = "library"
                st.rerun()
