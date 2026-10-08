# core/investment_decision.py

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class InvestmentDecision:
    """
    Immutable decision object representing an investment project.

    InvestmentDecision is intentionally separate from the generic Decision
    object because an investment is a composite project with its own
    assumptions, multi-year cash flows and Year-1 company impact.

    The investment engine remains responsible for evaluating the assumptions.
    This object only represents the investment as an item inside a
    DecisionPlan.
    """

    id: str
    name: str
    description: str
    assumptions: Any
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("InvestmentDecision id must be a non-empty string.")

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("InvestmentDecision name must be a non-empty string.")

        if not isinstance(self.description, str):
            raise TypeError("InvestmentDecision description must be a string.")

        if self.assumptions is None:
            raise ValueError("InvestmentDecision assumptions cannot be None.")

        if not isinstance(self.metadata, dict):
            raise TypeError("InvestmentDecision metadata must be a dictionary.")

    @classmethod
    def create(
        cls,
        decision_id: str,
        name: str,
        assumptions: Any,
        description: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> "InvestmentDecision":
        """
        Create an immutable InvestmentDecision.

        The assumptions object is deliberately kept as the investment
        assumptions contract supplied by the existing investment engine.
        """

        return cls(
            id=decision_id,
            name=name,
            description=description,
            assumptions=assumptions,
            metadata={} if metadata is None else dict(metadata),
        )

    def summary(self) -> Dict[str, Any]:
        """
        Return a compact representation suitable for plans, logs and UI.
        """

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "decision_type": "investment",
        }
