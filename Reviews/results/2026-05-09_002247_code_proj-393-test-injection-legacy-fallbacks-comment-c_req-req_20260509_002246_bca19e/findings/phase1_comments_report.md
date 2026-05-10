# Phase 1 Comment Cleanups & Code Quality — PROJ-393 Review

**Reviewer**: OpenCode (ocode-review-request)  
**Date**: 2026-05-09  
**Target**: PROJ-393 — Test-injection fallbacks + comment cleanups  

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0     |
| MAJOR    | 2     |
| MINOR    | 2     |
| INFO     | 2     |

The six explicitly-ticketed cleanups (LEG-03-002, LEG-03-003, LEG-02-005, LEG-02-017) and four Phase 3 tasks (3.1, 3.4, 3.6, 3.7) were all **correctly executed** at their target locations. The failing is that the same `ResourceCatalog.from_json()` module-level anti-pattern targeted by Task 3.4 exists in at least **5 other production files** that were not addressed. This is a "missed in spirit" scope gap.

---

## Phase 1 Comment Cleanup Verification

### LEG-03-002: `formation.py` legacy snap comment
**File**: `game/simulation/combat/formation.py:356–369`  
**Verdict**: PASS

The stale legacy-snap comment is deleted. The EPS snap logic is preserved with a clean, precise comment:

```python
# Snap floating-point noise near zero to exact zero so 2-team layouts
# report `(-500, 0)` / `(+500, 0)` byte-identically instead of
# `(-500, 6e-14)`. Threshold is small relative to any sensible arena
# radius.
_eps = 1e-9 * max(1.0, arena_radius)
```

The snap logic (`abs(x) < _eps` / `abs(y) < _eps`) remains intact at lines 366–369.

---

### LEG-03-003: `spec_compiler.py` EnvironmentalEffects comment
**File**: `game/strategy/combat/spec_compiler.py:446–457`  
**Verdict**: PASS (with MINOR note — see F-03 below)

The targeted legacy comment about `environmental_effects` is deleted. What remains is a 12-line historical block explaining removed `sector`/`system`/`empires` kwargs and the PROJ-343 ownership split. This is legitimate architecture documentation, not a stale comment, though its verbosity is noted in finding F-03.

No other stale comments were found immediately adjacent to lines 446–462. The nearby PROJ references (PROJ-271, PROJ-272, PROJ-343) on lines 446–457 are all architectural context, not TODOs or dead references.

---

### LEG-02-005: `save_game_service.py` historical comment
**File**: `game/strategy/systems/save_game_service.py:68`  
**Verdict**: PASS

No `# legacy` comment exists at or near line 68. The area around `SAVE_VERSION = "3.0.0"` (line 67) is clean. All `PROJ-312` references in the file (lines 25, 52, 61, 138, 184, 298) are live architectural tags for the active replay-store integration.

---

### LEG-02-017: `context.py` PROJ-258 docstring tag
**File**: `game/context.py`  
**Verdict**: PASS

1. **Stale line-13 comment deleted**: The docstring at lines 1–17 contains no `PROJ-258: Initial implementation` reference. Confirmed absent.
2. **Two intentionally-preserved references remain**:
   - **Line 41**: `set_default_planet_habitability_service (PROJ-258 pattern).` — legitimate architectural reference in docstring.
   - **Line 162**: `# PROJ-258: Set ALL module-level references so get_default_xxx()` — legitimate architectural reference in `create_production()`.
3. **Grep confirms exactly 2 references**: `rg "PROJ-258" game/context.py` returns only lines 41 and 162.

---

## Phase 3 Completed Task Verification

### Task 3.1: `planet_action_engine.py` PlanetaryShield fallback
**File**: `game/strategy/engine/planet_action_engine.py:352–376`  
**Verdict**: PASS

The `'PlanetaryShield'` hardcoded fallback is deleted. The `_find_target_facility` method now correctly:

1. Requires `dict` target (line 361 — non-dict returns `None`)
2. Looks up by `facility_instance_id` first (lines 364–368)
3. Falls back to `ability_name` lookup (lines 371–375)

The PROJ-393 comment block at line 355 documents the removal. The logic works correctly: an order with `{'ability_name': 'PlanetaryShield'}` (but no `facility_instance_id`) will still resolve via the ability-name fallback at line 374 — the only removed path was the **hardcoded** string `'PlanetaryShield'` bypassing target dict entirely.

---

### Task 3.4: `ResourceCatalog` lazy init
**File**: `game/ui/screens/build_queue_helpers.py:11–17`  
**Verdict**: PASS (target files only — see F-01/F-02 for scope gaps)

`build_queue_helpers.py`: Module-level `ResourceCatalog.from_json()` call replaced with `@lru_cache(maxsize=1)` getter:

```python
@lru_cache(maxsize=1)
def _get_planetary_ids() -> tuple[str, ...]:
    """PROJ-393: lazy-load planetary resource IDs (was a module-level..."""
    return tuple(d.id for d in ResourceCatalog.from_json().by_display_group("planetary"))
```

`strategy_ui.py:28–31`: Same pattern applied identically.

No other module-level `ResourceCatalog.from_json()` calls exist in *either file*. Both files are clean.

**However** — see F-01 and F-02 below for multiple other production files where this exact anti-pattern was not addressed.

---

### Task 3.6: `_LEGACY_PATTERN` deletion
**File**: `game/ui/renderer/sprites.py`  
**Verdict**: PASS

- `_LEGACY_PATTERN` is fully deleted from `sprites.py`. Only `_PORTRAIT_PATTERN` remains (line 12).
- The `else: match = _LEGACY_PATTERN.match(...)` dead branch is gone. The `_load_from_directory` loop (lines 65–90) has a single `_PORTRAIT_PATTERN.match(f)` match with clean control flow.
- `rg _LEGACY_PATTERN` across entire repo returns **zero matches** — confirmed fully removed.
- Test file `tests/unit/ui/test_sprite_loading.py:23` updated: the comment now reads `"PROJ-393: legacy Comp_NNN.bmp pattern was deleted"` and the mock data uses canonical `64Portrait_Comp_NNN.png` filenames. No test references legacy filenames in mock data.

---

### Task 3.7: `transfer_branches.py` first-species fallback
**File**: `game/strategy/engine/order_handlers/transfer_branches.py:101–126`  
**Verdict**: PASS

The "Legacy/Default: use first species" fallback is deleted. New behavior:

```python
# PROJ-393: species_id is now required; the legacy
# 'default to first species' fallback is gone.
if not species_id:
    logger.warning(
        "TransferHandler: passenger LOAD on %s missing species_id; "
        "no transfer performed (legacy first-species fallback removed in PROJ-393)",
        planet.name,
    )
    return 0
```

The TODO comment for future cargo-system species tracking is intact at lines 122–124:

```python
# Cargo system tracks "passengers" as a single
# bucket; species_id is consumed here for source-side accounting only.
```

---

## Findings

### F-01 [MAJOR] `planet_list_window.py:24` — Module-level `ResourceCatalog.from_json()` not converted

**Evidence**:  
```python
# game/ui/screens/planet_list_window.py:24
_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]
```

**Why it matters**: This is the exact same Pattern 12 violation that Task 3.4 fixed in `build_queue_helpers.py` and `strategy_ui.py`. Module-level `ResourceCatalog.from_json()` executes file I/O at import time, violating the documented pattern: "no heavy init at import time." The `@lru_cache(maxsize=1)` lazy pattern should be applied here too.

**Severity**: MAJOR — the file is in the same UI layer as the two already-fixed files; the scope gap appears to be an oversight in the same cleanup pass.

---

### F-02 [MAJOR] Five additional production files with same unconverted module-level pattern

**Evidence**: `rg "ResourceCatalog.from_json.*planetary" game/ --include="*.py"` yields:

| File | Line | Pattern |
|------|------|---------|
| `game/strategy/data/planet_gen.py` | 17 | `_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json()...]` |
| `game/strategy/engine/empire_economy_calculator.py` | 16 | `_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json()...]` |
| `game/strategy/engine/construction_forecast.py` | 18 | `_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json()...]` |
| `game/ui/panels/empire_treasury_panel.py` | 20 | `_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json()...]` |
| `game/ui/screens/planet_list_window.py` | 24 | `_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json()...]` |

**Why it matters**: PROJ-393 Task 3.4 fixed the pattern in 2 of ~8 sites where it appears. Each of these remaining sites executes file I/O at module import time. While Task 3.4's scope explicitly covered only `build_queue_helpers.py` and `strategy_ui.py`, the *spirit* of cleanup was "eliminate import-time `ResourceCatalog.from_json()` calls." This scope gap means the anti-pattern persists in 5 production files, three of which are in the Strategy layer (where import-time I/O has broader consequences for test isolation).

**Note**: These files are **outside** the two explicitly-targeted files, so they are not a failure of the ticket. They are a **scope expansion** recommendation for a follow-up PROJ.

---

### F-03 [MINOR] `spec_compiler.py:446–457` — Overly verbose historical comment block

**Evidence**: The 12-line comment documenting deleted kwargs from PROJ-271 Phase 9 and PROJ-272 Phase 7 is legitimate architecture documentation but verges on stale-adjacent. It describes code that no longer exists (deleted `_entries_from_modifier_source` helper, removed `sector`/`system`/`empires` kwargs) and references phases from completed projects.

**Why it matters**: While not wrong, historical-change comments of this density accumulate over time and make the module harder to scan. A 2-line summary referencing the relevant PROJ docs would serve the same purpose. Not actionable in PROJ-393 scope, but noted for future comment hygiene passes.

---

### F-04 [MINOR] `save_game_service.py:128` — Unexplained compatibility comment

**Evidence**:
```python
'turn_number': game_session.turn_number,  # For compatibility
```

**Why it matters**: The `# For compatibility` comment does not explain what it's compatible with. If this is a legacy save-format shim, it should carry a PROJ reference or be removed per the "no save-file migration" rule in AGENTS.md. If it's intentional forward-compatibility (both `latest_turn_number` and `turn_number` stored), the comment should state that clearly.

---

### F-05 [INFO] `stat_rows_dynamic.py:177` — Uncached `ResourceCatalog.from_json()` inside function

**Evidence**:
```python
# game/ui/screens/builder/stat_rows_dynamic.py:177
def get_construction_rows(ship) -> Any:
    PLANET_RESOURCE_NAMES = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]
```

**Why it matters**: This is not a Pattern 12 violation (run inside a function, not at module level), but `ResourceCatalog.from_json()` performs file I/O on every call. This function is called per-ship from the builder UI. Should use `@lru_cache` or receive the catalog as a parameter. Low priority because the builder UI is not a hot path.

---

### F-06 [INFO] `formation.py:326` — "legacy" used as behavioral descriptor

**Evidence**:
```python
# game/simulation/combat/formation.py:326
# team 1 at (+arena_radius, 0) facing west (180°). Preserves the
# legacy Battle Setup `_SIDE_ENTRY_VECTORS` layout byte-for-byte.
```

**Why it matters**: The word "legacy" here describes **preserved behavior** (byte-identical output), not stale/dead code. This is the correct usage of "legacy" in an architectural comment. No action needed.

---

## "Missed in Spirit" — Comment Cleanups Near Touched Files

A sweep of comments within 30 lines of each cleaned-up site reveals no other stale/legacy tags that should have been addressed. Specifically:

- **formation.py:356** — Surrounding comments (~322-370) are all architectural documentation, not stale tags.
- **spec_compiler.py:462** — The surrounding area (430-485) contains only live PROJ references (PROJ-343, PROJ-271/272 in the historical block). No dead TODOs or stale cleanup markers.
- **save_game_service.py:68** — Lines 55-140 have no `# legacy`, `# TODO`, or stale markers. All PROJ-312 references are live.
- **planet_action_engine.py:366** — Lines 350-387 are clean.
- **transfer_branches.py:107** — Lines 90-126 are clean.
- **sprites.py** — The entire file (125 lines) is clean after `_LEGACY_PATTERN` removal.

The "missed in spirit" finding is **F-02** — the `ResourceCatalog.from_json()` module-level pattern was not addressed in 5 additional files, even though the pattern is structurally identical to what was fixed.

---

## Task-by-Task Verdict Summary

| Task | Target | Verdict |
|------|--------|---------|
| LEG-03-002 | `formation.py:357` snap comment | PASS |
| LEG-03-003 | `spec_compiler.py:462` env effects comment | PASS |
| LEG-02-005 | `save_game_service.py:68` legacy comment | PASS |
| LEG-02-017 | `context.py:13` PROJ-258 tag | PASS |
| Task 3.1 | `planet_action_engine.py:366` shield fallback | PASS |
| Task 3.4 | `build_queue_helpers.py` + `strategy_ui.py` lazy init | PASS |
| Task 3.6 | `sprites.py` `_LEGACY_PATTERN` deletion | PASS |
| Task 3.7 | `transfer_branches.py:107` first-species fallback | PASS |

All 8 targeted cleanups are verified correct. No regressions detected at changed sites.
