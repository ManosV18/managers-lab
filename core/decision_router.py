from typing import Any, Dict, List

# =========================================================
# DECISION ROUTER
# =========================================================

class DecisionRouter:
    """
    Maps diagnostic findings to relevant Decision Labs.

    The router is deliberately lightweight.

    A diagnostic tells us:
        "This condition exists."

    The router answers:
        "Which existing decision areas can affect
         the drivers related to this condition?"

    It does NOT answer:
        "What should the owner do?"
    """

    # =====================================================
    # CASH FRAGILITY ROUTES
    # =====================================================

    @classmethod
    def routes_for_cash_fragility(
        cls,
        result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Return Decision Lab routes relevant to a
        Cash Fragility diagnostic.
        """

        if not isinstance(result, dict):
            return []

        routes: List[Dict[str, Any]] = []

        # -------------------------------------------------
        # RECEIVABLES
        # -------------------------------------------------

        routes.append(
            {
                "decision_area": "Receivables",
                "page": "💶 Receivables Lab",
                "driver": "ar_days",
                "label": "Test Customer Payment Terms",
                "description": (
                    "Test how different customer payment "
                    "terms could affect cash tied up "
                    "in receivables."
                ),
            }
        )

        # -------------------------------------------------
        # INVENTORY
        # -------------------------------------------------

        routes.append(
            {
                "decision_area": "Inventory",
                "page": "📦 Inventory Lab",
                "driver": "inventory_days",
                "label": "Test Inventory Levels",
                "description": (
                    "Test how different inventory levels "
                    "could affect cash tied up in stock."
                ),
            }
        )

        # -------------------------------------------------
        # SUPPLIER TERMS
        # -------------------------------------------------

        routes.append(
            {
                "decision_area": "Supplier Terms",
                "page": "🚚 Suppliers & Payables Lab",
                "driver": "ap_days",
                "label": "Test Supplier Terms",
                "description": (
                    "Test how different supplier payment "
                    "terms could affect operating liquidity."
                ),
            }
        )

        return routes
