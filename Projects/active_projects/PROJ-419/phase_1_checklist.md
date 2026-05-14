# Phase 1: Single-PR sweep of stale comments and dead imports

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-419 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Trim 4 stale comments and remove 3 dead `import pygame_gui` lines in one PR. All fixes are zero-call-site; total LOC affected is < 15.

Severity tier: Minor (5 zero-call-site fixes).

---

## Tasks

### Task 1.1: Trim stale legacy comment (race_summary_panel.py) (0 call sites — single-PR deletion)
**File:** `game/ui/panels/race_summary_panel.py`
**Tests:** `pytest tests/ --testmon`

- [x] Delete the stale `# legacy three-column split and the y-55 alignment hack.` comment at `race_summary_panel.py:149` (0 call sites — single-PR deletion). The preceding FEAT-23 marker already documents the current layout.

---

### Task 1.2: Trim stale `_rng_resolve_empty_fleets` reference (conflict_resolution_engine.py) (0 call sites — single-PR deletion)
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/ --testmon`

- [x] Trim the comment block at `conflict_resolution_engine.py:379` so it no longer references the deleted `_rng_resolve_empty_fleets` function. Keep the BUG-126 rationale; drop the trailing historical reference (0 call sites — single-PR deletion).

---

### Task 1.3: Reword "old route" temporal comment (open_warp_point.py) (0 call sites — single-PR deletion)
**File:** `game/strategy/engine/superweapon_handlers/open_warp_point.py`
**Tests:** `pytest tests/ --testmon`

- [x] Rewrite the `# old route would otherwise walk the entire stale path to completion.` comment at line 89 as a factual statement (e.g. `# Without this invalidation, fleets in flight would walk the stale path to completion.`) (0 call sites — single-PR deletion)

---

### Task 1.4: Resolve `PROJ-XX` placeholder (paths.py) (0 call sites — single-PR deletion)
**File:** `game/core/paths.py`
**Tests:** `pytest tests/ --testmon`

- [x] Replace the `PROJ-XX Star Expansion` placeholder at `paths.py:97` with `PROJ-231 star image variant support` — confirmed by codex via `star_image_registry.py:8` label and the introducing git commit 4fa6b08bc (2026-03-28, "feat: add star asset variants"). Rewrite as `# Star subdirectories (PROJ-231 star image variant support)` to match adjacent PLANETS_V3 comment style. Dropping the marker is also acceptable but inconsistent. (0 call sites — single-PR deletion)

---

### Task 1.5: Delete 3 dead `import pygame_gui` lines (screen_router.py) (0 call sites — single-PR deletion)
**File:** `game/screen_router.py`
**Tests:** `pytest tests/ --testmon`

- [x] Delete the dead `import pygame_gui  # noqa: F401 — historical import retained for parity.` lines at `screen_router.py:182`, `:304`, `:429` (0 call sites — single-PR deletion). Confirmed dead by codex: pygame_gui is NOT at module scope in screen_router.py, and none of the three function bodies (`start_strategy_layer`, `show_load_menu`, `start_race_setup`) reference any pygame_gui name after the import. Other pygame_gui uses in the file use separate `import pygame_gui.windows` statements unaffected by this deletion.
- [x] Verify: `pytest tests/ --testmon` passes; `grep -n 'historical import retained for parity' game/screen_router.py` returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
