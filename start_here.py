# start_here.py
import streamlit as st

def show_start_here():
    st.title("🧭 How to Use the Managers’ Lab")

    st.markdown("""
### What this Lab is — and what it is not

Managers’ Lab is **not** a dashboard.  
It does not summarize performance, forecast results, or optimize outcomes.

This is a **decision-testing environment**.

Its purpose is simple:
to expose what a decision *requires* in order not to fail.

---

### The core idea

Most business decisions look small when viewed in isolation.

A price change.  
A cost adjustment.  
An investment.  
A change in payment terms.

The risk is not the decision itself —  
but the **structural shift** it creates.

This Lab is built to make those shifts visible.

---

### How to think while using the tools

Do not ask:
> “Is this a good decision?”

Ask instead:
- What must be true for this decision to work?
- How much margin, volume, or timing error can I tolerate?
- Which assumption breaks first?

Break-even is not a target.  
It is a **survival condition**.

Sensitivity is not analysis.  
It is **fragility detection**.

---

### How to navigate the Lab

- Start with **Break-Even** to anchor survival.
- Use **Shifts & Sensitivity** to see how structure changes.
- Use **CLV and Cash tools** to test sustainability, not growth.
- Treat every output as a constraint — not an answer.

If the numbers feel uncomfortable, the Lab is working.

---

### A final note

Small decisions are never small  
because systems do not fail gradually —  
they fail when thresholds are crossed quietly.

This Lab exists to make those thresholds visible.
""")
