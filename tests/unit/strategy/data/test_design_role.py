"""
Unit tests for the design role system.

Phase 2: Design roles are classification labels assigned at ship design time.
They drive auto-suggestion for fleet organization and UI grouping but have
no direct combat behavior effect.

TDD: Written before implementation.
"""

import pytest


# =============================================================================
# DesignRole Enum
# =============================================================================

class TestDesignRole:
    """Tests for DesignRole enum."""

    def test_all_starter_roles_exist(self):
        """DesignRole has all 10 starter roles."""
        from game.strategy.data.design_role import DesignRole

        expected = [
            'LINE_COMBATANT', 'FLEET_ESCORT', 'INTERCEPTOR',
            'ASSAULT_SHIP', 'MISSILE_PLATFORM', 'RAIDER',
            'CARRIER', 'SUPPORT_SHIP', 'SCOUT', 'COMMAND_SHIP',
        ]
        for role_name in expected:
            assert hasattr(DesignRole, role_name), f"Missing role: {role_name}"

    def test_roles_have_string_values(self):
        """Roles use lowercase string values for serialization."""
        from game.strategy.data.design_role import DesignRole

        assert DesignRole.LINE_COMBATANT.value == "line_combatant"
        assert DesignRole.CARRIER.value == "carrier"

    def test_serialization_round_trip(self):
        """DesignRole serializes to string and back."""
        from game.strategy.data.design_role import DesignRole

        for role in DesignRole:
            assert DesignRole(role.value) == role

    def test_roles_are_unique(self):
        """Each role has a distinct value."""
        from game.strategy.data.design_role import DesignRole

        values = [r.value for r in DesignRole]
        assert len(values) == len(set(values))


# =============================================================================
# Role Classifier
# =============================================================================

class TestRoleClassifier:
    """Tests for auto-classifying ship design role from component loadout."""

    def test_carrier_detected_by_tactical_fighter_launch(self):
        """Ship with TacticalFighterLaunch ability is classified as Carrier.

        PROJ-FMS-C audit Fix 1: legacy ``VehicleLaunch`` was deleted; the
        new launch abilities (``TacticalFighterLaunch`` /
        ``StrategicFighterLaunch``) are the carrier markers.
        """
        from game.strategy.data.design_role import DesignRole, classify_design_role

        abilities = {"TacticalFighterLaunch": True, "CombatPropulsion": True}
        role = classify_design_role(abilities=abilities, mass=8000)
        assert role == DesignRole.CARRIER

    def test_missile_platform_detected_by_seeker_weapons(self):
        """Ship with SeekerWeaponAbility and no beam/projectile is Missile Platform."""
        from game.strategy.data.design_role import DesignRole, classify_design_role

        abilities = {"SeekerWeaponAbility": True, "CombatPropulsion": True}
        role = classify_design_role(abilities=abilities, mass=8000)
        assert role == DesignRole.MISSILE_PLATFORM

    def test_support_ship_detected_by_repair_or_shipyard(self):
        """Ship with ShipRepair or SpaceShipyard is Support Ship."""
        from game.strategy.data.design_role import DesignRole, classify_design_role

        abilities = {"ShipRepair": True, "CombatPropulsion": True}
        role = classify_design_role(abilities=abilities, mass=8000)
        assert role == DesignRole.SUPPORT_SHIP

    def test_scout_detected_by_sensor_emphasis(self):
        """Ship with high sensor abilities and few weapons is Scout."""
        from game.strategy.data.design_role import DesignRole, classify_design_role

        abilities = {
            "SensorAbility": True,
            "ECMAbility": True,
            "CombatPropulsion": True,
        }
        role = classify_design_role(abilities=abilities, mass=1000)
        assert role == DesignRole.SCOUT

    def test_command_ship_detected_by_tactical_data_link(self):
        """Ship with CommandAndControl + TacticalDataLink is Command Ship."""
        from game.strategy.data.design_role import DesignRole, classify_design_role

        abilities = {
            "CommandAndControl": True,
            "TacticalDataLinkAbility": True,
            "CombatPropulsion": True,
        }
        role = classify_design_role(abilities=abilities, mass=16000)
        assert role == DesignRole.COMMAND_SHIP

    def test_line_combatant_heavy_with_weapons(self):
        """Heavy ship with weapons defaults to Line Combatant."""
        from game.strategy.data.design_role import DesignRole, classify_design_role

        abilities = {
            "BeamWeaponAbility": True,
            "ProjectileWeaponAbility": True,
            "ShieldProjection": True,
            "CombatPropulsion": True,
            "CommandAndControl": True,
        }
        role = classify_design_role(abilities=abilities, mass=32000)
        assert role == DesignRole.LINE_COMBATANT

    def test_fleet_escort_light_with_weapons(self):
        """Light ship with weapons is Fleet Escort."""
        from game.strategy.data.design_role import DesignRole, classify_design_role

        abilities = {
            "BeamWeaponAbility": True,
            "CombatPropulsion": True,
            "CommandAndControl": True,
        }
        role = classify_design_role(abilities=abilities, mass=1000)
        assert role == DesignRole.FLEET_ESCORT

    def test_empty_abilities_defaults_to_line_combatant(self):
        """Ship with no distinguishing abilities defaults to Line Combatant."""
        from game.strategy.data.design_role import DesignRole, classify_design_role

        role = classify_design_role(abilities={}, mass=8000)
        assert role == DesignRole.LINE_COMBATANT

    def test_new_carrier_ability_classifies_without_design_role_edit(self) -> None:
        """PROJ-429 Phase 2: a new ability tagged ``RoleTag.CARRIER`` in
        the unified registry classifies as ``DesignRole.CARRIER`` without
        any edit to ``design_role.py`` — the whole point of TD-07's role
        unification is that registry tagging is sufficient.

        Mechanism: temporarily register a fake carrier ability through
        the registry's internal index and verify ``classify_design_role``
        picks it up. We restore the registry after the test.
        """
        from game.strategy.data.design_role import DesignRole, classify_design_role
        from game.strategy.services import ability_metadata as am

        fake_name = "FooLaunchAbility"
        assert fake_name not in am._BY_NAME, "test setup: name must be unused"
        fake_meta = am.AbilityMetadata(
            name=fake_name,
            role_tags=frozenset({am.RoleTag.CARRIER}),
        )
        am._BY_NAME[fake_name] = fake_meta
        existing_carriers = am._BY_ROLE_TAG.get(am.RoleTag.CARRIER, frozenset())
        am._BY_ROLE_TAG[am.RoleTag.CARRIER] = existing_carriers | {fake_name}
        try:
            abilities = {fake_name: True}
            role = classify_design_role(abilities=abilities, mass=8000)
            assert role == DesignRole.CARRIER, (
                "classify_design_role must read carrier names from the "
                "unified AbilityMetadataRegistry, not a local frozenset."
            )
        finally:
            del am._BY_NAME[fake_name]
            am._BY_ROLE_TAG[am.RoleTag.CARRIER] = existing_carriers

    def test_classify_from_design_data(self):
        """classify_from_design_data extracts abilities and classifies."""
        from game.strategy.data.design_role import DesignRole, classify_from_design_data

        # Minimal design with a beam weapon component
        design_data = {
            "ship_class": "Cruiser",
            "vehicle_type": "Ship",
            "layers": {
                "CORE": [{"id": "bridge"}],
                "OUTER": [{"id": "laser_cannon"}],
            },
        }
        # Need a component registry that maps IDs to abilities
        component_registry = {
            "bridge": {
                "id": "bridge",
                "abilities": {"CommandAndControl": True},
                "mass": 50,
            },
            "laser_cannon": {
                "id": "laser_cannon",
                "abilities": {"BeamWeaponAbility": {"damage": 10, "range": 5000}},
                "mass": 100,
            },
        }

        role = classify_from_design_data(design_data, component_registry)
        assert role in (DesignRole.LINE_COMBATANT, DesignRole.FLEET_ESCORT)


# =============================================================================
# ShipInstance Role Integration
# =============================================================================

class TestShipInstanceRole:
    """Tests for design role on ShipInstance."""

    def test_ship_instance_has_design_role(self):
        """ShipInstance has a design_role field."""
        from game.strategy.data.ship_instance import ShipInstance

        ship = ShipInstance(
            instance_id="test-1",
            design_id="test_design",
            name="Test Ship",
            owner_id=0,
        )
        assert ship.design_role is None  # not yet classified

    def test_ship_instance_has_role_override(self):
        """ShipInstance has a role_override field."""
        from game.strategy.data.ship_instance import ShipInstance

        ship = ShipInstance(
            instance_id="test-1",
            design_id="test_design",
            name="Test Ship",
            owner_id=0,
        )
        assert ship.role_override is None

    def test_effective_role_uses_override_when_set(self):
        """effective_role returns role_override when set."""
        from game.strategy.data.ship_instance import ShipInstance
        from game.strategy.data.design_role import DesignRole

        ship = ShipInstance(
            instance_id="test-1",
            design_id="test_design",
            name="Test Ship",
            owner_id=0,
        )
        ship.design_role = DesignRole.LINE_COMBATANT.value
        ship.role_override = DesignRole.ASSAULT_SHIP.value

        assert ship.effective_role == DesignRole.ASSAULT_SHIP.value

    def test_effective_role_falls_back_to_design_role(self):
        """effective_role returns design_role when no override."""
        from game.strategy.data.ship_instance import ShipInstance
        from game.strategy.data.design_role import DesignRole

        ship = ShipInstance(
            instance_id="test-1",
            design_id="test_design",
            name="Test Ship",
            owner_id=0,
        )
        ship.design_role = DesignRole.CARRIER.value

        assert ship.effective_role == DesignRole.CARRIER.value

    def test_role_serialization_round_trip(self):
        """design_role and role_override survive serialization."""
        from game.strategy.data.ship_instance import ShipInstance
        from game.strategy.data.design_role import DesignRole

        ship = ShipInstance(
            instance_id="test-1",
            design_id="test_design",
            name="Test Ship",
            owner_id=0,
            design_data={"name": "Test", "ship_class": "Escort"},
        )
        ship.design_role = DesignRole.FLEET_ESCORT.value
        ship.role_override = DesignRole.INTERCEPTOR.value

        data = ship.to_dict()
        assert data.get("design_role") == "fleet_escort"
        assert data.get("role_override") == "interceptor"

        restored = ShipInstance.from_dict(data)
        assert restored.design_role == "fleet_escort"
        assert restored.role_override == "interceptor"
        assert restored.effective_role == "interceptor"

    def test_role_absent_from_save_dict(self) -> None:
        """When `design_role`/`role_override` keys are absent, both default to None."""
        from game.strategy.data.ship_instance import ShipInstance

        data = {
            "instance_id": "test-1",
            "design_id": "test_design",
            "name": "Test Ship",
            "owner_id": 0,
            "design_data": {},
            "components": {},
        }

        ship = ShipInstance.from_dict(data)
        assert ship.design_role is None
        assert ship.role_override is None
        assert ship.effective_role is None
