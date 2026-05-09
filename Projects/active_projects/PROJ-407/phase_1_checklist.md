# Phase 1: Sweep stale docs/comments + non-modern type annotations

**Status:** Not Started
**Objective:** Close 8 of 9 Tier 3 items in a single sweep; document D-09 LOC-ceiling work as deferral.

---

## Tasks

### Task 1.1: D-01 — Update `command_handlers` doc references [Simple]
**Tests:** `rg "game\.strategy\.engine\.command_handlers" docs/`

- [ ] Run the search; capture every hit.
- [ ] For each hit, update to `game.strategy.engine.handlers/` (the canonical package path).
- [ ] Re-run the search — zero hits.

**Notes:**

### Task 1.2: D-02 — Update event-logging API references [Simple]
**Tests:** `rg "log_event|set_event_handler|get_event_handler" docs/`

- [ ] Run the search.
- [ ] Per architecture (PROJ-252), EventBus is session-scoped via constructor injection. Update each doc to reflect that path (no module-level helpers).
- [ ] Re-run the search — only legitimate hits remain (e.g., method-on-EventBus references, not module-level).

**Notes:**

### Task 1.3: D-03 — Reconcile `docs/05_ERROR_HANDLING.md` with EventBus arch [Medium]
**File:** `docs/05_ERROR_HANDLING.md` + actual EventBus code

- [ ] Read `docs/05_ERROR_HANDLING.md` end to end.
- [ ] Read the current EventBus implementation (likely `game/services/events/event_bus.py` or similar — grep first).
- [ ] Identify exact contradictions: error-routing patterns the doc describes that don't match the live code.
- [ ] Update the doc. Don't change the code.
- [ ] Document the changes in `decisions.md`.

**Notes:**

### Task 1.4: D-04 — Remove stale `pixel_to_hex` import comments [Simple]
**Tests:** `rg "pixel_to_hex" game/ui/screens/strategy_*`

- [ ] Run the search; identify every comment/docstring that references the deleted function.
- [ ] Remove the comments (or rewrite to point at `Camera.hex_at_screen`).
- [ ] Re-run focused tests for the affected screens to make sure no live code accidentally referenced it.

**Notes:**

### Task 1.5: D-05 — Update `Galaxy` facade wording [Simple]
**File:** `game/strategy/data/galaxy.py:67`

- [ ] Read the current docstring/comment block at and around line 67.
- [ ] Replace "public + grandfathered private API" framing with accurate post-PROJ-394 wording: the spatial private forwarders were intentionally removed; readers use `Galaxy.state`.
- [ ] Re-run `pytest tests/unit/strategy/data/test_galaxy_state_encapsulation.py` to confirm no test depends on the wording.

**Notes:**

### Task 1.6: D-06 + D-07 — Modern type syntax sweep across new modules [Medium]
**Files:** `game/strategy/engine/superweapon_handlers/*.py` + new modules from PROJ-380/391/396 — confirm via `git log --oneline --since=2026-04-01 --diff-filter=A -- game/`

- [ ] Identify all "new since PROJ-380" modules (use `git log` or grep for `Optional[`).
- [ ] Convert `Optional[X]` → `X | None`, `Union[X, Y]` → `X | Y`, `List[X]` → `list[X]`, `Dict[K, V]` → `dict[K, V]`, `Tuple[...]` → `tuple[...]`.
- [ ] Update import lines: remove `from typing import Optional, Union, List, Dict, Tuple` lines that are no longer needed.
- [ ] Run focused tests for each affected module.
- [ ] `rg "Optional\[" game/strategy/engine/superweapon_handlers/` — should return zero hits.

**Notes:**

### Task 1.7: D-08 — Tighten `FormationSpec` `object` slot [Medium]
**File:** `game/strategy/data/formation_spec.py` (confirm path)

- [ ] Read the current `FormationSpec` serialization. Identify the `object`-typed slot.
- [ ] Decide the correct concrete type (e.g., a Union of valid formation shape strings or a Literal type). Document in `decisions.md`.
- [ ] **Strict TDD**: write a regression test asserting that an unknown formation shape raises (currently silently dropped).
- [ ] Run test against current code — confirm RED.
- [ ] Tighten the type. Re-run test — GREEN.
- [ ] Run focused suite for formations.

**Notes:**

### Task 1.8: D-09 — LOC-ceiling audit (read-only, defer work) [Simple]
**Tests:** `find game/ -name "*.py" | xargs wc -l | sort -n | awk '$1 > 500'`

- [ ] Run the LOC audit on PROJ-380's manifest files.
- [ ] List files over 500 LOC in `findings/loc_deferrals.md` with current LOC count.
- [ ] **Do not split files in this project.** Splitting is real refactor work — that's its own future project. This task only documents what's over.

**Notes:**

### Task 1.9: Run focused suite to validate type sweep + D-08 [Simple]
**Tests:** `pytest tests/ -k "formation or superweapon or strategy_renderer or strategy_screens" -q`

- [ ] Suite passes.
- [ ] If anything fails, triage. Likely cause: a typing import that was removed but still referenced.

**Notes:**

### Task 1.10: Closeout
- [ ] Phase 1 status `Complete`
- [ ] Plan.md updated
- [ ] `Projects/projects_index.md` row for PROJ-407 set to `Complete`
- [ ] Validators PASS
- [ ] Commit `PROJ-407 phase 1: stale-doc + modern-typing sweep + FormationSpec tightening`
- [ ] Verification report at `findings/verification_report.md`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Status at top of this file is `Complete`
- [ ] plan.md updated
- [ ] Focused suite passes
- [ ] `python Projects/scripts/validate_phase.py PROJ-407 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-407` PASSED
