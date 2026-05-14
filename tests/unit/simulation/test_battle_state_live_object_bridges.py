"""Characterization tests for `battle_state.py` live-object bridge methods.

PROJ-331 Phase 1: pin behavior of `from_ship`/`to_ship`/`from_component`/
`from_projectile`/`to_projectile`/`capture_from_engine` and the
`BattleState`/`BattleResults` query methods.

Per master plan: tests describe what production CURRENTLY does. Real
Ship/Projectile/Component construction is heavy (registries + theme +
components), so all live-object bridges are exercised against `MagicMock`
instances. End-to-end fidelity is covered separately by
`tests/integration/save_load/test_roundtrip_ships.py` (D-003 in PROJ-331
decisions log).
"""
from __future__ import annotations

import re
import uuid
from unittest.mock import MagicMock, patch

import pytest

from game.core.constants import AttackType, LayerType
from game.core.exceptions import ValidationException
from game.simulation.battle_state import (
    BattleResults,
    BattleState,
    ComponentState,
    ProjectileState,
    ShipState,
)


UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# ComponentState.from_component
# ---------------------------------------------------------------------------


class TestComponentStateFromComponent:
    """Pin `ComponentState.from_component(component)`."""

    def test_from_component_extracts_id_hp_layer_and_serializes_modifiers(self):
        comp = MagicMock()
        comp.id = "laser_mk1"
        comp.current_hp = 8
        comp.max_hp = 10
        comp.is_active = True
        layer = MagicMock()
        layer.name = "OUTER"
        comp.layer_assigned = layer

        mod_a = MagicMock()
        mod_a.definition.id = "power_boost"
        mod_a.value = 2
        mod_b = MagicMock()
        mod_b.definition.id = "efficiency"
        mod_b.value = 1.5
        comp.modifiers = [mod_a, mod_b]

        state = ComponentState.from_component(comp)

        assert state.component_id == "laser_mk1"
        assert state.current_hp == 8
        assert state.max_hp == 10
        assert state.is_active is True
        assert state.layer == "OUTER"
        # Modifiers are dicts with `id` + `value`, not Modifier objects.
        assert state.modifiers == [
            {"id": "power_boost", "value": 2},
            {"id": "efficiency", "value": 1.5},
        ]


# ---------------------------------------------------------------------------
# ShipState.from_ship
# ---------------------------------------------------------------------------


def _make_mock_ship(*, current_target=None):
    """Build a MagicMock that satisfies `ShipState.from_ship` reads.

    Layers are empty (no components) so we don't need real components.
    """
    ship = MagicMock()
    ship.name = "Vagabond"
    ship.ship_class = "frigate"
    ship.theme_id = "default"
    ship.team_id = 0
    ship.color = (255, 100, 50)
    ship.movement_policy = "kite"
    ship.targeting_policy = "weakest"
    ship.x = 1234.5
    ship.y = -567.0
    velocity = MagicMock()
    velocity.x = 1.0
    velocity.y = -2.5
    ship.velocity = velocity
    ship.angle = 1.5708
    ship.hp = 80
    ship.max_hp = 100
    ship.current_shields = 30.0
    ship.max_shields = 50.0
    # No live components; layers iterates empty so capture skips.
    ship.layers = {}
    ship.resources = None
    ship.current_target = current_target
    ship.is_alive = True
    ship.is_derelict = False
    ship.retreat_status = None
    return ship


class TestShipStateFromShip:
    """Pin `ShipState.from_ship(ship, ship_id=None)`."""

    def test_from_ship_generates_uuid_when_ship_id_not_provided(self):
        ship = _make_mock_ship()
        state = ShipState.from_ship(ship, ship_id=None)
        assert UUID4_RE.match(state.ship_id), state.ship_id

    def test_from_ship_uses_provided_ship_id(self):
        ship = _make_mock_ship()
        state = ShipState.from_ship(ship, ship_id="my-id")
        assert state.ship_id == "my-id"

    def test_from_ship_resolves_current_target_to_target_name(self):
        target = MagicMock()
        target.name = "enemy-ship"
        ship = _make_mock_ship(current_target=target)
        state = ShipState.from_ship(ship)
        assert state.current_target_id == "enemy-ship"

    def test_from_ship_resolves_projectile_target_without_crashing(self):
        """A PDC ship can target a missile (Projectile), which has no .name.

        Regression: `from_ship` assumed `current_target` is always a Ship and
        did `current_target.name`, raising AttributeError on a Projectile.
        Projectiles expose `.id`, which is used as the target identifier.
        """
        # spec=[...] omits "name" so accessing it raises AttributeError,
        # exactly like a real Projectile.
        missile = MagicMock(spec=["id", "type", "is_alive", "team_id"])
        missile.id = "proj-42"
        ship = _make_mock_ship(current_target=missile)
        state = ShipState.from_ship(ship)
        assert state.current_target_id == "proj-42"


# ---------------------------------------------------------------------------
# ShipState.to_ship
# ---------------------------------------------------------------------------


def _basic_ship_state(**overrides) -> ShipState:
    base = dict(
        ship_id="state-ship",
        name="Vagabond",
        ship_class="frigate",
        theme_id="default",
        team_id=0,
        color=(255, 100, 50),
        movement_policy="kite",
        position=(0.0, 0.0),
        velocity=(0.0, 0.0),
        angle=0.0,
        current_hp=80,
        max_hp=100,
        current_shields=30.0,
        max_shields=50.0,
        components={},
        resource_levels={},
        resource_max={},
    )
    base.update(overrides)
    return ShipState(**base)


class TestShipStateToShip:
    """Pin `ShipState.to_ship(*, registries)`."""

    def test_to_ship_raises_validation_exception_when_registries_is_none(self):
        state = _basic_ship_state()
        with pytest.raises(ValidationException) as exc_info:
            state.to_ship(registries=None)
        # MISSING_DEPENDENCY = "C003"
        assert exc_info.value.code == "C003"

    def test_to_ship_skips_unknown_layer_with_warning(self, caplog):
        comp_state = ComponentState(
            component_id="laser_mk1",
            current_hp=8,
            max_hp=10,
            is_active=True,
            layer="OUTER",
            modifiers=[],
        )
        state = _basic_ship_state(
            components={"BOGUS": [comp_state]},
        )

        # Mock Ship constructor + registries so to_ship can run without
        # touching real Ship machinery.
        registries = MagicMock()
        registries.components = {}
        registries.modifiers = {}

        fake_ship = MagicMock()
        fake_ship.layers = {}
        fake_ship.resources = None

        with patch(
            "game.simulation.entities.ship.Ship", return_value=fake_ship
        ):
            with caplog.at_level("WARNING"):
                returned = state.to_ship(registries=registries)

        assert returned is fake_ship
        # Warning about unknown layer was emitted.
        assert any(
            "Unknown layer type" in rec.message and "BOGUS" in rec.message
            for rec in caplog.records
        )

    def test_to_ship_applies_modifiers_before_damage_state(self):
        """add_modifier triggers recalculate_stats which evaluates formulas
        against the ship's max_mass_budget — so the production code applies
        modifiers BEFORE setting current_hp / is_active. Pin this ordering.
        """
        comp_state = ComponentState(
            component_id="laser_mk1",
            current_hp=5,
            max_hp=10,
            is_active=True,
            layer="OUTER",
            modifiers=[{"id": "power_boost", "value": 2}],
        )
        state = _basic_ship_state(components={"OUTER": [comp_state]})

        # Build a mock component the registry returns from .clone().
        new_comp = MagicMock()
        sequence: list[str] = []
        new_comp.add_modifier = MagicMock(
            side_effect=lambda *a, **k: sequence.append("add_modifier")
        )

        # Track when current_hp gets set on the component.
        type(new_comp).current_hp = property(
            lambda self: 0,
            lambda self, value: sequence.append("current_hp"),
        )

        registry_entry = MagicMock()
        registry_entry.clone.return_value = new_comp
        registries = MagicMock()
        registries.components = {"laser_mk1": registry_entry}
        registries.modifiers = {"power_boost": MagicMock()}

        fake_ship = MagicMock()
        # Ensure the OUTER layer key is present so the populate path runs.
        fake_ship.layers = {LayerType.OUTER: MagicMock()}
        fake_ship.resources = None

        with patch(
            "game.simulation.entities.ship.Ship", return_value=fake_ship
        ):
            state.to_ship(registries=registries)

        assert "add_modifier" in sequence
        assert "current_hp" in sequence
        assert sequence.index("add_modifier") < sequence.index("current_hp")


# ---------------------------------------------------------------------------
# ProjectileState.from_projectile
# ---------------------------------------------------------------------------


def _make_mock_projectile(*, owner_id="ship_a", target_id="ship_b",
                          proj_type=AttackType.MISSILE):
    proj = MagicMock()
    owner = MagicMock()
    owner.id = owner_id
    proj.owner = owner
    target = MagicMock()
    target.id = target_id
    proj.target = target
    proj.team_id = 0
    pos = MagicMock(); pos.x = 10.0; pos.y = 20.0
    proj.position = pos
    vel = MagicMock(); vel.x = 1.0; vel.y = 2.0
    proj.velocity = vel
    proj.damage = 5.0
    proj.max_range = 1000.0
    proj.endurance = 50.0
    proj.max_endurance = 50.0
    proj.type = proj_type
    proj.turn_rate = 0.5
    proj.max_speed = 500.0
    proj.hp = 1
    proj.max_hp = 1
    proj.distance_traveled = 25.0
    proj.is_alive = True
    return proj


class TestProjectileStateFromProjectile:
    """Pin `ProjectileState.from_projectile(proj, ship_id_map)`."""

    def test_from_projectile_resolves_owner_and_target_via_ship_id_map(self):
        proj = _make_mock_projectile(owner_id="engine_owner",
                                     target_id="engine_target")
        ship_id_map = {
            "engine_owner": "battle_owner_id",
            "engine_target": "battle_target_id",
        }
        state = ProjectileState.from_projectile(proj, ship_id_map)
        assert state.owner_ship_id == "battle_owner_id"
        assert state.target_ship_id == "battle_target_id"

    def test_from_projectile_extracts_enum_type_value(self):
        proj = _make_mock_projectile(proj_type=AttackType.MISSILE)
        state = ProjectileState.from_projectile(proj, {})
        # Should be the Enum's .value (a str), not its repr.
        assert state.projectile_type == AttackType.MISSILE.value
        assert "AttackType" not in state.projectile_type


# ---------------------------------------------------------------------------
# ProjectileState.to_projectile
# ---------------------------------------------------------------------------


class TestProjectileStateToProjectile:
    """Pin `ProjectileState.to_projectile(ship_lookup)`."""

    def test_to_projectile_resolves_owner_and_target_via_ship_lookup(self):
        owner_ship = MagicMock(name="owner_ship")
        target_ship = MagicMock(name="target_ship")
        state = ProjectileState(
            projectile_id="proj-1",
            owner_ship_id="ship_a",
            team_id=0,
            position=(0.0, 0.0),
            velocity=(1.0, 0.0),
            damage=5.0,
            max_range=1000.0,
            endurance=50.0,
            max_endurance=50.0,
            projectile_type="missile",
            turn_rate=0.5,
            max_speed=500.0,
            target_ship_id="ship_missing",
            hp=1,
            max_hp=1,
        )
        ship_lookup = {"ship_a": owner_ship}  # target_id NOT in lookup

        fake_proj = MagicMock()
        with patch(
            "game.simulation.entities.projectile.Projectile",
            return_value=fake_proj,
        ) as MockProj:
            result = state.to_projectile(ship_lookup)

        assert result is fake_proj
        # Inspect kwargs the constructor was called with.
        kwargs = MockProj.call_args.kwargs
        assert kwargs["owner"] is owner_ship
        # Missing target id -> looked up to None (lookup.get default).
        assert kwargs["target"] is None


# ---------------------------------------------------------------------------
# BattleState.capture_from_engine
# ---------------------------------------------------------------------------


def _engine_ship_mock(*, ship_id):
    s = MagicMock()
    s.id = ship_id
    s.name = "ship"
    s.ship_class = "frigate"
    s.theme_id = "default"
    s.team_id = 0
    s.color = (1, 2, 3)
    s.movement_policy = "kite"
    s.targeting_policy = "standard"
    s.x = 0.0; s.y = 0.0
    velocity = MagicMock(); velocity.x = 0.0; velocity.y = 0.0
    s.velocity = velocity
    s.angle = 0.0
    s.hp = 1; s.max_hp = 1
    s.current_shields = 0.0; s.max_shields = 0.0
    s.layers = {}
    s.resources = None
    s.current_target = None
    s.is_alive = True
    s.is_derelict = False
    s.retreat_status = None
    return s


class TestBattleStateCaptureFromEngine:
    """Pin `BattleState.capture_from_engine(engine, ...)`."""

    def test_capture_from_engine_generates_battle_id_when_not_provided(self):
        engine = MagicMock()
        engine.ships = []
        engine.projectiles = []
        engine.tick_counter = 0
        engine.end_condition = None
        state = BattleState.capture_from_engine(engine, battle_id=None)
        assert UUID4_RE.match(state.battle_id), state.battle_id

    def test_capture_from_engine_reuses_existing_ship_id_map_entries(self):
        engine = MagicMock()
        engine.ships = [_engine_ship_mock(ship_id="engine_id")]
        engine.projectiles = []
        engine.tick_counter = 0
        engine.end_condition = None
        ship_id_map = {"engine_id": "preserved_id"}
        state = BattleState.capture_from_engine(
            engine, ship_id_map=ship_id_map,
        )
        assert "preserved_id" in state.ships
        assert "engine_id" not in state.ships

    def test_capture_from_engine_serializes_only_alive_projectiles(self):
        # Create three projectile mocks: 2 alive, 1 dead.
        alive_a = _make_mock_projectile(owner_id="ship_a", target_id="ship_b")
        alive_a.is_alive = True
        alive_b = _make_mock_projectile(owner_id="ship_a", target_id="ship_b")
        alive_b.is_alive = True
        dead = _make_mock_projectile(owner_id="ship_a", target_id="ship_b")
        dead.is_alive = False

        engine = MagicMock()
        engine.ships = []
        engine.projectiles = [alive_a, alive_b, dead]
        engine.tick_counter = 0
        engine.end_condition = None

        state = BattleState.capture_from_engine(engine)
        assert len(state.projectiles) == 2


# ---------------------------------------------------------------------------
# BattleState query methods
# ---------------------------------------------------------------------------


def _ship_state(ship_id, *, team_id=0, is_alive=True, retreat_status=None):
    return _basic_ship_state(
        ship_id=ship_id,
        team_id=team_id,
        is_alive=is_alive,
        retreat_status=retreat_status,
    )


class TestBattleStateQueries:
    """Pin BattleState query methods."""

    def test_get_ships_by_team_returns_only_matching_team_id(self):
        s_team0 = _ship_state("a", team_id=0)
        s_team1 = _ship_state("b", team_id=1)
        s_team0_b = _ship_state("c", team_id=0)
        bs = BattleState(ships={"a": s_team0, "b": s_team1, "c": s_team0_b})
        result = bs.get_ships_by_team(0)
        assert s_team0 in result and s_team0_b in result
        assert s_team1 not in result

    def test_get_surviving_ships_excludes_escaped_and_dead(self):
        alive_not_escaped = _ship_state("a", is_alive=True, retreat_status=None)
        alive_escaped = _ship_state("b", is_alive=True, retreat_status="escaped")
        dead_not_escaped = _ship_state("c", is_alive=False, retreat_status=None)
        dead_escaped = _ship_state("d", is_alive=False, retreat_status="escaped")
        bs = BattleState(ships={
            "a": alive_not_escaped, "b": alive_escaped,
            "c": dead_not_escaped, "d": dead_escaped,
        })
        result = bs.get_surviving_ships()
        assert result == [alive_not_escaped]

    def test_get_escaped_ships_returns_only_retreat_status_escaped(self):
        a = _ship_state("a", retreat_status=None)
        b = _ship_state("b", retreat_status="retreating")
        c = _ship_state("c", retreat_status="escaped")
        d = _ship_state("d", retreat_status="escaped")
        bs = BattleState(ships={"a": a, "b": b, "c": c, "d": d})
        result = bs.get_escaped_ships()
        assert c in result and d in result
        assert a not in result and b not in result

    def test_get_destroyed_ships_excludes_escaped_dead_ships(self):
        dead_not_escaped = _ship_state("a", is_alive=False, retreat_status=None)
        dead_escaped = _ship_state("b", is_alive=False, retreat_status="escaped")
        bs = BattleState(ships={"a": dead_not_escaped, "b": dead_escaped})
        result = bs.get_destroyed_ships()
        assert result == [dead_not_escaped]


# ---------------------------------------------------------------------------
# BattleResults query methods
# ---------------------------------------------------------------------------


class TestBattleResultsQueries:
    """Pin BattleResults query methods."""

    def test_get_team_survivors_filters_surviving_ships_by_team_id(self):
        s0 = _ship_state("a", team_id=0)
        s1 = _ship_state("b", team_id=1)
        s0_b = _ship_state("c", team_id=0)
        results = BattleResults(
            winner=0, tick_count=10, seed=None,
            surviving_ships=[s0, s1, s0_b],
        )
        team0 = results.get_team_survivors(0)
        assert s0 in team0 and s0_b in team0
        assert s1 not in team0

    def test_get_team_losses_filters_destroyed_ships_by_team_id(self):
        s0 = _ship_state("a", team_id=0, is_alive=False)
        s1 = _ship_state("b", team_id=1, is_alive=False)
        results = BattleResults(
            winner=0, tick_count=10, seed=None,
            destroyed_ships=[s0, s1],
        )
        assert results.get_team_losses(1) == [s1]
