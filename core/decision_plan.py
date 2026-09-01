from dataclasses import dataclass
from typing import Tuple

from core.decision import Decision


# =========================================================
# DECISION PLAN
# =========================================================

@dataclass(frozen=True)
class DecisionPlan:
    """
    Immutable collection of business Decisions
    evaluated together as one management choice.

    A DecisionPlan does NOT:
        - execute decisions
        - modify CompanyState
        - calculate financial impact
        - resolve conflicts
        - assign priorities

    Its responsibility is limited to composing,
    adding, removing, and describing Decisions.

    Architecture:

        Decision
             \
        Decision  ---> DecisionPlan
             /
        Decision
             ↓
        DecisionRunner.run_many()
             ↓
        Projected CompanyState
    """

    id: str
    name: str
    decisions: Tuple[Decision, ...]

    # =====================================================
    # VALIDATION
    # =====================================================

    def __post_init__(self) -> None:
        """
        Validate the structural integrity of the plan.
        """

        if not isinstance(self.id, str):
            raise TypeError(
                "DecisionPlan id must be a string."
            )

        if not self.id.strip():
            raise ValueError(
                "DecisionPlan id cannot be empty."
            )

        if not isinstance(self.name, str):
            raise TypeError(
                "DecisionPlan name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "DecisionPlan name cannot be empty."
            )

        if not isinstance(self.decisions, tuple):
            raise TypeError(
                "DecisionPlan decisions must be a tuple."
            )

        for decision in self.decisions:

            if not isinstance(
                decision,
                Decision,
            ):
                raise TypeError(
                    "DecisionPlan can contain only "
                    "Decision objects."
                )

        ids = [
            decision.id
            for decision in self.decisions
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "A DecisionPlan cannot contain "
                "the same Decision more than once."
            )

    # =====================================================
    # FACTORY
    # =====================================================

    @classmethod
    def create(
        cls,
        *,
        plan_id: str,
        name: str,
        decisions: Tuple[Decision, ...] = (),
    ) -> "DecisionPlan":
        """
        Create a DecisionPlan.

        The plan may initially be empty.

        Decisions can then be added using add().
        """

        if not isinstance(
            decisions,
            tuple,
        ):
            decisions = tuple(decisions)

        return cls(
            id=plan_id,
            name=name,
            decisions=decisions,
        )

    # =====================================================
    # ADD DECISION
    # =====================================================

    def add(
        self,
        decision: Decision,
    ) -> "DecisionPlan":
        """
        Return a NEW DecisionPlan containing the
        supplied Decision.

        The existing plan remains unchanged.
        """

        if not isinstance(
            decision,
            Decision,
        ):
            raise TypeError(
                "Only Decision objects can be "
                "added to a DecisionPlan."
            )

        if self.contains(decision.id):
            raise ValueError(
                f"Decision '{decision.id}' "
                "already exists in this plan."
            )

        return DecisionPlan(
            id=self.id,
            name=self.name,
            decisions=self.decisions + (
                decision,
            ),
        )

    # =====================================================
    # REMOVE DECISION
    # =====================================================

    def remove(
        self,
        decision_id: str,
    ) -> "DecisionPlan":
        """
        Return a NEW DecisionPlan without the
        specified Decision.
        """

        if not isinstance(
            decision_id,
            str,
        ):
            raise TypeError(
                "decision_id must be a string."
            )

        remaining = tuple(
            decision
            for decision in self.decisions
            if decision.id != decision_id
        )

        if len(remaining) == len(
            self.decisions
        ):
            raise ValueError(
                f"Decision '{decision_id}' "
                "does not exist in this plan."
            )

        return DecisionPlan(
            id=self.id,
            name=self.name,
            decisions=remaining,
        )

    # =====================================================
    # CONTAINS
    # =====================================================

    def contains(
        self,
        decision_id: str,
    ) -> bool:
        """
        Check whether a Decision with the supplied
        ID belongs to this plan.
        """

        return any(
            decision.id == decision_id
            for decision in self.decisions
        )

    # =====================================================
    # COUNT
    # =====================================================

    @property
    def decision_count(self) -> int:
        """
        Number of Decisions contained in the plan.
        """

        return len(self.decisions)

    # =====================================================
    # EMPTY
    # =====================================================

    @property
    def is_empty(self) -> bool:
        """
        True when the plan contains no Decisions.
        """

        return not self.decisions

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self) -> str:
        """
        Return a simple human-readable description
        of the plan.
        """

        if self.is_empty:
            return (
                f"{self.name}: "
                "No decisions selected."
            )

        decision_names = [
            decision.name
            for decision in self.decisions
        ]

        return (
            f"{self.name}: "
            + " + ".join(decision_names)
        )
