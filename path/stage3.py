import streamlit as st
from core.sync import sync_global_state

def run_stage3():
    st.header("💧 Stage 3: Liquidity Physics")
    
    metrics = sync_global_state()
    st.subheader("💰 Working Capital Analysis")
    
    st.write(f"Accounts Receivable: €{metrics.get('accounts_receivable',0):,.0f}")
    st.write(f"Inventory Value: €{metrics.get('wc_requirement',0):,.0f}")
    st.write(f"Accounts Payable: €{metrics.get('ap_days',0):,.0f} days")
    st.write(f"Net Cash Position: €{metrics.get('net_cash_position',0):,.0f}")
