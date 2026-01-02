# Ability System Refactor - Handoff & Context

## 1. High-Level Context
**Refactor Goal**: Transition from Inheritance-based Components (`Engine`, `Weapon`) to Composition-based Components (`Component` + `Abilities`).

**Current Phase**: Phase 7 Ready (Legacy Removal)  
**Tests**: 470/470 PASSED (as of 2026-01-02)

**Status Summary**:
- Phase 1 ✅ Foundation (abilities.py created)
- Phase 2 ✅ Core Refactor (Component class, Legacy Shim)
- Phase 3 ✅ Stats & Physics Integration
- Phase 4 ✅ Combat System Complete
- Phase 5 ✅ UI & Capabilities Complete
- Phase 6 ✅ Data Migration COMPLETE
- **Phase 7 ⏳ Legacy Removal (Ready to Execute)**

---

## 2. Phase 7 Audit Summary (14 Agents Completed)

### Critical Issues (P0)
| Finding | File:Line | Issue | Action |
|---------|-----------|-------|--------|
| Shield Bug | `ship_stats.py:325-330` | Overwrites correct ability aggregation | DELETE lines |
| Dead Code | `builder.py` | Entire file unused | DELETE file |

### Core Logic (P1) - 40+ Findings
| Area | File | Key Issues |
|------|------|------------|
| Combat | `ship_combat.py` | 15+ direct `comp.damage/range` accesses |
| AI | `ai.py:188` | `hasattr(c, 'damage')` for weapon detection |
| Ship | `ship.py:598,607` | `isinstance(Sensor/Electronics)` checks |
| Collision | `collision_system.py:67,71` | `beam_comp.calculate_hit_chance()` method |
| Projectiles | `projectile_manager.py:100-101` | `source_weapon.get_damage()` access |

### UI & Rendering (P2) - 25+ Findings
| Area | File | Key Issues |
|------|------|------------|
| Builder Panels | `detail_panel.py` | Legacy imports, `type_str` display |
| Weapons Panel | `weapons_panel.py` | 10+ `getattr(weapon, ...)` calls |
| Modifier Logic | `modifier_logic.py:123,161` | `data.get('firing_arc')` reads |
| Battle UI | `battle_ui.py:135-162` | Debug overlay legacy attributes |
| Rendering | `rendering.py:123` | `type_str == 'Armor'` color check |

### Data Files (P2)
| File | Issue |
|------|-------|
| `modifiers.json` | 10+ entries use `allow_types`/`deny_types` with legacy class names |
| `components.json:481` | `"PointDefense": true` legacy flag |
| `ship_validator.py:113,136` | `type_str` validation rules |

### Test Suite - 20+ Findings
| File | Key Issues |
|------|------------|
| `test_components.py` | `isinstance(Weapon)` assertions |
| `test_ship_stats.py` | Direct `Engine()` instantiation, legacy data dicts |
| `test_combat.py` | `isinstance(Bridge)` checks |
| `test_pdc.py` | `MockPDC(BeamWeapon)` inheritance |
| `test_modifiers.py` | `isinstance(ProjectileWeapon)` assertions |
| `test_strategy_system.py` | `c1.damage = 10` mock pattern |

---

## 3. Legacy Subclasses to Remove (Stage 6)

From `components.py`:
- `Bridge` (line 649)
- `Weapon` (line 655)  
- `ProjectileWeapon` (line 731)
- `BeamWeapon` (line 799)
- `SeekerWeapon` (line 862)
- `Engine` (line 750)
- `Thruster` (line 763)
- `Shield` (line 943)
- `COMPONENT_TYPE_MAP` (line 1021)
- `_instantiate_abilities` shim section (lines 182-296)

---

## 4. Key Technical Patterns

### Replace isinstance Checks
```python
# BEFORE (Legacy)
if isinstance(comp, Weapon):
    damage = comp.damage

# AFTER (Ability-based)
if comp.has_ability('WeaponAbility'):
    damage = comp.get_ability('WeaponAbility').damage
```

### Replace Direct Attribute Access
```python
# BEFORE (Legacy)
range_val = comp.range
firing_arc = comp.firing_arc

# AFTER (Ability-based)
weapon_ab = comp.get_ability('WeaponAbility')
range_val = weapon_ab.range
firing_arc = weapon_ab.firing_arc
```

### Replace Type String Checks
```python
# BEFORE (Legacy)
if comp.type_str == "Engine":

# AFTER (Ability-based)
if comp.has_ability('CombatPropulsion'):
```

---

## 5. Test Verification Commands

```powershell
# Run full suite
python -m pytest unit_tests/ -n 16 --tb=no -q

# Check for remaining isinstance patterns
Select-String -Path "*.py" -Pattern "isinstance\(.*, (Engine|Weapon|Shield|Thruster)\)"
```

---

## 6. Next Steps

1. **Stage 1**: Fix shield bug (`ship_stats.py:325-330`) + delete `builder.py`
2. **Stage 2**: Core logic migration (combat, AI, ship)
3. **Stage 3**: UI/rendering fixes
4. **Stage 4**: Data file updates (`modifiers.json`)
5. **Stage 5**: Test suite updates
6. **Stage 6**: Delete legacy subclasses from `components.py`

See `implementation_plan.md` for full line-by-line details.
