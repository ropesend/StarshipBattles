"""
Unit tests for the design_role registry — production data + registry behavior.

PROJ-278 Phase 2 migration: previously tested `DesignRoleRegistry` (deleted)
+ its custom API. Now tests the unified `RoleRegistry` instance returned by
`get_default_design_role_registry()` (which loads `data/design_roles.json`).
"""

import pytest

from game.strategy.data.design_role_registry import (
    get_default_design_role_registry,
    reset_default_design_role_registry,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    """Each test starts with a fresh module-level registry."""
    reset_default_design_role_registry()
    yield
    reset_default_design_role_registry()


class TestDesignRoleRegistryLoading:
    """Tests for loading role definitions from the production data file."""

    def test_registry_loads_from_data_file(self):
        """The default registry loads roles from data/design_roles.json."""
        registry = get_default_design_role_registry()
        assert len(registry.all()) > 0

    def test_all_expected_roles_present(self):
        """All starter roles are present in the data file."""
        registry = get_default_design_role_registry()
        all_ids = {r.id for r in registry.all()}

        expected = [
            "general_purpose", "line_combatant", "fleet_escort",
            "interceptor", "carrier", "support_ship", "scout",
            "command_ship", "resource_harvester", "defensive_platform",
            "colony_pod",
        ]
        for role_id in expected:
            assert role_id in all_ids, f"Missing role: {role_id}"


class TestVehicleTypeFiltering:
    """Tests for filtering roles by vehicle type."""

    def test_ship_gets_combat_roles(self):
        """Ship vehicle type includes combat roles."""
        registry = get_default_design_role_registry()
        roles = registry.get_roles_for_vehicle_type("Ship")
        role_ids = {r.id for r in roles}

        assert "line_combatant" in role_ids
        assert "fleet_escort" in role_ids
        assert "general_purpose" in role_ids

    def test_planetary_complex_gets_complex_roles(self):
        """Planetary Complex includes complex-specific roles."""
        registry = get_default_design_role_registry()
        roles = registry.get_roles_for_vehicle_type("Planetary Complex")
        role_ids = {r.id for r in roles}

        assert "resource_harvester" in role_ids
        assert "planetary_modifier" in role_ids
        assert "general_purpose" in role_ids

    def test_planetary_complex_excludes_ship_only_roles(self):
        """Planetary Complex does not include ship-only roles."""
        registry = get_default_design_role_registry()
        roles = registry.get_roles_for_vehicle_type("Planetary Complex")
        role_ids = {r.id for r in roles}

        assert "interceptor" not in role_ids
        assert "assault_ship" not in role_ids
        assert "raider" not in role_ids

    def test_fighter_gets_applicable_roles(self):
        """Fighter vehicle type gets appropriate roles."""
        registry = get_default_design_role_registry()
        roles = registry.get_roles_for_vehicle_type("Fighter")
        role_ids = {r.id for r in roles}

        assert "interceptor" in role_ids
        assert "fleet_escort" in role_ids
        assert "general_purpose" in role_ids

    def test_drop_pod_gets_pod_roles(self):
        """Drop Pod vehicle type includes pod-specific roles."""
        registry = get_default_design_role_registry()
        roles = registry.get_roles_for_vehicle_type("Drop Pod")
        role_ids = {r.id for r in roles}

        assert "colony_pod" in role_ids
        assert "general_purpose" in role_ids

    def test_roles_sorted_by_display_name(self):
        """Returned roles are sorted alphabetically by display_name."""
        registry = get_default_design_role_registry()
        roles = registry.get_roles_for_vehicle_type("Ship")
        names = [r.display_name for r in roles]

        assert names == sorted(names)


class TestNameIdLookup:
    """Tests for name/ID conversion via the new RoleRegistry API."""

    def test_get_role_display_name(self):
        """registry.get(id).display_name returns the display name."""
        registry = get_default_design_role_registry()

        assert registry.get("line_combatant").display_name == "Line Combatant"
        assert registry.get("carrier").display_name == "Carrier"

    def test_get_unknown_role_raises(self):
        """registry.get(missing_id) raises KeyError (dict-like API)."""
        registry = get_default_design_role_registry()
        with pytest.raises(KeyError):
            registry.get("nonexistent")

    def test_find_role_id_by_display_name(self):
        """Reverse lookup pattern: scan registry.all() for matching display_name."""
        registry = get_default_design_role_registry()

        line = next((r for r in registry.all() if r.display_name == "Line Combatant"), None)
        assert line is not None and line.id == "line_combatant"

        carrier = next((r for r in registry.all() if r.display_name == "Carrier"), None)
        assert carrier is not None and carrier.id == "carrier"

    def test_find_role_id_by_display_name_not_found(self):
        """Reverse lookup returns None for unknown display names."""
        registry = get_default_design_role_registry()

        result = next(
            (r.id for r in registry.all() if r.display_name == "Nonexistent Role"),
            None,
        )
        assert result is None


class TestShipDesignRoleSerialization:
    """Tests for design_role field on Ship serialization (UNCHANGED by PROJ-278)."""

    def test_ship_has_design_role_field(self, fresh_registries):
        """Ship has a design_role field defaulting to general_purpose."""
        from game.simulation.entities.ship import Ship

        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries)
        assert ship.design_role == "general_purpose"

    def test_design_role_serialized_in_to_dict(self, fresh_registries):
        """Ship.to_dict() includes design_role."""
        from game.simulation.entities.ship import Ship
        from game.simulation.entities.ship_serialization import ShipSerializer

        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries)
        ship.design_role = "carrier"

        data = ShipSerializer.to_dict(ship)
        assert data["design_role"] == "carrier"

    def test_design_role_loaded_from_dict(self, fresh_registries):
        """Ship.from_dict() restores design_role."""
        from game.simulation.entities.ship_serialization import ShipSerializer

        data = {
            "name": "Test",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "theme_id": "Federation",
            "team_id": 0,
            "color": [255, 255, 255],
            "movement_policy": "kite_max",
            "design_role": "missile_platform",
            "layers": {},
            "resources": {"fuel": 0, "energy": 0, "ammo": 0},
        }

        ship = ShipSerializer.from_dict(data, registries=fresh_registries)
        assert ship.design_role == "missile_platform"

    def test_design_role_defaults_for_old_saves(self, fresh_registries):
        """Old saves without design_role default to general_purpose."""
        from game.simulation.entities.ship_serialization import ShipSerializer

        data = {
            "name": "OldShip",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "theme_id": "Federation",
            "team_id": 0,
            "color": [255, 255, 255],
            "movement_policy": "kite_max",
            "layers": {},
            "resources": {"fuel": 0, "energy": 0, "ammo": 0},
        }

        ship = ShipSerializer.from_dict(data, registries=fresh_registries)
        assert ship.design_role == "general_purpose"
