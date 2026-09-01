from dataclasses import fields, replace
from typing import Any, Dict, List, Set, Tuple, Type, get_args, get_origin

from core.decision import Decision
from core.models import (
    CapitalStructure,
    CompanyState,
    OperationalDrivers,
    WorkingCapitalPolicy,
)


class DecisionEngine:
    """
    Pure Deterministic Execution Kernel.
    Applies canonical decisions to CompanyState without domain assumptions.
    Fails fast if an unknown/unmapped field is encountered.
    """

    # Comprehensive Compatibility Layer (Legacy/Alternative Aliases -> Canonical Fields)
    FIELD_ALIASES: Dict[str, str] = {
        # Working Capital Aliases
        "target_ar_days": "ar_days",
        "dso": "ar_days",
        "receivables_days": "ar_days",
        "target_inventory_days": "inventory_days",
        "dio": "inventory_days",
        "target_ap_days": "ap_days",
        "dpo": "ap_days",
        "payables_days": "ap_days",
        
        # Capital Structure / WACC Aliases
        "target_wacc": "wacc",
        "cost_of_equity": "ke",
    }

    @classmethod
    def apply(
        cls,
        state: CompanyState,
        decision: Decision,
    ) -> Tuple[CompanyState, Dict[str, Any]]:
        cls._validate_state(state)
        cls._validate_decision(decision)

        changes = decision.changes

        # 1. Υπολογισμός όλων των αποδεκτών canonical πεδίων του CompanyState (Union of Model Fields)
        valid_model_fields: Set[str] = (
            {f.name for f in fields(OperationalDrivers)}
            | {f.name for f in fields(CapitalStructure)}
            | {f.name for f in fields(WorkingCapitalPolicy)}
        )

        # 2. Strict Validation: Έλεγχος αν υπάρχουν άγνωστα πεδία στα changes (Fail-Fast)
        unknown_fields = []
        for raw_key in changes.keys():
            canonical_key = cls.FIELD_ALIASES.get(raw_key, raw_key)
            if canonical_key not in valid_model_fields:
                unknown_fields.append(raw_key)

        if unknown_fields:
            raise ValueError(
                f"Cannot apply decision '{decision.name}' (ID: {decision.id}). "
                f"Unknown or unmapped fields: {sorted(unknown_fields)}"
            )

        # 3. Εφαρμογή των αλλαγών στα επιμέρους sub-models
        operational, op_changes = cls._apply_model_changes(
            state.drivers, OperationalDrivers, changes
        )

        capital, cap_changes = cls._apply_model_changes(
            state.capital_structure, CapitalStructure, changes
        )

        working_capital, wc_changes = cls._apply_model_changes(
            state.working_capital, WorkingCapitalPolicy, changes
        )

        # 4. Δημιουργία του νέου Projected State (Immutable Update)
        projected_state = replace(
            state,
            version=state.version + 1,
            label=f"After Decision: {decision.name}",
            drivers=operational,
            capital_structure=capital,
            working_capital=working_capital,
        )

        trace = {
            "decision_id": decision.id,
            "decision_name": decision.name,
            "decision_category": decision.category,
            "description": decision.description,
            "base_version": state.version,
            "projection_version": projected_state.version,
            "changes": op_changes + cap_changes + wc_changes,
        }

        return projected_state, trace

    @classmethod
    def _apply_model_changes(
        cls,
        model_instance: Any,
        model_class: Type[Any],
        changes: Dict[str, Any],
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        Applies changes to a specific dataclass model if matching fields are found.
        """
        updated_instance = model_instance
        trace: List[Dict[str, Any]] = []

        model_fields = {f.name: f.type for f in fields(model_class)}

        for raw_key, raw_value in changes.items():
            target_field = cls.FIELD_ALIASES.get(raw_key, raw_key)

            # Αν το πεδίο δεν ανήκει σε αυτό το συγκεκριμένο model, προσπερνάμε
            if target_field not in model_fields or raw_value is None:
                continue

            old_val = getattr(updated_instance, target_field)
            expected_type = model_fields[target_field]
            target_type = cls._unwrap_type(expected_type)

            try:
                if target_type == int:
                    typed_val = int(raw_value)
                elif target_type == float:
                    typed_val = float(raw_value)
                else:
                    typed_val = raw_value
            except (ValueError, TypeError):
                typed_val = raw_value

            if isinstance(typed_val, (int, float)):
                cls._require_non_negative(target_field, float(typed_val))

            updated_instance = replace(updated_instance, **{target_field: typed_val})

            trace.append({
                "field": target_field,
                "old": old_val,
                "new": typed_val,
                "mode": "absolute",
            })

        return updated_instance, trace

    @staticmethod
    def _unwrap_type(type_hint: Any) -> Any:
        """Extracts primitive types from Optional / Union annotations."""
        origin = get_origin(type_hint)
        if origin is None:
            return type_hint
        args = [arg for arg in get_args(type_hint) if arg is not type(None)]
        return args[0] if args else type_hint

    @staticmethod
    def _validate_state(state: CompanyState) -> None:
        if not isinstance(state, CompanyState):
            raise TypeError("DecisionEngine expects a valid CompanyState instance.")

    @staticmethod
    def _validate_decision(decision: Decision) -> None:
        if not isinstance(decision, Decision):
            raise TypeError("DecisionEngine expects a valid Decision instance.")

    @staticmethod
    def _require_non_negative(field_name: str, value: float) -> None:
        if value < 0:
            raise ValueError(f"Field '{field_name}' cannot be negative. Got: {value}")
