"""PROJ-FMS-A Phase 1: Mine vehicle classes + Mine_Standard layer + new components.

Verifies data definitions only — no behavior. The four allowed-via-ability
components (Warhead/Laserhead/SmallTargetingSensor/Hull) must validate inside
``Mine_Standard``; everything else must be rejected by the layer whitelist.
"""
from __future__ import annotations

import pytest

from game.core.constants import LayerType
from game.simulation.entities.ship import Ship
from game.simulation.components.component_loader import create_component


MINE_CLASSES = ("Mine (Small)", "Mine (Medium)", "Mine (Large)", "Mine (Heavy)")


class TestMineVehicleClasses:
    def test_mine_classes_loaded(self, fresh_registries):
        for name in MINE_CLASSES:
            assert name in fresh_registries.vehicle_classes, name
            cls_def = fresh_registries.vehicle_classes[name]
            assert cls_def["type"] == "Mine"
            assert cls_def["layer_config"] == "Mine_Standard"
            assert "signature_bonus" in cls_def

    def test_mine_hulls_loaded(self, fresh_registries):
        comps = fresh_registries.components
        for hid in ("hull_mine_small", "hull_mine_medium",
                    "hull_mine_large", "hull_mine_heavy"):
            assert hid in comps, hid

    def test_warhead_components_loaded(self, fresh_registries):
        comps = fresh_registries.components
        for cid in ("warhead_small", "warhead_medium", "warhead_large"):
            assert cid in comps
            assert "Mine" in comps[cid].allowed_vehicle_types
            assert "Fighter" in comps[cid].allowed_vehicle_types

    def test_laserhead_components_loaded(self, fresh_registries):
        comps = fresh_registries.components
        for cid in ("laserhead_small", "laserhead_medium", "laserhead_large"):
            assert cid in comps
            assert comps[cid].allowed_vehicle_types == ["Mine"]

    def test_small_targeting_sensor_has_no_command_control(self, fresh_registries):
        comps = fresh_registries.components
        sensor = comps["small_targeting_sensor"]
        ab = sensor.data.get("abilities", {})
        assert "RequiresCommandAndControl" not in ab
        assert "ToHitAttackModifier" in ab

    def test_mini_sensor_still_requires_command_control(self, fresh_registries):
        comps = fresh_registries.components
        mini = comps["mini_sensor"]
        ab = mini.data.get("abilities", {})
        assert ab.get("RequiresCommandAndControl") is True

    def test_ram_target_component_loaded(self, fresh_registries):
        comps = fresh_registries.components
        rt = comps["ram_target_module"]
        assert set(rt.allowed_vehicle_types) >= {"Fighter", "Ship"}
        assert "RamTarget" in rt.data.get("abilities", {})


class TestMineLayerValidation:
    """The Mine_Standard layer must whitelist exactly the four ability families."""

    def _build_mine(self, fresh_registries, ship_class: str = "Mine (Medium)") -> Ship:
        return Ship(
            "Test Mine", 0, 0, (255, 255, 255),
            ship_class=ship_class,
            registries=fresh_registries,
        )

    def test_warhead_allowed_in_mine_core(self, fresh_registries):
        mine = self._build_mine(fresh_registries)
        warhead = create_component("warhead_small", registries=fresh_registries)
        assert warhead is not None
        assert mine.add_component(warhead, LayerType.CORE), (
            "Warhead component must be allowed in Mine_Standard CORE")

    def test_hull_allowed_in_mine_core(self, fresh_registries):
        mine = self._build_mine(fresh_registries)
        hull = create_component("hull_mine_medium", registries=fresh_registries)
        assert hull is not None
        assert mine.add_component(hull, LayerType.CORE)

    def test_small_targeting_sensor_allowed_in_mine_core(self, fresh_registries):
        mine = self._build_mine(fresh_registries)
        sensor = create_component("small_targeting_sensor", registries=fresh_registries)
        assert sensor is not None
        assert mine.add_component(sensor, LayerType.CORE)

    def test_laserhead_allowed_in_mine_core(self, fresh_registries):
        mine = self._build_mine(fresh_registries, "Mine (Large)")
        laser = create_component("laserhead_small", registries=fresh_registries)
        assert laser is not None
        assert mine.add_component(laser, LayerType.CORE)

    def test_engine_rejected_in_mine_core(self, fresh_registries):
        """A regular engine has no Warhead/Laserhead/StructuralIntegrity/ToHit
        ability and is also not 'allowed' on type=Mine — must fail."""
        mine = self._build_mine(fresh_registries)
        # mini_engine has thrust ability + Fighter-only — verify rejection.
        engine = create_component("mini_engine", registries=fresh_registries)
        assert engine is not None
        assert not mine.add_component(engine, LayerType.CORE)
