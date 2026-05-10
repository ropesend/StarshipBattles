# PROJ-387 — Galaxy backward-compat property forwarder removal — Code Review

**Request:** req_20260508_231157_6165cf
**Reviewer:** OpenCode (ocode-review-request)
**Date:** 2026-05-08T23:20:00Z
**Review Mode:** normal
**Branch:** feat/03c-phase-aware-execution
**Recommendation:** APPROVE_WITH_FOLLOW_UP

---

## Executive Summary

PROJ-387 deleted 5 backward-compat `@property` forwarders on `Galaxy` (`_global_hex_planets`, `_global_hex_zones`, `_global_hex_warp_points`, `_planet_to_system`, `_zone_to_system`) and migrated 3 production readers + 8 test files to access `galaxy._state.<field>` directly. The work is technically correct — no live callers of the deleted forwarders remain, behavior is preserved, and no new shims were introduced. However, the migration traded one form of private access for another, and a stale guard test risks masking future regressions.

**Findings summary:** 0 CRITICAL / 2 MAJOR / 3 MINOR / 8 INFO

---

## Findings

### MAJ-001 — Stale grandfathered entries in `test_galaxy_state_encapsulation.py` defeat guard's purpose

**File:** `tests/unit/strategy/data/test_galaxy_state_encapsulation.py:45-52`
**Severity:** MAJ

The guard test defines `GRANDFATHERED_EXTERNAL_READS` with 5 (file, attr) pairs corresponding to the now-migrated files:

```python
GRANDFATHERED_EXTERNAL_READS = frozenset({
    ("game/strategy/engine/handlers/movement.py", "_global_hex_warp_points"),
    ("game/strategy/services/fleet_navigation_service.py", "_global_hex_warp_points"),
    ("game/ui/screens/strategy_render/hex_outlines.py", "_global_hex_warp_points"),
    ("game/ui/screens/strategy_render/hex_outlines.py", "_global_hex_planets"),
    ("game/ui/screens/strategy_render/hex_outlines.py", "_global_hex_zones"),
})
```

After PROJ-387, **none of these files contain AST `Attribute` nodes with the restricted underscored attr names**. The migrated access pattern (`galaxy._state.global_hex_warp_points`) produces an AST with `attr='global_hex_warp_points'` (no underscore), which is NOT in `RESTRICTED_ATTRS`. Therefore:

1. The grandfathered entries filter nothing (there are no violations to filter).
2. If someone **re-introduces** `galaxy._global_hex_warp_points` access in one of these files, the guard would **silently grandfather it** and fail to detect the regression.

**Recommendation:** Remove all 5 entries from `GRANDFATHERED_EXTERNAL_READS`. The `test_allowed_files_actually_use_at_least_one_index` test on line 110 will also need attention — it currently expects zero entries and will pass, but its docstring says "Kept even though the current allow-list is empty" (referring to `ALLOWED_FILES`, not `GRANDFATHERED_EXTERNAL_READS`).

---

### MAJ-002 — `_state.<field>` access trades one private API for another; incomplete encapsulation fix

**Files affected:**
- `game/strategy/engine/handlers/movement.py:242` — `session.galaxy._state.global_hex_warp_points`
- `game/strategy/services/fleet_navigation_service.py:315` — `galaxy._state.global_hex_warp_points`
- `game/ui/screens/strategy_render/hex_outlines.py:34,45,57` — `r.galaxy._state.global_hex_planets|_zones|_warp_points`

**Severity:** MAJ

**Analysis:**

The migration replaces `galaxy._global_hex_warp_points` (a private `@property` forwarder on `Galaxy`) with `galaxy._state.global_hex_warp_points` (accessing `._state`, a private instance attribute on `Galaxy`, then reading a public field on `GalaxyState`). Both paths are Private API use on `Galaxy`:

| Before (deleted) | After (current) | Privateness |
|---|---|---|
| `galaxy._global_hex_planets` | `galaxy._state.global_hex_planets` | `._state` is private (single-underscore) |
| `galaxy._global_hex_zones` | `galaxy._state.global_hex_zones` | Same |
| `galaxy._global_hex_warp_points` | `galaxy._state.global_hex_warp_points` | Same |
| `galaxy._planet_to_system` | `galaxy._state.planet_to_system` | Same |
| `galaxy._zone_to_system` | `galaxy._state.zone_to_system` | Same |

**Is this meaningful or cosmetic?**

It is **incrementally meaningful** — the 5 forwarder definitions (28 lines of @property boilerplate + docstring) are gone, and the old forwarder names can no longer be inadvertently used. The migration reduces the surface area from "5 forwarders + 3 reader sites = 8 things to track" to "3 reader sites accessing `._state` directly."

However, the **same fundamental encapsulation breach** persists. The `Galaxy` class docstring (line 38-39) says "Public attribute reads (galaxy.systems etc.) are preserved via @property forwarders." The 3 external readers now bypass those forwarders entirely to reach into `._state`. This is equivalent to the PRE-PROJ-387 state where they bypassed Galaxy's public API via the underscore-prefixed property forwarders.

The `GalaxyState` module docstring (`galaxy_state.py:15-16`) explicitly acknowledges this design: "Galaxy re-exposes the under-prefixed names as @property forwarders for backwards-compat with the five grandfathered external read sites." That statement is now inaccurate — the forwarders are deleted, and the "grandfathered" sites now access `._state` directly.

**Recommendation:** A follow-up PROJ should expose `galaxy.state` as a public property returning `GalaxyState`, then migrate the 3 production readers to `galaxy.state.global_hex_*`. This would make the access pattern both greppable and officially supported:

```python
# Proposed public API
class Galaxy:
    @property
    def state(self) -> GalaxyState:
        return self._state
```

This is outside PROJ-387 scope, but should be tracked. The current state is defensible as an interim step — it removes dead code (the forwarders) while keeping callers working.

---

### MIN-003 — Guard test docstring is out of date

**File:** `tests/unit/strategy/data/test_galaxy_state_encapsulation.py:3-16`
**Severity:** MIN

The module docstring still describes the five private indexes as:
- "legacy compatibility properties" (line 5) — DELETED
- "compatibility-only surfaces that external callers must not read" (line 11) — No longer exist
- "except for the explicit grandfathered sites tracked below" (line 11-12) — Grandfathered sites are gone

The docstring should be updated to reflect the post-PROJ-387 state where the restricted attribute names no longer appear in any production code and the grandfathered list should be empty.

---

### MIN-004 — `galaxy_state.py` docstring references deleted architecture

**File:** `game/strategy/data/galaxy_state.py:13-16`
**Severity:** MIN

The docstring states:
> "Galaxy re-exposes the under-prefixed names as @property forwarders for backwards-compat with the five grandfathered external read sites."

The 5 forwarders (except `_next_planet_id`/`_next_fleet_id`) have been deleted. The grandfathered external read sites now access `GalaxyState` fields via `._state`. The docstring should describe the current architecture.

---

### MIN-005 — Plan `Key Files` table references wrong file path

**File:** `Projects/active_projects/PROJ-387/plan.md:40`
**Severity:** MIN

The "Key Files" table lists `game/strategy/data/movement.py` as the first external reader. This file does not exist. The actual file is `game/strategy/engine/handlers/movement.py`. The `phase_1_checklist.md` (Task 1.1 line 16) correctly notes the correction, but the plan itself has not been fixed.

---

### INFO-006 — Removal completeness confirmed (instruction 1)

Grep `galaxy\._(global_hex|planet_to_system|zone_to_system)\b` across the entire repo returns zero matches in live production/test code. Only audit/tracking documentation references these patterns. AST scanning confirms no `galaxy.py` property definitions for these names remain.

---

### INFO-007 — `_next_planet_id` and `_next_fleet_id` correctly preserved (instruction 6)

**File:** `game/strategy/data/galaxy.py:93-107`

Both properties remain in place with getter/setter delegation to `_state.next_planet_id` / `_state.next_fleet_id`. These were correctly excluded from deletion since they have setters and are genuinely needed for `to_dict()`/`from_dict()`.

---

### INFO-008 — No new shims, wrappers, or fallbacks introduced (instruction 7)

The change is a clean delete of 5 forwarder definitions plus direct caller migration. No compatibility wrappers, deprecation warnings, helper functions, or fallback mechanisms were added. Rule 3 (no compat shims) is satisfied.

---

### INFO-009 — Behavior preservation: mutation semantics confirmed (instruction 3)

The deleted forwarders were read-only `@property` returning the underlying dict (e.g., `return self._state.global_hex_warp_points`). The new path `galaxy._state.global_hex_warp_points` returns the **same underlying dict object**. Callers:

- **Read-only** (`fleet_navigation_service.py:315`): `galaxy._state.global_hex_warp_points.get(warp_point_hex)` — same behavior.
- **Mutating** (`galaxy.py:183,234`): `self._state.global_hex_warp_points.pop(...)` and `self._state.global_hex_warp_points[key] = value` — same behavior.
- **Test writes** (`test_galaxy_cleanup.py:86,88`): `galaxy._state.planet_to_system[planet] = system` — writes through to the dict, same behavior.

---

### INFO-010 — `_FakeGalaxyState` test fixture equivalence (instruction 4)

**File:** `tests/unit/strategy/engine/handlers/test_movement_handlers.py:27-30`

```python
class _FakeGalaxyState:
    def __init__(self) -> None:
        self.global_hex_warp_points: dict = {}
```

The fake mirrors the real `GalaxyState.global_hex_warp_points` attribute. Tests populate and read through `session.galaxy._state.global_hex_warp_points` (e.g., line 323: `session.galaxy._state.global_hex_warp_points[warp_hex] = object()`), matching the production access pattern (`galaxy._state.global_hex_warp_points.get(...)`). Test behavior is unchanged — only HOW data is accessed changed.

---

### INFO-011 — Plan path correction confirmed (instruction 5)

`game/strategy/data/movement.py` does not exist. The plan's "Key Files" table listed it as the first external reader, but the actual file is `game/strategy/engine/handlers/movement.py`. The correct file was migrated (line 242: `session.galaxy._state.global_hex_warp_points`). `phase_1_checklist.md` Task 1.1 line 16 correctly notes the correction.

---

### INFO-012 — PROJ-385 and PROJ-388 files unchanged (instruction 9)

`git log --all --grep="PROJ-385\|PROJ-388"` returns no commits. `git diff` confirms no changes to their scope files. The prior projects' changes are preserved.

---

### INFO-013 — Pre-existing `test_pathfinder_attached_after_init` failure is unrelated (instruction 10)

The `_intercept` attribute referenced in the `test_pathfinder_attached_after_init` test is created by `_intercept_for(galaxy)` in `game/strategy/data/pathfinding.py:64`, which constructs `InterceptCalculator(galaxy._pathfinder)`. This is a completely separate concern from the deleted property forwarders and is not in PROJ-387's scope.

---

### INFO-014 — Coverage: migrated hex_outlines branches are exercised (instruction 11)

`test_hex_outlines.py::test_build_data_combines_player_and_non_player_occupancy` explicitly tests all three migrated iteration paths:
- Planets (`galaxy._state.global_hex_planets`) — line 47
- Zones (`galaxy._state.global_hex_zones`) — line 50
- Warp points (`galaxy._state.global_hex_warp_points`) — line 54

No dead-branch migrations.

---

### INFO-015 — Scope discipline: GalaxyState public API unchanged (instruction 8)

`GalaxyState` has 11 fields (line 42-64): `radius`, `systems`, `name_map`, `planets_by_id`, `fleets_by_id`, `planet_to_system`, `global_hex_planets`, `global_hex_zones`, `global_hex_warp_points`, `zone_to_system`, `next_planet_id`, `next_fleet_id`. None were renamed, added, or removed. `Galaxy._state` was not renamed. Scope discipline holds.

---

## Verification Matrix

This is not a follow-up review — no parent findings to verify.

---

## Recommendation

**APPROVE_WITH_FOLLOW_UP**

The migration is technically correct: zero orphaned callers, behavior preserved, no new shims. The `_state.<field>` access pattern is an incremental improvement over the deleted forwarders.

However, MAJ-001 (stale grandfathered entries in the guard test) should be addressed before merging — it creates a regression-detection gap. MAJ-002 (private-to-private access shift) should be tracked as a follow-up PROJ to expose a public `galaxy.state` property.
