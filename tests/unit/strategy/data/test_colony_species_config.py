"""Unit tests for `ColonySpeciesConfig` (PROJ-284 Phase 1).

`ColonySpeciesConfig` stores per-colony per-species sliders. Currently
holds:
    food_allocation:  player-set linear scalar on consumption / happiness /
                      reproduction. Default 1.0.
    last_food_ratio:  TRANSIENT cache written by `OrganicsConsumptionEngine`
                      each turn. Reset to 1.0 on construction; NOT serialized
                      (would lie about the post-load demographic state).

The class is the home for future per-colony per-species knobs (labor,
tax, etc.) without polluting `SpeciesPopulation` (which stays pure
runtime state).
"""
from __future__ import annotations

import pytest


class TestColonySpeciesConfigDefaults:
    def test_default_food_allocation_is_one(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        assert cfg.food_allocation == 1.0

    def test_default_last_food_ratio_is_one(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        assert cfg.last_food_ratio == 1.0


class TestColonySpeciesConfigValidation:
    def test_negative_food_allocation_rejected(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        from game.core.exceptions import ValidationException
        with pytest.raises(ValidationException):
            ColonySpeciesConfig(food_allocation=-0.1)

    def test_zero_food_allocation_accepted(self):
        """Zero is the "starve this species" extreme; UI offers it."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=0.0)
        assert cfg.food_allocation == 0.0

    def test_high_food_allocation_accepted(self):
        """Range is 0..inf; UI caps at 5 but typed input can exceed."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=10.0)
        assert cfg.food_allocation == 10.0


class TestColonySpeciesConfigSerialization:
    def test_to_dict_emits_only_food_allocation(self):
        """Per the PROJ-284 design, `last_food_ratio` is TRANSIENT and
        must NOT appear in the serialized form — saving it would
        misrepresent the post-load demographic state, which the
        consumption engine recomputes on the next turn anyway."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=2.5, last_food_ratio=0.3)
        data = cfg.to_dict()
        assert data == {"food_allocation": 2.5}
        assert "last_food_ratio" not in data

    def test_from_dict_restores_food_allocation(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig.from_dict({"food_allocation": 0.5})
        assert cfg.food_allocation == 0.5

    def test_from_dict_resets_last_food_ratio_to_default(self):
        """Even if a corrupt/old save sneaks `last_food_ratio` in,
        from_dict ignores it — the field always starts at 1.0 and the
        next turn's consumption engine overwrites it."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig.from_dict({
            "food_allocation": 1.5,
            "last_food_ratio": 0.0,  # ignored
        })
        assert cfg.last_food_ratio == 1.0

    def test_from_dict_uses_default_when_food_allocation_missing(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig.from_dict({})
        assert cfg.food_allocation == 1.0
        assert cfg.last_food_ratio == 1.0

    def test_round_trip_preserves_food_allocation_resets_ratio(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        original = ColonySpeciesConfig(food_allocation=2.0, last_food_ratio=0.4)
        restored = ColonySpeciesConfig.from_dict(original.to_dict())
        assert restored.food_allocation == 2.0
        assert restored.last_food_ratio == 1.0  # transient — reset on round-trip


class TestColonySpeciesConfigFutureExtensibility:
    """Sanity check that the class is safe to extend without breaking
    the PROJ-284 invariants (food_allocation persists, transient fields
    don't)."""

    def test_food_allocation_is_a_float(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=3)  # int input
        assert isinstance(cfg.food_allocation, (int, float))
