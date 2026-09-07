from dataclasses import dataclass
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class SalesCostSummary:
    total_volume: float
    total_sales: float
    weighted_average_price: float
    total_variable_cost: float
    variable_cost_per_unit: float
    gross_profit: float
    gross_margin_pct: float

DEFAULT_COST_FIELDS = (
    "material_cost",
    "freight_cost",
    "packaging_cost",
    "sales_commission",
    "other_variable_cost",
)

def _to_float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)

def calculate_sales_cost_summary(
    rows: Iterable[Mapping[str, Any]],
    quantity_field: str = "quantity",
    sales_field: str = "sales",
    cost_fields: tuple[str, ...] = DEFAULT_COST_FIELDS,
) -> SalesCostSummary:
    total_volume = 0.0
    total_sales = 0.0
    total_variable_cost = 0.0

    for row in rows:
        quantity = _to_float(row.get(quantity_field))
        sales = _to_float(row.get(sales_field))
        if quantity < 0 or sales < 0:
            raise ValueError("Quantity and sales cannot be negative.")

        variable_cost = sum(_to_float(row.get(f)) for f in cost_fields)
        if variable_cost < 0:
            raise ValueError("Variable cost cannot be negative.")

        total_volume += quantity
        total_sales += sales
        total_variable_cost += variable_cost

    if total_volume <= 0:
        raise ValueError("Total volume must be greater than zero.")

    price = total_sales / total_volume
    variable_cost_per_unit = total_variable_cost / total_volume
    gross_profit = total_sales - total_variable_cost
    gross_margin = (gross_profit / total_sales * 100) if total_sales else 0.0

    return SalesCostSummary(
        total_volume=total_volume,
        total_sales=total_sales,
        weighted_average_price=price,
        total_variable_cost=total_variable_cost,
        variable_cost_per_unit=variable_cost_per_unit,
        gross_profit=gross_profit,
        gross_margin_pct=gross_margin,
    )
