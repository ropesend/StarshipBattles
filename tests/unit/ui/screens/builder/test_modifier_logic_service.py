"""Tests for ModifierLogicService — UI facade delegating to ModifierService.

PROJ-489: ``ModifierLogicService`` now takes a ``ModifierService`` directly
and delegates every shared method. Tests here pin the facade surface; the
underlying behavior is covered by ``tests/unit/simulation/services/test_modifier_service.py``.

Historical context: this file originally covered behavior implemented in
``ModifierLogicService``; that implementation has since been collapsed onto
``ModifierService`` (PROJ-489 / cluster ``modifier_service_canon``).
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.components.component_constants import Modifier


def _make_service(modifier_registry):
    """Build a ``ModifierLogicService`` backed by a real ``ModifierService``."""
    from game.simulation.services.modifier_service import ModifierService
    from game.ui.screens.builder.modifier_logic import ModifierLogicService

    return ModifierLogicService(ModifierService(modifier_registry=modifier_registry))


class TestModifierLogicServiceConstruction:
    """Constructor injection must follow codebase DI pattern."""

    def test_requires_modifier_service(self):
        """Passing None raises ValidationException."""
        from game.ui.screens.builder.modifier_logic import ModifierLogicService

        with pytest.raises(Exception):
            ModifierLogicService(None)

    def test_accepts_valid_modifier_service(self):
        """Valid ModifierService creates a usable facade instance."""
        from game.simulation.services.modifier_service import ModifierService
        from game.ui.screens.builder.modifier_logic import ModifierLogicService

        service = ModifierLogicService(ModifierService(modifier_registry={}))
        assert service is not None


class TestGetBaseFiringArc:
    """Base firing arc extraction is verified through the public API.

    PROJ-489: the underlying implementation now lives in ``ModifierService``
    and uses ``_has_arc_set_effect`` + generic ability iteration. These tests
    pin the facade surface; equivalent (and more exhaustive) tests live in
    ``test_modifier_service.py``.
    """

    @pytest.fixture
    def service(self):
        turret_def = Modifier({
            'id': 'turret_mount',
            'name': 'Turret Mount',
            'param': {'min': 0.0, 'max': 360.0, 'default': 50.0},
            'restrictions': {},
            'effects': [{'stat': 'arc_set', 'formula': 'param', 'operation': 'set'}],
        })
        return _make_service({'turret_mount': turret_def})

    def test_arc_at_root_level(self, service):
        """Finds firing_arc directly on component.data via public API."""
        comp = MagicMock()
        comp.data = {'firing_arc': 90}
        assert service.get_initial_value('turret_mount', comp) == 90.0

    def test_arc_in_projectile_ability(self, service):
        """Finds firing_arc nested inside ProjectileWeaponAbility via public API."""
        comp = MagicMock()
        comp.data = {
            'abilities': {
                'ProjectileWeaponAbility': {'firing_arc': 45, 'damage': 10}
            }
        }
        assert service.get_initial_value('turret_mount', comp) == 45.0

    def test_arc_in_beam_ability(self, service):
        """Finds firing_arc nested inside BeamWeaponAbility via public API."""
        comp = MagicMock()
        comp.data = {
            'abilities': {
                'BeamWeaponAbility': {'firing_arc': 30}
            }
        }
        assert service.get_initial_value('turret_mount', comp) == 30.0

    def test_no_arc_returns_min_val_fallback(self, service):
        """No arc found -> public API returns the modifier's min_val (0.0)."""
        comp = MagicMock()
        comp.data = {'abilities': {'SomeOtherAbility': {}}}
        assert service.get_initial_value('turret_mount', comp) == 0.0

    def test_root_arc_takes_precedence(self, service):
        """Root-level firing_arc takes precedence over ability-nested one (public API)."""
        comp = MagicMock()
        comp.data = {
            'firing_arc': 120,
            'abilities': {
                'WeaponAbility': {'firing_arc': 60}
            }
        }
        assert service.get_initial_value('turret_mount', comp) == 120.0


class TestGetInitialValue:
    """Initial value dispatch should match the canonical service."""

    @pytest.fixture
    def service(self):
        registry = {
            'simple_size_mount': Modifier({
                'id': 'simple_size_mount',
                'name': 'Size',
                'param': {'min': 1.0, 'max': 1024.0, 'default': 1.0},
                'restrictions': {},
                'effects': [],
            }),
            'range_mount': Modifier({
                'id': 'range_mount',
                'name': 'Range',
                'param': {'min': 0.0, 'max': 3.0, 'default': 0.0},
                'restrictions': {},
                'effects': [],
            }),
            'facing': Modifier({
                'id': 'facing',
                'name': 'Facing',
                'param': {'min': 0.0, 'max': 359.0, 'default': 0.0},
                'restrictions': {},
                'effects': [],
            }),
            'precision_mount': Modifier({
                'id': 'precision_mount',
                'name': 'Precision',
                'param': {'min': 0.0, 'max': 5.0, 'default': 0.0},
                'restrictions': {},
                'effects': [],
            }),
            'turret_mount': Modifier({
                'id': 'turret_mount',
                'name': 'Turret Mount',
                'param': {'min': 0.0, 'max': 360.0, 'default': 50.0},
                'restrictions': {},
                'effects': [{'stat': 'arc_set', 'formula': 'param', 'operation': 'set'}],
            }),
        }
        return _make_service(registry)

    def test_simple_size_mount_returns_1(self, service):
        comp = MagicMock()
        assert service.get_initial_value('simple_size_mount', comp) == 1.0

    def test_range_mount_returns_0(self, service):
        comp = MagicMock()
        assert service.get_initial_value('range_mount', comp) == 0.0

    def test_facing_returns_0(self, service):
        comp = MagicMock()
        assert service.get_initial_value('facing', comp) == 0.0

    def test_precision_mount_returns_0(self, service):
        comp = MagicMock()
        assert service.get_initial_value('precision_mount', comp) == 0.0

    def test_turret_mount_uses_base_arc(self, service):
        comp = MagicMock()
        comp.data = {'firing_arc': 45}
        assert service.get_initial_value('turret_mount', comp) == 45.0

    def test_turret_mount_falls_back_to_min_val(self, service):
        comp = MagicMock()
        comp.data = {'abilities': {}}
        assert service.get_initial_value('turret_mount', comp) == 0.0

    def test_unknown_modifier_returns_default_val(self):
        """Modifiers not in dispatch dict use mod_def.default_val."""
        registry = {
            'unknown_mod': Modifier({
                'id': 'unknown_mod',
                'name': 'Unknown',
                'param': {'min': 0.0, 'max': 100.0, 'default': 42.0},
                'restrictions': {},
                'effects': [],
            })
        }
        svc = _make_service(registry)
        comp = MagicMock()
        assert svc.get_initial_value('unknown_mod', comp) == 42.0

    def test_missing_modifier_returns_0(self, service):
        """Modifier not in registry returns 0."""
        comp = MagicMock()
        assert service.get_initial_value('nonexistent', comp) == 0


class TestGetLocalMinMax:
    """Min/max calculation should use the canonical arc_set detection."""

    @pytest.fixture
    def service(self):
        registry = {
            'turret_mount': Modifier({
                'id': 'turret_mount',
                'name': 'Turret Mount',
                'param': {'min': 0.0, 'max': 360.0, 'default': 50.0},
                'restrictions': {},
                'effects': [{'stat': 'arc_set', 'formula': 'param', 'operation': 'set'}],
            }),
            'range_mount': Modifier({
                'id': 'range_mount',
                'name': 'Range',
                'param': {'min': 0.0, 'max': 100.0, 'default': 0.0},
                'restrictions': {},
                'effects': [],
            }),
        }
        return _make_service(registry)

    def test_turret_mount_min_is_base_arc(self, service):
        """turret_mount min should be the component's base firing arc."""
        comp = MagicMock()
        comp.data = {'firing_arc': 30}
        lo, hi = service.get_local_min_max('turret_mount', comp)
        assert lo == 30.0
        assert hi == 360.0

    def test_non_turret_uses_mod_def_range(self, service):
        """Non-turret modifiers use standard min/max from definition."""
        comp = MagicMock()
        lo, hi = service.get_local_min_max('range_mount', comp)
        assert lo == 0.0
        assert hi == 100.0

    def test_missing_modifier_returns_default_range(self, service):
        lo, hi = service.get_local_min_max('nonexistent', MagicMock())
        assert lo == 0
        assert hi == 100


class TestCalculateSnapValue:
    """Snap calculation is a pure UI function — retained on ModifierLogicService."""

    def test_decrement_from_exact_multiple(self):
        from game.ui.screens.builder.modifier_logic import ModifierLogicService
        result = ModifierLogicService.calculate_snap_value(
            current=90, step=90, direction=-1, min_val=0, max_val=360
        )
        assert result == 0

    def test_increment_from_non_multiple(self):
        from game.ui.screens.builder.modifier_logic import ModifierLogicService
        result = ModifierLogicService.calculate_snap_value(
            current=22, step=15, direction=1, min_val=0, max_val=360
        )
        assert result == 30

    def test_smart_floor_below_step(self):
        from game.ui.screens.builder.modifier_logic import ModifierLogicService
        result = ModifierLogicService.calculate_snap_value(
            current=1.0, step=1.0, direction=-1, min_val=0.1, max_val=1024.0,
            smart_floor=True
        )
        assert result >= 0.1


class TestIsModifierMandatory:
    """Mandatory check delegates correctly to the canonical service."""

    @pytest.fixture
    def service(self):
        registry = {
            'mod_a': Modifier({
                'id': 'mod_a',
                'name': 'A',
                'param': {'min': 0, 'max': 10, 'default': 0},
                'restrictions': {},  # No restrictions = allowed for everything
                'effects': [],
            }),
            'mod_b': Modifier({
                'id': 'mod_b',
                'name': 'B',
                'param': {'min': 0, 'max': 10, 'default': 0},
                'restrictions': {'allow_types': ['weapon']},
                'effects': [],
            }),
        }
        return _make_service(registry)

    def test_unrestricted_modifier_is_mandatory(self, service):
        """Modifier with no restrictions is mandatory (allowed = mandatory in this system)."""
        comp = MagicMock()
        comp.type_str = 'weapon'
        comp.abilities = {}
        comp.data = {'abilities': {}}
        assert service.is_modifier_mandatory('mod_a', comp) is True

    def test_restricted_modifier_not_mandatory_for_wrong_type(self, service):
        """Modifier restricted to 'weapon' is not mandatory for 'armor' components."""
        comp = MagicMock()
        comp.type_str = 'armor'
        comp.abilities = {}
        comp.data = {'abilities': {}}
        assert service.is_modifier_mandatory('mod_b', comp) is False
