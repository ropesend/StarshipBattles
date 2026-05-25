"""PROJ-497 Phase 2 Task 2.1: efficient_engines modifier deletion.

The user reversed Decision 1 from REDESIGN to DELETE on 2026-05-23.
Verbatim rationale:

    "The efficient engine ability should be eliminated, continuing to work
    with it is a mistake as it is too specific to a specific type of
    component/ability."

This test pins down the delete: `efficient_engines` must be absent from
both the raw `data/modifiers.json` payload and the live modifier registry.
"""

from __future__ import annotations

import json
import os

import pytest


def _load_modifier_ids_from_json() -> set[str]:
    here = os.path.dirname(__file__)
    path = os.path.join(here, "..", "..", "..", "data", "modifiers.json")
    path = os.path.abspath(path)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {m["id"] for m in data.get("modifiers", [])}


MODIFIER_IDS_ON_DISK = _load_modifier_ids_from_json()


class TestEfficientEnginesDeleted:
    """efficient_engines must be deleted (Decision 1, user-reversed 2026-05-23)."""

    def test_efficient_engines_not_in_data_file(self) -> None:
        assert "efficient_engines" not in MODIFIER_IDS_ON_DISK, (
            "PROJ-497 Decision 1 (revised): efficient_engines must be removed "
            "from data/modifiers.json. User: 'too specific to a specific type "
            "of component/ability'."
        )

    def test_efficient_engines_not_in_loaded_registry(self) -> None:
        """The live modifier registry must not contain efficient_engines."""
        from game.simulation.components.component_loader import load_modifiers_data

        registry = load_modifiers_data()
        assert "efficient_engines" not in registry, (
            "PROJ-497 Decision 1 (revised): efficient_engines must not load "
            "into the modifier registry after deletion from data/modifiers.json."
        )

    def test_efficient_engines_not_in_icon_map(self) -> None:
        """The UI icon map must not reference the deleted modifier id."""
        from game.ui.services.modifier_icon_service import MODIFIER_ICON_MAP

        assert "efficient_engines" not in MODIFIER_ICON_MAP, (
            "PROJ-497 Decision 1 (revised): efficient_engines icon-map entry "
            "must be removed once the modifier itself is deleted. Stale dict "
            "keys are dead code per CLAUDE.md root-cause rule."
        )

    def test_efficiency_mount_still_present(self) -> None:
        """Defensive: the sibling/replacement modifier must NOT be removed."""
        assert "efficiency_mount" in MODIFIER_IDS_ON_DISK, (
            "Defensive check: efficiency_mount (the parameterized "
            "ResourceConsumption-targeting sibling) must remain — only "
            "efficient_engines was deleted."
        )
