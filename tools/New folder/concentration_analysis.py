import numpy as np
import pandas as pd


CONCENTRATION_THRESHOLD = 0.25


def calculate_concentration_metrics(df_clean: pd.DataFrame):
    """
    Calculate concentration metrics for a dataset.

    Expected columns:
        Name
        Value

    Returns:
        metrics: dict
        sorted DataFrame with cumulative percentages
    """

    if df_clean.empty or df_clean["Value"].sum() == 0:
        return {
            "hhi": 0,
            "gini": 0,
            "pareto_items_pct": 0,
            "pareto_count": 0,
            "total_items": 0,
            "total_value": 0,
            "status": "No Data",
            "risk_level": "none",
            "top_item_pct": 0,
            "top_item_name": "-",
        }, df_clean

    df = (
        df_clean
        .copy()
        .sort_values(by="Value", ascending=False)
        .reset_index(drop=True)
    )

    total_value = df["Value"].sum()
    total_items = len(df)

    # HHI
    df["Share_Pct"] = (df["Value"] / total_value) * 100
    hhi = float(np.sum(df["Share_Pct"] ** 2))

    # Pareto
    df["Cum_Sum"] = df["Value"].cumsum()
    df["Cum_Pct"] = (df["Cum_Sum"] / total_value) * 100

    items_to_80 = df[df["Cum_Pct"] >= 80].index.min()

    items_count_80 = (
        int(items_to_80 + 1)
        if pd.notna(items_to_80)
        else total_items
    )

    pareto_items_pct = (
        items_count_80 / total_items
    ) * 100

    # Gini
    values = df["Value"].to_numpy()
    n = len(values)

    if n > 1 and np.mean(values) != 0:
        diff_matrix = np.abs(values[:, None] - values)
        gini = float(
            np.sum(diff_matrix)
            / (2 * (n ** 2) * np.mean(values))
        )
    else:
        gini = 0.0

    # Risk classification
    if hhi < 1500:
        status = "Low Risk (Well Diversified)"
        risk_level = "low"

    elif hhi <= 2500:
        status = "Moderate Risk (Moderate Concentration)"
        risk_level = "moderate"

    else:
        status = "High Risk (Highly Concentrated)"
        risk_level = "high"

    # Top item
    top_item_pct = float(df.loc[0, "Share_Pct"] / 100)
    top_item_name = df.loc[0, "Name"]

    metrics = {
        "hhi": hhi,
        "gini": gini,
        "pareto_items_pct": pareto_items_pct,
        "pareto_count": items_count_80,
        "total_items": total_items,
        "total_value": float(total_value),
        "status": status,
        "risk_level": risk_level,
        "top_item_pct": top_item_pct,
        "top_item_name": top_item_name,
    }

    return metrics, df


def process_raw_text(text_input: str) -> pd.DataFrame:
    """
    Convert a pasted list of values into a clean DataFrame.
    """

    if not text_input.strip():
        return pd.DataFrame(columns=["Name", "Value"])

    lines = text_input.strip().splitlines()
    data = []

    for i, line in enumerate(lines):

        val_str = (
            line
            .replace("$", "")
            .replace("€", "")
            .replace(",", "")
            .strip()
        )

        try:
            value = float(val_str)

            if value > 0:
                data.append(
                    {
                        "Name": f"Item {i + 1}",
                        "Value": value,
                    }
                )

        except ValueError:
            continue

    return pd.DataFrame(data)


def calculate_customer_dependency(metrics: dict):
    """
    Evaluate whether the largest customer creates material
    concentration exposure.
    """

    top_pct = metrics.get("top_item_pct", 0.0)

    return {
        "material_concentration": (
            top_pct > CONCENTRATION_THRESHOLD
        ),
        "top_customer_pct": top_pct,
        "threshold": CONCENTRATION_THRESHOLD,
    }


def calculate_buyer_risk(
    top_pct: float,
    contractual_lock_in: bool,
    team_owned: bool,
    high_switching_cost: bool,
):
    """
    Evaluate qualitative buyer / investor concentration risk.

    Returns a simple risk classification based on:
    - revenue concentration
    - contractual protection
    - organizational ownership
    - switching costs
    """

    if top_pct <= CONCENTRATION_THRESHOLD:
        return {
            "risk_level": "low",
            "score": 0,
            "status": "Healthy Diversification",
        }

    high_risk_score = 0

    if not contractual_lock_in:
        high_risk_score += 1

    if not team_owned:
        high_risk_score += 1

    if not high_switching_cost:
        high_risk_score += 1

    if high_risk_score == 0:
        risk_level = "low"
        status = "Defensible Concentration"

    elif high_risk_score == 1:
        risk_level = "moderate"
        status = "Manageable Diligence Risk"

    else:
        risk_level = "high"
        status = "High Valuation Risk"

    return {
        "risk_level": risk_level,
        "score": high_risk_score,
        "status": status,
    }
