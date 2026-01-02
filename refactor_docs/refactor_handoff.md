# Ability System Refactor - Handoff & Context

## 1. High-Level Context
**Refactor Goal**: Transition from Inheritance-based Components (`Engine`, `Weapon`) to Composition-based Components (`Component` + `Abilities`).

**Current Phase**: Phase 7 In Progress (Legacy Removal)  
**Tests**: 470/470 PASSED (as of 2026-01-02 14:45 PST)

**Status Summary**:
- Phase 1 ✅ Foundation (abilities.py created)
- Phase 2 ✅ Core Refactor (Component class, Legacy Shim)
- Phase 3 ✅ Stats & Physics Integration
- Phase 4 ✅ Combat System Complete
- Phase 5 ✅ UI & Capabilities Complete
- Phase 6 ✅ Data Migration COMPLETE
- **Phase 7 🔄 Legacy Removal (IN PROGRESS)**
  - Stage 1 ✅ Critical Fixes (Complete)
  - Stage 2 ✅ Core Logic (Complete)
  - Stage 3 ✅ UI & Rendering (Complete)
  - Stage 4 ✅ Data Files (Complete)
  - Stage 5 ✅ Test Suite (Complete)
  - Stage 6 ⏳ The Big Delete (Not started - OPTIONAL)

---

## 2. Latest Session Summary (2026-01-02)

### Completed This Session

**Stage 1: Critical Fixes** ✅
1. Deleted `ship_stats.py:325-330` - Fixed shield overwrite bug
2. Deleted `builder.py` - Removed dead code
3. Fixed `ship_stats.py:72,78,182` - Replaced `major_classification == "Armor"` with ability check

**Stage 2: Core Logic** ✅ (7/7 complete)
1. ✅ `ship_combat.py` - Replaced 15+ `comp.damage/range/firing_arc` with `weapon_ab.*`
2. ✅ `ship_combat.py` - Replaced `comp.can_fire()` and `comp.fire()` with `weapon_ab.*`
3. ✅ `collision_system.py:67,71` - Updated to use `BeamWeaponAbility.calculate_hit_chance()` and `.get_damage()`
4. ✅ `projectile_manager.py:100-127` - Updated damage calculation to use `WeaponAbility.get_damage()`
5. ✅ `ai.py:188` - Replaced `hasattr(c, 'damage')` with `c.has_ability('WeaponAbility')`
6. ✅ `ai.py:372,383` - Replaced `comp.range/firing_arc` with `weapon_ab.*` access
7. ✅ `ship.py:598,607,610` - Replaced `isinstance(Sensor/Electronics/Armor)` with ability-based checks

**Stage 3: UI & Rendering** ✅
1. ✅ `detail_panel.py:5-7` - Removed unused legacy class imports
2. ✅ `schematic_view.py:125-127` - Replaced `getattr(weapon, ...)` with `weapon_ab.*` access
3. ✅ `battle_ui.py:135-162` - Replaced debug overlay direct attribute access with ability-based access
4. ✅ `rendering.py:123` - Replaced `type_str == 'Armor'` with ability/classification check

**Stage 4: Data Files** ✅
- Verified `modifiers.json` supports both `allow_types` and `allow_abilities`
- Confirmed no `PointDefense: true` legacy flags in `components.json`
- Removed unused `Weapon` import from `ship_validator.py`

**Stage 5: Test Suite** ✅
- All 470 unit tests passing with current ability-based patterns

### Stage 6: The Big Delete (OPTIONAL)
Not started - this stage involves deleting legacy subclasses which is a breaking change.
Consider deferring until next major release.

---

## 3. Context Window Reporting Requirement

> [!IMPORTANT]
> **All agents working on this refactor MUST report context window usage.**

### When to Report
- At the start of each session after reviewing docs
- After completing each major task/stage
- When prompted by user
- When approaching warning threshold

### Required Format
```
## 📊 Context Status
| Tokens Remaining | ~XX,000 |
| Usage | ~XX% used, ~XX% remaining |
| Status | 🟢 Healthy / 🟡 Caution / 🔴 Critical |
```

### Thresholds
- 🟢 **Healthy**: >50% remaining
- 🟡 **Caution**: 35-50% remaining (start summarizing)
- 🔴 **Critical**: <35% remaining (recommend handoff/reset)

---

## 4. Phase 7 Audit Summary (14 Agents Completed)

### Critical Issues (P0) - FIXED ✅
| Finding | File:Line | Issue | Status |
|---------|-----------|-------|--------|
| Shield Bug | `ship_stats.py:325-330` | Overwrites correct ability aggregation | ✅ FIXED |
| Dead Code | `builder.py` | Entire file unused | ✅ DELETED |

### Core Logic (P1) - Mixed Status
| Area | File | Key Issues | Status |
|------|------|------------|--------|
| Combat | `ship_combat.py` | 15+ direct `comp.damage/range` accesses | ✅ FIXED |
| AI | `ai.py:188` | `hasattr(c, 'damage')` for weapon detection | ⏳ TODO |
| Ship | `ship.py:598,607` | `isinstance(Sensor/Electronics)` checks | ⏳ TODO |
| Collision | `collision_system.py:67,71` | `beam_comp.calculate_hit_chance()` method | ✅ FIXED |
| Projectiles | `projectile_manager.py:100-101` | `source_weapon.get_damage()` access | ✅ FIXED |

### UI & Rendering (P2) - 25+ Findings (Not Started)
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

## 5. Legacy Subclasses to Remove (Stage 6)

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

## 6. Key Technical Patterns

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

## 7. Test Verification Commands

```powershell
# Run full suite
python -m pytest unit_tests/ -n 16 --tb=no -q

# Check for remaining isinstance patterns
Select-String -Path "*.py" -Pattern "isinstance\(.*, (Engine|Weapon|Shield|Thruster)\)"
```

---

## 8. Next Steps for New Agent

1. **Report context usage** (see Section 3)
2. **Complete Stage 2**: Remaining items (ai.py, ship.py)
3. **Stage 3**: UI/rendering fixes
4. **Stage 4**: Data file updates (`modifiers.json`)
5. **Stage 5**: Test suite updates
6. **Stage 6**: Delete legacy subclasses from `components.py`

See `task.md` for the detailed checklist.
