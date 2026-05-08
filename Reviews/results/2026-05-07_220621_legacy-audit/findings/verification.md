# Legacy Audit — Verification Report

## Critical Finding Verification

| Finding ID | Symbol/File | Verdict | Reason |
|------------|-------------|---------|--------|
| LEG-01-003 | AbilityManager deprecated statics (`ability_manager.py:290-341`) | **CONFIRMED** | 6 static methods, all marked `DEPRECATED`. Grep across `game/` found 0 production call sites (only definition lines). 3 test callers in `test_ability_manager.py` exist but are test-only. Code matches description. |
| LEG-01-004 | ModifierManager deprecated statics (`modifier_manager.py:221-330`) | **CONFIRMED** | 6 static methods, all marked `DEPRECATED`. Grep across `game/` found 1 internal-only call (`remove_modifier_inplace` inside `add_modifier_static`, line 247), 0 external callers. Test files only contain comments referencing the deprecated names, no actual calls. Code matches description. |
| LEG-01-005 | `command_handlers.py` re-export shim (`command_handlers.py:1-82`) | **CONFIRMED** | Full 82-line file is a pure re-export from `game.strategy.engine.handlers/`. Module docstring explicitly says "this shim is **transitional**." 6 production call sites + 25 test call sites confirmed via grep. Violates Rule 3 (no compatibility shims). Code matches description. |
| LEG-01-013 | Empty `game/simulation/components/__init__.py` (0 bytes) | **DISPUTED** | See Downgraded Findings below. |
| LEG-01-014 | Empty `game/strategy/data/__init__.py` (0 bytes) | **DISPUTED** | See Downgraded Findings below. |
| LEG-04-011 | Comment about deleted `_rng_resolve_empty_fleets` (`conflict_resolution_engine.py:415-418`) | **DISPUTED** | See Downgraded Findings below. |
| LEG-04-012 | Backward-compat aliases in `formula_evaluator.py:407-413` | **CONFIRMED** | Three module-level aliases (`evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`) explicitly marked "Backward-compatible aliases for existing test imports." 0 production call sites confirmed. 118 test call sites across 3 test files. Genuine legacy shim per Rule 3. However, 118 test callers make this a migration task, not a trivial delete — should be rated MAJOR due to test migration burden. Duplicated with LEG-04-001 (rated MAJOR). |

## Downgraded Findings

### LEG-01-013 / LEG-01-014 — Empty `__init__.py` files → MINOR, not CRITICAL

**Why DISPUTED:** Empty `__init__.py` files are Python package markers, not "dead code." They serve a structural purpose: they mark the directory as a regular package. In Python 3.3+, namespace packages don't require `__init__.py`, but removal changes import semantics (from regular package to implicit namespace package). Zero bytes occupy no maintenance cost. This is, at most, a MINOR style observation — not a CRITICAL legacy finding.

The report's claim that "An empty `__init__.py` is only needed for namespace packages" is incorrect — it's the opposite: namespace packages do NOT need `__init__.py`. The files are conventional markers for regular packages.

If removed, the packages would still import via Python 3.3+ implicit namespace package resolution, but the finding has no practical urgency or risk. Downgrade to MINOR or discard.

### LEG-04-011 — Comment referencing deleted function → MINOR, not CRITICAL

**Why DISPUTED:** This is a documentation comment (lines 415-418) explaining why a function was deleted and what the current behavior is:

```
# BUG-126: every-fleet-empty case is not a real combat. The
# legacy `_rng_resolve_empty_fleets` only existed to keep
# empire bookkeeping consistent when picking a "winner" — and
# the strategy layer no longer assigns winners. Skip silently.
```

The comment substantiates an edge-case design decision (BUG-126). It is not code, not a shim, not a compatibility layer. Comments are documentation, not legacy artifacts. This finding is also **duplicated** — LEG-04-003 rates the same code at the same location as MINOR (correctly). Calling it CRITICAL misunderstands its purpose as informational documentation. Downgrade to MINOR (consistent with LEG-04-003) and de-duplicate.

### LEG-04-012 — `formula_evaluator.py` aliases → MAJOR, not CRITICAL

**Why severity should be MAJOR:** While CONFIRMED as a legacy shim (0 production callers), there are 118 test call sites across 3 test files (`test_formula_system.py`, `test_formula_overflow_underflow.py`, `test_formula_exceptions.py`). This means removal requires non-trivial test migration — not a simple delete. The finding is also duplicated with LEG-04-001 (correctly rated MAJOR). Keep as MAJOR, not CRITICAL.

## Confirmed Critical — Safe-to-Act-On Legacy Removals

| ID | Symbol | LOC | Risk | Action |
|----|--------|-----|------|--------|
| LEG-01-003 | `AbilityManager.*_static` methods | 56 | Zero production callers. 3 test callers need migration. | Delete lines 286-341 of `ability_manager.py`. Update 3 test methods in `test_ability_manager.py` to use instance API. |
| LEG-01-004 | `ModifierManager.*_static` methods | 110 | Zero external callers. Only internal reference: `remove_modifier_inplace` called within `add_modifier_static` itself. | Delete lines 221-330 of `modifier_manager.py`. All 6 are self-contained dead code. |
| LEG-01-005 | `command_handlers.py` shim | 82 | 6 production + 25 test import sites. Shim is explicitly marked transitional. | Migrate production callers to `from game.strategy.engine.handlers import ...`, then delete file. Migration plan documented in the file's own docstring. |

**Total safe-to-remove LOC: 248** (166 from LEG-01-003 + LEG-01-004 immediate deletes, plus 82 from LEG-01-005 after migration).

## Inconclusive Findings

None. All 7 CRITICAL-flagged findings were resolved to CONFIRMED (4) or DISPUTED/downgraded (3).

## Cross-Report Observations

1. **Duplicate findings across reports:** LEG-04-011 duplicates LEG-04-003 (same file/lines, `conflict_resolution_engine.py:415-418`, rated CRITICAL vs MINOR). LEG-04-012 duplicates LEG-04-001 (same file/lines, `formula_evaluator.py:407-413`, rated CRITICAL vs MAJOR). This is a report-generation bug — the Shard 04 agent re-reported findings its deterministic scanner had already covered, inflating the CRITICAL count by 2.

2. **Adjusted CRITICAL count:** After deduplication and downgrades, true CRITICAL findings = 3 (LEG-01-003, LEG-01-004, LEG-01-005). Two of these (LEG-01-003, LEG-01-004) are zero-risk immediate deletes; one (LEG-01-005) requires call-site migration.

3. **Rule 3 (Root Cause Fixes) compliance:** The 3 CONFIRMED criticals are all explicit violations of Rule 3 — deprecated static methods retained as compatibility shims, and a documented transitional re-export shim. The DISPUTED findings (empty `__init__.py` files, informational comments) do not violate Rule 3.

4. **Biggest gap in the audit:** The `command_handlers.py` shim has 25 test import sites that must be migrated. The audit reports note the ~30 total call sites but don't provide a prioritized migration plan for the test files — only for the 5 production callers in report 4 (LEG-01-015, LEG-01-016, LEG-01-018).
