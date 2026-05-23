"""Characterization tests for EnvironmentalHazardEngine (PROJ-341 §1).

Green-field coverage of `game/strategy/engine/environmental_hazard_engine.py`.
Pins observable current behavior — no production refactors. Apparent bugs
are recorded as observations OBS-001..OBS-003 in PROJ-341/decisions.md and
locked in as current behavior so any future "fix" trips a red test here.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.exceptions import ValidationException
from game.core.hex_math import HexCoord
from game.strategy.engine.environmental_hazard_engine import (
    EnvironmentalHazardEngine,
    EnvironmentalEvent,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_ship(
    *,
    max_hp: int = 100,
    current_hp=None,
    fuel: float = 100.0,
    is_alive: bool = True,
):
    """Build a duck-typed ship that satisfies the engine's surface."""
    ship = MagicMock()
    ship.current_hp = current_hp
    ship.is_alive = is_alive
    ship.get_calculated_stats.return_value = {"max_hp": max_hp}
    ship.get_current_resource.return_value = fuel
    # consume_resource is a normal MagicMock — assertable via call_args_list.
    return ship


_UNSET = object()


def _make_hazard_fleet(
    *,
    fleet_id: int = 1,
    location=_UNSET,
    combat_ships=None,
):
    """Build a duck-typed fleet at a HexCoord location with combat ships.

    Pass ``location=None`` to deliberately omit the location (used by the
    `_validate_tick_inputs` raise tests). Omit the kwarg to default to (0,0).
    """
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.location = HexCoord(0, 0) if location is _UNSET else location
    fleet.get_combat_capable_ships.return_value = list(combat_ships or [])
    return fleet


# PROJ-479 Task 5.4 (DUP-005): _make_empire moved to engine/conftest.py
# Local wrapper preserves the empire_id=0 default + fleets-only positional API.
from .conftest import make_mock_empire as _make_mock_empire_canonical  # noqa: E402


def _make_empire(empire_id: int = 0, fleets=None):
    return _make_mock_empire_canonical(empire_id=empire_id, fleets=list(fleets or []))


def _make_galaxy(*, system=None, has_get_system_at_location: bool = True):
    """Build a galaxy where get_system_at_location returns ``system``.

    If ``has_get_system_at_location`` is False, the attribute is removed so
    the engine's `getattr(..., None)` lookup yields None.
    """
    galaxy = MagicMock(spec=["get_system_at_location"]) if has_get_system_at_location else MagicMock(spec=[])
    if has_get_system_at_location:
        galaxy.get_system_at_location = MagicMock(return_value=system)
    return galaxy


def _damage_effect(value: float, *, source_label=None, providers=None):
    """Build an EnvironmentalDamage effect dict with optional providers."""
    if providers is None:
        providers = []
        if source_label is not None:
            providers.append({"source_label": source_label})
    return {
        "ability_name": "EnvironmentalDamage",
        "aggregate_value": value,
        "providers": providers,
    }


def _fuel_effect(value: float, *, source_label=None, providers=None):
    if providers is None:
        providers = []
        if source_label is not None:
            providers.append({"source_label": source_label})
    return {
        "ability_name": "FuelDrain",
        "aggregate_value": value,
        "providers": providers,
    }


COLLECT_PATH = (
    "game.strategy.services.system_effects_collector.collect_sector_effects"
)


# ---------------------------------------------------------------------------
# 1.1 process_environmental_tick — happy path
# ---------------------------------------------------------------------------


class TestProcessEnvironmentalTickHappyPath:
    """Happy-path damage / fuel / aggregation / distribution behaviors."""

    def test_process_environmental_tick_returns_event_when_storm_deals_damage(self):
        """One fleet, one ship, one damage row → one EnvironmentalEvent."""
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        with patch(COLLECT_PATH, return_value=[_damage_effect(100.0)]):
            events = engine.process_environmental_tick(5, [empire], galaxy)

        assert len(events) == 1
        evt = events[0]
        assert isinstance(evt, EnvironmentalEvent)
        assert evt.fleet_id == fleet.id
        assert evt.tick == 5
        assert evt.damage_dealt == pytest.approx(1.0)
        assert evt.fuel_drained == 0.0

    def test_process_environmental_tick_returns_event_when_storm_drains_fuel(self):
        """Single FuelDrain row of 200/turn → 2.0 fuel drained per tick."""
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(fuel=100.0)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        with patch(COLLECT_PATH, return_value=[_fuel_effect(200.0)]):
            events = engine.process_environmental_tick(7, [empire], galaxy)

        assert len(events) == 1
        assert events[0].fuel_drained == pytest.approx(2.0)
        ship.consume_resource.assert_called_once_with("fuel", 2.0)

    def test_process_environmental_tick_aggregates_damage_across_multiple_sources(self):
        """Two damage rows (50 + 30) → total per-tick damage 0.8."""
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        with patch(COLLECT_PATH, return_value=[_damage_effect(50.0), _damage_effect(30.0)]):
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert len(events) == 1
        assert events[0].damage_dealt == pytest.approx(0.8)

    def test_process_environmental_tick_distributes_damage_evenly_across_combat_ships(self):
        """damage_per_turn=300 across 3 ships → 1.0 damage per ship per tick."""
        engine = EnvironmentalHazardEngine()
        ships = [_make_ship(current_hp=100, max_hp=100) for _ in range(3)]
        fleet = _make_hazard_fleet(combat_ships=ships)
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        with patch(COLLECT_PATH, return_value=[_damage_effect(300.0)]):
            events = engine.process_environmental_tick(1, [empire], galaxy)

        # Total damage == sum of per-ship damage; per-ship == 300/100/3 == 1.0
        assert len(events) == 1
        assert events[0].damage_dealt == pytest.approx(3.0)  # 1.0 per ship, 3 ships
        for ship in ships:
            # Each ship moved from 100 to 99 — i.e. took 1.0 damage.
            assert ship.current_hp == pytest.approx(99.0)

    def test_process_environmental_tick_drains_fuel_per_ship_without_dividing(self):
        """OBS-003: fuel drain is per-ship (not divided across the fleet)."""
        engine = EnvironmentalHazardEngine()
        ships = [_make_ship(fuel=100.0) for _ in range(3)]
        fleet = _make_hazard_fleet(combat_ships=ships)
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        with patch(COLLECT_PATH, return_value=[_fuel_effect(300.0)]):
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert len(events) == 1
        # Per-ship drain is 300/100 == 3.0. Three ships → 9.0 total.
        assert events[0].fuel_drained == pytest.approx(9.0)
        for ship in ships:
            ship.consume_resource.assert_called_once_with("fuel", 3.0)


# ---------------------------------------------------------------------------
# 1.2 process_environmental_tick — source label resolution
# ---------------------------------------------------------------------------


class TestProcessEnvironmentalTickSourceLabel:
    """source_label fallback / first-provider semantics."""

    def test_process_environmental_tick_uses_first_provider_source_label(self):
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        effect = _damage_effect(100.0, source_label="Ion Storm Alpha")
        with patch(COLLECT_PATH, return_value=[effect]):
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert len(events) == 1
        assert events[0].storm_name == "Ion Storm Alpha"

    def test_process_environmental_tick_falls_back_to_unknown_hazard_when_no_label(self):
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        # Provider entry exists but has no source_label key.
        effect = _damage_effect(100.0, providers=[{"some_other_key": "x"}])
        with patch(COLLECT_PATH, return_value=[effect]):
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert len(events) == 1
        assert events[0].storm_name == "Unknown Hazard"


# ---------------------------------------------------------------------------
# 1.3 process_environmental_tick — skip / continue paths
# ---------------------------------------------------------------------------


class TestProcessEnvironmentalTickSkipPaths:
    """Branches that produce no event."""

    def test_process_environmental_tick_returns_no_event_when_galaxy_has_no_get_system_at_location(self):
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(has_get_system_at_location=False)

        with patch(COLLECT_PATH, return_value=[_damage_effect(100.0)]) as mock_collect:
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert events == []
        mock_collect.assert_not_called()

    def test_process_environmental_tick_returns_no_event_when_fleet_not_in_a_system(self):
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=None)  # get_system_at_location returns None

        with patch(COLLECT_PATH, return_value=[_damage_effect(100.0)]) as mock_collect:
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert events == []
        mock_collect.assert_not_called()

    def test_process_environmental_tick_returns_no_event_when_no_effects_at_hex(self):
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        with patch(COLLECT_PATH, return_value=[]):
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert events == []

    def test_process_environmental_tick_returns_no_event_when_aggregate_values_are_zero(self):
        """OBS-002: a single negative-damage row passes the empty-list filter
        but is dropped by `damage_per_turn <= 0 and fuel_per_turn <= 0` so no
        healing or other side-effect happens."""
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=80, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        with patch(COLLECT_PATH, return_value=[_damage_effect(-50.0)]):
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert events == []
        # Ship HP was not modified.
        assert ship.current_hp == 80
        ship.consume_resource.assert_not_called()

    def test_process_environmental_tick_returns_no_event_when_fleet_has_no_combat_ships(self):
        engine = EnvironmentalHazardEngine()
        fleet = _make_hazard_fleet(combat_ships=[])
        empire = _make_empire(fleets=[fleet])
        galaxy = _make_galaxy(system=MagicMock())

        with patch(COLLECT_PATH, return_value=[_damage_effect(100.0)]):
            events = engine.process_environmental_tick(1, [empire], galaxy)

        assert events == []


# ---------------------------------------------------------------------------
# 1.4 _validate_tick_inputs
# ---------------------------------------------------------------------------


class TestValidateTickInputs:
    """PROJ-251 precondition guard."""

    def test_validate_tick_inputs_raises_validation_exception_when_fleet_location_is_none(self):
        engine = EnvironmentalHazardEngine()
        fleet = _make_hazard_fleet(location=None)
        empire = _make_empire(empire_id=42, fleets=[fleet])

        with pytest.raises(ValidationException) as exc_info:
            engine.process_environmental_tick(1, [empire], _make_galaxy(system=MagicMock()))

        ctx = exc_info.value.context
        assert ctx.get("empire_id") == 42
        assert ctx.get("fleet_id") == fleet.id

    def test_validate_tick_inputs_does_not_raise_for_valid_fleets(self):
        """Valid fleets return without raising; private helper returns None."""
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)
        fleet = _make_hazard_fleet(combat_ships=[ship])
        empire = _make_empire(fleets=[fleet])

        # Direct call: should not raise.
        assert engine._validate_tick_inputs([empire]) is None


# ---------------------------------------------------------------------------
# 1.5 _apply_damage_to_ship
# ---------------------------------------------------------------------------


class TestApplyDamageToShip:
    """Direct unit pins of the hull-damage helper."""

    def test_apply_damage_to_ship_reduces_current_hp_by_damage_amount(self):
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=100, max_hp=100)

        actual = engine._apply_damage_to_ship(ship, 25.0)

        assert actual == pytest.approx(25.0)
        assert ship.current_hp == pytest.approx(75.0)
        assert ship.is_alive is True

    def test_apply_damage_to_ship_marks_ship_dead_when_hp_reaches_zero(self):
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(current_hp=10, max_hp=100)

        actual = engine._apply_damage_to_ship(ship, 50.0)

        # Damage clamped to current HP — ship took 10, not 50.
        assert actual == pytest.approx(10.0)
        assert ship.current_hp == pytest.approx(0.0)
        assert ship.is_alive is False

    def test_apply_damage_to_ship_resets_current_hp_to_none_when_damage_is_zero_at_full_hp(self):
        """OBS-001 (PROJ-341 decisions.md): pin the dead `else` branch at
        line 195. With damage=0 and current_hp == max_hp, the helper falls
        into the "Reset to full" branch and overwrites current_hp with None.

        ANNOTATION (PROJ-353A Tier-7 T2.4): this branch is unreachable
        through the production caller because `_apply_damage_to_ship` is
        only invoked with `damage > 0` (see
        `environmental_hazard_engine.py:141`, where damage is computed
        from a positive `damage_per_ship`). The test exists as a
        characterization pin so a future cleanup that removes the dead
        branch surfaces here as an intentional change rather than as a
        silent regression. If you arrive here debugging a "test broke"
        signal, see `Projects/active_projects/PROJ-341/decisions.md`
        under OBS-001 — the right move is usually to delete this test
        and the dead `else` branch together.
        """
        engine = EnvironmentalHazardEngine()
        # current_hp=None means "full HP" per the engine's own coalesce
        # at line 185. Combined with damage=0, new_hp == max_hp, so the
        # `else` branch fires and re-assigns ship.current_hp = None.
        ship = _make_ship(current_hp=None, max_hp=100)

        actual = engine._apply_damage_to_ship(ship, 0.0)

        assert actual == 0.0
        assert ship.current_hp is None
        # is_alive untouched in the new_hp <= 0 branch (new_hp == 100, not 0).
        assert ship.is_alive is True


# ---------------------------------------------------------------------------
# 1.6 _drain_fuel_from_ship
# ---------------------------------------------------------------------------


class TestDrainFuelFromShip:
    """Direct unit pin of the fuel-drain helper."""

    def test_drain_fuel_from_ship_caps_at_current_fuel(self):
        engine = EnvironmentalHazardEngine()
        ship = _make_ship(fuel=5.0)

        drained = engine._drain_fuel_from_ship(ship, 20.0)

        assert drained == pytest.approx(5.0)
        ship.consume_resource.assert_called_once_with("fuel", 5.0)
