# PROJ-319 Phase 5+6 Remediation — Follow-Up Review Report

**Review Request:** req_20260503_050226_64328c
**Parent Request:** req_20260503_042208_1f0252
**Reviewer:** OpenCode (ocode-review-request skill)
**Date:** 2026-05-03
**Type:** Code review — follow-up verification (delegated by Claude Code)
**Scope:** Verify H1, H3, M1, M2 findings from parent review are RESOLVED; flag any regressions

---

## Verification Matrix

| Parent Finding | Status | Evidence |
|---|---|---|
| H1 (manifest gaps) | RESOLVED | All 54 git-diff files present in rewritten manifest; 0 phantom entries; `strategy_superweapons.py` correctly marked UNCHANGED; `list_filter_utils.py` present as Phase 6 NEW |
| H3 (sort-key duplication) | RESOLVED | Zero `def sort_key` in filter files; `make_attr_sort_key(col)` factory extracted to `list_filter_utils.py`; behavior byte-identical; all 38 sort tests pass |
| M1 (`__future__` imports) | RESOLVED | All 8 new modules have `from __future__ import annotations` (including Phase 6's `list_filter_utils.py`); all placed correctly after docstring, before regular imports |
| M2 (manifest naming) | RESOLVED | `_compute_circular_position` (with underscore) zero hits in rewritten manifest; correctly references `compute_circular_position` with deliberate-deviation note |

---

## 1. Per-Finding Verification

### H1 — Manifest Completeness: RESOLVED

**Cross-check method:** Extracted `git diff HEAD~1 HEAD --name-only | Select-String -Pattern '^(game|tests)/'` and compared against the rewritten `manifest.md` row-by-row.

| Check | Result |
|---|---|
| Files in git diff (game/ + tests/) | 54 files |
| Files in manifest | 54 production+test entries (all covered) |
| Omissions (file in diff, missing from manifest) | **0** |
| Phantom entries (manifest row, no real diff) | **0** |
| `strategy_superweapons.py` row accuracy | CORRECT — marked UNCHANGED with deferral note; `git diff` returns no output |
| `list_filter_utils.py` in manifest | PRESENT — line 62, Phase 6 NEW |

All three sub-checks pass. The implementer acted on the full 10 missing entries (not just the parent's quoted 9), including the self-discovered 10th (`column_toggle_section.py`).

### H3 — Sort-Key Duplication: RESOLVED

| Check | Result |
|---|---|
| `grep 'def sort_key'` in filter files | **ZERO hits** — both inline `sort_key` inner functions removed |
| `list_filter_utils.py` exists | YES — 43 lines, exports `make_attr_sort_key(col)` |
| `planet_list_filters.py` imports | `from game.ui.screens.list_filter_utils import make_attr_sort_key` (line 30) ✓ |
| `star_list_filters.py` imports | `from game.ui.screens.list_filter_utils import make_attr_sort_key` (line 12) ✓ |
| Usage location | Both at the `else:` fallback branch: `planets.sort(key=make_attr_sort_key(col), ...)` ✓ |

**Behavior verification (manual):**
- `func` extraction: `col['func'](entity)` — returns typed value (e.g. `42`) ✓
- `attr` extraction: walks `col['attr'].split('.')` dotted path — returns typed value (e.g. `5.5`) ✓
- Missing attr: returns `""` (empty string) ✓
- No func/no attr: returns `""` ✓
- No `str()` cast anywhere — numeric sort preserved ✓

**Behavior verification (test suite):**
- `test_planet_list_filters.py`: 25/25 passed ✓
- `test_star_list_filters.py`: 13/13 passed ✓
- Sort-specific tests (`test_planet_list_components.py` sort + both filter files): 7/7 passed ✓

**REGRESSION CHECK — M5 preservation:** The new `make_attr_sort_key` returns the raw `col['func'](entity)` result without any `str()` cast. If a column's `func` lambda returns `int` or `float`, the sort order is correct for numeric values. Confirmed — no regression.

### M1 — `__future__` Imports: RESOLVED

All 8 new modules have `from __future__ import annotations` placed correctly:

| File | Line | After docstring? | Before regular imports? |
|---|---|---|---|
| `game/strategy/services/race_resolver.py` | 8 | ✓ | ✓ |
| `game/ai/spatial_behaviors/_formation_utils.py` | 7 | ✓ | ✓ |
| `game/ui/widgets/range_slider_builder.py` | 8 | ✓ | ✓ |
| `game/ui/widgets/column_toggle_section.py` | 7 | ✓ | ✓ |
| `game/ui/screens/list_data_source_base.py` | 10 | ✓ | ✓ |
| `game/ui/screens/planet_target_editor_base.py` | 18 | ✓ | ✓ |
| `game/ui/screens/data_list_window_mixin.py` | 26 | ✓ | ✓ |
| `game/ui/screens/list_filter_utils.py` | 16 | ✓ | ✓ |

All 8 files follow the PEP 563 / project convention: `from __future__` sits between the module docstring and the first regular import. The parent review under-counted (3 of 7); the implementer fixed all 6 + the new Phase 6 file (8 total).

### M2 — Manifest Naming: RESOLVED

| Check | Result |
|---|---|
| `_compute_circular_position` in manifest.md | **ZERO hits** |
| Manifest correctly uses `compute_circular_position` | YES — line 57 with note about deliberate deviation |
| `plan.md` & `phase_5_checklist.md` reference `_compute_circular_position` | Only in context of documenting the fix — expected |

The misleading `_compute_circular_position` (audit's recommended name) no longer appears in the manifest. The manifest now uses the actual exported name with a clear note explaining the deliberate deviation.

---

## 2. Regression Findings

### CRITICAL (0)

None.

### HIGH (0)

None.

### MEDIUM (0)

None.

### LOW (1)

| ID | Severity | File:Line | Issue | Fix |
|----|----------|-----------|-------|-----|
| L1 | LOW | `planet_list_filters.py:241-244` / `star_list_filters.py` (same pattern) | `get_column_value` duplicates the `attr`-walking logic from `make_attr_sort_key`. Both walk `col['attr'].split('.')` identically. While `get_column_value` returns a display string (with `fmt` support) vs `make_attr_sort_key` returning a typed value, the `attr`-walking loop itself is duplicated. | Candidate for future cleanup — extract the walk into a shared `_resolve_attr(entity, attr_path)` helper. Not blocking — the two functions have different return-type contracts. |

---

## 3. Regression Checks (Systematic)

| Check | Result |
|---|---|
| Full test suite (`python Tools/test_sharded/test_sharded.py`) | **16374 passed, 0 failed, 3 skipped** — identical to implementer's reported result. No new failures. |
| Intermittent flake check | 0 failures on this run; the two documented flakes (`test_elapsed_seconds_is_monotonic_then_frozen`, `test_mutual_join_rendezvous.*`) did not manifest. If they had, they would not be considered regressions per the documented pattern. |
| Re-export check (`list_filter_utils`) | No test imports from `list_filter_utils` directly — tests import from `planet_list_filters` / `star_list_filters` which import the helper. No re-export gap. |
| Import-cycle check | `list_filter_utils.py` imports only `from __future__ import annotations` and `from typing import Any, Callable, Dict`. It imports nothing from `game/`. No cycle possible. The consumers (`planet_list_filters.py`, `star_list_filters.py`) import from `list_filter_utils.py` — a clean DAG. |
| `strategy_superweapons.py` re-check | `git diff HEAD~1 HEAD -- game/ui/screens/strategy_superweapons.py` returns no output — confirmed UNCHANGED. |
| Sort behavior spot-check (gravity, temperature, custom func) | `make_attr_sort_key` preserves typed values (`func` returns raw value, `attr` returns raw value). All sort-specific tests pass. Behavior identical to pre-extraction. |

---

## 4. Final Recommendation: APPROVE

All four parent findings (H1, H3, M1, M2) are **fully RESOLVED** with zero regressions and zero new issues above LOW severity.

- **H1** — Manifest now lists all 54 git-diff files with 0 omissions and 0 phantom entries.
- **H3** — Sort-key duplication eliminated; `make_attr_sort_key` factory is byte-identical to the original inline `sort_key` functions.
- **M1** — All 8 new modules have `from __future__ import annotations` in correct PEP 563 position.
- **M2** — Manifest naming corrected; `_compute_circular_position` replaced with actual exported name `compute_circular_position`.

The single LOW finding (duplicated `attr`-walking between `get_column_value` and `make_attr_sort_key`) is a future cleanup candidate — the two functions have different return-type contracts, so the duplication is incidental rather than problematic.

---

*Review conducted by single-agent analysis (scope: 8 files, 4 verification targets, 5 regression checks). Agent also used: `full_test_suite` (sharded runner), `sort_key_behavior_validation` (manual), `import_cycle_analysis` (AST inspection).*
