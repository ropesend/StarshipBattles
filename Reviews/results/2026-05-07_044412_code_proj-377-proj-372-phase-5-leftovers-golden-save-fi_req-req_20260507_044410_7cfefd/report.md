# PROJ-377 Review Report
**Request:** req_20260507_044410_7cfefd
**Review Type:** code
**Review Mode:** standard
**Scope:** 3 commits on feat/03c-phase-aware-execution — golden-save fixture, pathfinding shim partial sweep, AST guard
**Reviewer:** OpenCode
**Completed:** 2026-05-07T05:00:00Z

---

## Executive Summary

PROJ-377 is well-executed overall. The golden fixture + capture script is correct and well-documented. The 4 Phase 2 migrations preserve semantics. The Phase 3 revert is verified clean. The AST guard is accurate. The open issue is a cross-project documentation inconsistency in PROJ-372's decisions.md that reports 5 migrated sites (including one that was reverted) when the actual count is 4.

**Verdict:** Ship with one documentation fix.

---

## Finding Summary

| Severity | Count | IDs |
|----------|-------|-----|
| MAJ | 1 | MAJ-001 |
| MIN | 3 | MIN-001, MIN-002, MIN-003 |
| INFO | 12 | INFO-001 through INFO-012 |

---

## MAJ-001: PROJ-372 decisions.md cross-link reports incorrect migration count (5→4)

**File:** `Projects/active_projects/PROJ-372/decisions.md:38`
**Phase attributed to:** Phase 3 (the cross-link row was added in commit 9cb543f4c)

The PROJ-372 decisions.md row 2026-05-07 "PROJ-377 closeout" states:
> "pathfinding shim sweep migrated **5 of 14** production importers (Class A: **superweapon order processor** + 3 strategy-screen methods + colonization screen)"

This is incorrect:
1. Site #3 (`superweapon_order_processor.py`) was **migrated in Phase 2 and reverted in Phase 3** (commit 9cb543f4c) after 40 test regressions surfaced.
2. The actual migration count is **4 of 14** (sites #10, #11, #12, #14).
3. PROJ-377's own `plan.md` (line 25) and `decisions.md` (row 2026-05-07) correctly report 4.

**Fix:** Change "5 of 14" to "4 of 14" and remove "superweapon order processor" from the migrated-sites parenthetical, or note it was reverted and reclassified Class B.

---

## MIN-001: PROJ-372 decisions.md deferred-site listing incomplete

**File:** `Projects/active_projects/PROJ-372/decisions.md:38`

The row lists deferred Class B sites as: `game_session`, `handlers/base`, `fleet_navigation_service`, `strategy_superweapons`, `planet_slice`. But the reverted `superweapon_order_processor` (site #3, now Class B) is missing from this list. The deferred site count (8) is still arithmetically correct (8 deferred + 4 migrated + 2 Class C = 14), but the textual listing is incomplete.

**Fix:** Add `superweapon_order_processor` to the deferred-site list, or clarify it was attempted-then-reverted.

---

## MIN-002: Double-seed Galaxy init pattern in capture script is fragile

**File:** `tests/fixtures/saves/_capture_baseline.py:64-67`

```python
random.seed(2)
galaxy = Galaxy(radius=30)
random.seed(2)  # Galaxy.__init__ may have consumed an indeterminate amount
```

The re-seed after `Galaxy.__init__` assumes that re-seeding the global `random` module will also control any `random.Random()` instances created during construction. If `Galaxy.__init__` (or any code it calls) creates an internal `random.Random()` instance, the re-seed has no effect on it. This is latent fragility.

**Recommendation:** Document this as a known limitation and consider pinning to a load-only CI path (load from committed fixture, assert round-trip). Keep the capture script as a developer convenience with a warning.

---

## MIN-003: plan.md closeout readiness vs actual documentation state

**File:** `Projects/active_projects/PROJ-377/plan.md:24`

The Current State says "All phases complete; ready for review" but the PROJ-372 decisions.md cross-link (MAJ-001) and deferred-site listing (MIN-001) still have drift. These should be resolved before final closeout.

---

## INFO Findings

### INFO-001: `_normalize_image_fields` placeholders survive round-trip
`image_id` → `_fixture_planet_{id}.png` and `image_rotation` → `0.0` are plain string/float fields with no transformation — they round-trip identically.

### INFO-002: Storm stripping mirrors existing test convention
`_strip_storms()` matches `test_save_round_trip.py` synthetic tests. `Storm.to_dict()/from_dict()` drift documented and out of PROJ-372 scope.

### INFO-003: Decorated planet exercises key fields but not all 42 serialized fields
Fields like `construction_queue`, `staging_yard`, `max_staging_mass`, `facilities`, `energy`, `gravity_target`, `water_target`, `radiation_shielding`, `orders`, `species_configs` remain at defaults. Acceptable — the fixture targets structural drift; the other 5 synthetic round-trip tests exercise default paths.

### INFO-004: Capture idempotence trade-off correctly documented
The `_capture_baseline.py` docstring (lines 9-23) accurately explains seeding, normalization, unseeded fields, and the CI contract.

### INFO-005: strategy_screen.py migrations (sites #10, #11, #12) preserve semantics
All three migrated methods produce identical runtime behavior. Default radius=50 for `get_system_at_hex` matches between shim and service.

### INFO-006: strategy_colonization.py migration (site #14) preserves semantics
`_get_system_at_hex` at line 259 defaults to radius=50 — same as the shim. No regression.

### INFO-007: Site #3 revert is clean
`git show 9cb543f4c` confirms byte-level restoration of import and 5+ call sites from `galaxy._pathfinder.get_system_at_hex(...)` back to `get_system_at_hex(galaxy, ...)`.

### INFO-008: Root cause analysis for revert is correct
Tests patch `'game.strategy.engine.superweapon_order_processor.get_system_at_hex'` (local import name) not `'game.strategy.data.pathfinding.get_system_at_hex'` (shim path). Original planning grep missed this pattern. Lesson captured in decisions.md.

### INFO-009: `get_system_at_hex` import confirmed restored in superweapon_order_processor.py
Line 31: `from game.strategy.data.pathfinding import get_system_at_hex` — restored. The 8 deferred Class B sites were never touched.

### INFO-010: AST guard EXPECTED_SHIM_FUNCTIONS exactly matches pathfinding.py
All 10 names (8 free funcs + 2 helpers) verified against AST parse of `pathfinding.py`. No missing, no extras.

### INFO-011: Guard design is robust
Uses `frozenset`, AST-based parsing, clear error messages with diff output, and a secondary helper-level parametric test.

### INFO-012: pathfinding.py docstring rewrite is accurate
Correctly describes the shim's new role as "permanent test-patch transparency surface" with pointer to AST guard and PROJ-377 decisions.md. No longer references PROJ-376 or "deprecated" status.

---

## Instructions Checklist

| # | Instruction | Verdict |
|---|-------------|---------|
| 1 | Golden-fixture correctness | Pass — placeholders survive round-trip; decorated planet exercises key fields |
| 2 | Capture-script idempotence trade-off | Pass — documented correctly; MIN-002 notes fragility |
| 3 | Phase 2 migration semantics | Pass — radius defaults match, no hidden parameter changes |
| 4 | Site #3 revert correctness | Pass — verified clean restoration via git show |
| 5 | AST guard scope | Pass — all 10 names match pathfinding.py |
| 6 | Plan-vs-implementation drift | MIN-003 — PROJ-377 docs internally consistent; PROJ-372 cross-link has drift |
| 7 | Test-patch transparency invariant | Pass — shim import restored in superweapon_order_processor; no other deferred sites touched |
| 8 | PROJ-372 cross-link consistency | MAJ-001 — migration count wrong (5→4), migrated-site list includes reverted site |

---

## Recommendations

1. **Fix MAJ-001** in `Projects/active_projects/PROJ-372/decisions.md` row 38: correct "5 of 14" to "4 of 14"; remove superweapon_order_processor from migrated list; add it to deferred list.
2. **Fix MIN-001**: add `superweapon_order_processor` to the deferred-site text listing in the same row.
3. **Consider MIN-002**: add a comment in `_capture_baseline.py` noting the double-seed fragility and recommending CI load from committed fixture as the canonical path.
4. **Consider MIN-003**: update plan.md Current State or resolve the PROJ-372 docs drift before closeout.
