"""Tests for PlanetModifierEffectEngine — gravity/radiation effect application."""
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from game.strategy.engine.planet_modifier_effect_engine import PlanetModifierEffectEngine
from game.strategy.data.component_activation_state import (
    ComponentActivationState, ActivationPhase,
)


@dataclass
class MockFacility:
    design_data: Dict[str, Any] = field(default_factory=dict)
    is_operational: bool = True
    component_states: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockPlanet:
    name: str = "Test"
    surface_gravity: float = 9.8
    gravity_target: Optional[float] = None
    gravity_original: Optional[float] = None
    radiation_shielding: float = 0.0
    radiation_shielding_target: Optional[float] = None
    facilities: List = field(default_factory=list)


@dataclass
class MockEmpire:
    id: int = 0
    colonies: List = field(default_factory=list)


def _make_active_gravity_state():
    return ComponentActivationState(
        phase=ActivationPhase.ACTIVE,
        ability_name='GravityModifier',
        energy_drain_rate=30.0,
    )


def _make_inactive_gravity_state():
    return ComponentActivationState(
        phase=ActivationPhase.INACTIVE,
        ability_name='GravityModifier',
    )


def _make_active_radiation_state():
    return ComponentActivationState(
        phase=ActivationPhase.ACTIVE,
        ability_name='RadiationShield',
        energy_drain_rate=20.0,
    )


class TestGravityModifierEffect:

    def test_apply_gravity_when_active(self):
        """Should change gravity to target when modifier is ACTIVE."""
        facility = MockFacility(
            component_states={"CORE:0:gravity_modifier": _make_active_gravity_state()}
        )
        planet = MockPlanet(
            surface_gravity=9.8,
            gravity_target=5.0,
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.surface_gravity == pytest.approx(5.0)
        assert planet.gravity_original == pytest.approx(9.8)

    def test_no_change_when_inactive(self):
        """Should not change gravity when modifier is INACTIVE."""
        facility = MockFacility(
            component_states={"CORE:0:gravity_modifier": _make_inactive_gravity_state()}
        )
        planet = MockPlanet(
            surface_gravity=9.8,
            gravity_target=5.0,
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.surface_gravity == pytest.approx(9.8)
        assert planet.gravity_original is None

    def test_revert_gravity_when_deactivated(self):
        """Should revert gravity when modifier transitions to INACTIVE."""
        facility = MockFacility(
            component_states={"CORE:0:gravity_modifier": _make_inactive_gravity_state()}
        )
        planet = MockPlanet(
            surface_gravity=5.0,  # Currently modified
            gravity_target=5.0,
            gravity_original=9.8,  # Original value stored
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.surface_gravity == pytest.approx(9.8)
        assert planet.gravity_original is None

    def test_revert_gravity_when_facility_destroyed(self):
        """Should revert gravity when no active GravityModifier exists."""
        planet = MockPlanet(
            surface_gravity=5.0,  # Currently modified
            gravity_target=5.0,
            gravity_original=9.8,  # Original stored but facility gone
            facilities=[]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.surface_gravity == pytest.approx(9.8)
        assert planet.gravity_original is None

    def test_no_target_no_apply(self):
        """Should not apply if gravity_target is None."""
        facility = MockFacility(
            component_states={"CORE:0:gravity_modifier": _make_active_gravity_state()}
        )
        planet = MockPlanet(
            surface_gravity=9.8,
            gravity_target=None,
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.surface_gravity == pytest.approx(9.8)
        assert planet.gravity_original is None

    def test_idempotent_when_already_applied(self):
        """Repeated calls when already ACTIVE should not re-store original."""
        facility = MockFacility(
            component_states={"CORE:0:gravity_modifier": _make_active_gravity_state()}
        )
        planet = MockPlanet(
            surface_gravity=5.0,  # Already modified
            gravity_target=5.0,
            gravity_original=9.8,  # Already stored
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        # Should keep original as 9.8, not overwrite with 5.0
        assert planet.gravity_original == pytest.approx(9.8)
        assert planet.surface_gravity == pytest.approx(5.0)


class TestRadiationShieldEffect:

    def test_apply_shielding_when_active(self):
        """Should set radiation_shielding when RadiationShield is ACTIVE."""
        facility = MockFacility(
            component_states={"CORE:0:radiation_shield": _make_active_radiation_state()}
        )
        planet = MockPlanet(
            radiation_shielding=0.0,
            radiation_shielding_target=1.5,
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.radiation_shielding == pytest.approx(1.5)

    def test_revert_shielding_when_inactive(self):
        """Should revert shielding to 0 when no active RadiationShield."""
        facility = MockFacility(
            component_states={"CORE:0:radiation_shield": ComponentActivationState(
                phase=ActivationPhase.INACTIVE,
                ability_name='RadiationShield',
            )}
        )
        planet = MockPlanet(
            radiation_shielding=1.5,  # Currently shielded
            radiation_shielding_target=1.5,
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.radiation_shielding == pytest.approx(0.0)

    def test_revert_shielding_when_facility_destroyed(self):
        """Should revert shielding when facility is gone."""
        planet = MockPlanet(
            radiation_shielding=1.5,
            radiation_shielding_target=1.5,
            facilities=[]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.radiation_shielding == pytest.approx(0.0)

    def test_no_target_no_apply(self):
        """Should not apply if radiation_shielding_target is None."""
        facility = MockFacility(
            component_states={"CORE:0:radiation_shield": _make_active_radiation_state()}
        )
        planet = MockPlanet(
            radiation_shielding=0.0,
            radiation_shielding_target=None,
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = PlanetModifierEffectEngine()

        engine.process_modifier_effects_tick(0, [empire])

        assert planet.radiation_shielding == pytest.approx(0.0)
