import numpy as np

# =========================
# FINANCIAL FUNCTIONS
# =========================

def annuity_payment(rate, n_periods, present_value, payment_at_beginning=False):
    """
    Υπολογισμός σταθερής δόσης (τύπος PMT)
    """
    if rate == 0:
        return present_value / n_periods

    factor = (rate * (1 + rate) ** n_periods) / ((1 + rate) ** n_periods - 1)
    payment = present_value * factor

    if payment_at_beginning:
        payment /= (1 + rate)

    return payment


def total_interest(payment, n_periods, principal):
    return payment * n_periods - principal


# =========================
# INPUT PARAMETERS
# =========================

loan_interest = 0.06
working_capital_interest = 0.08
years = 15
months_per_year = 12
tax_rate = 0.35

financing_percentage_loan = 0.70
financing_percentage_leasing = 1.0

property_value = 250000
additional_expenses_loan = 35000
additional_expenses_leasing = 30000

working_capital_loan = 110000
working_capital_leasing = 30000

depreciation_period = 30
residual_value_leasing = 3530


# =========================
# LOAN SCENARIO
# =========================

loan_amount = property_value * financing_percentage_loan
n_months = years * months_per_year
monthly_rate_loan = loan_interest / 12

monthly_installment_loan = annuity_payment(
    monthly_rate_loan,
    n_months,
    loan_amount,
    payment_at_beginning=True
)

monthly_rate_wc = working_capital_interest / 12
monthly_installment_wc = annuity_payment(
    monthly_rate_wc,
    n_months,
    working_capital_loan
)

total_monthly_installment_loan = (
    monthly_installment_loan + monthly_installment_wc
)

total_interest_loan = total_interest(
    monthly_installment_loan,
    n_months,
    loan_amount
)

total_cost_loan = loan_amount + total_interest_loan

annual_depreciation = property_value / depreciation_period
total_depreciation_loan = annual_depreciation * years

deductible_expense_loan = total_interest_loan + total_depreciation_loan
tax_benefit_loan = deductible_expense_loan * tax_rate

final_net_burden_loan = total_cost_loan + additional_expenses_loan - tax_benefit_loan


# =========================
# LEASING SCENARIO
# =========================

leasing_amount = property_value * financing_percentage_leasing
monthly_installment_leasing = annuity_payment(
    monthly_rate_loan,
    n_months,
    leasing_amount
)

monthly_installment_wc_leasing = annuity_payment(
    monthly_rate_wc,
    n_months,
    working_capital_leasing
)

total_monthly_installment_leasing = (
    monthly_installment_leasing + monthly_installment_wc_leasing
)

total_interest_leasing = total_interest(
    monthly_installment_leasing,
    n_months,
    leasing_amount
)

total_cost_leasing = leasing_amount + total_interest_leasing

total_depreciation_leasing = residual_value_leasing + additional_expenses_leasing
deductible_expense_leasing = total_interest_leasing + total_depreciation_leasing
tax_benefit_leasing = deductible_expense_leasing * tax_rate

final_net_burden_leasing = total_cost_leasing + additional_expenses_leasing - tax_benefit_leasing


# =========================
# RESULTS
# =========================

print("===== LOAN =====")
print("Monthly Installment:", round(monthly_installment_loan, 2))
print("Total Interest:", round(total_interest_loan, 2))
print("Tax Benefit:", round(tax_benefit_loan, 2))
print("Final Net Burden:", round(final_net_burden_loan, 2))

print("\n===== LEASING =====")
print("Monthly Installment:", round(monthly_installment_leasing, 2))
print("Total Interest:", round(total_interest_leasing, 2))
print("Tax Benefit:", round(tax_benefit_leasing, 2))
print("Final Net Burden:", round(final_net_burden_leasing, 2))
