import streamlit as st
from discount_npv_logic import calculate_discount_npv
from utils import format_number_gr, format_percentage_gr


def show_discount_npv_ui():
    st.header("💳 Cash Discount – NPV Analysis")
    st.caption("Αξιολόγηση πιστωτικής πολιτικής με βάση την Καθαρή Παρούσα Αξία (NPV)")

    with st.sidebar:
        st.subheader("📥 Πωλήσεις & Πελάτες")
        current_sales = st.number_input("Τρέχουσες Πωλήσεις (€)", value=1000.0, step=100.0)
        extra_sales = st.number_input("Επιπλέον Πωλήσεις λόγω Έκπτωσης (€)", value=250.0, step=50.0)
        prc_clients_take_disc = st.number_input("Πελάτες που λαμβάνουν την έκπτωση (%)", value=40.0, step=1.0) / 100

        st.divider()
        st.subheader("⏱️ Ημέρες Πίστωσης")
        days_clients_take_discount = st.number_input("Ημέρες πληρωμής (με έκπτωση)", value=60, step=1)
        days_clients_no_discount = st.number_input("Ημέρες πληρωμής (χωρίς έκπτωση)", value=120, step=1)
        new_days_cash_payment = st.number_input("Νέες ημέρες πληρωμής με έκπτωση", value=10, step=1)

        st.divider()
        st.subheader("💸 Κόστος & Χρηματοδότηση")
        cogs = st.number_input("Κόστος Πωληθέντων – COGS (€)", value=800.0, step=100.0)
        discount_trial = st.number_input("Προτεινόμενη Έκπτωση (%)", value=2.0, step=0.1) / 100
        wacc = st.number_input("Κόστος Κεφαλαίου (WACC %)", value=20.0, step=0.1) / 100
        avg_days_pay_suppliers = st.number_input("Μέσες Ημέρες Πληρωμής Προμηθευτών", value=30, step=1)

        calculate = st.button("📊 Υπολογισμός")

    if not calculate:
        st.info("⬅️ Συμπλήρωσε τα στοιχεία στην πλαϊνή μπάρα και πάτησε **Υπολογισμός**")
        return

    results = calculate_discount_npv(
        current_sales,
        extra_sales,
        discount_trial,
        prc_clients_take_disc,
        days_clients_take_discount,
        days_clients_no_discount,
        new_days_cash_payment,
        cogs,
        wacc,
        avg_days_pay_suppliers
    )

    st.subheader("📌 Βασικά Αποτελέσματα")
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Τρέχουσα Μέση Περίοδος Είσπραξης",
        f"{results['avg_current_collection_days']} ημέρες"
    )
    col2.metric(
        "Νέα Μέση Περίοδος Είσπραξης",
        f"{results['new_avg_collection_period']} ημέρες"
    )
    col3.metric(
        "Απελευθερωμένο Κεφάλαιο",
        f"{format_number_gr(results['free_capital'])} €"
    )

    st.subheader("💰 Οικονομική Επίδραση")
    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Κέρδος από Επιπλέον Πωλήσεις",
        f"{format_number_gr(results['profit_from_extra_sales'])} €"
    )
    col5.metric(
        "Όφελος από Κεφάλαιο",
        f"{format_number_gr(results['profit_from_free_capital'])} €"
    )
    col6.metric(
        "Κόστος Έκπτωσης",
        f"{format_number_gr(results['discount_cost'])} €"
    )

    st.divider()

    st.subheader("📈 Απόφαση Πιστωτικής Πολιτικής")
    col7, col8, col9 = st.columns(3)

    col7.metric(
        "Καθαρή Παρούσα Αξία (NPV)",
        f"{format_number_gr(results['npv'])} €"
    )
    col8.metric(
        "Μέγιστη Αποδεκτή Έκπτωση",
        format_percentage_gr(results['max_discount'])
    )
    col9.metric(
        "Βέλτιστη Έκπτωση",
        format_percentage_gr(results['optimum_discount'])
    )

    with st.expander("📘 Ερμηνεία"):
        st.markdown(
            """
            - **NPV > 0**: η πολιτική έκπτωσης αυξάνει την αξία της επιχείρησης.
            - **Μέγιστη έκπτωση**: το ανώτατο όριο πριν η NPV γίνει μηδενική.
            - **Βέλτιστη έκπτωση**: θεωρητικό σημείο ισορροπίας μεταξύ χρόνου και κόστους.
            """
        )
