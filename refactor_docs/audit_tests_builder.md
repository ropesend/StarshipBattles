# Audit Report: Builder UI Unit Tests

## Executive Summary
Audited 14 unit test files covering Builder UI, Validation, and Modifier logic. Identified legacy patterns primarily in validation (string-based classification) and modifier tests (explicit type checking and direct attribute access). Most UI logic is generic and safe.

## Findings

### 1. `unit_tests\test_modifiers.py`

| Test Case | Line | Issue | Recommendation |
|-----------|------|-------|----------------|
| `test_clone_preserves_type` | 113 | `self.assertIsInstance(clone, ProjectileWeapon)` | **Fix**: Use `assertIn('ProjectileWeaponAbility', clone.abilities)` or check `comp.data['type']`. |
| `test_beam_weapon_clone` | 122-123 | `self.assertIsInstance(clone, BeamWeapon)` | **Fix**: Use `assertIn('BeamWeaponAbility', clone.abilities)`. |
| `test_modifier_restrictions` | 52-56 | Relies on `facing` modifier availability and implicit restrictions | **Update**: Ensure `facing` exists in `modifiers.json` or mock it properly to test generic restriction logic (checking `allowed_classifications` tag). |
| `test_add_modifier_to_component` | 27 | `create_component('railgun')` hard assumption | **Keep**: Valid component for testing, but ensure 'railgun' exists in `components.json`. |

### 2. `unit_tests\test_builder_validation.py`

| Test Case | Line | Issue | Recommendation |
|-----------|------|-------|----------------|
| `test_layer_restrictions` | 53 | `comp_data["major_classification"] = "Weapons"` | **Fix**: Use Tags. `comp_data["tags"] = ["weapon"]`. |
| `test_layer_restrictions` | 57 | `"block_classification:Weapons"` | **Fix**: Update to tag-based restriction: `"block_tag:weapon"`. |
| `test_layer_restrictions` | 69-84 | `"major_classification"] = "Armor"` & `"allow_classification:Armor"` | **Fix**: Update to tag-based restriction: `"allow_tag:armor"`. |

### 3. `unit_tests\test_builder_structure_features.py`

| Test Case | Line | Issue | Recommendation |
|-----------|------|-------|----------------|
| `setUp` | 25-33 | Mock data uses flat attributes `damage`, `hp` | **Fix**: Structure data to use `abilities` dict for `damage` and `hp` if testing detailed component interaction, though for UI structure tests this might be acceptable as a partial mock. |

### 4. `unit_tests\test_builder_logic.py`

| Test Case | Line | Issue | Recommendation |
|-----------|------|-------|----------------|
| `test_missing_bridge_requirement` | 68 | `any("Command And Control" in m ...)` | **Verify**: Ensure "Command And Control" is the display name of the relevant ability or requirement. If it's a hardcoded legacy string in `Ship.get_missing_requirements`, it needs update. |

### 5. `unit_tests\test_modifier_defaults_robustness.py`

| Test Case | Line | Issue | Recommendation |
|-----------|------|-------|----------------|
| `test_railgun_defaults_robustness` | 41 | `comp.firing_arc = 22.5` | **Fix**: If `firing_arc` is a read-only property derived from abilities, this assignment might fail or be ignored. Verify if this test intends to mock corruption by bypassing the property (e.g. `comp.data[...] = ...`). |

## Summary of actions
1.  **Refactor `test_modifiers.py`**: Remove `isinstance` checks for legacy subclasses.
2.  **Update `test_builder_validation.py`**: Switch from "major_classification" strings to Tags.
3.  **Sanitize Mocks**: Update mock data in `test_builder_structure_features.py` to resemble V2 component structure.
