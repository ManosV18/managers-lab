# home.py
import streamlit as st

def show_home():
    st.title("🎯 Welcome to Managers’ Lab!")
    st.subheader("Smart tools for data-driven financial decisions")

    st.markdown("""
**Managers’ Lab** is an online platform that helps you make faster, clearer, and better-informed financial decisions for your business.

No need for complex Excel sheets — all tools are available in a **friendly interface with simple input fields**.

---

## 📌 What you can do here:

🔹 **Break-Even Calculator** — Know your survival threshold instantly.  
🔹 **Break-Even Shift Analysis** — See how price, cost, or investment changes affect your break-even.  
🔹 **Customer Lifetime Value (CLV) Analysis** — Measure the long-term value of your customers.  
🔹 **Substitution Analysis** — Evaluate effects of switching products.  
🔹 **Complementary Product Analysis** — Identify synergies between products.  
🔹 **Loss Threshold Before Price Cut** — Estimate safe price changes.  
🔹 **Credit Policy Analysis** — Assess your receivables strategy.  
🔹 **Supplier Payment Analysis** — Manage payables efficiently.  
🔹 **Cash Cycle Calculator** — Optimize cash flow and working capital.  
🔹 **Gross Profit Estimation** — Measure profitability per product/service.  
🔹 **Economic Order Quantity (EOQ)** — Plan the most cost-effective stock orders.  
🔹 **Loan vs Leasing Analysis** — Compare financing options.  
🔹 **Unit Cost Calculator** — Determine production cost per unit.  
🔹 **Discount NPV Analysis** — Evaluate early payment discounts and their net effect.  
🔹 **Credit Days Calculator** — Monitor average credit terms.  
🔹 **Inventory Turnover Analysis** — Track stock movement efficiency.

---

## 🧭 How to start:

1. Choose a tool from the left sidebar.  
2. Fill in your own data in the input fields.  
3. See numbers, charts, and insights immediately.

---

## 💡 Tip:

Even small changes in price, cost, or marketing can have a big impact on your break-even, cash flow, and CLV. Experiment with the tools to understand the ripple effect of your decisions.

---

## 📬 Contact & Feedback

We are in **beta**, and your feedback is essential to improve the platform.  
Email us at: ✉️ [managersclub2025@gmail.com](mailto:managersclub2025@gmail.com)
""")

    # Beta notice box
    st.info("""
**Note:** Managers’ Club is currently in **beta phase**.  
Your suggestions and feedback help us improve the experience.  

*(This is not a professional collaboration offer — just a way to gather insights from early users.)*
""")

    st.markdown("""
---

## 🚀 Ready to take control?

Start from the sidebar and explore what **Managers’ Club** can do for your business.
""")
