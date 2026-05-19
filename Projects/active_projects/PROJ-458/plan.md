# PROJ-458: UIWindow retrofit completion (SettingsWindow + 4 PlanetTargetEditors)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-458` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-458 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03a-continue-working (serial on `main` per user standing preference; no worktrees).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. SettingsWindow (109 LOC, smallest) — characterization tests + two-stage retrofit + F-C-016 docs touch | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. AtmosphereTargetEditor (273 LOC, largest of the 4 planet-target editors) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. GravityTargetEditor (220 LOC) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. WaterTargetEditor (227 LOC) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. RadiationShieldEditor (231 LOC) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-19
**Active Phase:** Planning
**Last Action:** Group 3 pre-execution review fixes applied (codex + subagent reviews; see consult artifacts at `AgentCoordination/Scratchpad/Consult/20260519T024637Z_group3-pre-execution-review/` and `.agent_reports/group3_pre_execution_review/`). One fix: rewrote `phase_1_checklist.md:11` objective line to drop the misleading "F-C-016 README docs touch" framing — now states "F-C-016 closure limited to `docs/known-issues.md:37` stale warning; `tests/fixtures/README.md` is already current — see Task 1.4." This removes the risk that a skimming agent reopens the already-resolved README half. Earlier 2026-05-19 codex r5 audit fixes retained: (1) F-C-016 scope narrowed to `docs/known-issues.md:37` only — `tests/fixtures/README.md:22, 310-336` is already updated at HEAD; (2) Phase 1 Task 1.2 vs Task 1.3 inconsistency resolved by ADDING kw-only `ui_builder` parameter; (3) Phase 2 pytest node selector corrected to `::TestWindowManagerSignature::test_strategy_only_windows_require_explicit_window_manager`. Existing pre-flight findings unchanged: 1 owned (F-C-017) + F-C-016 carried; all 5 target windows confirmed unretrofitted at HEAD 2026-05-19.
**Next Action:** Run agent picks up PROJ-458 Phase 1 after PROJ-452 + PROJ-455 complete (PROJ-458 is **position 3 of 4** in Group C's serial order `452 → 455 → 458 → 460` — see Group C execution context in the Dependencies & Sibling Projects section and `Projects/active_projects/GroupC_execution_prompt.txt`).
**Blockers:** Serial gate: PROJ-452 + PROJ-455 must complete first within Group C. No external blockers — PROJ-458 is parallel-safe with PROJ-457 (Group B) and PROJ-456 (Group B); Codex r4 confirmed, 2026-05-19 verification re-confirmed disjoint write scopes (PROJ-458 touches 5 files in `game/ui/screens/`; PROJ-457 touches different 3 UI files + `game/core/exceptions.py`).
**2026-05-19 cross-group resolution (final):** No edits required to PROJ-458 beyond the Group C execution-context block. Zero file overlap with Group A or Group B verified.

## Overview
Apply Pattern #33 two-stage `UIWindow` bypass-init retrofit + dedicated behavior-locking characterization tests to the 5 windows PROJ-329A deferred. The recipe is established (5 already-retrofitted UIWindow subclasses in the repo as templates). Each phase tackles one window: write dedicated characterization tests against the bypass-init shell first (RED), then apply the two-stage `__init__` retrofit (GREEN), then verify both the bypass-init test path and the production initialization path work. Smallest-first ordering minimizes review burden and lets the team build muscle on the simplest case (`SettingsWindow`, 109 LOC, direct `UIWindow` subclass) before tackling the 4 `PlanetTargetEditor` subclasses which share a common base class (200-275 LOC each).

## Goals
- Land the two-stage `bypass_init` retrofit on all 5 windows per Pattern #33 (Stage 1 pure-Python state + delegate factory wiring above the bypass guard; `super().__init__(...)` + heavy widget tree via UI builder below).
- Write dedicated behavior-locking characterization tests for each window (state transitions, validation rules, ok/cancel paths) — NOT just structural "does it instantiate" checks.
- Retrofit must preserve all current observable behavior (the characterization tests written before the retrofit are the contract).
- Keep every phase independently shippable (5 sub-PRs internally per Codex r4 framing).
- Close F-C-016 (docs touch) in Phase 1 — scope narrowed by codex r5 audit (2026-05-19): the `tests/fixtures/README.md` half is already resolved at HEAD; the remaining live drift is a single stale-warning paragraph at `docs/known-issues.md:37`. Delete that paragraph in Phase 1 alongside the SettingsWindow retrofit.
- Land with full sharded suite green at the end of each phase.

## Scope

**In Scope:**
- F-C-017 (all 5 windows):
  - Phase 1: `SettingsWindow` (109 LOC) — direct `UIWindow` subclass; simplest case.
  - Phase 2: `AtmosphereTargetEditor` (273 LOC) — inherits from `PlanetTargetEditor`; largest of the 4.
  - Phase 3: `GravityTargetEditor` (220 LOC) — `PlanetTargetEditor` subclass.
  - Phase 4: `WaterTargetEditor` (227 LOC) — `PlanetTargetEditor` subclass.
  - Phase 5: `RadiationShieldEditor` (231 LOC) — `PlanetTargetEditor` subclass.
- F-C-016 (Phase 1 documentary touch): delete the stale-doc warning paragraph at `docs/known-issues.md:37` — the README half this warning references (`tests/fixtures/README.md:22, 310-336`) is already updated at HEAD as of 2026-05-19; only the known-issues warning remains live (codex r5 audit 2026-05-19).

**Out of Scope:**
- All PROJ-456 findings (UI shim retirement). Owned by PROJ-456.
- All PROJ-457 findings (UI structural debt extractions). Owned by PROJ-457.
- F-C-013, F-C-014 — protocol-layer residue. Owned by PROJ-449.
- F-C-015 — `stat_rows_dynamic.py` LABEL_ABBREV. Owned by PROJ-453.
- F-C-018, F-C-019 — static guards. Landed Stages 1+2.
- F-C-020 — `tests/fixtures/strategy_entities.py` legacy kwargs. Owned by PROJ-449.
- F-C-021..F-C-026 — test-skip wallpaper findings. Out of PROJ-458 scope.
- F-C-030 — protocol `Dict[]` / `List[]` annotations. Owned by PROJ-454.
- Refactoring the `PlanetTargetEditor` base class itself (lifted in Phases 2-5 if a common surface needs adjustment; otherwise leave). The shared retrofit pattern applies per-subclass, not base-class.

## Findings Summary

| ID | Severity | Owner phase | File |
|----|----------|-------------|------|
| F-C-017 | low | Phases 1-5 (one window per phase) | 5 UIWindow subclasses |
| F-C-016 | low | Phase 1 (documentary touch — scope narrowed by codex r5) | `docs/known-issues.md:37` (README half already resolved at HEAD) |

Full per-finding details: [findings/PROJ-458_findings.md](findings/PROJ-458_findings.md).

## Key Files

| Component | File Path | LOC (HEAD 2026-05-19) |
|-----------|-----------|---------------------:|
| SettingsWindow | `game/ui/screens/settings_window.py` | 109 |
| AtmosphereTargetEditor | `game/ui/screens/atmosphere_target_editor.py` | 273 |
| GravityTargetEditor | `game/ui/screens/gravity_target_editor.py` | 220 |
| WaterTargetEditor | `game/ui/screens/water_target_editor.py` | 227 |
| RadiationShieldEditor | `game/ui/screens/radiation_shield_editor.py` | 231 |
| PlanetTargetEditor base | `game/ui/screens/planet_target_editor_base.py` | (re-verify; ancestor of 4 of 5) |
| Pattern reference | `docs/02_PATTERNS.md` §33 | — |
| Known-issues docs touch (F-C-016 — scope narrowed 2026-05-19 codex r5) | `docs/known-issues.md:37` (README half already resolved at HEAD) | — |
| Retrofit templates | `game/ui/screens/strategy_modal_window.py`, `race_setup/screen.py`, `race_browser_dialog.py`, `new_game_setup_screen.py`, `design_selector_window.py` | — |
| Incidental coverage cross-references | `tests/unit/ui/screens/test_strategy_modal_window.py:367-398`, `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py:100-127` | — |
| New dedicated tests | `tests/unit/ui/screens/test_settings_window.py` (new), `test_atmosphere_target_editor.py` (new), `test_gravity_target_editor.py` (new), `test_water_target_editor.py` (new), `test_radiation_shield_editor.py` (new) | — |

Full enumeration in [manifest.md](manifest.md).

## Phase Breakdown

The same recipe applies to all 5 phases. Each phase touches one window file + one new test file. Per-phase tasks below.

### Per-phase recipe (applies to every phase)

1. **Read the target window** — identify (a) all `__init__` state assignments, (b) all `super().__init__(...)` calls (Stage 2 work), (c) all UI widget construction, (d) any callback wiring or registrar registration that happens in `__init__`.
2. **Read a retrofitted template** — pick one of the 5 already-retrofitted UIWindow subclasses (`race_setup/screen.py` is the most thoroughly retrofitted with both `if getattr(type(self), 'bypass_init', False):` guard and `Null/Mock UiBuilder` injection). Read the exact Stage 1 / guard / Stage 2 shape.
3. **Write dedicated characterization tests** (RED) — at `tests/unit/ui/screens/test_<window>.py`, write tests covering:
   - Construction (bypass-init shell + production shell both yield valid instances).
   - All public state transitions (Apply, Reset, Cancel, slider change, button press).
   - Validation rules (what inputs are rejected; what error states surface).
   - Callback emission (on_apply / on_close fire at the right moments with the right payloads).
   - Test uses `make_ui_widget(<WindowCls>, bypass_init=True)` per `tests/fixtures/ui_widget_factory.py`.
   - **Confirm all new tests FAIL before the retrofit** — proves they're locking real behavior.
4. **Apply the two-stage retrofit** (GREEN) — rewrite the target window's `__init__`:
   - **Stage 1 (above guard)**: pure-Python state initialization + delegate-factory wiring + UI-builder seam setup. No `pygame_gui` widgets, no `self.get_container()`, no asset I/O.
   - **Guard**: `if getattr(type(self), 'bypass_init', False): return` (use `type(self)` so inherited guards honor subclass flags).
   - **Stage 2 (below guard)**: `super().__init__(...)` + heavy widget tree via UI builder. `builder = ui_builder or DefaultXxxUiBuilder()`; `builder.build(self)`.
5. **Run all tests** — characterization tests now GREEN; sharded suite green.
6. **Cross-reference incidental coverage** — verify `test_strategy_modal_window.py:367-398` parametrized test still passes for this window (window_manager required). Verify `test_empire_panel_ctrl.py:100-127` still passes for `SettingsWindow` if applicable.

### Phase 1: SettingsWindow (109 LOC, smallest) — characterization tests + two-stage retrofit + F-C-016 docs touch
Phase 1 also includes the F-C-016 documentary touch — scope narrowed by codex r5 audit (2026-05-19): only `docs/known-issues.md:37` needs editing (delete the stale-doc warning). The `tests/fixtures/README.md` half is already resolved at HEAD.

`SettingsWindow` (verified 2026-05-19) inherits directly from `UIWindow`, not from a shared base — the simplest of the 5. Constructor takes `rect, manager, on_close_callback`; state is `on_close_callback` + `_settings` (a `GameSettings` instance) + 3 widget handles (`_brightness_slider`, `_brightness_label`, `_btn_reset`, `_btn_close`).

**Checkpoint:** `tests/unit/ui/screens/test_settings_window.py` exists with characterization tests; bypass-init test path works; `settings_window.py` has the two-stage `__init__` shape; sharded suite green; `tests/fixtures/README.md` references Pattern #33.

### Phase 2: AtmosphereTargetEditor (273 LOC, largest of the 4 planet-target editors)
`AtmosphereTargetEditor` (verified 2026-05-19) inherits from `PlanetTargetEditor` (at `game/ui/screens/planet_target_editor_base.py`). The base class's `__init__` is called via `super().__init__(...)` at line 74-79 with `window_display_title`, `resizable=True`, `window_manager`. The subclass handles gas-tier slider construction (~10 gases × slider+label+spin = ~30 widgets) and species-ideal preset wiring.

This phase is the largest of the 4 PlanetTargetEditor subclasses; tackling it first lets the executing agent discover the shared `PlanetTargetEditor` base-class retrofit pattern (if needed), so the remaining 3 phases share the proven approach.

**Checkpoint:** `tests/unit/ui/screens/test_atmosphere_target_editor.py` exists; bypass-init test path works; `atmosphere_target_editor.py` has the two-stage `__init__` shape; sharded suite green.

### Phase 3: GravityTargetEditor (220 LOC)
Same recipe as Phase 2; `GravityTargetEditor` is a `PlanetTargetEditor` subclass with a simpler value-grid (gravity has fewer dimensions than atmosphere).

**Checkpoint:** `tests/unit/ui/screens/test_gravity_target_editor.py` exists; retrofit applied; sharded suite green.

### Phase 4: WaterTargetEditor (227 LOC)
Same recipe; `WaterTargetEditor` is a `PlanetTargetEditor` subclass.

**Checkpoint:** `tests/unit/ui/screens/test_water_target_editor.py` exists; retrofit applied; sharded suite green.

### Phase 5: RadiationShieldEditor (231 LOC)
Same recipe; `RadiationShieldEditor` is a `PlanetTargetEditor` subclass.

**Checkpoint:** `tests/unit/ui/screens/test_radiation_shield_editor.py` exists; retrofit applied; sharded suite green. PROJ-458 complete.

## Dependencies & Sibling Projects

### Group C execution context (coordinator-assigned 2026-05-19)

**Group C serial order: PROJ-452 → PROJ-455 → PROJ-458 → PROJ-460.**

This is **PROJ-458 — position 3 of 4** in Group C. The run agent reaches this project only after PROJ-452 and PROJ-455 complete (all phases + codex audits + any audit-driven extra phases). When this project is complete, advance to PROJ-460.

Groups A (PROJ-449/451/450/459) and B (PROJ-456/454/457) run in parallel branches. Coordinator confirmed no hard cross-group blockers. See `Projects/active_projects/GroupC_execution_prompt.txt` for the run agent's full execution contract.

### Other-project relationships

- **No hard predecessor** within Group C beyond the serial gate.
- **Sibling: PROJ-457 (Group B)** is parallel-safe with PROJ-458 — Codex r4 confirmed, write scopes verified disjoint 2026-05-19. PROJ-457 touches `build_queue_screen.py`, `planet_list_window.py`, `test_lab/screen.py`, `game/core/exceptions.py`; PROJ-458 touches `settings_window.py`, `atmosphere_target_editor.py`, `gravity_target_editor.py`, `water_target_editor.py`, `radiation_shield_editor.py`. **Zero file overlap.**
- **Sibling: PROJ-456 (Group B)** is also parallel-safe with PROJ-458 — PROJ-456 touches a different set of UI files. The one minor coordination concern: PROJ-456 Phase 1 includes F-C-012 (`event_log_window.py` empire_name fallback) which would land in `event_log_window.py` — not one of the 5 PROJ-458 target windows. **Zero file overlap.**

**Write-scope overlap risk:** flagged but verified zero. If PROJ-456 or PROJ-457 lands changes that touch any of the 5 PROJ-458 target windows during PROJ-458's execution (unlikely per the verified scope tables), rebase PROJ-458's Phase N branch before continuing.

**No worktrees** per user standing preference. Serial execution in `main` checkout.

## Related Documents

- [design.md](design.md) — design rationale for the smallest-first phasing.
- [decisions.md](decisions.md) — full decisions log; per-phase choices (e.g. whether PlanetTargetEditor base class needs adjustment).
- [findings/PROJ-458_findings.md](findings/PROJ-458_findings.md) — 1 owned finding (F-C-017) + 1 carried-over docs touch (F-C-016).
- [manifest.md](manifest.md) — file-touch list grouped by phase.
- Codex r4 audit redesign: [`AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`](../../../AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md) — Job 10 row.
- Original bucket scan (2026-05-18): [`Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`](../../archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md).
- **Primary pattern reference**: `docs/02_PATTERNS.md` §33 — UI Widget Test Factory + two-stage `UIWindow` bypass-init recipe (the central pattern for this entire project).
- Compositional Construction pattern: `docs/02_PATTERNS.md` §32 — relevant if a retrofit surfaces multiple heavy collaborators.
- Existing retrofit templates: `game/ui/screens/race_setup/screen.py`, `race_browser_dialog.py`, `new_game_setup_screen.py`, `design_selector_window.py`.

## Verification

### Project Start (REQUIRED)
- [ ] Read `docs/02_PATTERNS.md` §33 (UI Widget Test Factory + two-stage UIWindow bypass-init) in full.
- [ ] Read `tests/fixtures/ui_widget_factory.py` and `tests/fixtures/test_ui_widget_factory.py` to understand the `make_ui_widget(...)` + `bypass_init(...)` helpers.
- [ ] Read all 5 retrofitted templates: `game/ui/screens/strategy_modal_window.py`, `race_setup/screen.py`, `race_browser_dialog.py`, `new_game_setup_screen.py`, `design_selector_window.py`. Note the consistent Stage 1 / guard / Stage 2 shape.
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — all tests pass (establishes baseline).

### After Each Phase
- [ ] Targeted tests for the touched window pass.
- [ ] Sharded suite green (no regression).
- [ ] Dedicated characterization test file committed for the touched window.
- [ ] Window's `__init__` has the two-stage shape: pure-Python state above the bypass guard, `super().__init__(...)` + UI builder below.
- [ ] `plan.md` Quick Status table updated for the closed phase.
- [ ] Current State `Last Updated` / `Active Phase` / `Last Action` / `Next Action` updated.

### Final Verification (after Phase 5)
- [ ] All 5 target windows have:
  - [ ] Dedicated characterization tests at `tests/unit/ui/screens/test_<window>.py`.
  - [ ] Two-stage `__init__` with the `if getattr(type(self), 'bypass_init', False): return` guard.
  - [ ] No regression on the incidental coverage tests at `test_strategy_modal_window.py:367-398` and `test_empire_panel_ctrl.py:100-127`.
- [ ] F-C-017 + F-C-016 flipped to `Status: resolved` in `findings/PROJ-458_findings.md`.
- [ ] `docs/known-issues.md:37` stale-doc warning paragraph removed (F-C-016 closed). The `tests/fixtures/README.md` half was already resolved at HEAD as of 2026-05-19 — no edit needed there.
- [ ] Sharded suite green: `python Tools/test_sharded/test_sharded.py`.
- [ ] Codex end-of-project consult landed; verified findings remediated.
- [ ] User applies the `verified` label.
