"""Characterization tests for game/strategy/data/species_population.py.

PROJ-335 Phase 1. These tests pin the **current** behavior of
SpeciesPopulation, including the absence of bounds validation on
``count`` and ``happiness``. Existing tests in
``tests/unit/strategy/data/test_population_model.py::TestSpeciesPopulation``
cover construction defaults / explicit values / boundary happiness; this
file covers the gap: ``from_dict`` happy path, ``from_dict`` missing-key
rejection, and out-of-range / negative inputs (no validation = silent
acceptance).

Mode: characterization-only. No bug fixes — see PROJ-335 decisions.md D-007.
"""
from __future__ import annotations

import pytest

from game.core.exceptions import PersistenceException
from game.strategy.data.species_population import SpeciesPopulation


class TestFromDictHappyPath:
    """from_dict pins the documented contract."""

    def test_from_dict_minimum_required_fields_defaults_happiness(self):
        """from_dict with {race_id, count} only defaults happiness to 0.5."""
        pop = SpeciesPopulation.from_dict({"race_id": "human", "count": 5})

        assert pop.race_id == "human"
        assert pop.count == 5
        assert pop.happiness == 0.5

    def test_from_dict_with_explicit_happiness(self):
        """Explicit happiness in payload is preserved."""
        pop = SpeciesPopulation.from_dict(
            {"race_id": "human", "count": 5, "happiness": 0.9}
        )

        assert pop.happiness == 0.9


class TestFromDictMissingKeys:
    """Missing required keys raise PersistenceException via require_keys."""

    def test_missing_count_raises(self):
        with pytest.raises(PersistenceException):
            SpeciesPopulation.from_dict({"race_id": "human"})

    def test_missing_race_id_raises(self):
        with pytest.raises(PersistenceException):
            SpeciesPopulation.from_dict({"count": 5})

    def test_empty_dict_raises(self):
        with pytest.raises(PersistenceException):
            SpeciesPopulation.from_dict({})


class TestNoBoundsValidation:
    """Pins the no-validation behavior. PROJ-335 D-007 observation."""

    def test_negative_count_accepted_silently(self):
        """Construct accepts negative count — no validation."""
        pop = SpeciesPopulation(race_id="human", count=-100)
        assert pop.count == -100

    def test_happiness_above_one_accepted_silently(self):
        """happiness > 1.0 is accepted with no clamp or error."""
        pop = SpeciesPopulation(race_id="human", happiness=1.5)
        assert pop.happiness == 1.5

    def test_happiness_below_zero_accepted_silently(self):
        """happiness < 0.0 is accepted with no clamp or error."""
        pop = SpeciesPopulation(race_id="human", happiness=-0.25)
        assert pop.happiness == -0.25

    def test_from_dict_passes_through_out_of_range_happiness(self):
        """from_dict does not validate happiness range either."""
        pop = SpeciesPopulation.from_dict(
            {"race_id": "human", "count": 5, "happiness": 9.0}
        )
        assert pop.happiness == 9.0
