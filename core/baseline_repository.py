from typing import Optional, Dict, Any

import streamlit as st

from core.models import CompanyState


class BaselineRepository:
    """
    Repository Layer for the canonical Baseline CompanyState.

    The baseline is stored in Streamlit session_state and acts
    as the immutable reference point for the application.

    Responsibilities:
    - Store the canonical CompanyState
    - Retrieve the canonical CompanyState
    - Check baseline existence
    - Provide baseline metadata
    - Clear the baseline

    Does NOT:
    - Modify CompanyState
    - Execute decisions
    - Evaluate DecisionPlans
    - Calculate financial metrics
    """

    _KEY = "locked_baseline"

    # =====================================================
    # SAVE
    # =====================================================

    @classmethod
    def save(cls, state: CompanyState) -> None:
        """
        Store a canonical CompanyState as the locked baseline.
        """

        if not isinstance(state, CompanyState):
            raise TypeError(
                "BaselineRepository.save() expects "
                "a core.models.CompanyState instance."
            )

        st.session_state[cls._KEY] = state

    # =====================================================
    # LOAD
    # =====================================================

    @classmethod
    def load(cls) -> Optional[CompanyState]:
        """
        Return the stored baseline, if one exists.

        This method intentionally does not raise when the
        baseline does not exist.
        """

        return st.session_state.get(cls._KEY)

    # =====================================================
    # GET
    # =====================================================

    @classmethod
    def get(cls) -> CompanyState:
        """
        Return the locked canonical CompanyState.

        Raises:
            RuntimeError:
                If no baseline exists.

            TypeError:
                If stale or incompatible data is found in
                session_state.
        """

        state = cls.load()

        if state is None:
            raise RuntimeError(
                "No baseline CompanyState is locked. "
                "Lock a baseline before using downstream modules."
            )

        if not isinstance(state, CompanyState):
            actual_type = type(state)

            raise TypeError(
                "Locked baseline is not the current canonical "
                "core.models.CompanyState. "
                f"Actual type: {actual_type.__module__}."
                f"{actual_type.__name__}"
            )

        return state

    # =====================================================
    # EXISTS
    # =====================================================

    @classmethod
    def exists(cls) -> bool:
        """
        Return True only when a baseline is present.

        A stale/incompatible object is not considered a valid
        canonical baseline.
        """

        state = cls.load()

        return isinstance(
            state,
            CompanyState,
        )

    # =====================================================
    # METADATA
    # =====================================================

    @classmethod
    def metadata(cls) -> Dict[str, Any]:
        """
        Return basic metadata for the current baseline.

        If the stored object is stale or incompatible,
        report no valid baseline rather than attempting to
        access its attributes.
        """

        state = cls.load()

        if not isinstance(
            state,
            CompanyState,
        ):
            return {
                "exists": False,
                "version": None,
                "created_at": None,
                "label": None,
            }

        return {
            "exists": True,
            "version": state.version,
            "created_at": state.created_at,
            "label": state.label,
        }

    # =====================================================
    # CLEAR
    # =====================================================

    @classmethod
    def clear(cls) -> None:
        """
        Remove the locked baseline from session_state.
        """

        st.session_state.pop(
            cls._KEY,
            None,
        )
