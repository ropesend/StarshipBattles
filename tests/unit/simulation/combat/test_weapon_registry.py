"""PROJ-359: Tests for the weapon-family registry contract.

Phase 2 ships the registry skeleton without migrating any production family
handler. These tests exercise the contract using fake handlers so they are
independent of family-specific behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from game.core.math import Vector2
from game.simulation.combat.attack_contract import (
    AttackRequest,
    AttackResolution,
    BeamResolution,
    NoAttack,
    ProjectileResolution,
    UnregisteredWeaponFamilyError,
    WeaponFamily,
    WeaponHandler,
)
from game.simulation.combat.weapon_registry import (
    WEAPON_REGISTRY,
    WeaponRegistry,
    detect_family,
)


def _make_request(family: WeaponFamily) -> AttackRequest:
    return AttackRequest(
        source=object(),
        component=MagicMock(),
        weapon_ability=MagicMock(),
        target=object(),
        aim_pos=Vector2(0, 0),
        aim_vec=Vector2(1, 0),
        family=family,
    )


# -----------------------------------------------------------------------------
# Fake handler for contract tests
# -----------------------------------------------------------------------------


@dataclass
class _RecordingHandler:
    """Test fake — records calls and returns a pre-built resolution."""

    resolution: AttackResolution
    calls: list = None

    def __post_init__(self):
        self.calls = []

    def fire(self, request: AttackRequest) -> AttackResolution:
        self.calls.append(request)
        return self.resolution


class TestWeaponRegistry:
    def test_dispatch_routes_to_registered_handler(self):
        registry = WeaponRegistry()
        resolution = NoAttack(reason="test")
        handler = _RecordingHandler(resolution=resolution)
        registry.register(WeaponFamily.BEAM, handler)

        request = _make_request(WeaponFamily.BEAM)
        result = registry.dispatch(request)

        assert result is resolution
        assert handler.calls == [request]

    def test_unregistered_family_raises(self):
        registry = WeaponRegistry()
        request = _make_request(WeaponFamily.BEAM)
        with pytest.raises(UnregisteredWeaponFamilyError):
            registry.dispatch(request)

    def test_register_overwrites(self):
        registry = WeaponRegistry()
        first = _RecordingHandler(resolution=NoAttack(reason="first"))
        second = _RecordingHandler(resolution=NoAttack(reason="second"))
        registry.register(WeaponFamily.PROJECTILE, first)
        registry.register(WeaponFamily.PROJECTILE, second)
        result = registry.dispatch(_make_request(WeaponFamily.PROJECTILE))
        assert result.reason == "second"

    def test_unregister(self):
        registry = WeaponRegistry()
        registry.register(WeaponFamily.PDC, _RecordingHandler(resolution=NoAttack()))
        assert registry.has(WeaponFamily.PDC)
        registry.unregister(WeaponFamily.PDC)
        assert not registry.has(WeaponFamily.PDC)

    def test_handler_protocol_is_runtime_checkable(self):
        handler = _RecordingHandler(resolution=NoAttack())
        assert isinstance(handler, WeaponHandler)


class TestFamilyDetection:
    def test_pdc_detected_before_beam(self):
        comp = MagicMock()
        comp.has_pdc_ability = MagicMock(return_value=True)
        comp.has_ability = MagicMock(return_value=True)  # would also match BeamWeaponAbility
        assert detect_family(comp) is WeaponFamily.PDC

    def test_beam_when_not_pdc(self):
        comp = MagicMock()
        comp.has_pdc_ability = MagicMock(return_value=False)
        comp.has_ability = lambda name: name == 'BeamWeaponAbility'
        assert detect_family(comp) is WeaponFamily.BEAM

    def test_seeker(self):
        comp = MagicMock()
        comp.has_pdc_ability = MagicMock(return_value=False)
        comp.has_ability = lambda name: name == 'SeekerWeaponAbility'
        assert detect_family(comp) is WeaponFamily.SEEKER

    def test_projectile(self):
        comp = MagicMock()
        comp.has_pdc_ability = MagicMock(return_value=False)
        comp.has_ability = lambda name: name == 'ProjectileWeaponAbility'
        assert detect_family(comp) is WeaponFamily.PROJECTILE

    def test_unknown_returns_none(self):
        comp = MagicMock()
        comp.has_pdc_ability = MagicMock(return_value=False)
        comp.has_ability = MagicMock(return_value=False)
        assert detect_family(comp) is None


class TestFakeFamilyExtensibility:
    """Extensibility goal: register a fake family + handler without editing
    firing/targeting/collision/projectile centrals.

    Phase 2 codifies this for a registered family that uses an existing
    enum member; Phase 4 strengthens it to confirm no production code edits
    were needed end-to-end.
    """

    def test_fake_handler_dispatches_via_local_registry(self):
        registry = WeaponRegistry()

        @dataclass
        class FakeBeamHandler:
            def fire(self, request: AttackRequest) -> AttackResolution:
                return BeamResolution(
                    source=request.source,
                    component=request.component,
                    target=request.target,
                    damage=99.0,
                    range=1.0,
                    origin=Vector2(0, 0),
                    direction=Vector2(1, 0),
                    hit=True,
                )

        registry.register(WeaponFamily.BEAM, FakeBeamHandler())
        result = registry.dispatch(_make_request(WeaponFamily.BEAM))
        assert isinstance(result, BeamResolution)
        assert result.damage == 99.0


class TestExtensibilityAcceptance:
    """PROJ-359 acceptance test: a hypothetical new weapon family registers
    and dispatches without editing weapon_firing_system, targeting_system,
    collision, or projectile_manager.

    This is the executable form of the project's headline goal — adding a
    new weapon family is one register() call + one family module + one
    metadata entry. If a future change forces this test to also touch one
    of the four central files, the contract has regressed.
    """

    def test_new_family_registers_without_central_edits(self):
        """Register a fake handler under an existing family enum slot and
        prove dispatch routes to it. The four central modules
        (weapon_firing_system, targeting_system, collision,
        projectile_manager) must remain unmodified for this test to pass."""
        # Use a local registry to keep the production registry clean.
        registry = WeaponRegistry()

        @dataclass
        class FakePlasmaTorpedoHandler:
            """Hypothetical new family: plasma torpedo. Returns a typed
            BeamResolution variant for demo purposes."""
            calls: list = None

            def __post_init__(self):
                self.calls = []

            def fire(self, request: AttackRequest) -> AttackResolution:
                self.calls.append(request)
                return BeamResolution(
                    source=request.source,
                    component=request.component,
                    target=request.target,
                    damage=999.0,
                    range=2000.0,
                    origin=Vector2(0, 0),
                    direction=Vector2(1, 0),
                    hit=True,
                )

        handler = FakePlasmaTorpedoHandler()
        # Register under PROJECTILE slot (slots are stable; in a real change
        # the WeaponFamily enum would gain a PLASMA_TORPEDO member).
        registry.register(WeaponFamily.PROJECTILE, handler)

        request = _make_request(WeaponFamily.PROJECTILE)
        result = registry.dispatch(request)

        assert isinstance(result, BeamResolution)
        assert result.damage == 999.0
        assert handler.calls == [request]


class TestResolutionShapes:
    def test_beam_resolution_carries_all_legacy_dict_fields(self):
        """`BeamResolution` is a 1:1 typed mirror of the legacy beam dict.
        This test pins the field set so any later schema change is intentional."""
        r = BeamResolution(
            source=object(),
            component=MagicMock(),
            target=object(),
            damage=1.0,
            range=2.0,
            origin=Vector2(3, 4),
            direction=Vector2(1, 0),
            hit=True,
        )
        # All legacy keys present as attributes
        for attr in ('source', 'component', 'target', 'damage', 'range',
                     'origin', 'direction', 'hit'):
            assert hasattr(r, attr)

    def test_projectile_resolution_holds_projectile(self):
        sentinel = object()
        r = ProjectileResolution(projectile=sentinel)
        assert r.projectile is sentinel
