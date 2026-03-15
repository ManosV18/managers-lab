import streamlit as st
import pandas as pd


def show_scenario_comparison():

    st.title("📊 Scenario Comparison")

    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = {}

    scenarios = st.session_state.saved_scenarios

    if not scenarios:

        st.info("No saved scenarios yet.")
        return

    rows = []

    for name, data in scenarios.items():

        rows.append({
            "Scenario": name,
            "Price": data.get("price",0),
            "Volume": data.get("volume",0),
            "ROIC": data.get("metrics",{}).get("roic",0),
            "Break Even": data.get("metrics",{}).get("bep_units",0),
            "Net Cash": data.get("metrics",{}).get("net_cash_position",0)
        })

    df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True)

    st.caption("Compare financial resilience across scenarios.")

    st.divider()

    # DELETE
    st.subheader("🗑 Delete Scenario")

    scenario_to_delete = st.selectbox(
        "Select Scenario to Delete",
        list(scenarios.keys())
    )

    if st.button("Delete Scenario", use_container_width=True):

        del st.session_state.saved_scenarios[scenario_to_delete]

        st.success(f"Scenario '{scenario_to_delete}' deleted.")

        st.rerun()
