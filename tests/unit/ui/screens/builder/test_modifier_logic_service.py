"""Tests for ModifierLogicService — the instance-based replacement for ModifierLogic.

Phase 2 of the Design Workshop tech debt plan. Tests written FIRST (TDD).
"""
import pytest
from unittest.mock import MagicMock, patch


class TestModifierLogicServiceConstruction:
    """Constructor injection must follow codebase DI pattern."""

    def test_requires_registry_provider(self):
        """Passing None raises ValidationException."""
        from game.ui.screens.builder.modifier_logic import ModifierLogicService

        with pytest.raises(Exception):
            ModifierLogicService(registry_provider=None)

    def test_accepts_valid_provider(self):
        """Valid provider creates a usable service instance."""
        from game.ui.screens.builder.modifier_logic import ModifierLogicService

        provider = MagicMock()
        provider.get_modifiers.return_value = {}
        provider.get_components.return_value = {}

        service = ModifierLogicService(registry_provider=provider)
        assert service is not None


class TestGetBaseFiringArc:
    """Base firing arc extraction is verified through the public API.

    PROJ-322 Task 3.17 / 5.27: rewritten to use ``get_initial_value`` and
    ``get_local_min_max`` with the ``turret_mount`` mod_id (which is the
    only public surface that actually consumes the arc) instead of calling
    the private ``_get_base_firing_arc`` helper directly. The public path
    exercises the same lookup logic — root-level ``firing_arc`` takes
    precedence over ``abilities`` nested values; missing arc falls back to
    the modifier's ``min_val``.
    """

    @pytest.fixture
    def service(self):
        from game.ui.screens.builder.modifier_logic import ModifierLogicService

        provider = MagicMock()
        # turret_mount is the only modifier that consumes the firing arc;
        # the public path uses its mod_def for the fallback min_val.
        turret_def = MagicMock()
        turret_def.min_val = 0.0
        turret_def.max_val = 360.0
        turret_def.default_val = 50.0
        provider.get_modifiers.return_value = {'turret_mount': turret_def}
        provider.get_components.return_value = {}
        return ModifierLogicService(registry_provider=provider)

    def test_arc_at_root_level(self, service):
        """Finds firing_arc directly on component.data via public API."""
        comp = MagicMock()
        comp.data = {'firing_arc': 90}
        # get_initial_value('turret_mount', comp) returns the arc when present.
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
        # When _get_base_firing_arc returned None internally, get_initial_value
        # falls back to mod_def.min_val per the production contract.
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
    """Initial value dispatch should use dict lookup, not hardcoded if chain."""

    @pytest.fixture
    def service(self):
        from game.ui.screens.builder.modifier_logic import ModifierLogicService

        provider = MagicMock()
        mod_def = MagicMock()
        mod_def.min_val = 0.0
        mod_def.max_val = 360.0
        mod_def.default_val = 50.0
        provider.get_modifiers.return_value = {'test_mod': mod_def, 'simple_size_mount': mod_def,
                                                'range_mount': mod_def, 'facing': mod_def,
                                                'precision_mount': mod_def, 'turret_mount': mod_def}
        provider.get_components.return_value = {}
        return ModifierLogicService(registry_provider=provider)

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

    def test_unknown_modifier_returns_default_val(self, service):
        """Modifiers not in dispatch dict use mod_def.default_val."""
        comp = MagicMock()
        # Need a provider that has 'unknown_mod' definition
        provider = MagicMock()
        mod_def = MagicMock()
        mod_def.default_val = 42.0
        provider.get_modifiers.return_value = {'unknown_mod': mod_def}
        provider.get_components.return_value = {}

        from game.ui.screens.builder.modifier_logic import ModifierLogicService
        svc = ModifierLogicService(registry_provider=provider)
        assert svc.get_initial_value('unknown_mod', comp) == 42.0

    def test_missing_modifier_returns_0(self, service):
        """Modifier not in registry returns 0."""
        comp = MagicMock()
        assert service.get_initial_value('nonexistent', comp) == 0


class TestGetLocalMinMax:
    """Min/max calculation should use extracted firing arc helper."""

    @pytest.fixture
    def service(self):
        from game.ui.screens.builder.modifier_logic import ModifierLogicService

        provider = MagicMock()
        turret_def = MagicMock()
        turret_def.min_val = 0.0
        turret_def.max_val = 360.0

        other_def = MagicMock()
        other_def.min_val = 0.0
        other_def.max_val = 100.0

        provider.get_modifiers.return_value = {
            'turret_mount': turret_def,
            'range_mount': other_def,
        }
        provider.get_components.return_value = {}
        return ModifierLogicService(registry_provider=provider)

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
    """Snap calculation is a pure function — should remain static."""

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
    """Mandatory check delegates correctly."""

    @pytest.fixture
    def service(self):
        from game.ui.screens.builder.modifier_logic import ModifierLogicService

        provider = MagicMock()
        mod_a = MagicMock()
        mod_a.restrictions = {}  # No restrictions = allowed for everything
        mod_b = MagicMock()
        mod_b.restrictions = {'allow_types': ['weapon']}

        provider.get_modifiers.return_value = {'mod_a': mod_a, 'mod_b': mod_b}
        provider.get_components.return_value = {}
        return ModifierLogicService(registry_provider=provider)

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
