"""Warhead / Laserhead ability classes.

QA 2026-05-16 Obs 1 collapsed the per-size component variants into
single ``warhead`` / ``laserhead`` entries scaled by ``simple_size_mount``.
QA 2026-05-16 Obs 1b removed the ``RamTargetAbility`` / ``RamTarget``
gate entirely — ramming is now a universal tactical action through
``RamTargetResolver.set_ram_target``. This file pins:

  - Registry resolution (ability_name -> class)
  - Field round-trip from component data
  - ``damage_mult`` scaling on warheads
  - MRO so LaserheadAbility still passes BeamWeaponAbility detection
"""
from __future__ import annotations

import pytest

from game.simulation.components.abilities import (
    ABILITY_REGISTRY,
    BeamWeaponAbility,
    LaserheadAbility,
    WarheadAbility,
)
from game.simulation.components.component_loader import create_component


class TestRegistration:
    def test_warhead_registered(self):
        assert ABILITY_REGISTRY["Warhead"] is WarheadAbility

    def test_laserhead_registered(self):
        assert ABILITY_REGISTRY["Laserhead"] is LaserheadAbility

    def test_ram_target_no_longer_registered(self):
        """QA 2026-05-16 Obs 1b: the ``RamTarget`` ability gate was
        removed when ramming became a universal tactical action."""
        assert "RamTarget" not in ABILITY_REGISTRY


class TestWarheadAbility:
    def test_field_roundtrip_dict(self, fresh_registries):
        """Consolidated component (Round 4 QA Obs 1): single ``warhead``
        carries the small-tier base damage; size tiers are emitted via
        ``simple_size_mount`` scaling."""
        comp = create_component("warhead", registries=fresh_registries)
        assert comp is not None
        warheads = [a for a in comp.ability_instances if isinstance(a, WarheadAbility)]
        assert len(warheads) == 1
        assert warheads[0].damage == 50.0

    def test_damage_scales_with_damage_mult(self, fresh_registries):
        """QA Obs 1 (2026-05-16): warhead damage must scale via
        ``damage_mult`` so ``simple_size_mount`` (the canonical size
        scaler) can produce the old small/medium/large tiers from a
        single component definition.

        Mirrors how ``WeaponAbility`` / ``BeamWeaponAbility`` already
        respond to ``damage_mult`` on size mounts."""
        comp = create_component("warhead", registries=fresh_registries)
        assert comp is not None
        warheads = [a for a in comp.ability_instances if isinstance(a, WarheadAbility)]
        wh = warheads[0]
        assert wh.damage == 50.0  # baseline

        # Simulate a size mount applying damage_mult = 4.0 (medium tier).
        comp.stats["damage_mult"] = 4.0
        wh.recalculate()
        assert wh.damage == 200.0

        # damage_mult = 16.0 (large tier).
        comp.stats["damage_mult"] = 16.0
        wh.recalculate()
        assert wh.damage == 800.0


class TestLaserheadAbility:
    """Consolidated to a single ``laserhead`` component (QA Obs 1,
    2026-05-16); size tiers come from ``simple_size_mount`` scaling
    inherited through ``BeamWeaponAbility``."""

    def test_isinstance_beam_weapon_ability(self, fresh_registries):
        """Critical: LaserheadAbility must remain isinstance of
        BeamWeaponAbility so the existing weapon-family detection at
        weapon_registry.py:78-94 still classifies it as the beam family."""
        comp = create_component("laserhead", registries=fresh_registries)
        assert comp is not None
        lasers = [
            a for a in comp.ability_instances if isinstance(a, LaserheadAbility)
        ]
        assert len(lasers) == 1
        assert isinstance(lasers[0], BeamWeaponAbility)

    def test_has_ability_beam_weapon_ability(self, fresh_registries):
        comp = create_component("laserhead", registries=fresh_registries)
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
        comp = create_component("laserhead", registries=fresh_registries)
        lasers = [
            a for a in comp.ability_instances if isinstance(a, LaserheadAbility)
        ]
        assert lasers[0].consume_on_fire is True

    def test_beam_attributes_inherited(self, fresh_registries):
        comp = create_component("laserhead", registries=fresh_registries)
        lasers = [
            a for a in comp.ability_instances if isinstance(a, LaserheadAbility)
        ]
        l = lasers[0]
        # damage / range parsed via WeaponAbility path — baseline values.
        assert l.damage == 30.0
        assert l.range == 600.0
        # accuracy comes from BeamWeaponAbility
        assert l.base_accuracy == 1.0
        # sigmoid hit-chance callable at zero distance
        hc = l.calculate_hit_chance(0.0)
        assert 0.0 <= hc <= 1.0


class TestRamTargetRemoval:
    """QA 2026-05-16 Obs 1b: ``RamTargetAbility`` and the
    ``ram_target_module`` component were deleted when ramming became
    a universal tactical action."""

    def test_ram_target_module_no_longer_loadable(self, fresh_registries):
        comp = create_component("ram_target_module", registries=fresh_registries)
        assert comp is None
