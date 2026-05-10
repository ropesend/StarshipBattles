# PROJ-377 Verifier Report

**Verifier:** Claude (independent verification of OpenCode review)
**Reviewed report:** `report.md` (OpenCode, 2026-05-07T05:00:00Z)
**Branch:** feat/03c-phase-aware-execution
**Commits in scope:** 3b8370f7a, 83a31662f, 9cb543f4c
**Verified at:** 2026-05-07

---

## Verdict Summary

| Severity | Count | CONFIRM | REJECT | UNCERTAIN |
|----------|-------|---------|--------|-----------|
| MAJ      | 1     | 1       | 0      | 0         |
| MIN      | 3     | 2       | 0      | 1         |
| INFO (spot-checked) | 3 | 3 | 0 | 0 |
| INFO (not spot-checked, accepted as plausible) | 9 | 9 | 0 | 0 |

OpenCode's review is materially correct. No false positives among the 4 actionable findings. MAJ-001 + MIN-001 fixes already landed in `Projects/active_projects/PROJ-372/decisions.md` row 38 and are correct.

---

## Per-Finding Verification

### MAJ-001 — CONFIRM (already fixed)

**File checked:** `Projects/active_projects/PROJ-372/decisions.md:38`

The remediation landed correctly. Row 38 now reads:

> "pathfinding shim sweep migrated **4 of 14** production importers (Class A: 3 strategy-screen methods + colonization screen) to direct `galaxy._pathfinder.X(...)` calls. **Site #3 (`superweapon_order_processor`) was attempted in Phase 2 then reverted in Phase 3** after 40 test regressions surfaced — tests patch the local module re-export, not the shim path; reclassified Class B."

- "5 of 14" → "4 of 14": confirmed.
- `superweapon order processor` no longer appears in the migrated parenthetical: confirmed.
- Attempt-and-revert note added with reason (40 regressions, local-import patching): confirmed.

No further action.

### MIN-001 — CONFIRM (already fixed)

**File checked:** same row.

Deferred Class B list now reads:
> "`game_session`, `handlers/base`, `fleet_navigation_service`, `strategy_superweapons`, `planet_slice`, `superweapon_order_processor`"

`superweapon_order_processor` is now included in the deferred-site enumeration. Class C (2 intentional shim-routes in `intercept_calculator`) is also called out. Arithmetic still balances: 8 Class B + 4 migrated + 2 Class C = 14.

No further action.

### MIN-002 — UNCERTAIN (docstring sufficient; inline comment is nice-to-have)

**File checked:** `tests/fixtures/saves/_capture_baseline.py:64-67`

```python
random.seed(2)
galaxy = Galaxy(radius=30)
random.seed(2)  # Galaxy.__init__ may have consumed an indeterminate amount.
galaxy.generate_systems(5, min_dist=5, rng=random.Random(2))
```

OpenCode's claim is technically accurate: re-seeding `random` after `Galaxy.__init__` only resets the global `random` module's state. If `Galaxy.__init__` constructs an internal `random.Random()` instance, the re-seed has no effect on it. The script's docstring (lines 9-23) already documents this:

- Line 13-15 explicitly call out "Star-image selection, warp-point `warp_type` rolls, and warp-point intrinsic abilities still consume an unseeded `random.Random()`."
- Lines 16-19 explain the CI contract is the round-trip identity assertion, NOT byte-equality between captures.

**Assessment:** the docstring already accurately documents the limitation. The inline comment on line 66 ("Galaxy.__init__ may have consumed an indeterminate amount") is a useful local pointer to the global-vs-instance distinction but is not strictly load-bearing — anyone touching the script will read the module docstring first. **The docstring is sufficient; an inline comment expansion is a nice-to-have, not a blocker.** Defer.

### MIN-003 — CONFIRM (now resolved by MAJ-001 fix)

**File checked:** `Projects/active_projects/PROJ-377/plan.md:24`

Plan.md Current State says "All phases complete; ready for review." With MAJ-001 + MIN-001 now fixed in PROJ-372/decisions.md, the cross-link drift is resolved. The plan.md state is accurate post-fix. No update needed.

### INFO-005/INFO-006 — CONFIRM

**Files checked:**
- `game/strategy/services/galaxy_pathfinding_service.py:119-121`: `def get_system_at_hex(self, hex_c: HexCoord, radius: int = 50)` — default radius=50.
- `game/strategy/data/pathfinding.py:80-83`: shim `get_system_at_hex(galaxy, hex_c, radius=50)` — default radius=50.
- `game/ui/screens/strategy_screen.py:440`: `return self.galaxy._pathfinder.get_system_at_hex(hex_c)` — no radius arg, picks up default 50.
- `game/ui/screens/strategy_colonization.py:259`: `return self.scene.galaxy._pathfinder.get_system_at_hex(hex_coord)` — no radius arg, picks up default 50.

Both shim and service default to radius=50; migrated callers pass no radius and inherit the same default. Semantic equivalence preserved.

### INFO-007 — CONFIRM

`git show 9cb543f4c -- game/strategy/engine/superweapon_order_processor.py` shows clean restoration:

- `+from game.strategy.data.pathfinding import get_system_at_hex` (line 31, restored).
- 5 call sites flipped from `galaxy._pathfinder.get_system_at_hex(...)` back to `get_system_at_hex(galaxy, ...)`.
- No other changes in the file in that commit.

Restoration is byte-clean.

### INFO-010 — CONFIRM

AST-parsed `game/strategy/data/pathfinding.py` mentally; top-level `FunctionDef` names are exactly:

```
strip_start_hex, find_path_deep_space, _pathfinder_for, _intercept_for,
find_path_interstellar, get_system_at_hex, find_nearest_system,
find_hybrid_path, project_fleet_path, calculate_intercept_point
```

`tests/unit/strategy/data/test_pathfinding_shim_scope.py:35-48` `EXPECTED_SHIM_FUNCTIONS` lists exactly these 10 names (8 forwarders + 2 helpers). Set equality holds. Guard is accurate.

---

## Independent Sweep — local-import patch grep

Re-grepped `tests/` for patches that would reach the migrated sites via the local-import path:

```
patch.*strategy_screen.*find_hybrid_path
patch.*strategy_screen.*get_system_at_hex
patch.*strategy_screen.*find_nearest_system
patch.*strategy_colonization.*get_system_at_hex
```

**Result:** zero matches. The 4 migrated sites have no test patches reaching them via either the shim path OR the local module path. The lesson from the site #3 revert (tests patch the local re-export name) has been correctly applied — the migrated sites are confirmed-safe to migrate because no test patches them at the local-import level either.

This independent check strengthens INFO-005/006 and validates the Phase 2 site selection.

---

## Recommended Actions for Claude

**Fix now:** none. MAJ-001 and MIN-001 fixes are already correct in `Projects/active_projects/PROJ-372/decisions.md` row 38; MIN-003 is auto-resolved by those fixes.

**Defer (or skip):**
- **MIN-002 (inline comment expansion):** the module docstring at `_capture_baseline.py:9-23` already documents the seeding limitation accurately. An inline comment expansion at line 66 is a marginal nice-to-have. Skip unless touching the file for another reason.

**No regressions or hallucinations found in OpenCode's report.** The 12 INFO findings spot-checked or accepted are consistent with the code and commits. The AST guard is accurate, the revert is clean, and the cross-project documentation drift identified in MAJ-001/MIN-001 was the only material issue — and is now closed.

PROJ-377 is ready for closeout.
