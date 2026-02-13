# Legacy System Holdovers Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 71
- **Total Issues Found:** 9
- **Critical:** 1 | **Major:** 3 | **Minor:** 4 | **Info:** 1

## Findings

#### CRITICAL: String-to-Enum Migration Support Code in BattleEngine
**ID:** LEG-SIM-001
**Location:** `game/simulation/systems/battle_engine.py:416-422`
**Issue:** The battle engine contains migration support code that converts string attack types to Enum values. Comment explicitly states this is "migration support". The code path handles the case where `raw_type` is a string and converts it to `AttackType(raw_type)`.
**Impact:** This backward compatibility layer suggests some code path is still passing string attack types instead of using the proper `AttackType` enum. This creates confusion about which format is authoritative and adds unnecessary runtime overhead.
**Code:**
```python
# Map string types to Enum if necessary (migration support)
attack_type = raw_type
if isinstance(raw_type, str):
     try:
         attack_type = AttackType(raw_type)
     except ValueError:
         pass # Unknown type string, keep as is
```
**Recommendation:** Trace all attack creation paths and ensure they use `AttackType` enum directly. Remove this migration support code once all call sites are updated.
**Effort:** Medium

---

#### MAJOR: V1 Modifier Format Validation Code Still Present
**ID:** LEG-SIM-002
**Location:** `game/simulation/components/modifier_schema.py:47-49`
**Issue:** The `is_v2_format()` function explicitly checks for and rejects V1 format modifiers. Per the docstring, "V1 format (dict-based effects with 'special' handlers) is no longer supported." However, the code still contains logic to detect V1 format:
```python
# V1 format: effects is a dict (with 'special' or direct stats)
if isinstance(effects, dict):
    return False
```
**Impact:** If V1 format is truly no longer supported, this detection code is dead code. If it's being used for validation errors, the function should raise an exception rather than silently returning False.
**Recommendation:** Since V1 is deprecated, either: (1) Remove V1 detection entirely and assume all inputs are V2, or (2) Raise a clear exception when V1 format is detected to surface any remaining V1 data files.
**Effort:** Simple

---

#### MAJOR: Defensive hasattr Check for Always-Present Attribute
**ID:** LEG-SIM-003
**Location:** `game/simulation/systems/battle_engine.py:407`
**Issue:** The code `if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:` performs a hasattr check on an attribute that is always initialized in `Ship.__init__` (line 158: `self.just_fired_projectiles: List[Any] = []`).
**Impact:** This defensive pattern suggests uncertainty about whether the attribute exists, which could indicate: (1) incomplete migration from an older API, (2) defensive coding for non-Ship entities, or (3) unnecessary caution. It adds minor runtime overhead and reduces code clarity.
**Recommendation:** If all objects in `self.ships` are guaranteed to be `Ship` instances, remove the hasattr check. If non-Ship entities are possible, add type hints and explicit checks.
**Effort:** Simple

---

#### MAJOR: retreat_status Attribute Accessed via hasattr Pattern
**ID:** LEG-SIM-004
**Location:** `game/simulation/managers/retreat_manager.py:170-171`, `game/simulation/battle_state.py:317`
**Issue:** Multiple places check `if hasattr(ship, 'retreat_status'):` before accessing the attribute. This suggests `retreat_status` is not a standard attribute on the Ship class, which creates inconsistency.
**Code:**
```python
# retreat_manager.py:170
if hasattr(ship, 'retreat_status'):
    ship.retreat_status = "escaped"

# battle_state.py:317
if hasattr(ship, 'retreat_status'):
```
**Impact:** Optional attributes accessed via hasattr create implicit contracts that are hard to maintain. Either all ships should have this attribute (add to Ship.__init__), or a separate retreat state tracking system should be used.
**Recommendation:** Add `retreat_status` as a formal attribute on Ship with a default value (e.g., `None` or `"active"`), then remove hasattr checks.
**Effort:** Simple

---

#### MINOR: Fallback Pattern Comment Suggesting Incomplete DI Migration
**ID:** LEG-SIM-005
**Location:** `game/simulation/entities/ship.py:340, 345, 395`
**Issue:** Multiple comments in Ship class reference "fallback" patterns:
- Line 340: `# PROJ-42: Use registries (always set via fallback in __init__)`
- Line 345: `# Fallback if no layers defined in vehicle class`
- Line 395: `# Fallback if no mass limits defined`
These suggest defensive coding for edge cases that may no longer occur now that strict DI is enforced (per PROJ-50).
**Impact:** These fallbacks may be dead code paths if strict DI ensures registries are always provided with complete data.
**Recommendation:** Review whether these fallback paths are ever executed in production. If not, consider raising exceptions instead to surface data configuration issues early.
**Effort:** Simple

---

#### MINOR: Ability Manager Fallback for Module Identity Drift
**ID:** LEG-SIM-006
**Location:** `game/simulation/components/ability_manager.py:57`
**Issue:** Code comment reads `# [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.` This indicates a workaround for a testing infrastructure issue rather than production code.
**Impact:** Test-specific workarounds in production code reduce clarity and may mask real issues. This suggests the test infrastructure could be improved.
**Recommendation:** Investigate the Module Identity Drift issue in tests and fix the root cause. Then remove this fallback from production code.
**Effort:** Medium

---

#### MINOR: Component Fallback Delegation Pattern
**ID:** LEG-SIM-007
**Location:** `game/simulation/components/component.py:200-222`
**Issue:** Three methods (`get_ability`, `get_ability_value`, `get_ability_state`) have nearly identical structure with "fallback" delegation to AbilityManager:
```python
# Fallback: delegate to AbilityManager (for edge cases)
```
This pattern is repeated three times, suggesting the `_ability_index` optimization may not be complete or the fallback is unnecessary.
**Impact:** If `_ability_index` is always properly populated, these fallbacks are dead code. If not, the index population logic has a bug.
**Recommendation:** Verify that `_ability_index` is always populated correctly. If so, convert fallbacks to assertions or remove them.
**Effort:** Simple

---

#### MINOR: Unused AbilityStatBinding.describe() Method
**ID:** LEG-SIM-008
**Location:** `game/simulation/components/abilities/stat_keys.py:170-177`
**Issue:** The `AbilityStatBinding.describe()` method is defined but grep found no callers in the codebase. This appears to be dead code.
**Code:**
```python
def describe(self) -> str:
    """Return a human-readable description of this binding."""
    op_desc = {
        'multiply': 'multiplied by',
        'add': 'increased by',
        'set': 'set to',
    }
    return f"{self.attribute_name} is {op_desc[self.operation]} {self.stat_key.value}"
```
**Impact:** Minor dead code. The method was likely added for debugging/introspection but never integrated into the UI or logging.
**Recommendation:** Either integrate this into the modifier introspection system or remove it.
**Effort:** Simple

---

#### INFO: TechPresetLoader Used Only in Tests
**ID:** LEG-SIM-009
**Location:** `game/simulation/systems/tech_preset_loader.py`
**Issue:** The `TechPresetLoader` class is defined in the simulation layer but grep shows it's only used in test files and documentation. It was designed for "standalone workshop mode" but may not be actively used in production.
**Impact:** The class is well-tested and documented, so this is not a problem. However, it may be a candidate for moving to a test utilities package if it's truly only used for testing.
**Recommendation:** No action required. If this is actively used in standalone workshop mode, add a usage reference. If not, consider marking as test-only utility.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **LEG-SIM-001 (CRITICAL):** String-to-Enum migration support in BattleEngine - This is an active backward compatibility layer that should be removed once all attack creation paths use AttackType enum directly.

2. **LEG-SIM-004 (MAJOR):** retreat_status hasattr pattern - This creates an implicit contract that's hard to maintain. Adding retreat_status as a formal Ship attribute would improve code clarity.

3. **LEG-SIM-002 (MAJOR):** V1 Modifier Format detection code - If V1 is truly deprecated, this should either be removed or converted to raise exceptions when V1 format is encountered.

4. **LEG-SIM-003 (MAJOR):** just_fired_projectiles hasattr check - Unnecessary defensive code for an always-present attribute.

5. **LEG-SIM-006 (MINOR):** Module Identity Drift workaround - Test infrastructure issue leaking into production code should be addressed at the root.
