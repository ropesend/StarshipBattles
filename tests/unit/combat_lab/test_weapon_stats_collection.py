"""
Tests for _collect_weapon_stats() on TestScenario.

Validates that per-weapon firing statistics (shots_fired, shots_hit) from
the simulation engine are correctly surfaced in test scenario results.

The simulation engine already tracks these counters on Component and Ship
objects — these tests verify the bridge from engine state to test results.
"""

from unittest.mock import Mock, MagicMock, patch, PropertyMock
from game.simulation.components.abilities.weapons import (
    WeaponAbility,
    BeamWeaponAbility,
    ProjectileWeaponAbility,
    SeekerWeaponAbility,
)


def _create_mock_component(name, ability_cls, shots_fired=0, shots_hit=0):
    """Create a mock component with a weapon ability.

    Args:
        name: Component display name.
        ability_cls: WeaponAbility subclass to use as the spec.
        shots_fired: Number of shots fired.
        shots_hit: Number of shots that hit.

    Returns:
        Mock component with ability_instances list.
    """
    ability = Mock(spec=ability_cls)
    comp = Mock()
    comp.name = name
    comp.shots_fired = shots_fired
    comp.shots_hit = shots_hit
    comp.ability_instances = [ability]
    return comp


def _create_non_weapon_component(name):
    """Create a mock component that is NOT a weapon (e.g., engine, shield)."""
    from game.simulation.components.abilities.propulsion import CombatPropulsion

    ability = Mock(spec=CombatPropulsion)
    comp = Mock()
    comp.name = name
    comp.shots_fired = 0
    comp.shots_hit = 0
    comp.ability_instances = [ability]
    return comp


def _create_mock_ship(components, total_shots_fired=None):
    """Create a mock ship with components in a single layer.

    Args:
        components: List of mock components.
        total_shots_fired: Override for ship aggregate counter.
            If None, sums component shots_fired.

    Returns:
        Mock ship with layers dict.
    """
    layer_data = Mock()
    layer_data.components = components

    ship = Mock()
    ship.layers = {"CORE": layer_data}
    if total_shots_fired is not None:
        ship.total_shots_fired = total_shots_fired
    else:
        ship.total_shots_fired = sum(c.shots_fired for c in components)
    return ship


def _create_scenario_instance():
    """Create a minimal TestScenario instance for testing.

    Uses patch to bypass __init__'s metadata requirement.
    """
    from combat_lab.scenarios.base import TestScenario

    with patch.object(TestScenario, "__init__", lambda self: None):
        scenario = TestScenario()
        scenario.results = {}
        return scenario


# =============================================================================
# Core functionality tests
# =============================================================================


class TestCollectWeaponStatsBasic:
    """Basic functionality of _collect_weapon_stats."""

    def test_stores_total_shots_fired(self):
        """Ship-level total_shots_fired is stored under '{role}_total_shots_fired'."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=7)
        ship = _create_mock_ship([comp], total_shots_fired=7)

        scenario._collect_weapon_stats(ship, "attacker")

        assert scenario.results["attacker_total_shots_fired"] == 7

    def test_stores_per_weapon_stats(self):
        """Per-weapon shots_fired and shots_hit are stored in '{role}_weapons' list."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=5, shots_hit=3)
        ship = _create_mock_ship([comp])

        scenario._collect_weapon_stats(ship, "attacker")

        weapons = scenario.results["attacker_weapons"]
        assert len(weapons) == 1
        assert weapons[0]["name"] == "Railgun"
        assert weapons[0]["type"] == "ProjectileWeaponAbility"
        assert weapons[0]["shots_fired"] == 5
        assert weapons[0]["shots_hit"] == 3

    def test_multiple_weapons(self):
        """All weapons on a ship are captured individually."""
        scenario = _create_scenario_instance()
        beam = _create_mock_component("Laser", BeamWeaponAbility, shots_fired=10, shots_hit=8)
        proj = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=5, shots_hit=3)
        ship = _create_mock_ship([beam, proj], total_shots_fired=15)

        scenario._collect_weapon_stats(ship, "attacker")

        weapons = scenario.results["attacker_weapons"]
        assert len(weapons) == 2
        names = {w["name"] for w in weapons}
        assert names == {"Laser", "Railgun"}

    def test_different_roles(self):
        """Different role prefixes produce separate result keys."""
        scenario = _create_scenario_instance()
        att_weapon = _create_mock_component("Beam", BeamWeaponAbility, shots_fired=10)
        tgt_weapon = _create_mock_component("PDC", BeamWeaponAbility, shots_fired=2)
        att_ship = _create_mock_ship([att_weapon])
        tgt_ship = _create_mock_ship([tgt_weapon])

        scenario._collect_weapon_stats(att_ship, "attacker")
        scenario._collect_weapon_stats(tgt_ship, "target")

        assert "attacker_total_shots_fired" in scenario.results
        assert "target_total_shots_fired" in scenario.results
        assert scenario.results["attacker_weapons"][0]["shots_fired"] == 10
        assert scenario.results["target_weapons"][0]["shots_fired"] == 2


# =============================================================================
# Edge cases
# =============================================================================


class TestCollectWeaponStatsEdgeCases:
    """Edge cases for _collect_weapon_stats."""

    def test_no_weapons(self):
        """Ship with only non-weapon components produces empty weapons list."""
        scenario = _create_scenario_instance()
        engine = _create_non_weapon_component("Engine")
        ship = _create_mock_ship([engine], total_shots_fired=0)

        scenario._collect_weapon_stats(ship, "attacker")

        assert scenario.results["attacker_total_shots_fired"] == 0
        assert scenario.results["attacker_weapons"] == []

    def test_no_layers(self):
        """Ship with no layers produces empty weapons list."""
        scenario = _create_scenario_instance()
        ship = Mock()
        ship.layers = {}
        ship.total_shots_fired = 0

        scenario._collect_weapon_stats(ship, "attacker")

        assert scenario.results["attacker_weapons"] == []

    def test_zero_shots(self):
        """Weapons that never fired are still included (important for diagnosis)."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=0, shots_hit=0)
        ship = _create_mock_ship([comp], total_shots_fired=0)

        scenario._collect_weapon_stats(ship, "attacker")

        weapons = scenario.results["attacker_weapons"]
        assert len(weapons) == 1
        assert weapons[0]["shots_fired"] == 0
        assert weapons[0]["shots_hit"] == 0

    def test_mixed_weapon_and_non_weapon(self):
        """Only weapon components are captured; non-weapons are excluded."""
        scenario = _create_scenario_instance()
        weapon = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=5)
        engine = _create_non_weapon_component("Engine")
        shield = _create_non_weapon_component("Shield Generator")
        ship = _create_mock_ship([weapon, engine, shield], total_shots_fired=5)

        scenario._collect_weapon_stats(ship, "attacker")

        weapons = scenario.results["attacker_weapons"]
        assert len(weapons) == 1
        assert weapons[0]["name"] == "Railgun"

    def test_seeker_weapon_type(self):
        """Seeker weapons are correctly identified and typed."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Missile Pod", SeekerWeaponAbility, shots_fired=3, shots_hit=2)
        ship = _create_mock_ship([comp])

        scenario._collect_weapon_stats(ship, "attacker")

        weapons = scenario.results["attacker_weapons"]
        assert weapons[0]["type"] == "SeekerWeaponAbility"

    def test_no_ability_instances_attribute(self):
        """Components without ability_instances are safely skipped."""
        scenario = _create_scenario_instance()
        comp = Mock()
        comp.name = "Bare Hull"
        comp.shots_fired = 0
        comp.shots_hit = 0
        del comp.ability_instances  # no ability_instances attribute

        layer_data = Mock()
        layer_data.components = [comp]
        ship = Mock()
        ship.layers = {"HULL": layer_data}
        ship.total_shots_fired = 0

        scenario._collect_weapon_stats(ship, "attacker")

        assert scenario.results["attacker_weapons"] == []

    def test_multiple_layers(self):
        """Weapons across different layers are all captured."""
        scenario = _create_scenario_instance()
        beam = _create_mock_component("Beam", BeamWeaponAbility, shots_fired=10)
        pdc = _create_mock_component("PDC", BeamWeaponAbility, shots_fired=4)

        layer_core = Mock()
        layer_core.components = [beam]
        layer_outer = Mock()
        layer_outer.components = [pdc]

        ship = Mock()
        ship.layers = {"CORE": layer_core, "OUTER": layer_outer}
        ship.total_shots_fired = 14

        scenario._collect_weapon_stats(ship, "attacker")

        weapons = scenario.results["attacker_weapons"]
        assert len(weapons) == 2
        total = sum(w["shots_fired"] for w in weapons)
        assert total == 14


# =============================================================================
# In-flight projectile tracking
# =============================================================================


def _create_mock_projectile(owner_ship, alive=True):
    """Create a mock projectile with owner reference."""
    proj = Mock()
    proj.owner = owner_ship
    proj.is_alive = alive
    return proj


def _create_mock_engine(projectiles=None):
    """Create a mock engine with a projectiles list."""
    engine = Mock()
    engine.projectiles = projectiles or []
    return engine


class TestInFlightTracking:
    """Tests for in-flight projectile counting in weapon stats."""

    def test_counts_in_flight_projectiles(self):
        """In-flight projectiles owned by the ship are counted."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=10, shots_hit=7)
        ship = _create_mock_ship([comp], total_shots_fired=10)

        engine = _create_mock_engine([
            _create_mock_projectile(ship, alive=True),
            _create_mock_projectile(ship, alive=True),
            _create_mock_projectile(ship, alive=False),  # dead, not in flight
        ])

        scenario._collect_weapon_stats(ship, "attacker", engine=engine)

        assert scenario.results["attacker_in_flight"] == 2
        assert scenario.results["attacker_resolved_shots"] == 8  # 10 - 2
        assert scenario.results["attacker_resolved_hits"] == 7

    def test_no_engine_skips_in_flight(self):
        """Without engine reference, in-flight keys are not set."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=5, shots_hit=3)
        ship = _create_mock_ship([comp])

        scenario._collect_weapon_stats(ship, "attacker")

        assert "attacker_in_flight" not in scenario.results

    def test_in_flight_excludes_other_ships_projectiles(self):
        """Only projectiles owned by the specific ship are counted."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=5, shots_hit=3)
        ship = _create_mock_ship([comp], total_shots_fired=5)
        other_ship = Mock()

        engine = _create_mock_engine([
            _create_mock_projectile(ship, alive=True),
            _create_mock_projectile(other_ship, alive=True),  # different owner
            _create_mock_projectile(other_ship, alive=True),
        ])

        scenario._collect_weapon_stats(ship, "attacker", engine=engine)

        assert scenario.results["attacker_in_flight"] == 1

    def test_zero_in_flight(self):
        """Zero in-flight when all projectiles have resolved."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=10, shots_hit=10)
        ship = _create_mock_ship([comp], total_shots_fired=10)

        engine = _create_mock_engine([])

        scenario._collect_weapon_stats(ship, "attacker", engine=engine)

        assert scenario.results["attacker_in_flight"] == 0
        assert scenario.results["attacker_resolved_shots"] == 10

    def test_resolved_hit_rate(self):
        """Resolved hit rate excludes in-flight from denominator."""
        scenario = _create_scenario_instance()
        comp = _create_mock_component("Railgun", ProjectileWeaponAbility, shots_fired=100, shots_hit=96)
        ship = _create_mock_ship([comp], total_shots_fired=100)

        engine = _create_mock_engine([
            _create_mock_projectile(ship, alive=True),
            _create_mock_projectile(ship, alive=True),
            _create_mock_projectile(ship, alive=True),
            _create_mock_projectile(ship, alive=True),
        ])

        scenario._collect_weapon_stats(ship, "attacker", engine=engine)

        # 100 shots - 4 in flight = 96 resolved, 96 hits = 100%
        assert scenario.results["attacker_resolved_shots"] == 96
        assert scenario.results["attacker_resolved_hits"] == 96
