"""Characterization tests for game/strategy/data/planetary_facility.py.

PROJ-335 Phase 1. Pins the gap-fill behaviors not already covered by:

- ``test_facility_activation.py`` (component activation states)
- ``test_facility_construction_queue.py`` (queue mutation)
- ``test_facility_resource_tracking.py`` (fuel storage / withdraw / overflow)
- ``test_construction_queue_paused_persistence.py`` (paused flag round-trip)

Specifically pins:

- Required-key validation in ``from_dict``.
- The ``is_shipyard`` short-circuit to False when ``is_operational`` is False.
- The ``is_shipyard`` True path with an active space_shipyard component.
- ``set_component_active`` / ``is_component_active`` round-trip through the
  ComponentActivationState bridge.
- Top-level field round-trip via ``to_dict`` / ``from_dict``.

Mode: characterization-only. No bug fixes.
"""
from __future__ import annotations

import pytest

from game.core.exceptions import PersistenceException
from game.strategy.data.planetary_facility import PlanetaryFacility


def _minimal_facility(**overrides) -> PlanetaryFacility:
    """Build a minimal valid facility for round-trip tests."""
    kwargs = {
        "instance_id": "fac-1",
        "design_id": "test_complex",
        "name": "Test Complex",
        "design_data": {"layers": {"OUTER": []}},
    }
    kwargs.update(overrides)
    return PlanetaryFacility(**kwargs)


class TestFromDictRequiredKeys:
    """from_dict validates the 4-key contract via require_keys."""

    def test_empty_dict_raises_persistence_exception(self):
        with pytest.raises(PersistenceException):
            PlanetaryFacility.from_dict({})

    def test_missing_instance_id_raises(self):
        with pytest.raises(PersistenceException):
            PlanetaryFacility.from_dict({
                "design_id": "d",
                "name": "n",
                "design_data": {},
            })

    def test_missing_design_data_raises(self):
        with pytest.raises(PersistenceException):
            PlanetaryFacility.from_dict({
                "instance_id": "i",
                "design_id": "d",
                "name": "n",
            })

    # PROJ-353A Tier-7 (T2.7): coverage gap — only `instance_id` and
    # `design_data` missing-key paths were pinned previously. Add the
    # other two required keys plus an extra-key tolerance pin.

    def test_missing_design_id_raises(self):
        with pytest.raises(PersistenceException):
            PlanetaryFacility.from_dict({
                "instance_id": "i",
                "name": "n",
                "design_data": {},
            })

    def test_missing_name_raises(self):
        with pytest.raises(PersistenceException):
            PlanetaryFacility.from_dict({
                "instance_id": "i",
                "design_id": "d",
                "design_data": {},
            })

    def test_extra_keys_are_tolerated(self):
        """`from_dict` must ignore unknown top-level keys so adding new
        save-format fields in a future release doesn't break the loader
        when an older version reads a newer save."""
        facility = PlanetaryFacility.from_dict({
            "instance_id": "i",
            "design_id": "d",
            "name": "n",
            "design_data": {"layers": {}},
            "_unknown_future_key": "should-be-ignored",
            "another_extra": 42,
        })
        assert facility.instance_id == "i"
        assert facility.design_id == "d"


class TestRoundTripPreservesTopLevelFields:
    """to_dict -> from_dict preserves all top-level fields."""

    def test_round_trip_default_facility(self):
        facility = _minimal_facility(
            consumable_levels={"fuel": 12.5, "ore": 4.0},
            component_states={"OUTER:0:thing": {"phase": "active"}},
            is_operational=False,
            construction_queue=[{"id": "q1"}],
            construction_queue_paused=True,
        )

        data = facility.to_dict()
        restored = PlanetaryFacility.from_dict(data)

        assert restored.instance_id == "fac-1"
        assert restored.design_id == "test_complex"
        assert restored.name == "Test Complex"
        assert restored.design_data == {"layers": {"OUTER": []}}
        assert restored.is_operational is False
        assert restored.construction_queue == [{"id": "q1"}]
        assert restored.construction_queue_paused is True
        assert restored.consumable_levels == {"fuel": 12.5, "ore": 4.0}
        assert restored.component_states == {
            "OUTER:0:thing": {"phase": "active"},
        }


# PROJ-349 T6.1: TestLegacyResourceLevelsKey deleted. The
# `resource_levels` save-format alias was a save-migration shim that
# violated the repo rule "old saves are disposable" (CLAUDE.md). Both
# the alias and the tests pinning it have been removed; saves written
# under the legacy schema will no longer load (this is the documented
# behavior — saves are disposable across major refactors).


class TestIsShipyard:
    """Pins the is_shipyard predicate, including the operational
    short-circuit (D-007 observation)."""

    def _shipyard_design(self) -> dict:
        return {"layers": {"OUTER": [{"id": "space_shipyard"}]}}

    def test_returns_false_when_not_operational_even_with_shipyard_component(self):
        facility = _minimal_facility(
            design_data=self._shipyard_design(),
            is_operational=False,
        )
        assert facility.is_shipyard is False

    def test_returns_true_when_operational_and_shipyard_component_present(self):
        facility = _minimal_facility(
            design_data=self._shipyard_design(),
            is_operational=True,
        )
        assert facility.is_shipyard is True

    def test_returns_false_when_no_shipyard_component(self):
        facility = _minimal_facility(
            design_data={"layers": {"OUTER": [{"id": "habitat"}]}},
            is_operational=True,
        )
        assert facility.is_shipyard is False

    def test_recognizes_shipyard_via_abilities_dict(self):
        """Component without id 'space_shipyard' but with SpaceShipyard
        ability is also recognized."""
        facility = _minimal_facility(
            design_data={
                "layers": {
                    "OUTER": [
                        {"id": "custom_yard", "abilities": {"SpaceShipyard": {}}}
                    ]
                }
            },
            is_operational=True,
        )
        assert facility.is_shipyard is True


class TestComponentActiveLegacyBridge:
    """set_component_active / is_component_active round-trip via the
    ComponentActivationState bridge."""

    def test_set_then_read_active_true(self):
        facility = _minimal_facility()
        facility.set_component_active("OUTER:0:weapon", True)

        assert facility.is_component_active("OUTER:0:weapon") is True

    def test_set_then_read_active_false(self):
        facility = _minimal_facility()
        facility.set_component_active("OUTER:0:weapon", False)

        assert facility.is_component_active("OUTER:0:weapon") is False

    def test_unknown_key_reads_as_inactive(self):
        facility = _minimal_facility()
        assert facility.is_component_active("never_set") is False
