# PROJ-456 Phase 1: Smallest-shim cluster (5 fixes, each independently shippable)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-456 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** None
**Review Mode:** standard
**Objective:** Burn down 5 independent <30-LOC shim fixes. Each task is self-contained; no inter-task dependencies. Can land as one PR or five — operator's choice. Smallest-first per Codex r4 review-burden risk.

**Source-of-truth findings:** [`findings/PROJ-456_findings.md`](findings/PROJ-456_findings.md) — read F-C-002, F-C-005, F-C-007, F-C-010, F-C-012 before starting each task.

---

## Tasks

### Task 1.1: F-C-002 — `transfer_dialog._on_confirm` broad-catch marker [Simple]
**File:** `game/ui/screens/transfer_dialog.py:412`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py -q`

- [ ] Read existing `except Exception:` at line 412; confirm the body comment ("Catastrophic dispatch failure — close the modal...") exists but no convention-required `# Intentional broad catch: <reason>` marker is present.
- [ ] **GREEN-only** (no test change — this is convention compliance): Add `# Intentional broad catch: dialog-level catastrophic failure must not leak; kill modal then re-raise.` immediately above line 412 (or on the same line after `except Exception:`).
- [ ] Verify no other `except Exception` blocks in `game/ui/` lack the marker (PowerShell-safe): `rg -n "except\s+Exception\s*:" game/ui/screens/ | Select-String -NotMatch "Intentional"` should return no hits.
- [ ] Run targeted tests; full sharded suite green for the touched file.

**Notes:** This is the only existing broad-catch convention violation in `game/ui/` per F-C-002. No test change needed.

---

### Task 1.2: F-C-005 — Module-level `draw_grid` free function retirement [Simple]
**File:** `game/ui/screens/strategy_render/grid.py:104-110`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py tests/unit/ui/screens/strategy_render/test_grid_and_storms.py -q`

- [ ] Read `draw_grid(r, screen)` at grid.py:104-110 and `GridLayer.draw(...)` directly below it. Confirm `draw_grid` is a thin wrapper around `_render_grid_to_surface(r, screen)` (line 110) — same path GridLayer uses internally.
- [ ] **RED**: Migrate `tests/unit/ui/screens/test_strategy_renderer.py` from importing/calling `draw_grid(...)` to instantiating `GridLayer()` and calling `.draw(...)`. Run; existing assertions should hold (same render path). If any assertion targeted the free-function form specifically, rewrite to target `GridLayer.draw`.
- [ ] **RED**: Migrate `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py` to `GridLayer()`/`.draw(...)`. Same pattern.
- [ ] **GREEN**: Delete the `draw_grid(r, screen)` function at grid.py:104-110 (5 lines + 2-line gap before `class GridLayer:`).
- [ ] **Verify (PowerShell-safe)**: `rg -n "draw_grid\(" game tests` returns 0 hits. The 4 game files that previously matched (`strategy_renderer.py`, `strategy_render/grid.py`, `battle_ui.py`, `battle_screen.py`) — the latter two are `self.draw_grid` method names, unrelated to the deleted free function.
- [ ] Run targeted tests; full sharded suite green for the touched files.

**Notes:** F-C-005 says "Production callers all use `_draw_grid` method on the renderer; only the two test files reach the module-level function." Verified 2026-05-19 — exactly two test files import `draw_grid`.

---

### Task 1.3: F-C-007 — `RaceSetupScreen._description_controller` shim retirement [Simple]
**File:** `game/ui/screens/race_setup/screen.py:277-285`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py tests/unit/ui/screens/race_setup/test_controller.py tests/unit/ui/screens/race_setup/test_panel_factory.py -q`

- [ ] Read property + setter at race_setup/screen.py:277-285. Confirm getter returns `self._controller.description_controller`; setter calls `self._controller.attach_description_controller(value)`.
- [ ] **RED**: Migrate the 12 test references found in 3 files (verified 2026-05-19):
  - `tests/unit/ui/screens/test_race_setup_screen.py` (1 ref) → `screen._controller.description_controller` (read) / `screen._controller.attach_description_controller(...)` (write).
  - `tests/unit/ui/screens/race_setup/test_controller.py` (4 refs) → same migration.
  - `tests/unit/ui/screens/race_setup/test_panel_factory.py` (7 refs) → same migration.
  - Run each test file; assertions hold (same underlying state).
- [ ] **GREEN**: Delete property + setter at race_setup/screen.py:277-285 (9 lines).
- [ ] Also check the 15 production-side references in `game/ui/screens/race_setup/controller.py` (8), `panel_factory.py` (2), `screen.py` (5). The 5 in `screen.py` are inside the property/setter being deleted plus the comment header; the 2 in `panel_factory.py` and 8 in `controller.py` are the underlying canonical surface — leave intact.
- [ ] **Verify (PowerShell-safe)**: `rg -n "screen\._description_controller|self\._description_controller" game tests` returns 0 hits outside the deleted block.
- [ ] Run targeted tests; full sharded suite green.

**Notes:** Bypass-init helpers also wire through `_description_controller` per finding. Run (PowerShell-safe) `rg -n "_description_controller" tests/fixtures/` before deleting to catch any fixture-side reads.

---

### Task 1.4: F-C-010 — `OrdersWindow._get_order_description` shim retirement [Simple]
**File:** `game/ui/screens/orders_window.py:464-475`
**Tests:** `pytest tests/unit/ui/screens/test_orders_window.py tests/unit/ui/screens/test_fleet_orders_refresh.py tests/integration/ui/test_fleet_build_button.py -q`

- [ ] Read `_get_order_description` at orders_window.py:464-475. Confirm body is `return self._order_describer.describe(order, self.entity)`.
- [ ] Read `OrderDescriber.describe(order, entity)` (likely at `game/ui/screens/order_describer.py` — verify path via `rg -n "class OrderDescriber" game`). Confirm canonical surface.
- [ ] **RED**: Migrate test callers from `screen._get_order_description(order)` to `OrderDescriber().describe(order, screen.entity)`:
  - `tests/unit/ui/screens/test_orders_window.py` — confirm `TestOrderDescriber` block at lines 67-94 (already uses `OrderDescriber()` directly per the grep snippet); the remaining `_get_order_description` references in this file may be in different tests — migrate each.
  - `tests/unit/ui/screens/test_fleet_orders_refresh.py` — same migration.
  - `tests/integration/ui/test_fleet_build_button.py` — same migration.
- [ ] **GREEN**: Delete shim method + comment block at orders_window.py:464-475 (12 lines).
- [ ] **Verify (PowerShell-safe)**: `rg -n "_get_order_description\(" game tests` returns 0 hits.
- [ ] Run targeted tests; full sharded suite green.

**Notes:** F-C-010 confirms production calls `OrderDescriber` directly. The 27-file grep hit list was inflated by docs / archived projects / review artifacts.

---

### Task 1.5: F-C-012 — `EventLogWindow.empire_name=None` fallback retirement [Simple]
**File:** `game/ui/screens/event_log_window.py:113-116`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_no_copy.py tests/unit/ui/screens/test_event_log_replay_button.py tests/unit/ui/screens/test_event_log_row_pool_visibility.py tests/unit/ui/screens/test_event_log_window_reuse.py tests/unit/ui/screens/test_strategy_modal_hidden_input.py tests/integration/ui/test_event_log_replay_e2e.py tests/integration/replay/test_event_log_graceful_degradation.py tests/performance/test_panel_full_open_benchmark.py -q`

- [ ] Read `event_log_window.py:105-117` and the title-rendering block (find via `rg -n "Event Log" game/ui/screens/event_log_window.py`). Confirm the docstring at 113-116 documents the `None` fallback; the rendering branch is where the `if empire_name is None:` (or equivalent) lives.
- [ ] **Decision**: option (a) remove the `None` fallback entirely — change `empire_name` to a required keyword-only parameter; option (b) keep `None` as the documented default but require all 8 test sites to supply an explicit value. Prefer (a) per F-C-012 suggested action.
- [ ] **RED**: For each of the 8 test files (verified 2026-05-19), audit `EventLogWindow(...)` constructor calls and supply `empire_name="<some empire name>"` (use `"Test Empire"` for test fixtures, or thread through whatever empire object the test already has).
- [ ] **GREEN**: Change `event_log_window.py` `__init__` signature: remove `empire_name=None` default, make it required keyword-only (`empire_name: str`). Remove the `None`-branch in the title-rendering code (always use the `"Event Log — <empire_name> Empire"` form).
- [ ] Update the docstring at 113-116 — drop the "back-compat for callers that don't supply it, including tests" line.
- [ ] **Verify (PowerShell-safe)**: `rg -n "EventLogWindow\(" tests | Select-String -NotMatch "empire_name"` returns 0 hits (every construction passes `empire_name=`).
- [ ] Run targeted tests; full sharded suite green.

**Notes:** This finding is the smallest of the 5; the choice between option (a) and (b) should be recorded in `decisions.md`. Option (a) is the root-cause fix; option (b) is the half-measure.

---

## Phase Completion Checklist

When all 5 tasks are checked off:
- [ ] All 5 finding entries (F-C-002, F-C-005, F-C-007, F-C-010, F-C-012) flipped to `Status: resolved` in `findings/PROJ-456_findings.md` with a one-line note.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-456 1` — PASSED.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 2.
- [ ] Commit message: `PROJ-456 Phase 1: retire 5 small UI back-compat shims (F-C-002, F-C-005, F-C-007, F-C-010, F-C-012)`.
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
