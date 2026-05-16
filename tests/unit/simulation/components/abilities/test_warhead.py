"""PROJ-FMS-A Phase 2: Warhead / Laserhead / RamTarget ability classes.

These are data-bearing skeletons. Behavior is added in PROJ-FMS-B; this
file pins:
  - Registry resolution (ability_name -> class)
  - Field round-trip from component data
  - MRO so LaserheadAbility still passes BeamWeaponAbility detection
"""
from __future__ import annotations

import pytest

from game.simulation.components.abilities import (
    ABILITY_REGISTRY,
    BeamWeaponAbility,
    LaserheadAbility,
    RamTargetAbility,
    WarheadAbility,
)
from game.simulation.components.component_loader import create_component


class TestRegistration:
    def test_warhead_registered(self):
        assert ABILITY_REGISTRY["Warhead"] is WarheadAbility

    def test_laserhead_registered(self):
        assert ABILITY_REGISTRY["Laserhead"] is LaserheadAbility

    def test_ram_target_registered(self):
        assert ABILITY_REGISTRY["RamTarget"] is RamTargetAbility


class TestWarheadAbility:
    def test_field_roundtrip_dict(self, fresh_registries):
        comp = create_component("warhead_medium", registries=fresh_registries)
        assert comp is not None
        warheads = [a for a in comp.ability_instances if isinstance(a, WarheadAbility)]
        assert len(warheads) == 1
        assert warheads[0].damage == 200.0

    def test_field_roundtrip_small(self, fresh_registries):
        comp = create_component("warhead_small", registries=fresh_registries)
        assert comp is not None
        warheads = [a for a in comp.ability_instances if isinstance(a, WarheadAbility)]
        assert warheads[0].damage == 50.0

    def test_field_roundtrip_large(self, fresh_registries):
        comp = create_component("warhead_large", registries=fresh_registries)
        assert comp is not None
        warheads = [a for a in comp.ability_instances if isinstance(a, WarheadAbility)]
        assert warheads[0].damage == 800.0


class TestLaserheadAbility:
    def test_isinstance_beam_weapon_ability(self, fresh_registries):
        """Critical: LaserheadAbility must remain isinstance of
        BeamWeaponAbility so the existing weapon-family detection at
        weapon_registry.py:78-94 still classifies it as the beam family."""
        comp = create_component("laserhead_small", registries=fresh_registries)
        assert comp is not None
        lasers = [
            a for a in comp.ability_instances if isinstance(a, LaserheadAbility)
        ]
        assert len(lasers) == 1
        assert isinstance(lasers[0], BeamWeaponAbility)

    def test_has_ability_beam_weapon_ability(self, fresh_registries):
        comp = create_component("laserhead_medium", registries=fresh_registries)
        assert comp is not None
        # `has_ability` uses class-name strings; the bound check is what
        # `weapon_registry.py` queries — verify both names resolve.
        assert comp.has_ability("Laserhead")
        # The instance is also a BeamWeaponAbility (MRO check, not key).
        lasers = [
            a for a in comp.ability_instances if isinstance(a, LaserheadAbility)
        ]
        assert any(isinstance(a, BeamWeaponAbility) for a in lasers)

    def test_consume_on_fire_default_true(self, fresh_registries):
        comp = create_component("laserhead_small", registries=fresh_registries)
        lasers = [
            a for a in comp.ability_instances if isinstance(a, LaserheadAbility)
        ]
        assert lasers[0].consume_on_fire is True

    def test_beam_attributes_inherited(self, fresh_registries):
        comp = create_component("laserhead_medium", registries=fresh_registries)
        lasers = [
            a for a in comp.ability_instances if isinstance(a, LaserheadAbility)
        ]
        l = lasers[0]
        # damage / range parsed via WeaponAbility path
        assert l.damage == 120.0
        assert l.range == 900.0
        # accuracy comes from BeamWeaponAbility
        assert l.base_accuracy == 1.0
        # sigmoid hit-chance callable at zero distance
        hc = l.calculate_hit_chance(0.0)
        assert 0.0 <= hc <= 1.0


class TestRamTargetAbility:
    def test_instantiation(self, fresh_registries):
        comp = create_component("ram_target_module", registries=fresh_registries)
        assert comp is not None
        rams = [a for a in comp.ability_instances if isinstance(a, RamTargetAbility)]
        assert len(rams) == 1
        # Runtime state defaults to None — combat engine assigns later.
        assert rams[0].target_id is None
