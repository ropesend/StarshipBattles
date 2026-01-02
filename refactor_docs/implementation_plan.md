# Phase 7: Legacy Removal Implementation Plan

## Status: Ready to Execute
**Pre-requisites**: Phase 6 Data Migration COMPLETE ✅ (470/470 tests passing)

---

## Critical Bugs (P0) - Fix Immediately

### 1. Shield Calculation Overwrite Bug
- **File**: `ship_stats.py:325-330`
- **Issue**: Lines 325-330 overwrite the correct `ShieldProjection` ability aggregation with legacy dictionary lookups
- **Action**: Delete lines 325-330 entirely

### 2. Dead Code Removal
- **File**: `builder.py` (entire file)
- **Issue**: Completely unused legacy code, not imported anywhere
- **Action**: Delete entire file

---

## Stage 1: Critical Fixes

### ship_stats.py
| Line | Issue | Fix |
|------|-------|-----|
| 72, 78 | `comp.major_classification == "Armor"` checks | Use `comp.has_ability('ArmorAbility')` or tag check |
| 182 | `comp.major_classification == "Armor"` for layer | Use ability check |
| 325-330 | Shield overwrite bug | **DELETE these lines** |
| 464 | `if t == "Engine" or t == "Thruster": return 1` | Use `comp.has_ability('CombatPropulsion')` |

---

## Stage 2: Core Logic Migration

### ship_combat.py (15+ attribute accesses)
| Line | Legacy Pattern | Replacement |
|------|---------------|-------------|
| 116 | `max_range = comp.range` | `comp.get_ability('WeaponAbility').range` |
| 119 | `comp.projectile_speed * comp.endurance` | Use ability values |
| 131 | `comp.firing_arc` | Use ability values |
| 161, 162 | `comp.damage`, `comp.range` | Use ability values |
| 183, 190, 191 | `comp.projectile_speed`, `comp.damage` | Use ability values |
| 194 | `turn_rate=comp.turn_rate` | Use ability values |
| 212, 213 | `damage=comp.damage`, `range_val=comp.range` | Use ability values |
| 236 | `if dist > comp.range` in `_find_pdc_target` | Use ability values |
| 141 | `comp.fire(target)` | `ability = comp.get_ability('WeaponAbility'); ability.fire(target)` |

### collision_system.py
| Line | Legacy Pattern | Replacement |
|------|---------------|-------------|
| 67 | `beam_comp.calculate_hit_chance(...)` | Access via ability |
| 71 | `damage = beam_comp.get_damage(hit_dist)` | Access via ability |

### projectile_manager.py
| Line | Legacy Pattern | Replacement |
|------|---------------|-------------|
| 100-101 | `hasattr(p.source_weapon, 'get_damage')` | Check ability instead |
| 127 | `p.source_weapon.shots_hit += 1` | Use `ability.record_hit()` |

### ai.py
| Line | Legacy Pattern | Replacement |
|------|---------------|-------------|
| 188 | `hasattr(c, 'damage')` for weapon detection | `c.has_ability('WeaponAbility')` |
| 365 | `from components import Weapon` | Remove import |
| 372 | `if dist > comp.range` | `comp.get_ability('WeaponAbility').range` |
| 383 | `comp.firing_arc / 2` | Access via ability |

### ship.py
| Line | Legacy Pattern | Replacement |
|------|---------------|-------------|
| 10-15 | Legacy subclass imports | Remove unused imports |
| 248-249 | `hasattr(comp, 'range')` fallback | Remove after migration |
| 598 | `isinstance(comp, Sensor)` | `comp.has_ability('SensorAbility')` |
| 607, 610 | `isinstance(comp, Electronics)`, `isinstance(comp, Armor)` | Use ability checks |

---

## Stage 3: UI & Rendering

### ui/builder/detail_panel.py
| Line | Issue | Fix |
|------|-------|-----|
| 5-7 | Legacy imports (`Engine`, `Thruster`, etc.) | Remove imports |
| 115 | `comp.type_str` display | Use role/tag based label |
| 132 | `hasattr(comp, 'base_accuracy')` | Migrate to ability `get_ui_rows()` |
| 142 | `hasattr(comp, 'to_hit_defense')` | Migrate to ability |
| 153-198 | Manual `comp.abilities` loop | Use aggregated `get_ui_rows()` |

### ui/builder/weapons_panel.py (10+ getattr calls)
| Line | Issue | Fix |
|------|-------|-----|
| 275-278 | `getattr(weapon, 'base_accuracy/falloff/range/damage')` | Use `WeaponAbility` properties |
| 361, 439-443, 549-550, 654-655, 674, 742 | Direct attribute access | Use ability access |
| 475, 674, 742 | `hasattr(weapon, 'get_damage')` | Use `WeaponAbility.get_damage()` |

### ui/builder/modifier_logic.py
| Line | Issue | Fix |
|------|-------|-----|
| 23, 27 | `component.type_str not in mod_def.restrictions` | Consider ability-based restrictions |
| 123, 161 | `component.data.get('firing_arc')` | Read from ability dict first |

### ui/builder/schematic_view.py
| Line | Issue | Fix |
|------|-------|-----|
| 125-127 | `getattr(weapon, 'firing_arc/range/facing_angle')` | Use `WeaponAbility` |

### battle_ui.py
| Line | Issue | Fix |
|------|-------|-----|
| 135-136 | `comp.range` in debug overlay | `comp.get_ability('WeaponAbility').range` |
| 161-162 | `comp.firing_arc`, `comp.range` | Use ability access |

### rendering.py
| Line | Issue | Fix |
|------|-------|-----|
| 123 | `elif comp.type_str == 'Armor': color = ...` | Use `comp.has_ability('ArmorAbility')` or tags |

---

## Stage 4: Data Files

### modifiers.json - Migrate to Ability-Based Restrictions
Current entries using legacy `allow_types`/`deny_types`:
- `hardened`: `"deny_types": ["Armor"]` → `"deny_abilities": ["ArmorAbility"]`
- `turret_mount`: `"allow_types": ["Weapon", "ProjectileWeapon", ...]` → `"allow_abilities": ["WeaponAbility"]`
- `range_mount`: `"allow_types": ["ProjectileWeapon", "BeamWeapon"]` → `"allow_abilities": ["WeaponAbility"]`
- (and 8 other entries)

### components.json
| Line | Issue | Fix |
|------|-------|-----|
| 481 | `"PointDefense": true` | Convert to `"PointDefenseAbility": {}` or add `"tags": ["pdc"]` |

### ship_validator.py
| Line | Issue | Fix |
|------|-------|-----|
| 113 | `if component.type_str == blocked_type` | Support `block_ability` or `block_tag` |
| 136 | `if component.type_str == target` | Support `allow_ability` or `allow_tag` |
| 219 | `legacy_req` variable | Rename to `crew_deficit` |

---

## Stage 5: Test Suite Updates

### test_components.py
| Line | Issue | Fix |
|------|-------|-----|
| 32 | `self.assertIsInstance(railgun, Weapon)` | `self.assertTrue(railgun.has_ability('WeaponAbility'))` |
| 36 | `self.assertIsInstance(tank, Tank)` | `self.assertTrue(tank.has_ability('ResourceStorage'))` |
| 126 | `base_range = railgun.range` | `railgun.get_ability('WeaponAbility').range` |

### test_ship_stats.py (High Priority)
| Line | Issue | Fix |
|------|-------|-----|
| 36-44 | Imports of `Engine`, `Thruster`, `Shield` | Remove imports, use `create_component` |
| 114, 137, 176, 205, 234 | Direct class instantiation | Use `create_component()` |
| 109, 135, 158, 203 | `thrust_force`, `turn_speed` at root | Put in `abilities` dict |
| 208 | `self.assertEqual(engine.thrust_force, 2000)` | Test via ability |

### test_combat.py
| Line | Issue | Fix |
|------|-------|-----|
| 110, 151 | `isinstance(c, Bridge)` | `c.has_ability('CommandAndControl')` |
| 247 | `isinstance(c, Weapon)` | Check for `WeaponAbility` |

### test_pdc.py
| Line | Issue | Fix |
|------|-------|-----|
| 13 | `class MockPDC(BeamWeapon)` | Inherit from `Component`, compose abilities |
| 65-66 | `self.abilities = {'PointDefense': True}` | Use tags setup only |

### test_modifiers.py
| Line | Issue | Fix |
|------|-------|-----|
| 113 | `self.assertIsInstance(clone, ProjectileWeapon)` | Check abilities dict |
| 122-123 | `self.assertIsInstance(clone, BeamWeapon)` | Check abilities dict |

### test_strategy_system.py
| Line | Issue | Fix |
|------|-------|-----|
| 77 | `c1.damage = 10` | Use real component or proper ability mock |

### test_builder_validation.py
| Line | Issue | Fix |
|------|-------|-----|
| 53, 57, 69-84 | `major_classification` strings | Use tags |

---

## Stage 6: The Big Delete (components.py)

### Legacy Subclasses to Remove
- Line 649: `class Bridge(Component)`
- Line 655: `class Weapon(Component)`
- Line 731: `class ProjectileWeapon(Weapon)`
- Line 750: `class Engine(Component)`
- Line 763: `class Thruster(Component)`
- Line 799: `class BeamWeapon(Weapon)`
- Line 862: `class SeekerWeapon(Weapon)`
- Line 943: `class Shield(Component)`

### Legacy Shims to Remove
- Lines 182-296: `_instantiate_abilities` shim section
- Lines 527-529: `hasattr(self, 'thrust_force/turn_speed')` checks
- Line 1021: `COMPONENT_TYPE_MAP` (hardcoded mapping to legacy subclasses)

### Legacy Attribute Patterns to Remove
- Line 114: Formula parsing forcing `damage`/`range` onto component
- Line 519: `recalculate_stats` weapon data reads

---

## Verification Plan

1. **After each stage**: Run `python -m pytest unit_tests/ -n 16 --tb=no -q`
2. **After Stage 6**: `grep -r "isinstance.*Engine\|isinstance.*Weapon" *.py` should return 0 results
3. **Visual verification**: Test Ship Builder and Battle UI
