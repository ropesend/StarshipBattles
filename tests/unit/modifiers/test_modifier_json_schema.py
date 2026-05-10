"""
Tests for Modifier JSON V2 Schema - Phase 2 Task 2.1

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
import json


class TestModifierV2Schema:
    """Tests for the new modifier JSON schema format."""

    def test_new_format_has_effects_array(self):
        """New modifier format should have 'effects' array instead of 'special'."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        modifier = {
            'id': 'test_mod',
            'name': 'Test',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param'}
            ]
        }

        assert validate_modifier_v2(modifier) is True

    def test_effect_has_stat_and_formula(self):
        """Each effect should have 'stat' and 'formula' fields."""
        from game.simulation.components.modifier_schema import validate_effect_v2

        effect = {'stat': 'damage_mult', 'formula': 'param'}
        assert validate_effect_v2(effect) is True

        # Missing stat should fail
        bad_effect = {'formula': 'param'}
        assert validate_effect_v2(bad_effect) is False

        # Missing formula should fail
        bad_effect2 = {'stat': 'damage_mult'}
        assert validate_effect_v2(bad_effect2) is False

    def test_effect_operation_defaults_to_multiply(self):
        """operation should default to 'multiply' if not specified."""
        from game.simulation.components.modifier_schema import normalize_effect_v2

        effect = {'stat': 'damage_mult', 'formula': 'param'}
        normalized = normalize_effect_v2(effect)

        assert normalized['operation'] == 'multiply'

    def test_effect_operation_explicit(self):
        """Explicit operation should be preserved."""
        from game.simulation.components.modifier_schema import normalize_effect_v2

        effect = {'stat': 'accuracy_add', 'formula': 'param * 0.5', 'operation': 'add'}
        normalized = normalize_effect_v2(effect)

        assert normalized['operation'] == 'add'

    def test_effect_target_ability_is_optional(self):
        """target_ability should be optional."""
        from game.simulation.components.modifier_schema import validate_effect_v2

        # Without target_ability
        effect1 = {'stat': 'mass_mult', 'formula': 'param'}
        assert validate_effect_v2(effect1) is True

        # With target_ability
        effect2 = {'stat': 'damage_mult', 'formula': 'param', 'target_ability': 'WeaponAbility'}
        assert validate_effect_v2(effect2) is True

    def test_param_definition_structure(self):
        """param should have name, type, min, max, default."""
        from game.simulation.components.modifier_schema import validate_param_v2

        param = {
            'name': 'Level',
            'type': 'linear',
            'min': 0,
            'max': 5,
            'default': 1
        }

        assert validate_param_v2(param) is True

    def test_param_missing_required_fields(self):
        """param missing required fields should fail validation."""
        from game.simulation.components.modifier_schema import validate_param_v2

        # Missing 'name'
        bad_param = {'type': 'linear', 'min': 0, 'max': 5, 'default': 1}
        assert validate_param_v2(bad_param) is False

        # Missing 'min'
        bad_param2 = {'name': 'Level', 'type': 'linear', 'max': 5, 'default': 1}
        assert validate_param_v2(bad_param2) is False

    def test_restrictions_allow_abilities(self):
        """restrictions should support 'allow_abilities' list."""
        from game.simulation.components.modifier_schema import validate_restrictions_v2

        restrictions = {
            'allow_abilities': ['WeaponAbility', 'BeamWeaponAbility']
        }

        assert validate_restrictions_v2(restrictions) is True

    def test_restrictions_deny_abilities(self):
        """restrictions should support 'deny_abilities' list."""
        from game.simulation.components.modifier_schema import validate_restrictions_v2

        restrictions = {
            'deny_abilities': ['Armor']
        }

        assert validate_restrictions_v2(restrictions) is True

    def test_restrictions_require_mode(self):
        """restrictions should support 'require_mode' for all/any."""
        from game.simulation.components.modifier_schema import validate_restrictions_v2

        restrictions = {
            'allow_abilities': ['WeaponAbility', 'ShieldProjection'],
            'require_mode': 'any'
        }

        assert validate_restrictions_v2(restrictions) is True

        restrictions_all = {
            'allow_abilities': ['WeaponAbility', 'ShieldProjection'],
            'require_mode': 'all'
        }

        assert validate_restrictions_v2(restrictions_all) is True

    def test_complete_modifier_v2_validation(self):
        """Complete V2 modifier should pass validation."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        modifier = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'description': 'HP increases as the square of mass multiplier.',
            'param': {
                'name': 'Mass Mult',
                'type': 'linear',
                'min': 1.0,
                'max': 10.0,
                'default': 1.0
            },
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param', 'operation': 'multiply'},
                {'stat': 'hp_mult', 'formula': 'param ^ 2', 'operation': 'multiply'},
                {'stat': 'cost_mult', 'formula': 'param', 'operation': 'multiply'}
            ],
            'restrictions': {
                'deny_abilities': ['Armor']
            }
        }

        assert validate_modifier_v2(modifier) is True

    def test_detect_v2_vs_v1_format(self):
        """Should correctly detect V2 format and reject V1 with error."""
        from game.simulation.components.modifier_schema import is_v2_format

        v2_modifier = {
            'id': 'test',
            'effects': [{'stat': 'mass_mult', 'formula': 'param'}]
        }

        non_v2_modifier = {
            'id': 'test',
            'effects': {'special': 'hardened_mount'}  # dict instead of list
        }

        assert is_v2_format(v2_modifier) is True

        # Non-list effects returns False (not V2 format)
        assert is_v2_format(non_v2_modifier) is False

    def test_v2_format_with_depends_on(self):
        """effects can have 'depends_on' for stat-referencing formulas."""
        from game.simulation.components.modifier_schema import validate_effect_v2

        effect = {
            'stat': 'damage_mult',
            'formula': '1.0 + (mass_mult - 1.0) * 0.5',
            'depends_on': ['mass_mult']
        }

        assert validate_effect_v2(effect) is True


class TestModifierV2EdgeCases:
    """Tests for edge cases in V2 schema validation (Phase 14)."""

    def test_empty_effects_array_rejected(self):
        """A modifier with an empty effects array should be rejected."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        modifier_with_empty_effects = {
            'id': 'test_empty',
            'name': 'Empty Modifier',
            'effects': []  # Empty array - should be rejected
        }

        assert validate_modifier_v2(modifier_with_empty_effects) is False, \
            "Modifier with empty effects array should be rejected"

    def test_modifier_without_effects_key_rejected(self):
        """A modifier without an 'effects' key should be rejected."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        modifier_no_effects = {
            'id': 'test_no_effects',
            'name': 'No Effects Modifier'
            # No 'effects' key at all
        }

        assert validate_modifier_v2(modifier_no_effects) is False, \
            "Modifier without effects key should be rejected"

    def test_invalid_operation_value_rejected(self):
        """An effect with an invalid operation value should be rejected."""
        from game.simulation.components.modifier_schema import validate_effect_v2

        effect_with_invalid_op = {
            'stat': 'damage_mult',
            'formula': 'param',
            'operation': 'invalid_operation'  # Not a valid operation
        }

        assert validate_effect_v2(effect_with_invalid_op) is False, \
            "Effect with invalid operation should be rejected"

    def test_modifier_with_invalid_effect_rejected(self):
        """A modifier with an invalid effect should be rejected."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        modifier_with_bad_effect = {
            'id': 'test_bad_effect',
            'name': 'Bad Effect Modifier',
            'effects': [
                {
                    'stat': 'damage_mult',
                    'formula': 'param',
                    'operation': 'bogus_op'  # Invalid operation
                }
            ]
        }

        assert validate_modifier_v2(modifier_with_bad_effect) is False, \
            "Modifier with invalid effect should be rejected"


class TestModifierV2Examples:
    """Tests with real modifier examples from current_formulas.md."""

    def test_hardened_mount_v2_structure(self):
        """hardened_mount should have correct V2 structure."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        hardened = {
            'id': 'hardened_mount',
            'name': 'Hardened',
            'description': 'HP increases as the square of mass multiplier.',
            'param': {
                'name': 'Mass Mult',
                'type': 'linear',
                'min': 1.0,
                'max': 10.0,
                'default': 1.0
            },
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'},
                {'stat': 'hp_mult', 'formula': 'param ^ 2'},
                {'stat': 'cost_mult', 'formula': 'param'}
            ],
            'restrictions': {
                'deny_abilities': ['Armor']
            }
        }

        assert validate_modifier_v2(hardened) is True

    def test_range_mount_v2_structure(self):
        """range_mount should have correct V2 structure."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        range_mount = {
            'id': 'range_mount',
            'name': 'Range Mount',
            'description': 'Each level doubles range.',
            'param': {
                'name': 'Level',
                'type': 'linear',
                'min': 0,
                'max': 10,
                'default': 0
            },
            'effects': [
                {'stat': 'range_mult', 'formula': '2 ^ param'},
                {'stat': 'mass_mult', 'formula': '3.5 ^ param'},
                {'stat': 'hp_mult', 'formula': '3.5 ^ param'},
                {'stat': 'cost_mult', 'formula': '3.5 ^ param'}
            ],
            'restrictions': {
                'allow_abilities': ['ProjectileWeaponAbility', 'BeamWeaponAbility'],
                'deny_abilities': ['SeekerWeaponAbility']
            }
        }

        assert validate_modifier_v2(range_mount) is True

    def test_turret_mount_v2_with_ln_formula(self):
        """turret_mount should have correct V2 structure with ln formula."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        turret = {
            'id': 'turret_mount',
            'name': 'Turret Mount',
            'description': 'Adds firing arc.',
            'param': {
                'name': 'Arc',
                'type': 'linear',
                'min': 0,
                'max': 180,
                'default': 45
            },
            'effects': [
                {'stat': 'mass_mult', 'formula': '1.0 + 0.514 * ln(1.0 + param / 30.0)'},
                {'stat': 'arc_set', 'formula': 'param', 'operation': 'set'}
            ],
            'restrictions': {
                'allow_abilities': ['ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility']
            }
        }

        assert validate_modifier_v2(turret) is True

    def test_rapid_fire_v2_with_additive(self):
        """rapid_fire should have correct V2 structure with additive mass."""
        from game.simulation.components.modifier_schema import validate_modifier_v2

        rapid = {
            'id': 'rapid_fire',
            'name': 'Rapid Fire',
            'description': 'Increases fire rate.',
            'param': {
                'name': 'Fire Rate',
                'type': 'linear',
                'min': 1.0,
                'max': 10.0,
                'default': 1.0
            },
            'effects': [
                {'stat': 'reload_mult', 'formula': '1.0 / param'},
                {'stat': 'mass_add', 'formula': '(param - 1.0) * 2.0', 'operation': 'add'},
                {'stat': 'cost_mult', 'formula': 'sqrt(param)'}
            ],
            'restrictions': {
                'allow_abilities': ['ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility']
            }
        }

        assert validate_modifier_v2(rapid) is True
