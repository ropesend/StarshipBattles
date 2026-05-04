# PROJ-325: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

- Continuation review of PROJ-321 / 322 / 323 dated 2026-05-04
- OpenCode 323-review: `Reviews/results/2026-05-04_020005_consistency_proj-323-p2-opportunistic-test-polish-completion-c_req-req_20260504_020003_a5290a/report.md`
- OpenCode 322-review (RaceSetupScreen analysis): `Reviews/results/2026-05-04_015938_consistency_proj-322-p1-brittle-bloated-test-remediation-compl_req-req_20260504_015935_7d4449/report.md`
- Continuation plan: [`AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`](AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md)

## Phase 1 — PROJ-323 Documentation Corrections

The OpenCode 323-review found 1 CRIT and 15 MIN findings, almost all documentation-only. The CRIT-001 is the most important: PROJ-323 `phase_3_checklist.md` Tasks 3.3 and 3.6 are checked `[x]` as completed but their target files were deleted by upstream PROJ-321. Sibling items in the same tasks correctly show `_(skipped — upstream project already deleted target file)_` markers, so the discrepancy is a documentation defect — the worker mis-checked instead of skipping.

**Concrete fixes:**

| Finding | Action |
|---|---|
| FND-CC-001 | In `Projects/active_projects/PROJ-323/phase_3_checklist.md`: re-mark Task 3.3 (S11-CAT10-005, target `test_colonization_facade.py`) and Task 3.6 (S11-CAT10-007, target `test_color_helpers.py`) as `_(skipped — upstream project already deleted target file)_`. Combined claimed LOC delta (~314) is fictitious. |
| FND-CC-002 | In `plan.md` header table: reconcile "items" (CAT-finding counts: 32+32+53+15+27=159) vs "tasks" (Task N.M counts: 149) terminology. Add a footnote explaining the difference. |
| FND-CC-003 | In phase checklist verify lines: annotate per-task LOC delta numbers as "(estimate from source review)" or replace with actual git-stat deltas. |
| FND-CC-004 | In `manifest.md`: remove ~42 entries for files PROJ-321 deleted upstream. |
| FND-CC-005 | In `phase_3_checklist.md` Task 3.10: marked `[x]` but annotated "deferred". Pick one — either un-check and add deferral annotation, or remove the deferral annotation if it's actually done. |
| FND-CC-006 | Tasks 2.8 and 2.9 LOC deltas (~307, ~250) double-count work done in Phase 1. Re-derive from git stats. |
| FND-P2-001 | In `tests/unit/simulation/projectile/test_projectile_manager.py` Task 5.19: docstring derivations use ~ approximations (~0.94, ~0.9787) but assertion uses `rel=1e-9` tolerance on `-0.005596103475344202`. Either add intermediate values to docstring at assertion precision, or relax tolerance to `rel=1e-5`. |
| FND-P2-003 | In `Projects/active_projects/PROJ-323/design.md:41`: references deleted `test_projectile_manager.py` as canonical example. Replace with a surviving example. |
| FND-P2-004 | Task 4.9 mis-categorized — it's data cleanup, not fragile-assertion replacement. Re-categorize in checklist text. |
| FND-P2-005 | In `design.md:42`: mischaracterizes Task 4.2 pattern as "advisory soft assertions" when the actual implementation uses hard assertions with soft thresholds. Reword. |

These are all surface-level fixes — no production or test code changes required for FND-CC-001..006 + FND-P2-003..005. Only Task 5.19 requires a touch to `test_projectile_manager.py`.

## Phase 2 — Task 3.34 + Task 3.37 Parametrize

### Task 3.34: 11-handler `fleet_not_found` cluster

PROJ-323 deferred this with rationale "per-class structure aligns with production." The OpenCode 323-review found this rationale **factually weak**: production handlers are split across 5 sub-module files, but the test file is monolithic 1899 LOC. The genuine concern — construction-queue handlers use `entity_id` instead of `fleet_id` — is resolvable with a **two-group parametrization**.

**Approach:**
- Group A: handlers using `fleet_id` (~9 of 11). Class-level `@pytest.mark.parametrize` over the handler classes, each test asserts the same `fleet_not_found` error.
- Group B: handlers using `entity_id` (~2 construction-queue handlers). Separate parametrize cluster with the entity_id-shaped fixture.
- Estimated savings: ~75 LOC.

The Task 3.2 precedent in the same project phase already demonstrated successful class-level parametrize across handler classes — so this is a proven pattern.

### Task 3.37: zero/negative cargo pairs

OpenCode 323-review FND-P1-003: zero/negative cargo amount tests across load/unload are textbook 2-member parametrize candidates that were unnecessarily blocked by the strict ≥3-member threshold rule. Estimated savings: ~10 LOC.

## Phase 3 — RaceSetupScreen Testable Construction

This phase is **conditional on PROJ-324 Phase 3 Task 3.4 outcome.**

> **PROJ-324 Phase 3 Task 3.4 outcome (2026-05-04): NO-GO confirmed.** PROJ-325 Phase 3 is now ON: NO-GO path applies. Head-start data captured below in "NO-GO findings from PROJ-324 Phase 3 Task 3.4 probe".

### NO-GO findings from PROJ-324 Phase 3 Task 3.4 probe (2026-05-04)

`make_ui_widget(RaceSetupScreen, ...)` inside `with bypass_init(RaceSetupScreen):` constructs cleanly (no exceptions, no real pygame display required). The `bypass_init` production guard at `screen.py:98-99` works as designed. **However**, because the guard early-returns *before* `super().__init__()` and *before* all the production attribute-mirror assignments, the resulting instance is bare — no `race_config`, no `_controller`, no `_view_model`, no `step_panels`, no buttons. Tests would still need to manually wire ~30 attributes (real `RaceSetupController`/`RaceSetupRenderer`/`RaceSetupViewModel`/`LLMDialogService`/`RaceSetupInputHandler` delegates plus 8 panel + 8 button MagicMock slots). The 62 tests in `test_race_setup_screen.py` routinely call `screen._controller.on_save()`, `screen._controller.on_race_selected(...)`, etc. — they exercise REAL delegate behaviour, so the delegates cannot be MagicMock substitutes.

Net LOC delta of a `bypass_init`-only migration: ~0. Net complexity reduction: 0. The existing `__new__`-based helper is unchanged in shape; only the bypass mechanism would be substituted.

**Implication for the panel-registry refactor:** the refactor must address `_create_ui()` specifically (the `_create_tab_buttons` + `_create_step_panels` + `_create_navigation_buttons` + `error_label` block on `screen.py:199-219`). That is the sole heavy chunk. The 5 delegate constructions (RaceSetupViewModel, RaceSetupRenderer, RaceSetupController, LLMDialogService, RaceSetupInputHandler) are CHEAP in the headless-test sense — they don't touch pygame_gui directly; they're plain Python classes. So a successful refactor only needs to factor out `_create_ui()` (or its three sub-methods), not the full `__init__`.

**Concrete construction wiring needed by tests** (extracted from existing helper at `tests/unit/ui/screens/test_race_setup_screen.py:31-148`):

- 4 mandatory `__init__` params: `rect: pygame.Rect`, `manager: UIManager` (Mock OK), `on_complete_callback: Callable` (Mock OK), `on_cancel_callback: Callable` (Mock OK).
- 2 optional `__init__` params: `race_to_edit: Optional[RaceConfig]`, `race_registry: Optional[IRaceRegistry]`. Both default-None.
- Production `__init__` builds: `RaceConfig` (or uses `race_to_edit`), `RaceLibrary()` (no-arg), `RaceAssetLoader()` (no-arg), `RaceSetupViewModel(is_editing=...)`, `RaceSetupRenderer(screen=self)`, `RaceSetupController(screen=..., view_model=..., renderer=..., race_config=..., race_library=..., race_registry=..., on_complete_callback=..., on_cancel_callback=...)`, `LLMDialogService(view_model=..., renderer=...)`, `RaceSetupInputHandler(screen=self)`. None of these are pygame_gui-touching.
- Then `_create_ui()` builds tab buttons (one `pygame_gui.elements.UIButton` per tab name), 7 panels via `panel_factory.create_*_panel(self, panel)` (each panel calls `pygame_gui.elements.UIPanel`), 4 navigation buttons, and the `error_label`. **This is the sole pygame_gui-heavy block.**

**Recommended refactor approach (SUPERSEDED 2026-05-04):** The original "panel-registry seam alone is sufficient" framing in this section was incorrect — see Codex–Claude consensus. `pygame_gui.elements.UIWindow.__init__` is MRO-bound and heavy regardless of any panel-registry abstraction, so `bypass_init` must stay as the shell-bypass mechanism. The refactor is about (a) what runs *before* the bypass point (cheap state + delegate factory/bundle) and (b) what runs *after* the bypass point (per-class UI builder with paired Null/Mock variants), not replacing `bypass_init`.

**Canonical refactor spec:** [`findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`](findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md). All execution agents for PROJ-325 Phase 3 + PROJ-328 should treat that plan + the discussion's `outcome.md` as the source of truth.

**PoC findings (REQUIRED reading before any UIWindow-subclass refactor):** [`findings/poc_findings.md`](findings/poc_findings.md) captures 4 refinements to the consensus plan headline that were discovered DURING the RaceSetupScreen PoC implementation (commit `92a7490b6`). Applying the consensus plan verbatim without these findings re-discovers all 4 issues from scratch. Originally only documented in [`Projects/active_projects/PROJ-328/phase_1_checklist.md`](../PROJ-328/phase_1_checklist.md); backported here 2026-05-04 (audit-remediation S1.7).



### Background

`RaceSetupScreen` ([`game/ui/screens/race_setup/screen.py:60`](game/ui/screens/race_setup/screen.py#L60)) is the highest-touch UIWindow subclass:

- 6 declared `__init__` parameters
- ~37 instance attributes assigned
- ~10 major collaborators directly constructed (RaceLibrary, RaceConfig, 4 MVVM delegates: RaceAssetLoader, RaceSetupViewModel, RaceSetupRenderer, RaceSetupController, LLMDialogService, RaceSetupInputHandler)
- 8 lazy-initialized panels (summary, identity, environment, aptitudes, description, flag, portrait, theme galleries)
- Test file ~1464 LOC with ~150 tests

### GO path (bypass_init alone is sufficient)

If PROJ-324 Phase 3 Task 3.4 reports GO, this phase is mechanical migration only:

- Replace existing `__new__` bypass-init helper with `bypass_init(RaceSetupScreen)` + `make_ui_widget`.
- Migrate fixtures.
- Verify ~150 tests still pass.
- Document the LOC delta.

This path is consistent with PROJ-324 Tasks 3.1-3.7.

### NO-GO path (active per consensus 2026-05-04)

PROJ-324 Phase 3 Task 3.4 reported NO-GO. PROJ-325 Phase 3 is the **canonical proof-of-concept** for the two-stage construction pattern that PROJ-328A/B/C will then apply to the other 6 UIWindow subclasses.

**Canonical refactor spec:** [`findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`](findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md) (Codex–Claude consensus, agreed 2026-05-04).

**Headline pattern:**

```python
def __init__(self, rect, manager, ..., *, ui_builder=None, delegate_factory=None):
    self._init_state(...)
    self._init_widget_refs()
    self._delegates = (delegate_factory or DefaultRaceSetupDelegateFactory()).build(self)

    if getattr(type(self), "bypass_init", False):
        self.ui_manager = manager
        self.rect = rect
        self._window_init_bypassed = True
        return

    super().__init__(rect, manager, ...)
    (ui_builder or RaceSetupUiBuilder()).build(self)
```

**Acceptance criteria:** see consensus plan section "PROJ-325 Phase 3 Acceptance Criteria" (8 items). Phase 3 checklist mirrors them.

**Stop condition:** if PoC grows beyond what's scoped here, stop and spin out the remainder. Do NOT balloon PROJ-325 with PROJ-328 work.

**Structural target:** `RaceSetupScreen.__init__` should structurally resemble [`game/ui/screens/battle_setup/screen.py`](../../../game/ui/screens/battle_setup/screen.py) `__init__` (the cleanest in-repo MVVM exemplar).

## Architecture

No new architectural patterns introduced. Phase 1 + Phase 2 are mechanical doc + parametrize work. Phase 3 either reuses PROJ-324's `bypass_init` pattern (GO) or introduces a new `PanelRegistry` protocol (NO-GO).

## Risks

1. **Phase 1 cascade.** Updating PROJ-323 `manifest.md` to remove ~42 deleted-file entries is a wide doc edit. If a future agent reads the manifest after this update, they need a way to know it was edited intentionally — leave a comment at the top of the manifest noting the FND-CC-004 cleanup date.

2. **Task 3.34 parametrize scope creep.** The 11-handler cluster lives in a 1899-LOC file. Touching that file for parametrize may surface other latent issues (e.g., other clusters that should also be parametrized). Stay scoped: only the 11 fleet_not_found tests get parametrized this phase. Other cluster discoveries are PROJ-327 territory.

3. **Phase 3 NO-GO underestimate.** The "1-2 sessions" NO-GO estimate is for a clean panel-registry extraction. If RaceSetupScreen's `__init__` has hidden coupling (state mutation across panel construction order, callback registration before/after panel creation), the refactor is larger. **If the NO-GO estimate balloons past 3 sessions, stop and notify the user — defer to a dedicated PROJ-32y rather than ballooning PROJ-325 Phase 3.**

4. **Parallel-work file conflict on `test_race_setup_screen.py` and `screen.py`.** PROJ-324 Phase 3 Task 3.4 will touch the test file (briefly, for the GO/NO-GO probe). PROJ-325 Phase 3 must not start until that probe completes and PROJ-324 has either rolled back its changes (NO-GO) or landed them (GO).

## Patterns Reused

- **`make_ui_widget` factory** + `bypass_init` context manager (PROJ-322 + PROJ-324) — used in Phase 3 GO path
- **Class-level `@pytest.mark.parametrize` across handler classes** (PROJ-323 Phase 3 Task 3.2 precedent) — used in Phase 2

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
