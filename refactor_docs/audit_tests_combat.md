# Audit Report: Combat Unit Tests

## Overview
**Files Audited:**
- `unit_tests/test_weapons.py`
- `unit_tests/test_combat.py`
- `unit_tests/test_combat_endurance.py`
- `unit_tests/test_pdc.py`
- `unit_tests/test_multitarget.py`
- `unit_tests/test_projectiles.py`
- `unit_tests/test_collision_system.py`
- `unit_tests/test_shields.py`
- `unit_tests/test_firing_arc_logic.py`

## Findings

### 1. `unit_tests/test_weapons.py`

| Test / Context | Line | Pattern | Validity | Fix Needed |
| :--- | :--- | :--- | :--- | :--- |
| `TestWeaponCooldowns.test_weapon_cooldown_decreases` | 247 | `isinstance(c, Weapon)` | **NO** | Replace with check for `WeaponAbility` or `c.is_weapon`. |

### 2. `unit_tests/test_combat.py`

| Test / Context | Line | Pattern | Validity | Fix Needed |
| :--- | :--- | :--- | :--- | :--- |
| `TestDamageLayerLogic.test_bridge_destruction_kills_ship` | 110 | `isinstance(c, Bridge)` | **NO** | Replace with `c.has_ability('CommandAndControl')` or usage of `type_str`. |
| `TestDamageLayerLogic.test_bridge_requirement_kills_ship` | 151 | `isinstance(c, Bridge)` | **NO** | Replace with `c.has_ability('CommandAndControl')`. |
| `TestWeaponCooldowns.test_weapon_cooldown_decreases` | 247 | `isinstance(c, Weapon)` | **NO** | Replace with check for `WeaponAbility`. |

### 3. `unit_tests/test_pdc.py`

| Test / Context | Line | Pattern | Validity | Fix Needed |
| :--- | :--- | :--- | :--- | :--- |
| `MockPDC.__init__` | 65-66 | `self.abilities = {'PointDefense': True}` | **NO** | Remove legacy ability dict. Ensure `tags=['pdc']` setup (Lines 54-62) is sufficient. |
| `MockPDC` (Class inheritance) | 13 | `class MockPDC(BeamWeapon):` | **Needs Review** | Should ideally inherit from `Component` and compose abilities, rather than inheriting from legacy `BeamWeapon` class. |

### 4. `unit_tests/test_combat_endurance.py`

| Test / Context | Line | Pattern | Validity | Fix Needed |
| :--- | :--- | :--- | :--- | :--- |
| `test_standard_components_defaults` | 250 | `laser.data.get('reload', 0)` | **YES** (Partial) | The test attempts to read legacy `reload` data directly. Needs to update to read strict ability definition first, matching V2 architecture. |

### 5. `unit_tests/test_shields.py`

*No critical legacy patterns found.* Uses `ShieldProjection` and `ShieldRegenerator` abilities.

### 6. `unit_tests/test_multitarget.py`

*No critical legacy patterns found.* Uses `COMPONENT_REGISTRY` and new AI strategy system.

### 7. `unit_tests/test_projectiles.py`

*No critical legacy patterns found.* Tests `Projectile` data class which is valid.

### 8. `unit_tests/test_collision_system.py`

*No critical legacy patterns found.* Mocks logic effectively.

### 9. `unit_tests/test_firing_arc_logic.py`

*No critical legacy patterns found.* Pure logic test.

## Summary of Fixes

1.  **Remove `isinstance` checks** in `test_weapons.py` and `test_combat.py`. Replace with ability presence checks.
2.  **Clean up `MockPDC`** in `test_pdc.py` to remove legacy dictionary assignments.
3.  **Update Data Access** in `test_combat_endurance.py` to prioritize ability dictionary structure over root-level data attributes.

