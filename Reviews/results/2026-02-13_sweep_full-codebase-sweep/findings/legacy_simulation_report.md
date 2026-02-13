# Legacy System Holdovers Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 70
- **Sweep Cycle:** 2 (Verification of Cycle 1 findings)
- **Date:** 2026-02-13
- **Total Issues Found:** 4
- **Critical:** 0 | **Major:** 0 | **Minor:** 3 | **Info:** 1

## Status of Previous Findings (Cycle 1)

### RESOLVED Issues

#### LEG-SIM-001 (was CRITICAL): String-to-Enum Migration Support Code
**Status:** RESOLVED
**Evidence:** Grep search for "migration support" and "isinstance(raw_type, str)" returns no matches.
The string-to-enum migration support code has been removed from `battle_engine.py`.

---

#### LEG-SIM-002 (was MAJOR): V1 Modifier Format Validation Code
**Status:** RESOLVED - Correctly Implemented
**Evidence:** The `modifier_schema.py` file (lines 46-52) now raises an explicit ValueError when V1 format is detected:
```python
if isinstance(effects, dict):
    mod_id = modifier.get('id', 'unknown')
    raise ValueError(
        f"Modifier '{mod_id}' uses deprecated V1 format (dict-based effects). "
        f"V1 format is no longer supported. Convert to V2 array format."
    )
```
This is the correct behavior - the code no longer silently returns False but raises a clear exception to surface any V1 data files.

---

#### LEG-SIM-003 (was MAJOR): Defensive hasattr Check for just_fired_projectiles
**Status:** RESOLVED
**Evidence:** Grep search for "hasattr.*just_fired_projectiles" returns no matches.
Line 407 of `battle_engine.py` now directly accesses `s.just_fired_projectiles` without hasattr check:
```python
if s.just_fired_projectiles:
    new_attacks.extend(s.just_fired_projectiles)
```

---

#### LEG-SIM-004 (was MAJOR): retreat_status hasattr Pattern
**Status:** RESOLVED
**Evidence:**
1. `retreat_status` is now a formal attribute on Ship class (line 140): `self.retreat_status: Optional[str] = None`
2. Grep for "hasattr.*retreat_status" returns no matches - all hasattr checks have been removed
3. Direct attribute access is now used throughout

---

### REMAINING Issues

#### MINOR: Module Identity Drift Fallback in AbilityManager
**ID:** LEG-SIM-006
**Location:** `game/simulation/components/ability_manager.py:57-65`
**Issue:** Code contains a fallback for "Module Identity Drift in tests":
```python
# [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.
# When test modules reload ability classes, isinstance() fails due to
# different class objects. This __name__ check provides test isolation.
# Ref: Phase 2 Task 2.5 audit - documented as intentional tech debt.
else:
    for cls in ab.__class__.mro():
        if cls.__name__ == ability_name:
            found.append(ab)
            break
```
**Status:** Still present, documented as intentional tech debt
**Impact:** Test-specific workaround in production code reduces clarity
**Recommendation:** Track in backlog for future test infrastructure improvement
**Effort:** Medium

---

#### MINOR: Component Ability Index Fallback Pattern
**ID:** LEG-SIM-007
**Location:** `game/simulation/components/component.py:199-223`
**Issue:** Three methods use hasattr pattern with fallback:
```python
if hasattr(self, '_ability_index') and ability_name in self._ability_index:
    return list(self._ability_index[ability_name])
# Fallback: delegate to AbilityManager (for edge cases)
return AbilityManager.get_abilities(ability_name, self.ability_instances)
```
**Status:** Still present
**Impact:** If `_ability_index` is always populated, fallbacks are dead code
**Recommendation:** Verify `_ability_index` is always set; convert fallbacks to assertions
**Effort:** Simple

---

#### MINOR: Duplicate Exception Handling in design_loader.py
**ID:** LEG-SIM-NEW-001
**Location:** `game/simulation/services/design_loader.py:118-133`
**Issue:** The final except clause catches exceptions already caught by earlier clauses:
```python
    except json.JSONDecodeError as e:  # Line 118
        ...
    except (KeyError, TypeError, ValueError) as e:  # Line 122
        ...
    except OSError as e:  # Line 126
        ...
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:  # Line 130 - DEAD CODE
        ...
```
Line 130-133 catches the same exceptions as lines 118-128 and will never execute.
**Impact:** Dead code, minor code smell
**Recommendation:** Remove the duplicate exception handling block
**Effort:** Simple

---

#### INFO: TechPresetLoader Only Used in Tests
**ID:** LEG-SIM-009
**Location:** `game/simulation/systems/tech_preset_loader.py`
**Issue:** Well-documented utility class for standalone workshop mode; usage may be limited to tests.
**Status:** Still present, no action needed
**Recommendation:** Document intended use case if actively used in production standalone mode

---

## False Positive Clarifications

#### AbilityStatBinding.describe() - NOT Dead Code
**Location:** `game/simulation/components/abilities/stat_keys.py:170-177`
**Previous Concern:** Was flagged as potentially unused
**Clarification:** Grep shows `.describe()` is actively called in:
- `modifier_introspection.py:72` - `effects_preview.append(effect.describe())`
- `modifier_introspection.py:142` - `effect_descriptions = [e.describe() for e in effects]`
- `modifier_introspection.py:229` - `effect_line = f"  * {effect.describe()}"`
- `modifier_effects.py:93` - `'description': self.describe()`

This method IS used and should NOT be removed.

---

## Top 5 Priority Issues

1. **LEG-SIM-NEW-001 (MINOR):** Duplicate exception handling in design_loader.py - Simple cleanup, dead code removal.

2. **LEG-SIM-007 (MINOR):** Component ability index fallback pattern - Verify if fallbacks are needed.

3. **LEG-SIM-006 (MINOR):** Module Identity Drift workaround - Documented tech debt, track in backlog.

4. (Resolved) All previous CRITICAL/MAJOR issues have been addressed.

5. (Resolved) Migration patterns are complete.

---

## Conclusion

**Cycle 2 Assessment:** The `game/simulation/` directory is in excellent condition.

Key improvements since Cycle 1:
- String-to-Enum migration code removed (CRITICAL resolved)
- retreat_status added as formal Ship attribute (MAJOR resolved)
- hasattr defensive patterns removed (MAJOR resolved)
- V1 modifier rejection now raises exceptions (MAJOR resolved)

Remaining items are MINOR issues with low impact:
- One piece of dead code (duplicate exception handling)
- Two documented fallback patterns for edge cases/tests

The codebase demonstrates clean migration practices with proper error handling for deprecated formats.
