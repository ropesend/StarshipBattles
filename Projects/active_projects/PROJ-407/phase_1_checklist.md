# Phase 1: Sweep stale docs/comments + non-modern type annotations

**Status:** Complete
**Objective:** Close 8 of 9 Tier 3 items in a single sweep; document D-09 LOC-ceiling work as deferral.

---

## Tasks

### Task 1.1: D-01 — Update `command_handlers` doc references [Simple]
**Tests:** `rg "game\.strategy\.engine\.command_handlers" docs/`

- [x] Run the search; capture every hit.
- [x] For each hit, update to `game.strategy.engine.handlers/` (the canonical package path).
- [x] Re-run the search — zero hits remain that describe the deleted shim as current; remaining mentions are explicitly historical (PROJ-383 retirement notes).

**Notes:** 4 doc files updated (`docs/02_PATTERNS.md`, `docs/systems/strategy_layer.md`, `docs/systems/orders_system.md`, `docs/systems/production_system.md`). Total of 8 inline references rewritten. Surviving mentions are now correctly framed as "PROJ-383 deleted the shim".

### Task 1.2: D-02 — Update event-logging API references [Simple]
**Tests:** `rg "log_event|set_event_handler|get_event_handler" docs/`

- [x] Run the search.
- [x] Per architecture (PROJ-252), EventBus is session-scoped via constructor injection. Updated `docs/01_ARCHITECTURE.md` line 96 and `docs/05_ERROR_HANDLING.md` lines 13, 147-154.
- [x] Re-run — only legitimate hits remain (`EventBus.log_event` method calls and historical PROJ-390 retirement notes).

**Notes:** 2 doc files updated.

### Task 1.3: D-03 — Reconcile `docs/05_ERROR_HANDLING.md` with EventBus arch [Medium]
**File:** `docs/05_ERROR_HANDLING.md` + actual EventBus code

- [x] Read `docs/05_ERROR_HANDLING.md` end to end.
- [x] Read the current EventBus implementation at `game/core/event_logging.py`. Live API: `EventBus(handler=None)`, `EventBus.set_handler(handler)`, `EventBus.log_event(event_type, **kwargs)`. Module-level shim is gone.
- [x] Identified contradictions: (a) Source Files line 13 said "session-scoped EventBus plus module-level compatibility API"; (b) Structured Events section claimed module-level shims "remain compatibility API"; (c) referenced non-existent method `set_event_handler` (live name is `set_handler`).
- [x] Updated the doc. Did not change the code.
- [x] Documented the changes in `decisions.md`.

**Notes:** See `decisions.md` for the divergence log.

### Task 1.4: D-04 — Remove stale `pixel_to_hex` import comments [Simple]
**Tests:** `rg "pixel_to_hex" game/ui/screens/strategy_*`

- [x] Run the search; identified 3 module-docstring "Cross-layer imports" notes still claiming `pixel_to_hex`.
- [x] Updated each to point at `Camera.hex_at_screen`, the helper actually used by the live code.
- [x] Re-ran focused tests — D-04 changes are pure docstring; suite pass confirmed by Task 1.9.

**Notes:** `strategy_fleet_ops.py`, `strategy_colonization.py`, `strategy_superweapons.py` — 1 line each.

### Task 1.5: D-05 — Update `Galaxy` facade wording [Simple]
**File:** `game/strategy/data/galaxy.py:67`

- [x] Read the current docstring/comment block at and around line 67.
- [x] Replaced "preserve public + grandfathered private API" with accurate post-PROJ-394 wording: "public read-only access to GalaxyState; the 5 spatial private forwarders were intentionally removed; new readers use Galaxy.state".
- [x] Re-ran `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` — 2 passed.

**Notes:** Single-line comment update at `game/strategy/data/galaxy.py:67`.

### Task 1.6: D-06 + D-07 — Modern type syntax sweep across new modules [Medium]
**Files:** `game/strategy/engine/superweapon_handlers/*.py` + new modules from PROJ-380/391/396 — confirmed via `git log --grep="PROJ-XXX" --diff-filter=A`

- [x] Identified new-since-PROJ-380 modules: `game/services/provider_factory.py` (PROJ-380), `game/strategy/engine/superweapon_handlers/{stellerate_star,implode_planet,create_dyson_sphere,open_warp_point,close_warp_point}.py` (PROJ-396). PROJ-391 added no new files.
- [x] Converted `Optional[X]` -> `X | None`, `Union[X, Y]` -> `X | Y`, `List[X]` -> `list[X]`, `Dict[K, V]` -> `dict[K, V]`, `Tuple[...]` -> `tuple[...]`.
- [x] Trimmed unused `from typing import Optional, Union, List, Dict, Tuple` imports.
- [x] Ran focused tests — 395 superweapon/provider_factory tests pass.
- [x] `rg "Optional\[" game/strategy/engine/superweapon_handlers/` returns zero hits.

**Notes:** 6 files modernized; PROJ-391 added no new files.

### Task 1.7: D-08 — Tighten `FormationSpec` `object` slot [Medium]
**File:** `game/simulation/battle_spec.py` (the upstream slot, not `formation_spec.py`)

- [x] Read the current `TaskForceSpec` definition. Identified `formation: object  # FormationSpec — real type lands in Task 1.4` — a Phase 1 vestige.
- [x] Decided the correct concrete type: `FormationSpec | None` (per replay tests, None is a legitimate free-maneuver value). Documented in `decisions.md`.
- [x] **Strict TDD**: wrote a regression test `test_task_force_spec_rejects_non_formation_spec` asserting `TypeError` when `formation=object()`.
- [x] Ran test against current code — confirmed RED (test failed: silent acceptance).
- [x] Tightened the type via `__post_init__` (frozen dataclass, no native annotation enforcement). Re-ran test — GREEN.
- [x] Replaced the silent isinstance-drop fallback in `_task_force_spec_to_dict` with a direct call.
- [x] Updated test fixture `_SENTINEL_FORMATION` to a real `FormationSpec(LINE_ABREAST, 100.0)`. Rewrote the legacy "serializes non-FormationSpec as None" test to assert the new TypeError contract.
- [x] Ran formation-related focused suite via Task 1.9.

**Notes:** New constraint type: `FormationSpec | None`.

### Task 1.8: D-09 — LOC-ceiling audit (read-only, defer work) [Simple]
**Tests:** `wc -l <PROJ-380 manifest files>`

- [x] Ran the LOC audit on PROJ-380's touched files (29 game/*.py files identified via `git log --grep="PROJ-380" --name-only`).
- [x] Listed 7 files over 500 LOC in `findings/loc_deferrals.md` with current LOC counts and a recommendation for a future coordinated decomp project.
- [x] **No splits in this project.** Documented only.

**Notes:** Largest: `battle_controller.py` (831), `battle_state.py` (830), `battle_runner.py` (734).

### Task 1.9: Run focused suite to validate type sweep + D-08 [Simple]
**Tests:** `pytest tests/ -k "formation or superweapon or strategy_renderer or strategy_screens" -q`

- [x] Suite passes. **540 passed** in 11.88s.

**Notes:** Run on `feat/03c-phase-aware-execution` post-D-08.

### Task 1.10: Closeout
- [x] Phase 1 status `Complete`
- [x] Plan.md updated
- [x] `Projects/projects_index.md` row for PROJ-407 set to `Complete`
- [x] Validators PASS (run by parent agent at handoff)
- [x] Commits per cluster:
    - `48741b0cd` PROJ-407 phase 1: D-01 update command_handlers doc references
    - `d3b7faccc` PROJ-407 phase 1: D-02 + D-03 reconcile EventBus docs with live code
    - `f0ef345fa` PROJ-407 phase 1: D-04 + D-05 fix stale strategy-screen + Galaxy comments
    - `0dd1b23af` PROJ-407 phase 1: D-06 + D-07 modern type syntax in new modules
    - `924012525` PROJ-407 phase 1: D-08 tighten TaskForceSpec.formation type
    - closeout commit appended after this checkbox is checked.
- [x] Verification report at `findings/loc_deferrals.md` (D-09) and `decisions.md` (D-03 + D-08).

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Status at top of this file is `Complete`
- [x] plan.md updated
- [x] Focused suite passes
- [x] `python Projects/scripts/validate_phase.py PROJ-407 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-407` PASSED
