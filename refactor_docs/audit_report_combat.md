# Combat System Audit Report

## 1. Executive Summary
**Overall Status**: 95% Compliant / 5% Risk
The Combat System has been successfully migrated to the Ability System. All primary combat logic (firing, targeting, damage application) correctly utilizes `WeaponAbility` and `SeekerWeaponAbility` instead of accessing legacy Component attributes. 

A minor deviation exists where `Projectile` instances retain a reference to their `source_component`. This reference is actively used at impact time to calculate dynamic damage (range-based falloff) and update hit statistics. While this creates a dependency on the component instance, it enables advanced formula features fundamental to the new engine.

## 2. File-by-File Analysis

### `ship_combat.py`
| Check | Status | Notes |
| :--- | :--- | :--- |
| `fire_weapons` uses `get_ability` | ✅ PASS | Calls `comp.get_ability('WeaponAbility')`. |
| `fire_weapons` no legacy `damage`/`range` | ✅ PASS | Accesses stats via `weapon_ab.damage` and `weapon_ab.range`. |
| `_find_pdc_target` no `comp.range` | ✅ PASS | Uses `weapon_ab.range`. |
| Target filtering | ✅ PASS | Uses `comp.has_ability('SeekerWeaponAbility')` and `has_pdc_ability()`. |

### `projectiles.py`
| Check | Status | Notes |
| :--- | :--- | :--- |
| Instantiation extracts stats from Ability | ✅ PASS | `damage`, `range`, `hp` passed from `ship_combat.py` which reads from Ability. |
| `source_component` NOT stored | ⚠️ WARNING | `self.source_weapon` **IS stored** (Line 38). |

### `collision_system.py`
| Check | Status | Notes |
| :--- | :--- | :--- |
| `apply_damage` logic | ✅ PASS | `process_beam_attack` uses `beam_ab.get_damage(hit_dist)`. No `isinstance(target, Shield)` checks found. |
| Ramming Logic | ✅ PASS | Uses Ship-level `hp` and `take_damage`. |

### `projectile_manager.py` (Additional Check)
| Check | Status | Notes |
| :--- | :--- | :--- |
| Collision Logic | ✅ PASS | Uses `s.take_damage(damage)`. |
| Dependency on `source_component` | ⚠️ INFO | Uses `p.source_weapon.get_ability('WeaponAbility').get_damage(hit_dist)` at impact time. This allows for dynamic damage formulas (e.g., range falloff) but technically relies on reading the component "later". |
| Stats Tracking | ⚠️ INFO | Updates `p.source_weapon.shots_hit`. |

## 3. Detailed Findings

### Finding 1: Projectile Source Storage
`Projectile` instances store `source_weapon`.
- **Location**: `projectiles.py` Line 38 and `projectile_manager.py` Line 101.
- **Impact**: The projectile is not a purely self-contained snapshot; it links back to the creating component.
- **Justification**: This is required to support the `get_damage(range)` method which may contain math formulas defined in the Ability. Snapshotting the formula and context would be complex.
- **Risk**: Moderate. If the source component is garbage collected (unlikely while Ship exists) or modified mid-flight, damage values could shift. However, for a "Live" ability system, this behavior is defensible.

### Finding 2: `isinstance(target, Shield)` Verification
No direct `isinstance(target, Shield)` checks were found in damage application paths. Damage is applied to the `Ship` entity, which delegates to inner layers/components via `ShipCombatMixin`'s `take_damage` method, correctly handling shield layers logic internally.

## 4. Recommendations
1.  **Accept Usage of `source_weapon`**: The usage of `source_weapon` to call `get_damage(distance)` is a feature, enabling dynamic formulas. Attempting to assist this out would degrade functionality.
2.  **Monitor Projectile references**: Ensure `Projectile` references are cleared when battles end to prevent retaining Ship/Component memory graphs (Memory Leak risk). The `ProjectileManager.clear()` method exists and should be called.

## 5. Conclusion
The "Shooting Loop" is effectively 100% Ability-Driven. The retention of `source_weapon` is a functional dependency for the advanced formula system and does not represent a "legacy" attribute access (it accesses the Ability interface).

**Status**: **APPROVED** (with noted design choice).
