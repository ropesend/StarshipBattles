"""
Tests for BattleState serialization round-trip (PROJ-118 Phase 2, Task 2.13).

Tests the serialization and deserialization of:
- ComponentState: to_dict() and from_dict()
- ShipState: to_dict() and from_dict()
- ProjectileState: to_dict() and from_dict()
- BattleState: to_dict(), from_dict(), to_json(), from_json()
- BattleResults: to_dict() and from_dict()

Focus on:
- Round-trip correctness (serialize -> deserialize -> compare)
- Edge cases (empty state, partial data, optional fields)
- All fields preserved correctly
"""
import pytest
import json
from typing import Dict, Any

from game.simulation.battle_state import (
    ComponentState,
    ShipState,
    ProjectileState,
    BattleState,
    BattleResults,
)


# =============================================================================
# ComponentState Tests
# =============================================================================

class TestComponentStateSerialization:
    """Tests for ComponentState to_dict() and from_dict()."""

    @pytest.fixture
    def basic_component_state(self) -> ComponentState:
        """Create a basic ComponentState for testing."""
        return ComponentState(
            component_id="laser_mk1",
            current_hp=8,
            max_hp=10,
            is_active=True,
            layer="OUTER",
            modifiers=[],
        )

    @pytest.fixture
    def component_state_with_modifiers(self) -> ComponentState:
        """Create a ComponentState with modifiers."""
        return ComponentState(
            component_id="shield_generator",
            current_hp=15,
            max_hp=20,
            is_active=True,
            layer="INNER",
            modifiers=[
                {"id": "power_boost", "value": 2},
                {"id": "efficiency", "value": 1.5},
            ],
        )

    @pytest.fixture
    def damaged_inactive_component(self) -> ComponentState:
        """Create a damaged and inactive ComponentState."""
        return ComponentState(
            component_id="engine_core",
            current_hp=0,
            max_hp=25,
            is_active=False,
            layer="CORE",
            modifiers=[],
        )

    def test_to_dict_contains_all_fields(self, basic_component_state):
        """to_dict() should include all ComponentState fields."""
        result = basic_component_state.to_dict()

        assert "component_id" in result
        assert "current_hp" in result
        assert "max_hp" in result
        assert "is_active" in result
        assert "layer" in result
        assert "modifiers" in result

    def test_to_dict_values_match(self, basic_component_state):
        """to_dict() values should match the original state."""
        result = basic_component_state.to_dict()

        assert result["component_id"] == "laser_mk1"
        assert result["current_hp"] == 8
        assert result["max_hp"] == 10
        assert result["is_active"] is True
        assert result["layer"] == "OUTER"
        assert result["modifiers"] == []

    def test_round_trip_basic(self, basic_component_state):
        """Serialize and deserialize should produce equivalent state."""
        data = basic_component_state.to_dict()
        restored = ComponentState.from_dict(data)

        assert restored.component_id == basic_component_state.component_id
        assert restored.current_hp == basic_component_state.current_hp
        assert restored.max_hp == basic_component_state.max_hp
        assert restored.is_active == basic_component_state.is_active
        assert restored.layer == basic_component_state.layer
        assert restored.modifiers == basic_component_state.modifiers

    def test_round_trip_with_modifiers(self, component_state_with_modifiers):
        """Modifiers should be preserved through round-trip."""
        data = component_state_with_modifiers.to_dict()
        restored = ComponentState.from_dict(data)

        assert len(restored.modifiers) == 2
        assert restored.modifiers[0] == {"id": "power_boost", "value": 2}
        assert restored.modifiers[1] == {"id": "efficiency", "value": 1.5}

    def test_round_trip_damaged_inactive(self, damaged_inactive_component):
        """Damaged and inactive components should be preserved."""
        data = damaged_inactive_component.to_dict()
        restored = ComponentState.from_dict(data)

        assert restored.current_hp == 0
        assert restored.is_active is False

    def test_from_dict_missing_modifiers_defaults_to_empty(self):
        """from_dict() should default modifiers to empty list if missing."""
        data = {
            "component_id": "test_comp",
            "current_hp": 10,
            "max_hp": 10,
            "is_active": True,
            "layer": "OUTER",
            # modifiers intentionally omitted
        }
        restored = ComponentState.from_dict(data)

        assert restored.modifiers == []

    def test_json_serializable(self, component_state_with_modifiers):
        """to_dict() output should be JSON serializable."""
        data = component_state_with_modifiers.to_dict()
        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        restored = ComponentState.from_dict(parsed)
        assert restored.component_id == component_state_with_modifiers.component_id


# =============================================================================
# ShipState Tests
# =============================================================================

class TestShipStateSerialization:
    """Tests for ShipState to_dict() and from_dict()."""

    @pytest.fixture
    def minimal_ship_state(self) -> ShipState:
        """Create a minimal ShipState with no components."""
        return ShipState(
            ship_id="ship-001",
            name="Scout Alpha",
            ship_class="Scout",
            theme_id="federation",
            team_id=0,
            color=(100, 150, 200),
            movement_policy="kite_max",
            position=(500.0, 300.0),
            velocity=(10.0, -5.0),
            angle=45.0,
            current_hp=80,
            max_hp=100,
            current_shields=25.0,
            max_shields=50.0,
            components={},
            resource_levels={},
            resource_max={},
            is_alive=True,
            is_derelict=False,
            retreat_status=None,
            current_target_id=None,
        )

    @pytest.fixture
    def ship_state_with_components(self) -> ShipState:
        """Create a ShipState with components in multiple layers."""
        outer_comp = ComponentState(
            component_id="laser_mk1",
            current_hp=10,
            max_hp=10,
            is_active=True,
            layer="OUTER",
            modifiers=[],
        )
        inner_comp = ComponentState(
            component_id="shield_gen",
            current_hp=15,
            max_hp=20,
            is_active=True,
            layer="INNER",
            modifiers=[{"id": "efficiency", "value": 1}],
        )
        return ShipState(
            ship_id="ship-002",
            name="Battlecruiser Omega",
            ship_class="Battlecruiser",
            theme_id="empire",
            team_id=1,
            color=(255, 50, 50),
            movement_policy="brawl_close",
            position=(800.0, 600.0),
            velocity=(0.0, 0.0),
            angle=180.0,
            current_hp=500,
            max_hp=500,
            current_shields=200.0,
            max_shields=200.0,
            components={
                "OUTER": [outer_comp],
                "INNER": [inner_comp],
            },
            resource_levels={"fuel": 80.0, "energy": 100.0},
            resource_max={"fuel": 100.0, "energy": 100.0},
            is_alive=True,
            is_derelict=False,
            retreat_status=None,
            current_target_id="ship-001",
        )

    @pytest.fixture
    def destroyed_ship_state(self) -> ShipState:
        """Create a destroyed ship state."""
        return ShipState(
            ship_id="ship-003",
            name="Destroyed Frigate",
            ship_class="Frigate",
            theme_id="pirates",
            team_id=1,
            color=(100, 100, 100),
            movement_policy="kite_medium",
            position=(200.0, 400.0),
            velocity=(0.0, 0.0),
            angle=0.0,
            current_hp=0,
            max_hp=150,
            current_shields=0.0,
            max_shields=75.0,
            components={},
            resource_levels={},
            resource_max={},
            is_alive=False,
            is_derelict=True,
            retreat_status=None,
            current_target_id=None,
        )

    @pytest.fixture
    def retreating_ship_state(self) -> ShipState:
        """Create a ship that is retreating."""
        return ShipState(
            ship_id="ship-004",
            name="Retreating Carrier",
            ship_class="Carrier",
            theme_id="federation",
            team_id=0,
            color=(200, 200, 50),
            movement_policy="hold_position",
            position=(1500.0, 800.0),
            velocity=(50.0, 25.0),
            angle=315.0,
            current_hp=100,
            max_hp=400,
            current_shields=10.0,
            max_shields=150.0,
            components={},
            resource_levels={},
            resource_max={},
            is_alive=True,
            is_derelict=False,
            retreat_status="retreating",
            current_target_id=None,
        )

    def test_to_dict_contains_all_fields(self, minimal_ship_state):
        """to_dict() should include all ShipState fields."""
        result = minimal_ship_state.to_dict()

        expected_fields = [
            "ship_id", "name", "ship_class", "theme_id", "team_id",
            "color", "movement_policy", "position", "velocity", "angle",
            "current_hp", "max_hp", "current_shields", "max_shields",
            "components", "resource_levels", "resource_max",
            "is_alive", "is_derelict", "retreat_status", "current_target_id",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_to_dict_converts_tuples_to_lists(self, minimal_ship_state):
        """Tuples should be converted to lists for JSON serialization."""
        result = minimal_ship_state.to_dict()

        assert isinstance(result["color"], list)
        assert isinstance(result["position"], list)
        assert isinstance(result["velocity"], list)

    def test_round_trip_minimal(self, minimal_ship_state):
        """Minimal ship should round-trip correctly."""
        data = minimal_ship_state.to_dict()
        restored = ShipState.from_dict(data)

        assert restored.ship_id == minimal_ship_state.ship_id
        assert restored.name == minimal_ship_state.name
        assert restored.ship_class == minimal_ship_state.ship_class
        assert restored.theme_id == minimal_ship_state.theme_id
        assert restored.team_id == minimal_ship_state.team_id
        assert restored.color == minimal_ship_state.color
        assert restored.movement_policy == minimal_ship_state.movement_policy
        assert restored.position == minimal_ship_state.position
        assert restored.velocity == minimal_ship_state.velocity
        assert restored.angle == minimal_ship_state.angle
        assert restored.current_hp == minimal_ship_state.current_hp
        assert restored.max_hp == minimal_ship_state.max_hp
        assert restored.current_shields == minimal_ship_state.current_shields
        assert restored.max_shields == minimal_ship_state.max_shields
        assert restored.is_alive == minimal_ship_state.is_alive
        assert restored.is_derelict == minimal_ship_state.is_derelict
        assert restored.retreat_status == minimal_ship_state.retreat_status
        assert restored.current_target_id == minimal_ship_state.current_target_id

    def test_round_trip_with_components(self, ship_state_with_components):
        """Ship with components should round-trip correctly."""
        data = ship_state_with_components.to_dict()
        restored = ShipState.from_dict(data)

        assert len(restored.components) == 2
        assert "OUTER" in restored.components
        assert "INNER" in restored.components
        assert len(restored.components["OUTER"]) == 1
        assert len(restored.components["INNER"]) == 1

        outer_comp = restored.components["OUTER"][0]
        assert outer_comp.component_id == "laser_mk1"
        assert outer_comp.current_hp == 10

        inner_comp = restored.components["INNER"][0]
        assert inner_comp.component_id == "shield_gen"
        assert inner_comp.modifiers == [{"id": "efficiency", "value": 1}]

    def test_round_trip_with_resources(self, ship_state_with_components):
        """Resource levels should be preserved through round-trip."""
        data = ship_state_with_components.to_dict()
        restored = ShipState.from_dict(data)

        assert restored.resource_levels == {"fuel": 80.0, "energy": 100.0}
        assert restored.resource_max == {"fuel": 100.0, "energy": 100.0}

    def test_round_trip_destroyed_ship(self, destroyed_ship_state):
        """Destroyed ship state should be preserved."""
        data = destroyed_ship_state.to_dict()
        restored = ShipState.from_dict(data)

        assert restored.is_alive is False
        assert restored.is_derelict is True
        assert restored.current_hp == 0

    def test_round_trip_retreating_ship(self, retreating_ship_state):
        """Retreat status should be preserved."""
        data = retreating_ship_state.to_dict()
        restored = ShipState.from_dict(data)

        assert restored.retreat_status == "retreating"

    def test_round_trip_escaped_ship(self):
        """Escaped retreat status should be preserved."""
        ship = ShipState(
            ship_id="escaped-001",
            name="Escaped Ship",
            ship_class="Scout",
            theme_id="default",
            team_id=0,
            color=(100, 100, 100),
            movement_policy="hold_position",
            position=(2000.0, 2000.0),
            velocity=(0.0, 0.0),
            angle=0.0,
            current_hp=50,
            max_hp=100,
            current_shields=0.0,
            max_shields=50.0,
            components={},
            resource_levels={},
            resource_max={},
            is_alive=True,
            is_derelict=False,
            retreat_status="escaped",
            current_target_id=None,
        )
        data = ship.to_dict()
        restored = ShipState.from_dict(data)

        assert restored.retreat_status == "escaped"

    def test_from_dict_defaults_for_missing_optional_fields(self):
        """from_dict() should use defaults for missing optional fields."""
        data = {
            "ship_id": "test-ship",
            "name": "Test",
            "ship_class": "Scout",
            "theme_id": "default",
            "team_id": 0,
            "color": [100, 100, 100],
            "movement_policy": "kite_max",
            "position": [0.0, 0.0],
            "velocity": [0.0, 0.0],
            "angle": 0.0,
            "current_hp": 100,
            "max_hp": 100,
            "current_shields": 0.0,
            "max_shields": 0.0,
            # Optional fields omitted: components, resource_levels, etc.
        }
        restored = ShipState.from_dict(data)

        assert restored.components == {}
        assert restored.resource_levels == {}
        assert restored.resource_max == {}
        assert restored.is_alive is True  # Default
        assert restored.is_derelict is False  # Default
        assert restored.retreat_status is None
        assert restored.current_target_id is None

    def test_json_serializable(self, ship_state_with_components):
        """to_dict() output should be fully JSON serializable."""
        data = ship_state_with_components.to_dict()
        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        restored = ShipState.from_dict(parsed)
        assert restored.ship_id == ship_state_with_components.ship_id
        assert restored.name == ship_state_with_components.name


# =============================================================================
# ProjectileState Tests
# =============================================================================

class TestProjectileStateSerialization:
    """Tests for ProjectileState to_dict() and from_dict()."""

    @pytest.fixture
    def basic_projectile(self) -> ProjectileState:
        """Create a basic projectile state."""
        return ProjectileState(
            projectile_id="proj-001",
            owner_ship_id="ship-001",
            team_id=0,
            position=(400.0, 300.0),
            velocity=(100.0, 50.0),
            damage=25.0,
            max_range=500.0,
            endurance=3.0,
            max_endurance=5.0,
            projectile_type="projectile",
            turn_rate=0.0,
            max_speed=0.0,
            target_ship_id=None,
            hp=1,
            max_hp=1,
            distance_traveled=150.0,
            is_alive=True,
        )

    @pytest.fixture
    def missile_projectile(self) -> ProjectileState:
        """Create a missile-type projectile with tracking."""
        return ProjectileState(
            projectile_id="missile-001",
            owner_ship_id="ship-002",
            team_id=1,
            position=(600.0, 400.0),
            velocity=(80.0, 60.0),
            damage=100.0,
            max_range=1000.0,
            endurance=10.0,
            max_endurance=10.0,
            projectile_type="missile",
            turn_rate=5.0,
            max_speed=150.0,
            target_ship_id="ship-001",
            hp=3,
            max_hp=3,
            distance_traveled=200.0,
            is_alive=True,
        )

    @pytest.fixture
    def destroyed_projectile(self) -> ProjectileState:
        """Create a destroyed projectile state."""
        return ProjectileState(
            projectile_id="proj-dead",
            owner_ship_id="ship-001",
            team_id=0,
            position=(450.0, 320.0),
            velocity=(0.0, 0.0),
            damage=25.0,
            max_range=500.0,
            endurance=0.0,
            max_endurance=5.0,
            projectile_type="projectile",
            turn_rate=0.0,
            max_speed=0.0,
            target_ship_id=None,
            hp=0,
            max_hp=1,
            distance_traveled=500.0,
            is_alive=False,
        )

    def test_to_dict_contains_all_fields(self, basic_projectile):
        """to_dict() should include all ProjectileState fields."""
        result = basic_projectile.to_dict()

        expected_fields = [
            "projectile_id", "owner_ship_id", "team_id", "position", "velocity",
            "damage", "max_range", "endurance", "max_endurance", "projectile_type",
            "turn_rate", "max_speed", "target_ship_id", "hp", "max_hp",
            "distance_traveled", "is_alive",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_to_dict_converts_tuples_to_lists(self, basic_projectile):
        """Tuples should be converted to lists for JSON serialization."""
        result = basic_projectile.to_dict()

        assert isinstance(result["position"], list)
        assert isinstance(result["velocity"], list)

    def test_round_trip_basic(self, basic_projectile):
        """Basic projectile should round-trip correctly."""
        data = basic_projectile.to_dict()
        restored = ProjectileState.from_dict(data)

        assert restored.projectile_id == basic_projectile.projectile_id
        assert restored.owner_ship_id == basic_projectile.owner_ship_id
        assert restored.team_id == basic_projectile.team_id
        assert restored.position == basic_projectile.position
        assert restored.velocity == basic_projectile.velocity
        assert restored.damage == basic_projectile.damage
        assert restored.max_range == basic_projectile.max_range
        assert restored.endurance == basic_projectile.endurance
        assert restored.max_endurance == basic_projectile.max_endurance
        assert restored.projectile_type == basic_projectile.projectile_type
        assert restored.distance_traveled == basic_projectile.distance_traveled
        assert restored.is_alive == basic_projectile.is_alive

    def test_round_trip_missile(self, missile_projectile):
        """Missile with tracking should round-trip correctly."""
        data = missile_projectile.to_dict()
        restored = ProjectileState.from_dict(data)

        assert restored.projectile_type == "missile"
        assert restored.turn_rate == 5.0
        assert restored.max_speed == 150.0
        assert restored.target_ship_id == "ship-001"
        assert restored.hp == 3
        assert restored.max_hp == 3

    def test_round_trip_destroyed(self, destroyed_projectile):
        """Destroyed projectile state should be preserved."""
        data = destroyed_projectile.to_dict()
        restored = ProjectileState.from_dict(data)

        assert restored.is_alive is False
        assert restored.hp == 0
        assert restored.endurance == 0.0

    def test_from_dict_defaults_for_missing_optional_fields(self):
        """from_dict() should use defaults for missing optional fields."""
        data = {
            "projectile_id": "proj-minimal",
            "team_id": 0,
            "position": [100.0, 100.0],
            "velocity": [10.0, 10.0],
            "damage": 10.0,
            "max_range": 100.0,
            "endurance": 1.0,
            "max_endurance": 1.0,
            "projectile_type": "projectile",
            # Optional fields omitted
        }
        restored = ProjectileState.from_dict(data)

        assert restored.owner_ship_id is None
        assert restored.turn_rate == 0
        assert restored.max_speed == 0
        assert restored.target_ship_id is None
        assert restored.hp == 1
        assert restored.max_hp == 1
        assert restored.distance_traveled == 0
        assert restored.is_alive is True

    def test_json_serializable(self, missile_projectile):
        """to_dict() output should be fully JSON serializable."""
        data = missile_projectile.to_dict()
        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        restored = ProjectileState.from_dict(parsed)
        assert restored.projectile_id == missile_projectile.projectile_id


# =============================================================================
# BattleState Tests
# =============================================================================

class TestBattleStateSerialization:
    """Tests for BattleState to_dict(), from_dict(), to_json(), from_json()."""

    @pytest.fixture
    def empty_battle_state(self) -> BattleState:
        """Create an empty BattleState."""
        return BattleState(
            version="1.0",
            battle_id="battle-empty",
            seed=12345,
            tick_count=0,
            ships={},
            projectiles=[],
            end_condition_data={"type": "team_eliminated"},
            allow_retreat=False,
            allow_reinforcements=False,
            created_at="2024-01-01T12:00:00",
            mode="manual",
        )

    @pytest.fixture
    def battle_state_with_ships(self) -> BattleState:
        """Create a BattleState with ships from both teams."""
        ship1 = ShipState(
            ship_id="ship-alpha",
            name="Alpha Fighter",
            ship_class="Fighter",
            theme_id="federation",
            team_id=0,
            color=(100, 100, 255),
            movement_policy="brawl_close",
            position=(200.0, 300.0),
            velocity=(5.0, 0.0),
            angle=0.0,
            current_hp=80,
            max_hp=100,
            current_shields=40.0,
            max_shields=50.0,
            components={},
            resource_levels={},
            resource_max={},
            is_alive=True,
            is_derelict=False,
        )
        ship2 = ShipState(
            ship_id="ship-beta",
            name="Beta Cruiser",
            ship_class="Cruiser",
            theme_id="empire",
            team_id=1,
            color=(255, 100, 100),
            movement_policy="kite_medium",
            position=(800.0, 300.0),
            velocity=(-5.0, 0.0),
            angle=180.0,
            current_hp=300,
            max_hp=300,
            current_shields=100.0,
            max_shields=100.0,
            components={},
            resource_levels={"fuel": 100.0},
            resource_max={"fuel": 100.0},
            is_alive=True,
            is_derelict=False,
        )
        return BattleState(
            version="1.0",
            battle_id="battle-001",
            seed=42,
            tick_count=500,
            ships={
                "ship-alpha": ship1,
                "ship-beta": ship2,
            },
            projectiles=[],
            end_condition_data={"type": "team_eliminated"},
            allow_retreat=True,
            allow_reinforcements=False,
            created_at="2024-01-15T14:30:00",
            mode="strategy",
        )

    @pytest.fixture
    def full_battle_state(self) -> BattleState:
        """Create a BattleState with ships and projectiles."""
        ship1 = ShipState(
            ship_id="ship-001",
            name="Warship",
            ship_class="Cruiser",
            theme_id="federation",
            team_id=0,
            color=(100, 150, 200),
            movement_policy="kite_max",
            position=(300.0, 400.0),
            velocity=(0.0, 0.0),
            angle=90.0,
            current_hp=150,
            max_hp=200,
            current_shields=50.0,
            max_shields=80.0,
            components={
                "OUTER": [
                    ComponentState(
                        component_id="laser_mk2",
                        current_hp=10,
                        max_hp=10,
                        is_active=True,
                        layer="OUTER",
                        modifiers=[],
                    ),
                ],
            },
            resource_levels={"energy": 80.0},
            resource_max={"energy": 100.0},
            is_alive=True,
            is_derelict=False,
        )
        proj1 = ProjectileState(
            projectile_id="proj-001",
            owner_ship_id="ship-001",
            team_id=0,
            position=(400.0, 400.0),
            velocity=(100.0, 0.0),
            damage=30.0,
            max_range=600.0,
            endurance=4.0,
            max_endurance=5.0,
            projectile_type="projectile",
        )
        return BattleState(
            version="1.0",
            battle_id="battle-full",
            seed=99999,
            tick_count=1000,
            ships={"ship-001": ship1},
            projectiles=[proj1],
            end_condition_data={"type": "team_eliminated"},
            allow_retreat=True,
            allow_reinforcements=True,
            created_at="2024-02-01T10:00:00",
            mode="test",
        )

    def test_to_dict_contains_all_fields(self, empty_battle_state):
        """to_dict() should include all BattleState fields."""
        result = empty_battle_state.to_dict()

        expected_fields = [
            "version", "battle_id", "seed", "tick_count",
            "ships", "projectiles", "end_condition_data", "allow_retreat",
            "allow_reinforcements", "created_at", "mode",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_round_trip_empty(self, empty_battle_state):
        """Empty battle state should round-trip correctly."""
        data = empty_battle_state.to_dict()
        restored = BattleState.from_dict(data)

        assert restored.version == empty_battle_state.version
        assert restored.battle_id == empty_battle_state.battle_id
        assert restored.seed == empty_battle_state.seed
        assert restored.tick_count == empty_battle_state.tick_count
        assert restored.ships == {}
        assert restored.projectiles == []
        assert restored.end_condition_data == empty_battle_state.end_condition_data
        assert restored.allow_retreat == empty_battle_state.allow_retreat
        assert restored.allow_reinforcements == empty_battle_state.allow_reinforcements
        assert restored.created_at == empty_battle_state.created_at
        assert restored.mode == empty_battle_state.mode

    def test_round_trip_with_ships(self, battle_state_with_ships):
        """Battle state with ships should round-trip correctly."""
        data = battle_state_with_ships.to_dict()
        restored = BattleState.from_dict(data)

        assert len(restored.ships) == 2
        assert "ship-alpha" in restored.ships
        assert "ship-beta" in restored.ships

        alpha = restored.ships["ship-alpha"]
        assert alpha.name == "Alpha Fighter"
        assert alpha.team_id == 0
        assert alpha.current_hp == 80

        beta = restored.ships["ship-beta"]
        assert beta.name == "Beta Cruiser"
        assert beta.team_id == 1
        assert beta.resource_levels == {"fuel": 100.0}

    def test_round_trip_with_projectiles(self, full_battle_state):
        """Battle state with projectiles should round-trip correctly."""
        data = full_battle_state.to_dict()
        restored = BattleState.from_dict(data)

        assert len(restored.projectiles) == 1
        proj = restored.projectiles[0]
        assert proj.projectile_id == "proj-001"
        assert proj.owner_ship_id == "ship-001"
        assert proj.damage == 30.0

    def test_round_trip_nested_components(self, full_battle_state):
        """Nested component states should be preserved."""
        data = full_battle_state.to_dict()
        restored = BattleState.from_dict(data)

        ship = restored.ships["ship-001"]
        assert "OUTER" in ship.components
        assert len(ship.components["OUTER"]) == 1
        assert ship.components["OUTER"][0].component_id == "laser_mk2"

    def test_to_json_produces_valid_json(self, battle_state_with_ships):
        """to_json() should produce valid JSON string."""
        json_str = battle_state_with_ships.to_json()

        # Should not raise
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_from_json_restores_state(self, battle_state_with_ships):
        """from_json() should restore state from JSON string."""
        json_str = battle_state_with_ships.to_json()
        restored = BattleState.from_json(json_str)

        assert restored.battle_id == battle_state_with_ships.battle_id
        assert len(restored.ships) == 2

    def test_json_round_trip(self, full_battle_state):
        """Full JSON round-trip should preserve all data."""
        json_str = full_battle_state.to_json()
        restored = BattleState.from_json(json_str)

        assert restored.version == full_battle_state.version
        assert restored.battle_id == full_battle_state.battle_id
        assert restored.seed == full_battle_state.seed
        assert restored.tick_count == full_battle_state.tick_count
        assert len(restored.ships) == 1
        assert len(restored.projectiles) == 1

    def test_from_dict_defaults_for_missing_fields(self):
        """from_dict() should use defaults for missing optional fields."""
        data = {
            # Minimal required data
        }
        restored = BattleState.from_dict(data)

        assert restored.version == "1.0"
        assert restored.battle_id == ""
        assert restored.seed is None
        assert restored.tick_count == 0
        assert restored.ships == {}
        assert restored.projectiles == []
        assert restored.end_condition_data == {"type": "team_eliminated"}
        assert restored.allow_retreat is False
        assert restored.allow_reinforcements is False
        assert restored.created_at == ""
        assert restored.mode == "manual"

    def test_get_ships_by_team(self, battle_state_with_ships):
        """get_ships_by_team() should filter ships correctly."""
        team_0 = battle_state_with_ships.get_ships_by_team(0)
        team_1 = battle_state_with_ships.get_ships_by_team(1)

        assert len(team_0) == 1
        assert team_0[0].name == "Alpha Fighter"
        assert len(team_1) == 1
        assert team_1[0].name == "Beta Cruiser"

    def test_get_alive_ships(self, battle_state_with_ships):
        """get_alive_ships() should return only living ships."""
        alive = battle_state_with_ships.get_alive_ships()
        assert len(alive) == 2

    def test_seed_none_preserved(self):
        """None seed should be preserved through round-trip."""
        state = BattleState(seed=None)
        data = state.to_dict()
        restored = BattleState.from_dict(data)

        assert restored.seed is None



# =============================================================================
# BattleResults Tests
# =============================================================================

class TestBattleResultsSerialization:
    """Tests for BattleResults to_dict() and from_dict()."""

    @pytest.fixture
    def minimal_results(self) -> BattleResults:
        """Create minimal battle results (no nested states)."""
        return BattleResults(
            winner=0,
            tick_count=5000,
            seed=12345,
            initial_state=None,
            final_state=None,
            surviving_ships=[],
            destroyed_ships=[],
            escaped_ships=[],
            captured_ships=[],
        )

    @pytest.fixture
    def full_results(self) -> BattleResults:
        """Create full battle results with all data."""
        surviving_ship = ShipState(
            ship_id="survivor-001",
            name="Victorious Cruiser",
            ship_class="Cruiser",
            theme_id="federation",
            team_id=0,
            color=(100, 150, 200),
            movement_policy="brawl_close",
            position=(500.0, 500.0),
            velocity=(0.0, 0.0),
            angle=0.0,
            current_hp=50,
            max_hp=200,
            current_shields=0.0,
            max_shields=80.0,
            components={},
            resource_levels={},
            resource_max={},
            is_alive=True,
            is_derelict=False,
        )
        destroyed_ship = ShipState(
            ship_id="destroyed-001",
            name="Fallen Frigate",
            ship_class="Frigate",
            theme_id="empire",
            team_id=1,
            color=(255, 100, 100),
            movement_policy="kite_medium",
            position=(600.0, 400.0),
            velocity=(0.0, 0.0),
            angle=0.0,
            current_hp=0,
            max_hp=100,
            current_shields=0.0,
            max_shields=50.0,
            components={},
            resource_levels={},
            resource_max={},
            is_alive=False,
            is_derelict=True,
        )
        initial = BattleState(
            battle_id="battle-001",
            tick_count=0,
            ships={"survivor-001": surviving_ship},
        )
        final = BattleState(
            battle_id="battle-001",
            tick_count=5000,
            ships={
                "survivor-001": surviving_ship,
                "destroyed-001": destroyed_ship,
            },
        )
        return BattleResults(
            winner=0,
            tick_count=5000,
            seed=42,
            initial_state=initial,
            final_state=final,
            surviving_ships=[surviving_ship],
            destroyed_ships=[destroyed_ship],
            escaped_ships=[],
            captured_ships=[],
        )

    @pytest.fixture
    def draw_results(self) -> BattleResults:
        """Create battle results ending in a draw."""
        return BattleResults(
            winner=-1,
            tick_count=100000,
            seed=99999,
            initial_state=None,
            final_state=None,
        )

    @pytest.fixture
    def incomplete_results(self) -> BattleResults:
        """Create incomplete battle results (winner=None)."""
        return BattleResults(
            winner=None,
            tick_count=2500,
            seed=11111,
        )

    def test_to_dict_contains_all_fields(self, minimal_results):
        """to_dict() should include all BattleResults fields."""
        result = minimal_results.to_dict()

        expected_fields = [
            "winner", "tick_count", "seed", "initial_state", "final_state",
            "surviving_ships", "destroyed_ships", "escaped_ships", "captured_ships",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_round_trip_minimal(self, minimal_results):
        """Minimal results should round-trip correctly."""
        data = minimal_results.to_dict()
        restored = BattleResults.from_dict(data)

        assert restored.winner == minimal_results.winner
        assert restored.tick_count == minimal_results.tick_count
        assert restored.seed == minimal_results.seed
        assert restored.initial_state is None
        assert restored.final_state is None
        assert restored.surviving_ships == []
        assert restored.destroyed_ships == []
        assert restored.escaped_ships == []
        assert restored.captured_ships == []

    def test_round_trip_full(self, full_results):
        """Full results with nested states should round-trip correctly."""
        data = full_results.to_dict()
        restored = BattleResults.from_dict(data)

        assert restored.winner == 0
        assert restored.tick_count == 5000
        assert restored.seed == 42

        # Check nested states
        assert restored.initial_state is not None
        assert restored.initial_state.battle_id == "battle-001"

        assert restored.final_state is not None
        assert len(restored.final_state.ships) == 2

        # Check ship lists
        assert len(restored.surviving_ships) == 1
        assert restored.surviving_ships[0].name == "Victorious Cruiser"

        assert len(restored.destroyed_ships) == 1
        assert restored.destroyed_ships[0].name == "Fallen Frigate"

    def test_round_trip_draw(self, draw_results):
        """Draw results (-1 winner) should round-trip correctly."""
        data = draw_results.to_dict()
        restored = BattleResults.from_dict(data)

        assert restored.winner == -1

    def test_round_trip_incomplete(self, incomplete_results):
        """Incomplete results (None winner) should round-trip correctly."""
        data = incomplete_results.to_dict()
        restored = BattleResults.from_dict(data)

        assert restored.winner is None

    def test_to_json_produces_valid_json(self, full_results):
        """to_json() should produce valid JSON string."""
        json_str = full_results.to_json()

        # Should not raise
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_json_round_trip(self, full_results):
        """Full JSON round-trip should preserve all data."""
        json_str = full_results.to_json()
        parsed = json.loads(json_str)
        restored = BattleResults.from_dict(parsed)

        assert restored.winner == full_results.winner
        assert restored.tick_count == full_results.tick_count
        assert len(restored.surviving_ships) == len(full_results.surviving_ships)
        assert len(restored.destroyed_ships) == len(full_results.destroyed_ships)

    def test_from_dict_defaults_for_missing_fields(self):
        """from_dict() should use defaults for missing optional fields."""
        data = {
            "winner": 1,
            "tick_count": 1000,
            # Other fields omitted
        }
        restored = BattleResults.from_dict(data)

        assert restored.winner == 1
        assert restored.tick_count == 1000
        assert restored.seed is None
        assert restored.initial_state is None
        assert restored.final_state is None
        assert restored.surviving_ships == []
        assert restored.destroyed_ships == []
        assert restored.escaped_ships == []
        assert restored.captured_ships == []

    def test_get_team_survivors(self, full_results):
        """get_team_survivors() should filter by team_id."""
        team_0 = full_results.get_team_survivors(0)
        team_1 = full_results.get_team_survivors(1)

        assert len(team_0) == 1
        assert team_0[0].name == "Victorious Cruiser"
        assert len(team_1) == 0

    def test_get_team_losses(self, full_results):
        """get_team_losses() should filter by team_id."""
        team_0 = full_results.get_team_losses(0)
        team_1 = full_results.get_team_losses(1)

        assert len(team_0) == 0
        assert len(team_1) == 1
        assert team_1[0].name == "Fallen Frigate"


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================

class TestSerializationEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_string_fields_preserved(self):
        """Empty strings should be preserved, not converted to None."""
        state = BattleState(battle_id="", created_at="")
        data = state.to_dict()
        restored = BattleState.from_dict(data)

        assert restored.battle_id == ""
        assert restored.created_at == ""

    def test_zero_values_preserved(self):
        """Zero values should be preserved correctly."""
        ship = ShipState(
            ship_id="zero-ship",
            name="Zero Ship",
            ship_class="Test",
            theme_id="test",
            team_id=0,
            color=(0, 0, 0),
            movement_policy="test_do_nothing",
            position=(0.0, 0.0),
            velocity=(0.0, 0.0),
            angle=0.0,
            current_hp=0,
            max_hp=0,
            current_shields=0.0,
            max_shields=0.0,
        )
        data = ship.to_dict()
        restored = ShipState.from_dict(data)

        assert restored.current_hp == 0
        assert restored.max_hp == 0
        assert restored.position == (0.0, 0.0)
        assert restored.color == (0, 0, 0)

    def test_negative_values_preserved(self):
        """Negative values should be preserved (for velocity)."""
        ship = ShipState(
            ship_id="negative-ship",
            name="Backwards Ship",
            ship_class="Test",
            theme_id="test",
            team_id=0,
            color=(100, 100, 100),
            movement_policy="test_do_nothing",
            position=(-100.0, -200.0),
            velocity=(-50.0, -25.0),
            angle=-45.0,
            current_hp=100,
            max_hp=100,
            current_shields=50.0,
            max_shields=50.0,
        )
        data = ship.to_dict()
        restored = ShipState.from_dict(data)

        assert restored.position == (-100.0, -200.0)
        assert restored.velocity == (-50.0, -25.0)
        assert restored.angle == -45.0

    def test_large_values_preserved(self):
        """Large numeric values should be preserved."""
        state = BattleState(
            tick_count=999999999,
            seed=2147483647,  # Max int32
        )
        data = state.to_dict()
        restored = BattleState.from_dict(data)

        assert restored.tick_count == 999999999
        assert restored.seed == 2147483647

    def test_float_precision_preserved(self):
        """Float values should maintain reasonable precision."""
        ship = ShipState(
            ship_id="precision-ship",
            name="Precise Ship",
            ship_class="Test",
            theme_id="test",
            team_id=0,
            color=(100, 100, 100),
            movement_policy="test_do_nothing",
            position=(123.456789, 987.654321),
            velocity=(0.123456, 0.654321),
            angle=45.6789,
            current_hp=100,
            max_hp=100,
            current_shields=12.3456789,
            max_shields=50.0,
        )
        data = ship.to_dict()
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        restored = ShipState.from_dict(parsed)

        # Check approximate equality for floats
        assert abs(restored.position[0] - 123.456789) < 0.0001
        assert abs(restored.position[1] - 987.654321) < 0.0001
        assert abs(restored.current_shields - 12.3456789) < 0.0001

    def test_unicode_in_strings(self):
        """Unicode characters in strings should be preserved."""
        ship = ShipState(
            ship_id="unicode-ship",
            name="Alpha-Omega",
            ship_class="Cruiser",
            theme_id="test",
            team_id=0,
            color=(100, 100, 100),
            movement_policy="kite_max",
            position=(0.0, 0.0),
            velocity=(0.0, 0.0),
            angle=0.0,
            current_hp=100,
            max_hp=100,
            current_shields=0.0,
            max_shields=0.0,
        )
        data = ship.to_dict()
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        restored = ShipState.from_dict(parsed)

        assert restored.name == "Alpha-Omega"

    def test_deeply_nested_structure(self):
        """Deeply nested structures should serialize correctly."""
        # Ship with multiple components in multiple layers, each with modifiers
        comp1 = ComponentState(
            component_id="comp1",
            current_hp=10,
            max_hp=10,
            is_active=True,
            layer="OUTER",
            modifiers=[
                {"id": "mod1", "value": 1},
                {"id": "mod2", "value": 2},
            ],
        )
        comp2 = ComponentState(
            component_id="comp2",
            current_hp=20,
            max_hp=20,
            is_active=True,
            layer="OUTER",
            modifiers=[],
        )
        comp3 = ComponentState(
            component_id="comp3",
            current_hp=15,
            max_hp=15,
            is_active=False,
            layer="INNER",
            modifiers=[{"id": "mod3", "value": 3}],
        )
        ship = ShipState(
            ship_id="nested-ship",
            name="Complex Ship",
            ship_class="Battleship",
            theme_id="test",
            team_id=0,
            color=(100, 100, 100),
            movement_policy="kite_max",
            position=(500.0, 500.0),
            velocity=(10.0, 10.0),
            angle=90.0,
            current_hp=1000,
            max_hp=1000,
            current_shields=500.0,
            max_shields=500.0,
            components={
                "OUTER": [comp1, comp2],
                "INNER": [comp3],
            },
            resource_levels={"fuel": 100.0, "energy": 200.0, "ammo": 50.0},
            resource_max={"fuel": 100.0, "energy": 200.0, "ammo": 100.0},
            is_alive=True,
            is_derelict=False,
        )
        state = BattleState(
            battle_id="nested-battle",
            ships={"nested-ship": ship},
            projectiles=[
                ProjectileState(
                    projectile_id="p1",
                    owner_ship_id="nested-ship",
                    team_id=0,
                    position=(600.0, 500.0),
                    velocity=(100.0, 0.0),
                    damage=50.0,
                    max_range=1000.0,
                    endurance=5.0,
                    max_endurance=5.0,
                    projectile_type="missile",
                    turn_rate=3.0,
                    max_speed=200.0,
                    target_ship_id=None,
                ),
            ],
        )

        # Full round-trip through JSON
        json_str = state.to_json()
        restored = BattleState.from_json(json_str)

        # Verify structure
        assert len(restored.ships) == 1
        restored_ship = restored.ships["nested-ship"]
        assert len(restored_ship.components["OUTER"]) == 2
        assert len(restored_ship.components["INNER"]) == 1
        assert len(restored_ship.components["OUTER"][0].modifiers) == 2
        assert len(restored.projectiles) == 1

    def test_many_ships_and_projectiles(self):
        """State with many ships and projectiles should serialize."""
        ships = {}
        for i in range(50):
            ships[f"ship-{i}"] = ShipState(
                ship_id=f"ship-{i}",
                name=f"Ship {i}",
                ship_class="Fighter",
                theme_id="test",
                team_id=i % 2,
                color=(100, 100, 100),
                movement_policy="brawl_close",
                position=(float(i * 100), float(i * 50)),
                velocity=(float(i), float(-i)),
                angle=float(i * 7.2),
                current_hp=100 - i,
                max_hp=100,
                current_shields=50.0,
                max_shields=50.0,
            )

        projectiles = []
        for i in range(100):
            projectiles.append(ProjectileState(
                projectile_id=f"proj-{i}",
                owner_ship_id=f"ship-{i % 50}",
                team_id=i % 2,
                position=(float(i * 10), float(i * 5)),
                velocity=(100.0, 50.0),
                damage=25.0,
                max_range=500.0,
                endurance=3.0,
                max_endurance=5.0,
                projectile_type="projectile",
            ))

        state = BattleState(
            battle_id="mass-battle",
            ships=ships,
            projectiles=projectiles,
        )

        json_str = state.to_json()
        restored = BattleState.from_json(json_str)

        assert len(restored.ships) == 50
        assert len(restored.projectiles) == 100
