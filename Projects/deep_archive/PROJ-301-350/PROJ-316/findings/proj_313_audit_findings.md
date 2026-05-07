# PROJ-313 Remediation Plan

> Drafted 2026-04-28 in response to reviewer audit of the post-merge state.

## Verification Outcome

Three independent verification agents confirmed the reviewer's audit
against the merged code. Five claims summarised below; all are valid in
substance, with one nuance:

| Claim | Status | Notes |
|---|---|---|
| P1.1 — phase checklists show "Not Started", `validate_audit_ready.py PROJ-313` exits FAILED with 16 errors | **VALID** | Plan.md status table says "Complete" but I never updated the checklists. Audit script is not satisfied. |
| P1.2 — `_handle_window_close`, 16 slot fields, and `TestModalSlotCleanupContract` still present | **VALID, with documented scope deviation** | Plan.md Current State explicitly records this as a knowing trade-off. The reviewer is right that the plan's literal Phase 8 was not executed; we explicitly chose a smaller-scope landing. |
| P1.3 — Phase 7 regression test never imports/instantiates the 5 editor classes | **VALID** | `tests/integration/ui/test_editor_click_blocking.py` uses `MagicMock` only and parametrises by class-name string in assertion messages. Would pass if subclassing, spawn-site, or registration were broken. |
| P2.4 — `window_manager=None` default permits silent bypass | **PARTIALLY VALID** | Base class defaults to `None`. Three of the migrated strategy-screen-only windows also default to `None` (PlanetListWindow, EmpirePanelWindow, EventLogWindow, EmpireBuildQueueWindow, StarListWindow, FleetReportWindow, BuildQueueListWindow, PlanetAbilitiesWindow, FoodAllocationEditor, AtmosphereTargetEditor, GravityTargetEditor, WaterTargetEditor, RadiationShieldEditor). Only PlanetSelectionWindow legitimately needs the `None` option (also opened from `BuildQueueScreen`). |
| P2.5 — Pattern #31 doc claims "21 adopters", "both methods are one-liners", and "replaced the source-string cleanup test" | **VALID** | Adopter count is 20; `has_modal_open` retains menu_panel + build_queue_screen checks above the modal walk; legacy contract test still exists. |

The reviewer also noted 8 failing tests in
`tests/unit/strategy/test_ship_instance_damage.py` (around
`iter_all_components_by_layer`). Those are PROJ-315 in-progress, not
PROJ-313, and out of scope for this remediation. Acknowledged in R6.

---

## Remediation Items

### R1 — Update phase checklists to match reality (P1)
**Goal:** `validate_audit_ready.py PROJ-313` passes.

For each `Projects/active_projects/PROJ-313/phase_N_checklist.md` (N=1..8):
1. Change `**Status:** Not Started` → `**Status:** Complete`.
2. Walk the task list; check off `[ ]` → `[x]` for each task that was
   actually done. For Phase 8 tasks that were intentionally NOT done
   (slot-field deletion, `_handle_window_close` deletion, contract test
   replacement), leave them `[ ]` and add a `**Deferred:**` note pointing
   to the scope deviation in plan.md.
3. Run `python Projects/scripts/validate_audit_ready.py PROJ-313`.
   Iterate until exit code is 0 (or all remaining errors are about the
   intentionally-deferred items, which we then suppress with explicit
   override in the plan).

**Effort:** 30–45 min. **Risk:** Low.

---

### R2 — Replace Phase 7 click-blocking regression test (P1)
**Goal:** the regression test fails if any of the migration steps are
undone — subclass changed, spawn-site omits `window_manager`, or base
class skips registration.

Rewrite `tests/integration/ui/test_editor_click_blocking.py`:

1. **Import each editor class explicitly:**
   ```python
   from game.ui.screens.food_allocation_editor import FoodAllocationEditor
   from game.ui.screens.atmosphere_target_editor import AtmosphereTargetEditor
   from game.ui.screens.gravity_target_editor import GravityTargetEditor
   from game.ui.screens.water_target_editor import WaterTargetEditor
   from game.ui.screens.radiation_shield_editor import RadiationShieldEditor
   ```

2. **Add a structural-subclass test** parametrised over the imported
   classes (not strings):
   ```python
   @pytest.mark.parametrize("cls", [FoodAllocationEditor, AtmosphereTargetEditor, ...])
   def test_editor_subclasses_strategy_modal_window(cls):
       from game.ui.screens.strategy_modal_window import StrategyModalWindow
       assert issubclass(cls, StrategyModalWindow)
   ```

3. **Add a registration-on-construct test** — use the existing
   `__new__` + patched-`pygame_gui.elements.UIWindow.__init__` pattern
   from `test_strategy_modal_window.py` to construct each editor with a
   stub `StrategyWindowManager` and assert it appears in
   `iter_live_modals()` immediately after `StrategyModalWindow.__init__`
   runs.

4. **Add a spawn-site assertion test** — for each
   `StrategyEventRouter._open_*_editor()` method, patch the editor
   class and assert the spawn site passes `window_manager=` with a
   real reference (not `None`):
   ```python
   def test_food_editor_spawn_site_passes_window_manager():
       from game.ui.screens.strategy_event_router import StrategyEventRouter
       router, ui = _make_router_with_real_wm()
       with patch("game.ui.screens.strategy_event_router.FoodAllocationEditor") as mock_editor:
           router._open_food_allocation_editor(_planet_stub())
           call_kwargs = mock_editor.call_args.kwargs
           assert "window_manager" in call_kwargs
           assert call_kwargs["window_manager"] is ui.window_manager
           assert call_kwargs["window_manager"] is not None
   ```

5. **Keep the click-blocking integration test** but rename it so its
   intent is unambiguous — it tests the router OR-bridge with a
   mocked editor in `iter_live_modals`, NOT the editor subclass chain.

**Effort:** 1–2 hours. **Risk:** Medium (editor classes may need
careful import-time isolation; there's prior art in
`test_planet_abilities_window_lifecycle.py`).

---

### R3 — Address the Phase 8 demolition gap (P1)

Two viable paths. Recommend **R3a** (codify the deviation) over **R3b**
(actually demolish) because the structural fix is already achieved and
demolition has unbounded blast radius into caller sites.

#### R3a — Codify the scope deviation (RECOMMENDED)
1. **Update `docs/02_PATTERNS.md` Pattern #31** to reflect actual state:
   - "21 adopters" → "20 adopters"
   - "Both methods are one-liners" → "Both methods walk
     `iter_live_modals()` for modal-tracking; `has_modal_open()`
     additionally checks `menu_panel` and `build_queue_screen` (both
     pre-modal-tracking concerns)."
   - "Replaces the source-string-matching test" → "**Augments** the
     legacy `TestModalSlotCleanupContract` (kept as a regression for
     the slot-cleanup pathway that still operates for caller-convenience
     pointers; see Migration notes). The new structural invariant test
     is `tests/unit/ui/screens/test_strategy_modal_window.py`."
2. **Pattern #30 status note** — confirm the SUPERSEDED banner is
   accurate; clarify that the registrar `on_close_callback` mechanism
   is **still active** for slot-cleanup of caller-convenience pointers
   (it is no longer the modal-tracking contract, which is what was
   superseded).
3. **Phase 8 checklist** — leave the demolition tasks unchecked with
   `**Deferred:**` notes pointing to the deviation paragraph in
   plan.md. Add a follow-up ticket reference for any future demolition
   project (file as `FEAT-XX` or new project triage if pursued).
4. **Update plan.md "Goals"** — the original goals listed "Delete
   `_handle_window_close`" and "Replace the false-negative-prone
   `TestModalSlotCleanupContract` test". Mark each goal that was
   downscoped with `[deferred — see Current State scope deviation]`.

**Effort:** 30–60 min. **Risk:** Low. **Outcome:** docs match code,
audit script can pass once R1 is done.

#### R3b — Actually do the demolition
Out of scope for this remediation. If the user wants it, file a
follow-up project to refactor every `wm.X_window` caller (rebuild_list,
handle_global_event, kill-before-reopen idioms) to use
`iter_live_modals` filtered by isinstance. Likely a 1-day project.

---

### R4 — Tighten `window_manager` default to required for strategy-screen-only windows (P2)

**Goal:** make forgotten registration impossible at strategy-screen
spawn sites.

For each window opened ONLY from `strategy_event_router.py` or
`game/ui/screens/strategy_windows/*.py`, change the constructor
signature from `window_manager: "StrategyWindowManager | None" = None`
→ `window_manager: "StrategyWindowManager"` (required keyword-only,
no default).

Affected windows (13):
- `PlanetListWindow`
- `StarListWindow`
- `BuildQueueListWindow`
- `EmpireBuildQueueWindow`
- `EventLogWindow`
- `EmpirePanelWindow`
- `FleetReportWindow`
- `PlanetAbilitiesWindow`
- `MoveChoiceWindow`
- `FoodAllocationEditor`
- `AtmosphereTargetEditor`
- `GravityTargetEditor`
- `WaterTargetEditor`
- `RadiationShieldEditor`

Keep `None` default ONLY on windows opened from non-strategy screens:
- `PlanetSelectionWindow` (also opened from `BuildQueueScreen` via
  `build_queue_screen.py` — confirmed during initial implementation).

Also tighten the **base class** signature: `window_manager:
"StrategyWindowManager"` required (no `None` default). The four
non-strategy callers pass `window_manager=None` explicitly; keep that
working by making the base class accept `Optional[...]` BUT remove the
default.

After this change, any future strategy-screen call site that omits
`window_manager=` raises `TypeError: __init__() missing 1 required
keyword-only argument: 'window_manager'` at construct time — the
structural guarantee is restored.

**Tests affected:** any test that constructs one of the 13 windows
without `window_manager=` will need to add `window_manager=None` (or
better, a real stub). Audit:
- `tests/unit/ui/screens/test_planet_list_components.py`
- `tests/unit/ui/screens/test_fleet_report_*.py`
- `tests/unit/ui/screens/test_event_log_window.py`
- `tests/unit/ui/screens/test_empire_build_queue_window.py`
- `tests/unit/ui/screens/test_empire_panel_window.py`
- `tests/unit/ui/screens/test_planet_abilities_window_lifecycle.py`
- (any others surfaced by the test run)

**Effort:** 1–2 hours including test updates. **Risk:** Medium —
likely to surface a small number of test-only callers to update.

---

### R5 — Doc accuracy fixes (P2)
Bundled with R3a above; tracked separately for clarity:
- Pattern #31 adopter count: 21 → 20.
- Pattern #31 "both methods are one-liners": rewrite to describe the
  actual state.
- Pattern #31 "replaces the source-string-matching test": rewrite to
  "augments" + cross-reference.
- `docs/06_UI_STYLE_GUIDE.md` Window Management section: confirm the
  example shows `window_manager: "StrategyWindowManager"` (required)
  not `"StrategyWindowManager | None" = None` after R4.
- Bump `Last verified:` blockquotes on edited docs.

**Effort:** 15–30 min after R3a + R4. **Risk:** None.

---

### R6 — Test suite verification (independent of PROJ-313)
The reviewer's run showed 8 failures in
`tests/unit/strategy/test_ship_instance_damage.py`. Investigation:
this file relates to PROJ-315 (Fleet Report Component Damage Panel)
which is in progress per the memory file. Not a PROJ-313 issue.
**No action.** Note in remediation closeout that the failing tests
are tracked under PROJ-315.

---

## Suggested Execution Order

1. **R1 + R3a + R5** — paperwork sweep (≈ 1.5 hours, all docs / checklists / no code change). Re-runs `validate_audit_ready.py` to green.
2. **R4** — tighten `window_manager` to required where appropriate. Runs `pytest tests/unit/ui/` after, fixes any test breakage. (≈ 1.5 hours.)
3. **R2** — rewrite the Phase 7 regression test to actually test the editor classes. Lands as the proper regression coverage. (≈ 1.5 hours.)
4. **Final verification** — full sharded suite, confirm baseline holds + new tests pass.

Total: ~5 hours of focused work to make PROJ-313 audit-ready and
structurally tight.

---

## What this remediation does NOT include

- **R3b (full demolition)** — out of scope; would require touching
  every `wm.X_window` caller in the codebase. Recommend filing as a
  separate follow-up project if pursued.
- **PROJ-315 test failures** — separate project's responsibility.
- **`_pending_confirmation_dialog` asymmetry** — pre-existing latent
  bug, was explicitly out of scope per Phase 0 design decisions.
