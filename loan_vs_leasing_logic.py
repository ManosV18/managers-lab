import numpy_financial as npf

def pmt(rate, nper, pv, fv=0, when=0):
    return -npf.pmt(rate, nper, pv, fv, when)

def calculate_final_burden(
    loan_rate,
    wc_rate,
    duration_years,
    property_value,
    loan_financing_percent,
    leasing_financing_percent,
    add_expenses_loan,
    add_expenses_leasing,
    residual_value_leasing,
    depreciation_years,
    tax_rate,
    pay_when
):
    months = 12
    n_months = duration_years * months

    acquisition_cost_loan = property_value + add_expenses_loan
    acquisition_cost_lease = property_value + add_expenses_leasing

    wc_loan = property_value - (property_value * loan_financing_percent) + add_expenses_loan
    wc_lease = property_value - (property_value * leasing_financing_percent) + add_expenses_leasing

    monthly_loan = pmt(loan_rate / months, n_months, property_value * loan_financing_percent, 0, pay_when)
    monthly_lease = pmt(loan_rate / months, n_months, property_value * leasing_financing_percent, 0, pay_when)
    monthly_wc_loan = pmt(wc_rate / months, n_months, wc_loan, 0, pay_when)
    monthly_wc_lease = pmt(wc_rate / months, n_months, wc_lease, 0, pay_when)

    total_monthly_loan = monthly_loan + monthly_wc_loan
    total_monthly_lease = monthly_lease + monthly_wc_lease

    total_interest_loan = (total_monthly_loan * n_months) - property_value
    total_interest_lease = (total_monthly_lease * n_months) - property_value

    total_cost_loan = total_interest_loan + property_value
    total_cost_lease = total_interest_lease + property_value

    depreciation_loan = acquisition_cost_loan / depreciation_years * duration_years
    depreciation_lease = acquisition_cost_lease + residual_value_leasing

    deductible_loan = total_interest_loan + depreciation_loan
    deductible_lease = (monthly_wc_lease * n_months - wc_lease) + depreciation_lease

    tax_benefit_loan = deductible_loan * tax_rate
    tax_benefit_lease = deductible_lease * tax_rate

    final_loan = total_cost_loan - tax_benefit_loan
    final_lease = total_cost_lease - tax_benefit_lease

    return round(final_loan), round(final_lease)
