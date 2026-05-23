# Phase 3: Strict-mode migration (unknown/top-level, ui)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-464 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the top-level/app and ui layers to `mypy --strict` last (ui is the highest-error layer, majority from untyped `pygame_gui`). Per-layer counts are audit estimates; confirm the real count at task start. Depends on PROJ-462 (foundation) and ideally PROJ-463 (domain) landing first since UI consumes their types.

---

## Tasks

### Task 3.1: Adopt strict for the top-level/app layer [Medium]
**File:** `game/app.py`, `game/app_bootstrap.py`, `game/run_loop.py`, `game/screen_router.py` (mypy config)
**Tests:** `mypy --strict game/app.py game/app_bootstrap.py game/run_loop.py game/screen_router.py` then `pytest tests/ --testmon`

- [ ] Confirm current strict error count for top-level (audit estimate: ~16 — `app.py` scene accessors are intentionally `Any`/REJECTED, so focus on the other `no-any-return`/`arg-type`/`assignment` sites)
- [ ] Resolve residual errors WITHOUT narrowing the `Game` scene accessor proxies (those stay `Any` per the rejected TYP-APP finding — they are loose by design for tests)
- [ ] Add `--strict` to the top-level mypy config
- [ ] Verify: pytest passes; `mypy --strict` on the top-level files shows no errors

### Task 3.2: Adopt strict for the ui layer [High]
**File:** `game/ui/` (mypy config)
**Tests:** `mypy --strict game/ui/` then `pytest tests/ --testmon`

- [ ] Confirm current count (audit estimate: ~1,084 — 491 `attr-defined` from untyped `pygame_gui`, 181 `assignment`, 144 `arg-type`, 76 `no-any-return`)
- [ ] Decide and document handling for `pygame_gui` untyped library calls (stub package, targeted per-module ignores with justification, or a typed wrapper) — the majority of `attr-defined` errors are external
- [ ] Resolve the `no-any-return` sites (Phase 1/2 narrowing covers many) and project-owned `assignment`/`arg-type` errors
- [ ] Add `--strict` to the ui layer's mypy config (or per-module strict where pygame_gui boundaries require relaxation, with justification comments)
- [ ] Verify: pytest passes; `mypy --strict game/ui/` shows no project-owned errors (external pygame_gui handled per the documented decision)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
