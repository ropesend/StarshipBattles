"""PROJ-436 Phase 5 integration: ``Empire.resource_pool`` pure-query
aggregation across colonies.

Pins the new post-Phase-5 contract end-to-end:

* ``Empire.resource_pool`` walks ``self.colonies[*].stockpile`` only and
  sums by ``resource_id``. The legacy ``_fleet_resource_pool`` summand
  is gone; fleet ship cargo is NOT folded into the aggregate (fleet
  construction reads ``Fleet.has_cargo_resources`` /
  ``Fleet.get_cargo_resource`` directly — see
  ``game/strategy/engine/production_engine.py``).
* The aggregate reflects per-colony stockpile mutation through the
  Planet helpers (``add_to_stockpile`` / ``consume_from_stockpile``).
* ``Empire.has_resources`` / ``Empire.get_resource`` route through the
  same aggregate.
* The empire's save shape no longer carries a top-level
  ``resource_pool`` key; round-tripping through ``to_dict`` /
  ``from_dict`` does NOT resurrect the deleted ``_fleet_resource_pool``.

This is the missing integration test the project plan
(``Projects/active_projects/PROJ-436/manifest.md`` line 116)
called out for Phase 5 — landed as the 5g verified-finding
remediation after Codex's post-cutover consult flagged its
absence (decisions.md 2026-05-18, finding 3).
"""
from __future__ import annotations

import pytest

from game.strategy.data.empire import Empire
from tests.fixtures.strategy_entities import create_test_planet


def _empire() -> Empire:
    return Empire(empire_id=1, name="Aggregation Test", color=(0, 0, 0))


def _colony(stockpile: dict, *, name: str = "Colony") -> object:
    return create_test_planet(
        has_facilities=False,
        has_population=False,
        name=name,
        _stockpile=dict(stockpile),
    )


class TestEmpireResourcePoolAggregation:
    """``Empire.resource_pool`` walks colony stockpiles end-to-end."""

    def test_empty_empire_has_empty_pool(self):
        e = _empire()
        assert e.resource_pool == {}

    def test_single_colony_aggregate(self):
        e = _empire()
        e.colonies.append(_colony({"metals": 100.0, "fuel": 25.0}))
        assert e.resource_pool == {"metals": 100.0, "fuel": 25.0}

    def test_multi_colony_aggregate_sums_by_resource_id(self):
        e = _empire()
        e.colonies.append(_colony({"metals": 100.0, "organics": 50.0}))
        e.colonies.append(_colony({"metals": 200.0, "fuel": 30.0},
                                  name="Colony2"))
        e.colonies.append(_colony({"organics": 25.0, "fuel": 15.0},
                                  name="Colony3"))

        pool = e.resource_pool
        assert pool["metals"] == pytest.approx(300.0)
        assert pool["organics"] == pytest.approx(75.0)
        assert pool["fuel"] == pytest.approx(45.0)

    def test_aggregate_reflects_stockpile_mutation(self):
        e = _empire()
        colony = _colony({"metals": 100.0})
        e.colonies.append(colony)

        assert e.resource_pool["metals"] == 100.0

        colony.add_to_stockpile("metals", 50.0)
        assert e.resource_pool["metals"] == pytest.approx(150.0)

        colony.consume_from_stockpile("metals", 75.0)
        assert e.resource_pool["metals"] == pytest.approx(75.0)

    def test_aggregate_reflects_adding_a_new_colony(self):
        e = _empire()
        e.colonies.append(_colony({"metals": 100.0}))
        assert e.resource_pool["metals"] == 100.0

        e.colonies.append(_colony({"metals": 300.0, "ammo": 10.0},
                                  name="NewColony"))
        pool = e.resource_pool
        assert pool["metals"] == pytest.approx(400.0)
        assert pool["ammo"] == pytest.approx(10.0)

    def test_aggregate_reflects_removing_a_colony(self):
        e = _empire()
        c1 = _colony({"metals": 100.0})
        c2 = _colony({"metals": 250.0, "fuel": 50.0}, name="Colony2")
        e.colonies.extend([c1, c2])

        assert e.resource_pool["metals"] == pytest.approx(350.0)

        e.colonies.remove(c2)
        pool = e.resource_pool
        assert pool["metals"] == pytest.approx(100.0)
        assert "fuel" not in pool

    def test_returned_dict_is_a_snapshot(self):
        """Mutating the returned dict does not affect the empire."""
        e = _empire()
        e.colonies.append(_colony({"metals": 100.0}))

        snap = e.resource_pool
        snap["metals"] = 999.0
        snap["organics"] = 50.0

        # Underlying colony stockpile unchanged.
        assert e.colonies[0].stockpile["metals"] == 100.0
        # Next read returns a fresh aggregate.
        fresh = e.resource_pool
        assert fresh == {"metals": 100.0}


class TestEmpireResourceQueryHelpers:
    """``has_resources`` / ``get_resource`` route through ``resource_pool``."""

    def test_get_resource_reads_aggregate(self):
        e = _empire()
        e.colonies.append(_colony({"metals": 50.0}))
        e.colonies.append(_colony({"metals": 75.0}, name="Colony2"))
        assert e.get_resource("metals") == pytest.approx(125.0)
        assert e.get_resource("missing") == 0.0

    def test_has_resources_succeeds_when_aggregate_covers_costs(self):
        e = _empire()
        e.colonies.append(_colony({"metals": 100.0, "organics": 80.0}))
        assert e.has_resources({"metals": 50.0, "organics": 50.0}) is True

    def test_has_resources_fails_on_any_shortfall(self):
        e = _empire()
        e.colonies.append(_colony({"metals": 100.0, "organics": 5.0}))
        assert e.has_resources({"metals": 50.0, "organics": 10.0}) is False

    def test_has_resources_empty_costs_is_true(self):
        e = _empire()
        assert e.has_resources({}) is True


class TestEmpireResourceSaveShape:
    """PROJ-436 Phase 5: save shape no longer carries empire-level pool."""

    def test_to_dict_omits_legacy_resource_pool_key(self):
        e = _empire()
        e.max_storage = {"metals": 1000.0}
        # Even with a colony seeded, the empire-level save does not
        # carry an aggregated ``resource_pool`` — that lives on each
        # Planet's serializer.
        e.colonies.append(_colony({"metals": 250.0}))
        data = e.to_dict()
        assert "resource_pool" not in data
        assert data["max_storage"] == {"metals": 1000.0}

    def test_from_dict_ignores_legacy_resource_pool_key(self):
        """Pre-Phase-5 saves carrying ``resource_pool`` are loaded with the
        legacy key silently dropped (CLAUDE.md "no save-file migration").
        """
        legacy = {
            "id": 1,
            "name": "Legacy",
            "color": [0, 0, 0],
            # Pre-Phase-5 top-level pool — must be ignored.
            "resource_pool": {"metals": 9999.0},
            "max_storage": {"metals": 5000.0},
        }
        restored = Empire.from_dict(legacy)
        # No fleet-side pool resurrected.
        assert "_fleet_resource_pool" not in vars(restored)
        # No colonies were resolved (galaxy=None), so aggregate is empty.
        assert restored.resource_pool == {}
        # max_storage still round-trips.
        assert restored.max_storage == {"metals": 5000.0}

    def test_round_trip_max_storage_with_no_colonies(self):
        e = _empire()
        e.max_storage = {"fuel": 2000.0, "ammo": 500.0}
        restored = Empire.from_dict(e.to_dict())
        assert restored.max_storage == {"fuel": 2000.0, "ammo": 500.0}
        assert restored.resource_pool == {}
