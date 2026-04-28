"""Tests pinning the canonical SHIP_CLASSES_WITH_VISUAL_THEMES set.

PROJ-314 Phase 1: this set is the schema-validation source of truth for
every `theme.json` file. Drift here breaks all ship-theme assets, so
the contract is locked down with explicit tests.
"""
from __future__ import annotations

from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES


class TestShipClassesWithVisualThemes:
    """Pin the canonical 19-entry visual-theme ship-class set."""

    def test_canonical_set_size(self) -> None:
        """The canonical set has exactly 19 entries."""
        assert len(SHIP_CLASSES_WITH_VISUAL_THEMES) == 19

    def test_all_capital_classes_present(self) -> None:
        """All 11 capital ship classes (Escort through Monitor) are in the set."""
        capitals = {
            "Escort",
            "Frigate",
            "Destroyer",
            "Light Cruiser",
            "Cruiser",
            "Heavy Cruiser",
            "Battle Cruiser",
            "Battleship",
            "Dreadnought",
            "Superdreadnought",
            "Monitor",
        }
        assert capitals <= SHIP_CLASSES_WITH_VISUAL_THEMES

    def test_all_fighter_classes_present(self) -> None:
        """All 4 Fighter sizes are in the set."""
        fighters = {
            "Fighter (Small)",
            "Fighter (Medium)",
            "Fighter (Large)",
            "Fighter (Heavy)",
        }
        assert fighters <= SHIP_CLASSES_WITH_VISUAL_THEMES

    def test_all_satellite_classes_present(self) -> None:
        """All 4 Satellite sizes are in the set."""
        satellites = {
            "Satellite (Small)",
            "Satellite (Medium)",
            "Satellite (Large)",
            "Satellite (Heavy)",
        }
        assert satellites <= SHIP_CLASSES_WITH_VISUAL_THEMES

    def test_set_is_frozen(self) -> None:
        """The constant is a frozenset, so it cannot be mutated at runtime."""
        assert isinstance(SHIP_CLASSES_WITH_VISUAL_THEMES, frozenset)
