"""Unit tests for Empire domain methods.

PROJ-287 Phase 3: resident_species() — canonical set of race_ids with at
least one population unit anywhere across the empire's colonies.
"""
from types import SimpleNamespace

from game.strategy.data.empire import Empire
from game.strategy.data.species_population import SpeciesPopulation


def _make_colony(populations):
    """Minimal stand-in for a Planet — only needs `.populations`."""
    return SimpleNamespace(populations=list(populations))


def _make_empire(colonies=None):
    empire = Empire(empire_id=1, name="Testers", color=(255, 255, 255))
    empire.colonies = list(colonies or [])
    return empire


class TestEmpireResidentSpecies:
    """PROJ-287: Empire.resident_species() returns race_ids with count >= 1
    on ANY colony. User-confirmed threshold: a species counts as resident
    if ANY colony has at least one population unit of it."""

    def test_no_colonies_returns_empty_set(self):
        empire = _make_empire(colonies=[])

        assert empire.resident_species() == set()

    def test_colonies_with_no_populations_returns_empty_set(self):
        empire = _make_empire(colonies=[_make_colony([]), _make_colony([])])

        assert empire.resident_species() == set()

    def test_single_colony_single_species_included(self):
        empire = _make_empire(colonies=[
            _make_colony([SpeciesPopulation(race_id="human", count=1000)]),
        ])

        assert empire.resident_species() == {"human"}

    def test_multi_colony_multi_species_deduplicated(self):
        empire = _make_empire(colonies=[
            _make_colony([SpeciesPopulation(race_id="human", count=500)]),
            _make_colony([SpeciesPopulation(race_id="voidari", count=300)]),
            _make_colony([
                SpeciesPopulation(race_id="human", count=200),
                SpeciesPopulation(race_id="voidari", count=100),
            ]),
        ])

        assert empire.resident_species() == {"human", "voidari"}

    def test_species_with_count_zero_everywhere_excluded(self):
        empire = _make_empire(colonies=[
            _make_colony([SpeciesPopulation(race_id="extinct_one", count=0)]),
            _make_colony([SpeciesPopulation(race_id="extinct_one", count=0)]),
        ])

        assert empire.resident_species() == set()

    def test_species_present_on_any_colony_included(self):
        """A species with count=0 on colony A but count>=1 on colony B
        is INCLUDED (any colony meets the threshold)."""
        empire = _make_empire(colonies=[
            _make_colony([SpeciesPopulation(race_id="voidari", count=0)]),
            _make_colony([SpeciesPopulation(race_id="voidari", count=1)]),
        ])

        assert empire.resident_species() == {"voidari"}
