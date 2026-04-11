"""
Unit tests for DesignRoleRegistry — data-driven role definitions.

Tests loading from JSON, vehicle type filtering, and name/ID lookup.
"""

import pytest


class TestDesignRoleRegistryLoading:
    """Tests for loading role definitions from JSON."""

    def test_registry_loads_from_data_file(self):
        """DesignRoleRegistry loads roles from data/design_roles.json."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        assert len(registry.get_all_role_ids()) > 0

    def test_all_expected_roles_present(self):
        """All starter roles are present in the data file."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        expected = [
            "general_purpose", "line_combatant", "fleet_escort",
            "interceptor", "carrier", "support_ship", "scout",
            "command_ship", "resource_harvester", "defensive_platform",
            "colony_pod",
        ]
        all_ids = registry.get_all_role_ids()
        for role_id in expected:
            assert role_id in all_ids, f"Missing role: {role_id}"


class TestVehicleTypeFiltering:
    """Tests for filtering roles by vehicle type."""

    def test_ship_gets_combat_roles(self):
        """Ship vehicle type includes combat roles."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        roles = registry.get_roles_for_vehicle_type("Ship")
        role_ids = {r["id"] for r in roles}

        assert "line_combatant" in role_ids
        assert "fleet_escort" in role_ids
        assert "general_purpose" in role_ids

    def test_planetary_complex_gets_complex_roles(self):
        """Planetary Complex includes complex-specific roles."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        roles = registry.get_roles_for_vehicle_type("Planetary Complex")
        role_ids = {r["id"] for r in roles}

        assert "resource_harvester" in role_ids
        assert "planetary_modifier" in role_ids
        assert "general_purpose" in role_ids

    def test_planetary_complex_excludes_ship_only_roles(self):
        """Planetary Complex does not include ship-only roles."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        roles = registry.get_roles_for_vehicle_type("Planetary Complex")
        role_ids = {r["id"] for r in roles}

        assert "interceptor" not in role_ids
        assert "assault_ship" not in role_ids
        assert "raider" not in role_ids

    def test_fighter_gets_applicable_roles(self):
        """Fighter vehicle type gets appropriate roles."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        roles = registry.get_roles_for_vehicle_type("Fighter")
        role_ids = {r["id"] for r in roles}

        assert "interceptor" in role_ids
        assert "fleet_escort" in role_ids
        assert "general_purpose" in role_ids

    def test_drop_pod_gets_pod_roles(self):
        """Drop Pod vehicle type includes pod-specific roles."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        roles = registry.get_roles_for_vehicle_type("Drop Pod")
        role_ids = {r["id"] for r in roles}

        assert "colony_pod" in role_ids
        assert "general_purpose" in role_ids

    def test_roles_sorted_by_name(self):
        """Returned roles are sorted alphabetically by name."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        roles = registry.get_roles_for_vehicle_type("Ship")
        names = [r["name"] for r in roles]

        assert names == sorted(names)


class TestNameIdLookup:
    """Tests for name/ID conversion."""

    def test_get_role_name(self):
        """get_role_name returns display name for a role ID."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        assert registry.get_role_name("line_combatant") == "Line Combatant"
        assert registry.get_role_name("carrier") == "Carrier"

    def test_get_role_name_unknown(self):
        """get_role_name returns the ID itself for unknown roles."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        assert registry.get_role_name("nonexistent") == "nonexistent"

    def test_get_role_id_by_name(self):
        """get_role_id_by_name finds ID from display name."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        assert registry.get_role_id_by_name("Line Combatant") == "line_combatant"
        assert registry.get_role_id_by_name("Carrier") == "carrier"

    def test_get_role_id_by_name_not_found(self):
        """get_role_id_by_name returns None for unknown names."""
        from game.strategy.data.design_role import DesignRoleRegistry

        registry = DesignRoleRegistry()
        registry.load()

        assert registry.get_role_id_by_name("Nonexistent Role") is None


class TestShipDesignRoleSerialization:
    """Tests for design_role field on Ship serialization."""

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
            "ai_strategy": "standard_ranged",
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
            "ai_strategy": "standard_ranged",
            "layers": {},
            "resources": {"fuel": 0, "energy": 0, "ammo": 0},
        }

        ship = ShipSerializer.from_dict(data, registries=fresh_registries)
        assert ship.design_role == "general_purpose"
