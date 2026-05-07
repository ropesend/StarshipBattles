# Duplication Review: Core, Engine, AI, Research & Assets

**Scope:** `game/core/`, `game/engine/`, `game/ai/`, `game/research/`, `game/assets/`, `game/app.py`, `game/exit_dialog.py`, `game/__init__.py`
**Date:** 2026-03-24
**Reviewer:** Claude Code Agent

---

## Summary

Overall, the target directories are **relatively clean** in terms of duplication. Many prior consolidation projects (PROJ-21, PROJ-38, PROJ-45, PROJ-108, PROJ-192, PROJ-204) have already addressed the most common duplication patterns (ValidationResult, registry access, layer iteration, combat_utils extraction). The remaining findings are mostly minor, with one major finding around the `_has_attrs` helper duplication across protocol modules.

**Findings:** 7 total (1 MAJOR, 6 MINOR)

---

## Findings

#### MAJOR: `_has_attrs` Helper Duplicated Across 3 Protocol Modules
**ID:** DUP-CEA-001
**Location:** `game/core/protocols.py:694`, `game/ai/protocols.py:174`, `game/simulation/interfaces/entity_protocols.py:480`, `game/simulation/interfaces/ability_protocols.py:315`
**Issue:** The exact same helper function is copy-pasted in 4 separate files:
```python
def _has_attrs(obj: Any, *attrs: str) -> bool:
    """Check if obj has all specified attributes (duck typing helper)."""
    return all(hasattr(obj, attr) for attr in attrs)
```
Each module defines its own private copy of this identical one-liner. All 4 implementations are byte-for-byte identical (minus docstrings).
**Impact:** Not a maintenance risk for such a simple function, but it sets a bad precedent. If the implementation ever needs to change (e.g., adding logging, handling mock objects differently), all 4 copies must be found and updated. More importantly, it signals a missing shared utility.
**Recommendation:** Extract to `game/core/protocols.py` as a public function `has_attrs()` (or keep it private as `_has_attrs` in core and import from there). The AI and simulation protocol modules should import it from core. This respects the layer dependency direction: core has no dependencies, AI/simulation can import from core.
**Effort:** Simple

---

#### MINOR: `TICK_DURATION` Class Constants Duplicate `PhysicsConfig.TICK_RATE`
**ID:** DUP-CEA-002
**Location:** `game/ai/behaviors.py:192` (AttackRunBehavior), `game/ai/behaviors.py:274` (FormationBehavior)
**Issue:** Two behavior classes define their own class constant `TICK_DURATION: float = PhysicsConfig.TICK_RATE` and then use `self.TICK_DURATION` throughout their methods. This creates an unnecessary indirection that duplicates the constant assignment.
**Impact:** Low. The aliasing is technically harmless since both resolve to the same value. However, it introduces a maintenance risk if someone changes one alias but not the other, or if someone reads the code and wonders whether TICK_DURATION might differ from TICK_RATE.
**Recommendation:** Use `PhysicsConfig.TICK_RATE` directly in method bodies. The class constant aliases add no value since the config is already a named constant with clear semantics.
**Effort:** Simple

---

#### MINOR: `SimulationConstants.TICKS_PER_SECOND` vs `PhysicsConfig.TICK_RATE` - Redundant Tick Rate Constants
**ID:** DUP-CEA-003
**Location:** `game/core/constants.py:65` (`TICKS_PER_SECOND = 100`) and `game/core/config.py:97` (`TICK_RATE: float = 0.01`)
**Issue:** These are semantic inverses of each other (100 TPS = 0.01 seconds/tick). They exist in two different configuration classes with no explicit link between them. A change to one without the other creates an inconsistency.
**Impact:** Low risk but conceptually confusing. Two different modules define the same concept from two different perspectives without referencing each other.
**Recommendation:** Define one as the canonical value and derive the other. For example, `TICK_RATE = 1.0 / TICKS_PER_SECOND` or vice versa. Place both in the same class or explicitly cross-reference.
**Effort:** Simple

---

#### MINOR: `resources.py` Imports `json` Directly Despite Using `json_utils`
**ID:** DUP-CEA-004
**Location:** `game/core/resources.py:11`
**Issue:** The file imports `json` at the top level even though the actual JSON loading is done via `load_json_required` from `json_utils`. The `json` import is only used in exception handlers (catching `json.JSONDecodeError`). However, `load_json_required` already raises `json.JSONDecodeError` naturally, so the explicit import is needed for the exception type.
**Impact:** Minimal. The `json` import is actually needed for the exception type in the `except` clause. However, the error handling in `load_resources_data` duplicates the same error-handling pattern that `load_json` (the safe variant) already provides internally: catch FileNotFoundError, JSONDecodeError, PermissionError and return a default.
**Recommendation:** Replace the manual error handling with `load_json(resolved_path, default=None)` and check for None, which would eliminate the `import json` and the four separate `except` blocks. The function already has a "return defaults" fallback -- using `load_json` would consolidate this.
**Effort:** Simple

---

#### MINOR: Inline Angle Normalization in `projectile.py` Duplicates Pattern from `core/math.angle_diff`
**ID:** DUP-CEA-005
**Location:** `game/simulation/entities/projectile.py:158-165`
**Issue:** The projectile seeker tracking code manually normalizes an angle difference to [-180, 180]:
```python
angle_diff = current_dir.angle_to(desired_dir)
if angle_diff > 180:
    angle_diff -= 360
elif angle_diff < -180:
    angle_diff += 360
```
This is the same normalization that `game.core.math.angle_diff()` performs, but applied to a different input (Vector2.angle_to result vs two absolute angles). The core function handles the same mathematical concept.
**Impact:** Low. The projectile code works with Vector2's `angle_to()` method which returns a different range than absolute angles, so the function signature doesn't match exactly. Still, the normalization logic is duplicated.
**Recommendation:** Consider adding a `normalize_angle_diff(angle: float) -> float` utility to `game/core/math.py` that just does the [-180, 180] normalization without computing the diff itself. Both `angle_diff()` and the projectile code could use it.
**Effort:** Simple

---

#### MINOR: `quickstart_builder.py` Uses Raw `json.load()` Instead of `json_utils`
**ID:** DUP-CEA-006
**Location:** `game/strategy/quickstart_builder.py:258`
**Issue:** This file uses `json.load(f)` directly rather than the project's canonical `load_json` / `load_json_required` from `game.core.json_utils`. The json_utils module's docstring explicitly states: "Do NOT use json.load/json.dump directly for file operations in game/."
**Impact:** Minor consistency issue. The direct `json.load()` call bypasses the centralized error handling and logging that `json_utils` provides.
**Recommendation:** Replace with `load_json_required()` or `load_json()` from `game.core.json_utils`.
**Effort:** Simple

---

#### MINOR: Similar `_flee_direction` Logic Used in Multiple AI Behaviors
**ID:** DUP-CEA-007
**Location:** `game/ai/behaviors.py:71-85` (module-level function), used by `FleeBehavior.update()` (line 115), `KiteBehavior.update()` (line 163), `AttackRunBehavior.update()` (line 227)
**Issue:** The `_flee_direction` function is well-extracted as a shared helper. However, the flee-toward-a-point pattern (compute flee direction, scale by FLEE_DISTANCE, navigate) is repeated almost identically in `FleeBehavior` and `AttackRunBehavior`:
```python
# FleeBehavior
flee_dir = _flee_direction(ship_pos, target.position)
flee_pos = ship_pos + flee_dir * self.FLEE_DISTANCE
self.controller.navigate_to(flee_pos, stop_dist=0)

# AttackRunBehavior (retreat phase)
flee_dir = _flee_direction(ship_pos, target.position)
flee_pos = ship_pos + flee_dir * self.FLEE_DISTANCE
self.controller.navigate_to(flee_pos, stop_dist=0)
```
These are 3 identical lines duplicated in both behaviors.
**Impact:** Low. Only 3 lines, but it's a recognizable pattern.
**Recommendation:** Consider extracting a `_navigate_away_from(controller, ship_pos, target_pos, distance)` helper function, or leave as-is given the small duplication. This is borderline -- not worth a refactor on its own.
**Effort:** Simple (but low priority)

---

## Items NOT Flagged (Clean Patterns)

The following areas were reviewed and found to be clean:

1. **Singleton pattern** -- All 7+ singletons use `SingletonMeta` correctly with consistent `clear()`/`reset()` patterns. No handrolled singletons found.

2. **Registry/DI pattern** -- `DefaultRegistryProvider`, `TestRegistryProvider`, and `GameRegistries` are well-separated. No duplicate registry access patterns.

3. **Validation pattern** -- `ValidationResult` is properly consolidated in `game/core/validation.py` per PROJ-21.

4. **JSON loading** -- All files in scope (except the 2 noted) properly use `json_utils`.

5. **Exception hierarchy** -- Clean, no duplicate exception definitions.

6. **Layer iterator** -- Properly consolidated in `game/core/patterns/layer_iterator.py` per PROJ-204.

7. **Combat utils** -- Well-consolidated from PROJ-108. `get_position`, `safe_distance`, `get_hp_percent`, `is_in_pdc_arc` are all single-source.

8. **Protocol definitions** -- Core protocols, AI protocols, and simulation protocols are properly separated by layer concern. No overlapping protocol definitions (each protocol addresses a different entity type).

9. **Research system** -- Clean, self-contained with no duplication within or outside.

10. **AssetManager** -- Clean singleton with proper caching. No duplicate asset loading patterns.

---

## Top 5 Priority List

| Priority | ID | Title | Severity | Effort |
|----------|-----|-------|----------|--------|
| 1 | DUP-CEA-001 | `_has_attrs` duplicated in 4 protocol modules | MAJOR | Simple |
| 2 | DUP-CEA-003 | TICKS_PER_SECOND vs TICK_RATE redundant constants | MINOR | Simple |
| 3 | DUP-CEA-004 | resources.py manual error handling duplicates load_json | MINOR | Simple |
| 4 | DUP-CEA-006 | quickstart_builder uses raw json.load() | MINOR | Simple |
| 5 | DUP-CEA-005 | Inline angle normalization in projectile.py | MINOR | Simple |

---

## Conclusion

The codebase in these directories is in good shape regarding duplication. Prior refactoring projects have been thorough. The only actionable MAJOR finding is the `_has_attrs` duplication (DUP-CEA-001), which should be consolidated into `game/core/protocols.py` and imported by other protocol modules. The remaining findings are minor consistency improvements that could be addressed opportunistically.
