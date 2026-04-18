# Phase 6: Project Closure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_close_ready.py PROJ-278`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18, after closure-audit fixes landed)
**Objective:** Final closure — full sharded test suite confirms no regressions, doc sync verified, MEMORY.md updated, project archived.

---

## Tasks

### Task 6.1: Full sharded test suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite
- [x] **Result: 14745 tests | 14744 passed | 1 failed | 0 errors** (16 shards, 69.5s wall time)
- [x] Investigate the single failure: `tests/unit/quickstart/test_quickstart_builder.py::TestQuickstartBuilderDesignCopying::test_copy_designs_without_themes_preserves_original` — assertion `data["theme_id"] == "Federation"` fails with `'Klingons' == 'Federation'`
- [x] Confirm failure is UNRELATED to PROJ-278: the test exercises `QuickstartBuilder.copy_quickstart_designs` (quickstart ship design system, last touched by commit `a307a2db`); PROJ-278 commits (`ed39ef46`, `6d97bc98`, `6345cb05`) did not touch quickstart, themes, or the design template system

**Notes:** Memory's prior baseline mentioned "1 pre-existing baseline failure preserved" — this is consistent. The failure shifted location (was previously in `test_galaxy_cleanup.py` per Phase 2 notes; now in `test_quickstart_builder.py`) — appears to be ongoing pre-existing churn in unrelated subsystems.

### Task 6.2: Doc sync verification [Simple]
**File:** Doc files updated by Phases 1-5
**Tests:** N/A

- [x] [docs/01_ARCHITECTURE.md](../../../docs/01_ARCHITECTURE.md) — `roles.py` row, export count 42→45, `Roles (PROJ-278)` exports entry, `design_role.py` + `design_role_registry.py` mention in `game/strategy/data/` row (3 PROJ-278 mentions)
- [x] [docs/03_CONVENTIONS.md](../../../docs/03_CONVENTIONS.md) — `data/design_roles.json` row updated (1 PROJ-278 mention)
- [x] [docs/systems/strategy_layer.md](../../../docs/systems/strategy_layer.md) — Design Roles section fully rewritten with new file split, layered loading, runtime add semantics, RoleRegistry API, authoring rule for cachers (5 PROJ-278 mentions)
- [x] [docs/systems/combat_simulation.md](../../../docs/systems/combat_simulation.md) — Combat Lab Scenario Role Tagging section added (1 PROJ-278 mention)
- [x] [docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md) — §"2.5 Scenario Role Labels" added; directory tree updated (4 PROJ-278 mentions)

**Notes:** Five docs total. All retained PROJ-278 content through the recent merge (verified by user-requested merge inspection — only PROJ-277's services row was added externally; all my edits preserved).

### Task 6.3: MEMORY.md update [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** N/A

- [x] Added PROJ-278 entry to "In-Progress Projects (PROJ-273+)" section with full summary covering all 5 implementation phases + future opportunities flagged in Phase 5

**Notes:** Entry placed alongside PROJ-273/274/275 since they're all current/recent. Will move to "Recently Archived" section when Task 6.5 (archival) runs.

### Task 6.4: Closure summary in plan.md [Simple]
**File:** `Projects/active_projects/PROJ-278/plan.md`
**Tests:** N/A

- [x] Closure summary added (see plan.md)

**Notes:** Comprehensive summary covering deliverables, deletions, migrations, tests, docs, and future opportunities. Lists 66 new tests across 6 test files.

### Task 6.5: Archive project [Simple]
**File:** `Projects/active_projects/PROJ-278/` → `Projects/archived_projects/PROJ-278/`
**Tests:** N/A

- [x] Run `python Projects/scripts/archive_project.py PROJ-278 --force`
- [x] Verify `Projects/projects_index.md` updated to status `Archived`

**Notes:** Archival completed after Task 6.6 audit-driven fixes landed.

### Task 6.6: Apply audit-driven fixes [Medium]
**Files:** `game/core/roles.py`, `tests/unit/core/test_role_registry.py`, `tests/unit/strategy/data/test_design_role_registry_loader.py`
**Tests:** `pytest tests/unit/core/ tests/unit/strategy/data/`

User approved fixing the 4 worth-fixing items surfaced by the closure audit (5 skeptical agents) before archival.

- [x] **Implementation Bug #2 (re-entrance guard):** added `_firing_callbacks` flag + try/finally to `RoleRegistry._fire_invalidation_callbacks` — recursive `add_user_role` from inside a callback now applies the mutation but suppresses nested invalidation firing. Added test `test_reentrant_add_user_role_in_callback_does_not_recurse`.
- [x] **Test gap #1 (missing required-field validation):** added 3 tests proving `load_from_file` raises `KeyError` when JSON role dicts omit `id` / `display_name` / `description`.
- [x] **Test gap #2 (missing `roles` key behavior):** added `test_missing_roles_key_loads_zero_roles_silently` documenting that comment-only/template files load cleanly with zero roles. Added `test_empty_roles_array_loads_zero_roles` for symmetry.
- [x] **Test gap #3 (mod layer untested):** added 3 tests in `test_design_role_registry_loader.py`: mod overlay overrides base, user overlay overrides mod, multiple mods load in sorted order.
- [x] Tidied 2 pre-existing unused imports in the loader test file (`Path`, `List`)
- [x] Final regression: 4692 tests passed across `tests/unit/core/ tests/unit/strategy/data/ tests/unit/combat_lab/ tests/unit/simulation/`

**Audit findings DEFERRED (with rationale):**
- **Implementation Bug #1 (singleton race condition):** This same `if _default is None: _default = build()` pattern is used by every other module-level service accessor in the codebase (the convention pre-dates PROJ-278 — see ApplicationContext services). Pygame is single-threaded; no current threading concern. Fixing this in PROJ-278 alone would be inconsistent — it's a codebase-wide pattern question, not a PROJ-278 issue.
- **Implementation Bug #3 (callback fires for identical role re-add):** Not a bug — the semantic "every successful add_user_role fires invalidation" is consistent and predictable. Optimizing for "skip if equal" would introduce role-equality edge cases without clear benefit.
- **Test gap #4 (AST scanner dynamic-reference blind spot):** Already documented as an explicit known limitation in [test_scenario_roles_consistency.py](../../../tests/unit/combat_lab/test_scenario_roles_consistency.py)'s module docstring. Not a hidden gap.
- **Test gap #5 (invalidation test uses fake cacher):** By design. Phase 5 audit found zero real cachers exist; the fake `_FakeRoleArchetypeCache` IS the worked example future implementers will copy.

**Notes:** Updated test counts:
- `test_role_registry.py`: 29 → 35 tests (6 new: 1 re-entrance + 5 malformed-loading)
- `test_design_role_registry_loader.py`: 12 → 15 tests (3 new mod-layer)
- **Total PROJ-278 tests:** 66 → 75

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (except 6.5 archival itself, pending user approval)
- [x] Full sharded suite shows zero PROJ-278-introduced failures
- [x] All 5 docs verified to contain PROJ-278 references
- [x] MEMORY.md captures the complete project summary
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to "Awaiting user approval to archive"
