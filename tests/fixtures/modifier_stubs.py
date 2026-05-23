"""Shared modifier stub classes for builder UI tests.

PROJ-479 Task 5.5 (DUP-006, NEEDS_REWORK with narrowed scope per
verification_report.md): consolidates the `_Modifier` / `_SpecialModifier`
stub classes that were duplicated in builder UI tests.

Verification adjusted the original review's claim that 3+ files needed
consolidation — `test_workshop_viewmodel_selection.py` uses a `_Component`
stub not Modifier stubs; `test_propulsion_ability_bindings.py` uses inline
`MockComponent` for STAT_BINDINGS in a different domain. This fixture
file is for the builder-UI domain only.
"""
from __future__ import annotations

from typing import Any


class _Modifier:
    """Stub modifier with `definition` (any) and `value` (float)."""

    def __init__(self, definition: Any, value: float) -> None:
        self.definition = definition
        self.value = value


class _SpecialModifier(_Modifier):
    """Subclass marker for tests that need to distinguish modifier flavors."""
    pass
