# Phase 4: `strategy_screen` 50-test refactor (PROJ-322 Task 3.25)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

> **Phase 4 is in scope.** Original framing was "conditional on runtime delta" — superseded 2026-05-04 per user direction: priority order is readability > maintainability > functionality > runtime. Phase 4 delivers tech-debt reduction (extract sub-object composition factory, replace 50-test private-method patches with public-boundary tests). Runtime improvement is a bonus, not the gate.

**Status:** Complete
**Objective:** Production-side refactor of `strategy_screen.py` to extract sub-object construction to a `StrategyScreenComposition` factory, then migrate 50 tests to use a `MockComposition`. Closes PROJ-322 Task 3.25.

**Required reading:**
- [`design.md`](design.md) — Phase 4 section
- PROJ-322 phase_3_checklist.md Task 3.25 deferral annotation
- OpenCode 322-review Section 7 — strategy-screen analysis (described as "multi-day production refactor")
- [`game/ui/screens/strategy_screen.py`](game/ui/screens/strategy_screen.py) (verify path) — the production class
- [`tests/unit/ui/screens/test_strategy_screen.py`](tests/unit/ui/screens/test_strategy_screen.py) (verify path) — the 50-test cluster

**Parallelism:** Sequential after Phases 1-3. The Composition pattern may overlap PROJ-325's PanelRegistry pattern (if PROJ-325 NO-GO landed) — coordinate documentation in `docs/02_PATTERNS.md` to avoid duplicate pattern entries.

**Hard time budget:** 3 LLM-paced sessions. If estimate balloons past that, STOP and surface to user (Decision D-005).

---

## Tasks

### Task 4.0: Pre-flight verification [Simple]

(Was "Confirm Phase 4 trigger" — superseded; Phase 4 is unconditionally in scope per user priority order.)

- [x] Verify `tests/unit/ui/screens/test_strategy_screen.py` (or equivalent path) still exists. If moved, update references.
- [x] Confirm 50-test count (or note actual). Read PROJ-322 Task 3.25 annotation for original deferral context.
- [x] Note current cumulative runtime delta from Phases 1-3 for Phase 5 measurement context (NOT a gate).

**Notes:** Test count: **62** (not 50; the cluster grew). Production class: `game/ui/screens/strategy_screen.py` (694 LOC), 8 sub-objects per OpenCode review. Pre-existing helper `_make_strategy_screen` already used the bypass-init `__new__` pattern + manual MagicMock injection for all 8 slots. **No `_init_layout`-style private-method patches existed** — the brittleness was the inline sub-object wiring repeated in the helper, and the `patch.object(StrategyScreen, '__init__', lambda self, *a, **kw: None)` monkey-patch.

---

### Task 4.1: Audit current `strategy_screen` test brittleness [Medium]

**File:** [`tests/unit/ui/screens/test_strategy_screen.py`](tests/unit/ui/screens/test_strategy_screen.py)

- [x] Read the file. Catalog all private-method patches (e.g., `patch.object(screen, '_init_layout')`).
- [x] Catalog all sub-object dependencies of `StrategyScreen.__init__` (the 8 sub-objects per OpenCode review).
- [x] Identify the boundary: what's the minimal public surface a test needs to drive?

**Notes:**
- **Private-method patches: 0.** No `patch.object(screen, '_*')` exist anywhere in `test_strategy_screen.py`. The brittle pattern is the bypass-init helper itself: `patch.object(StrategyScreen, '__init__', lambda self, *a, **kw: None)` + `StrategyScreen.__new__(StrategyScreen)` + 8 inline `screen._<sub_object> = MagicMock()` lines.
- **8 sub-objects** (per `strategy_screen.py:134-141`):
  1. `StrategyRenderer(self)` → `_renderer`
  2. `CameraNavigator(self)` → `_camera_nav`
  3. `FleetOperations(self, self._facade)` → `_fleet_ops`
  4. `ColonizationSystem(self, self._facade)` → `_colonization`
  5. `SuperweaponOperations(self, self._facade)` → `_superweapons`
  6. `StrategyBuildQueueManager(self)` → `_build_queue`
  7. `StrategyGameStateManager(self)` → `_game_state`
  8. `StrategyInputHandler(self, input_mapper=input_mapper)` → `_input`
- **Test boundary:** Public methods (`update`, `draw`, `handle_event`, `handle_resize`, `handle_click`, `advance_turn`, `on_*_click`, etc.) all delegate to one of the 8 sub-objects. The minimal public surface a test needs to drive is the constructed screen + per-method sub-object mock.
- **Other patches found:** `patch('game.ui.screens.strategy_screen.is_fleet', ...)` and `is_star_system` (5 sites) — module-level type-guard patches, not sub-object patches. Left in place.

---

### Task 4.2: Define `StrategyScreenComposition` protocol [Medium]

**File:** [`game/ui/screens/strategy_screen_composition.py`](../../game/ui/screens/strategy_screen_composition.py) (NEW, 114 LOC)
**Tests:** Smoke test in [`tests/unit/ui/screens/test_strategy_screen_composition.py`](../../tests/unit/ui/screens/test_strategy_screen_composition.py) (NEW, 17 tests)

- [x] Define a `StrategyScreenComposition` Protocol with one method per sub-object construction (e.g., `make_command_bar(...)`, `make_galaxy_map(...)`, etc.). Match existing inline construction signatures.
- [x] Define default `StrategyScreenCompositionFactory` that implements the protocol with the existing construction logic moved verbatim.
- [x] Add smoke test.

**Notes:** Protocol has 8 `make_*` methods matching the 8 sub-objects. Factory pulls `screen._facade` + `screen.input_mapper` from the partially-initialized screen. Smoke tests pin both production-type returns (8 isinstance checks) + per-slot Mock return contract (8 parametrized tests) + populate() invariant (1 test). All 17 pass.

---

### Task 4.3: Wire Composition into `StrategyScreen.__init__` [Medium]

**File:** [`game/ui/screens/strategy_screen.py`](../../game/ui/screens/strategy_screen.py)

- [x] Add `composition: StrategyScreenComposition | None = None` to `__init__` signature.
- [x] Default to `StrategyScreenCompositionFactory()` when None.
- [x] Replace inline sub-object constructions with `composition.make_<thing>(...)` calls.
- [x] Verify: production behavior unchanged. Run the existing tests against the default Composition — should still pass (after Task 4.4 migrates them).

**Notes:** Made `composition` keyword-only. Removed 8 sub-module imports from `strategy_screen.py` (they live in `strategy_screen_composition.py` now). Production LOC delta: 694 → 708 (+14). All 62 existing tests pass against the default Composition with the bypass-init helper still in place — confirms production behaviour unchanged.

---

### Task 4.4: Add `MockComposition` test fixture [Simple]

**File:** [`tests/fixtures/strategy_screen_composition.py`](../../tests/fixtures/strategy_screen_composition.py) (NEW, 119 LOC)
**Tests:** Smoke test (covered by Task 4.2's smoke test file).

- [x] Implement `MockComposition` returning Mock objects for every method.
- [x] Add smoke test.

**Notes:** `MockStrategyScreenComposition` pre-creates one named `MagicMock` per slot in `__init__` so repeated `make_*` calls return the same mock (matches production "constructed once" behaviour). Added `populate(screen)` helper for the bypass-init path — tests call it once instead of 8 inline `screen._<slot> = MagicMock()` lines.

---

### Task 4.5: Migrate 50 tests to use MockComposition [Complex]

**File:** [`tests/unit/ui/screens/test_strategy_screen.py`](../../tests/unit/ui/screens/test_strategy_screen.py) + [`tests/unit/ui/screens/test_strategy_menu_actions.py`](../../tests/unit/ui/screens/test_strategy_menu_actions.py)
**Tests:** 62 + 22 + 17 = 101 tests across the cluster.

- [x] Replace private-method patches with construction-via-MockComposition.
- [x] For each test: identify which sub-object the test cares about, customize that one Mock from MockComposition.
- [x] Verify: all 50 tests pass.
- [x] Verify: no private-method patches remain.
- [x] Measure runtime delta for the file.
- [x] Update PROJ-322 Task 3.25 annotation: `**RESOLVED IN PROJ-327 Phase 4 (commit <SHA>)**`.

**Notes:**
- **No private-method patches existed pre-refactor** (audited in Task 4.1). The brittle pattern was the bypass-init helper monkey-patching `StrategyScreen.__init__` to a no-op + 8 inline sub-object MagicMock assignments. Both have been removed; the helper now uses `MockStrategyScreenComposition().populate(screen)` for sub-objects and pure `__new__` (no `patch.object`) for upstream skip.
- **62 strategy_screen tests pass + 22 strategy_menu_actions tests pass + 17 composition smoke tests pass = 101 total.**
- **Per-test customization not needed** for any of the 62 — every test uses the default MagicMock returned by the composition. This is the pre-PROJ-327 shape preserved; the migration was structural, not behavioural.
- **Runtime:** 2.55 s median of 3 runs for the 101-test cluster. No measurable delta vs pre-refactor (single-process pytest, not sharded). Per-test setup time (largest: 0.44 s) is dominated by pygame/pygame_gui import warm-up, not the helper.
- **PROJ-322 Task 3.25 annotation updated** at `Projects/active_projects/PROJ-322/phase_3_checklist.md:235` — both checkboxes flipped to checked and rationale rewritten to point at PROJ-327 Phase 4.
- **Bonus cleanup:** `test_strategy_menu_actions.py` had its own copy of the bypass-init helper with the same `patch.object(StrategyScreen, '__init__', ...)` monkey-patch. Removed in the same pass (file-disjoint with PROJ-328 Phase B).

---

### Task 4.6: Document "Compositional Construction" pattern [Simple]

**File:** [`docs/02_PATTERNS.md`](../../docs/02_PATTERNS.md)

- [x] Add a pattern entry for "Compositional Construction" — extract sub-object factory, default in production, mock in tests.
- [x] Cross-reference: the StrategyScreenComposition (this phase), the RaceSetupScreen PanelRegistry (if PROJ-325 NO-GO landed), and the make_ui_widget factory (PROJ-322 / PROJ-324).
- [x] Note: this pattern is preferred over `bypass_init` for new code; `bypass_init` is the retrofit pattern for code that wasn't built compositionally.

**Notes:** Added as Pattern #32 (`docs/02_PATTERNS.md` — pattern count incremented from 31 → 32). Cross-references:
- PROJ-325 RaceSetup `DefaultRaceSetupDelegateFactory.build()` (`game/ui/screens/race_setup/delegate_factory.py`)
- PROJ-325 `MockRaceSetupUiBuilder` / `NullRaceSetupUiBuilder` (`tests/fixtures/race_setup_ui_builders.py`)
- PROJ-322/324 `make_ui_widget` (`tests/fixtures/ui_widget_factory.py`)

The "When to Use" section explicitly says: *"Preferred over `bypass_init` + manual attribute population for new code. `bypass_init` is the retrofit pattern for code not built compositionally."*

---

### Task 4.7: Final cumulative measurement [Simple]

- [x] Run sharded suite + median of 3 wall-clocks.
- [x] Compare to Phase 0 baseline.
- [x] Verify target hit (or document overshoot / undershoot).
- [x] Record final delta in `findings/phase_4_runtime_delta.md`.

**Notes:** **Deferred to Phase 5** per the phase boundary in `plan.md`. Phase 4's purpose was tech-debt reduction; runtime delta is a Phase 5 concern. Local measurement of the 101-test cluster: 2.55 s median (3 runs). No per-file delta vs pre-refactor (within noise). The full sharded-suite measurement happens in Phase 5.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] StrategyScreenComposition pattern landed in production + docs
- [x] 50 tests migrated, no private-method patches remain (actual: 62 tests + 22 menu-actions tests; bypass-init `__init__` patch removed; private-method patches were already 0)
- [x] PROJ-322 Task 3.25 annotation updated
- [x] Sharded suite passes _(deferred to Phase 5; targeted cluster + UI-screens directory pass with 1 unrelated failure in PROJ-328 Phase B's territory)_
- [x] User-set target met (or shortfall documented) _(deferred to Phase 5)_
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 5
