# Decomposition Design: app.py

**Current size:** 855 lines (verified via `wc -l` on 2026-04-27; design.md sketch listed 849, file has grown slightly since)
**Target post-split:** every resulting module <500 lines

---

## Current responsibilities

A close read identifies **seven** distinct concerns interleaved in this single file. Lines refer to `game/app.py` as of 2026-04-27.

1. **Module-level imports + constants** (lines 1-62) — pygame, pygame_gui, all UI screen classes (10+ heavy imports), `Paths`, `DisplayConfig`, `GameState`, `BG_COLOR`, `FPS`, `DEFAULT_WIDTH/HEIGHT`. Eager top-of-file imports drag in the entire UI layer at module-load time.
2. **Logging configuration** (lines 18-29) — `configure_logging()`. Standalone module-level helper, only called from `main()`.
3. **CLI argument parsing** (lines 65-71) — `parse_args()`. Standalone helper.
4. **Screen-transition policy** (lines 74-99) — `_SCREEN_TRANSITIONS` frozen-set declaring all valid `GameState` edges. Pure data, consumed by `ScreenStateMachine` in `__init__`.
5. **Bootstrap / services wiring** (lines 105-208, in `Game.__init__`) — pygame init, font init, monitor detection, resolution selection, surface acquisition, `ApplicationContext.create_production()`, registry/component/modifier/ship-data loading via `Paths`, `ResourceCatalog` hydration, `GameRegistries` container, `InputMapper` load, `SpriteManager.load_sprites`, scene instantiation (Menu / Workshop / BattleSetup / Battle / Strategy / TestLab). ~100 lines doing ~10 different things.
6. **Screen lifecycle / scene routing** (lines 210-543, 769-829) — every `start_*` method (`start_builder`, `start_battle_setup`, `start_strategy_layer`, `start_quickstart_1p/2p`, `show_load_menu`, `start_test_lab`, `start_research_tree`, `start_galaxy_test`, `start_keybindings`, `start_race_setup`), every `on_*_return` callback, every `_on_*_start/cancel/complete/load` overlay-dialog handler, `_handle_strategy_action`, `_handle_test_lab_action`, `_handle_battle_setup_action`, `_handle_battle_action`, `_return_to`, `_create_workshop_context`, `_switch_scene`. This is the **biggest** chunk — easily 300+ lines.
7. **Battle launch** (lines 545-587) — `start_battle(spec, *, headless)`: builds `BattleConfig`, instantiates `BattleController`, calls `start_from_spec`, transitions to `BATTLE`. Distinct from generic scene routing because of its simulation-layer wiring (PROJ-270/PROJ-274/PROJ-306).
8. **Main run loop** (lines 589-612) — `run()`: per-frame `clock.tick`, `pygame.event.get()`, dispatch to `_handle_exit_dialog_events` or `_handle_normal_events`, `_update_and_draw`, `pygame.display.flip()`, plus shutdown (LLM `shutdown_all_calls`, `pygame.quit`).
9. **Event handling + per-frame update/draw** (lines 614-805) — `_handle_exit_dialog_events`, `_handle_normal_events`, `_forward_event_to_scene`, `_handle_resize`, `_update_and_draw`. Tightly coupled to the run loop but logically separable.
10. **Entry point** (lines 832-855) — `main()`: calls `configure_logging`, `parse_args`, constructs `Game`, calls `freeze_registry`, runs `game.run()` inside the top-level crash handler, saves profiler history, plus `if __name__ == "__main__"`.

The design.md sketch was right that bootstrap / run-loop / screen-management are the three big chunks, but #7 (battle launch) deserves its own home (tight simulation-layer coupling), and #2-3 (logging + CLI) can live in a tiny `entrypoint` module alongside `main()`.

---

## Proposed sub-modules

Five modules total: a slim entry-point `app.py`, plus four siblings.

### 1. `game/app.py` — Slim orchestrator (kept; thin) — **~120 LOC**
- **Responsibility:** Define the `Game` class **shell**: `__init__` calls into `app_bootstrap`, holds the resulting attributes, exposes the `state` property + `_switch_scene`. Defers everything else to siblings.
- **Symbols:** `Game` class, `_SCREEN_TRANSITIONS` frozenset (kept here because it's tightly coupled to `Game`'s state-machine instance).
- **Depends on:** `app_bootstrap`, `app_run_loop`, `screen_router`, `app_entrypoint`.

The `Game` class becomes the composition root. Its methods become **thin delegates** that call into the helper modules; no more 100-line `__init__` and no more 300 lines of `start_*` methods directly on the class. Exact split below.

### 2. `game/app_bootstrap.py` — Bootstrap + services wiring — **~180 LOC**
- **Responsibility:** Everything currently between lines 18-208 except scene instantiation: logging config, CLI args, pygame init, font init, resolution detection, `ApplicationContext` creation, registry/component/modifier/ship-data loading, `ResourceCatalog` hydration, `GameRegistries` build, `InputMapper` load, `SpriteManager.load_sprites`.
- **Symbols:**
  - `configure_logging() -> None`
  - `parse_args() -> argparse.Namespace`
  - `BootstrapResult` (frozen dataclass): `ctx`, `screen`, `width`, `height`, `clock`, `registries`, `input_mapper`, `font_small`, `font_med`, `font_large`.
  - `bootstrap(args: argparse.Namespace) -> BootstrapResult` — runs the entire init sequence in deterministic order, returns the wired-up result.
  - `_detect_resolution(args, monitor_w, monitor_h) -> tuple[int, int]` (private, testable in isolation)
- **Estimated LOC:** 180.
- **Depends on:** stdlib (argparse, logging, os), pygame, `game.context`, `game.core.config`, `game.core.paths`, `game.core.registry`, `game.core.resources`, `game.simulation.components.component`, `game.simulation.entities.ship_loader`, `game.ui.fonts`, `game.ui.renderer.sprites`, `game.ui.services.input_mapper`.
- **Why a dataclass:** the current `__init__` writes ~15 attributes on `self`. Returning a dataclass keeps the bootstrap function pure-ish and gives us a single place to assert "everything required is wired" — the dataclass field list IS the post-bootstrap contract.

### 3. `game/screen_router.py` — Scene lifecycle, transitions, overlay dialogs — **~340 LOC**
- **Responsibility:** All `start_*`, `on_*_return`, `_on_*_start/cancel/complete/load`, `_handle_*_action`, `_return_to`, `_create_workshop_context`, `_handle_resize` (resize forwards to scenes — that's a routing concern). Owns the scene **instances** (workshop, battle_setup, battle, strategy, test_lab, menu, plus dynamically-created research_tree, galaxy_test, keybindings, race_setup, new_game_setup, save_selection).
- **Class:** `ScreenRouter` — receives the `BootstrapResult`, `state_machine`, and a `Callable[[], None]` "request shutdown" hook (so `_handle_strategy_action("quit_game")` can flag the run loop to stop without `Game` plumbing). The `ScreenRouter` exposes a single property `active_scene` that the run loop reads each frame.
- **Symbols:** `ScreenRouter` class with all the `start_*` / `on_*_return` / `_handle_*_action` methods; the `_create_workshop_context` private helper.
- **Estimated LOC:** 340 (largest module — still under 500).
- **Depends on:** All UI screen classes (heavy import list, but localized here instead of polluting `app.py`); `game.core.state_machine.ScreenStateMachine`; `game.core.constants.GameState`; `game.simulation.battle_controller`, `game.simulation.battle_config` (for `start_battle`); `game.ai.ai_factory.AIControllerFactory`; `game.ui.utils.create_centered_rect`.

If 340 still feels too large, a follow-up could pull `_handle_*_action` methods (~80 LOC) into a `game/screen_router_actions.py`. Defer that decision to execution time — let's see the actual numbers post-split.

### 4. `game/run_loop.py` — Main loop + event/draw dispatch — **~140 LOC**
- **Responsibility:** Currently lines 589-805: `run()`, `_handle_exit_dialog_events`, `_handle_normal_events`, `_forward_event_to_scene`, `_update_and_draw`. Tightly coupled to the `ScreenRouter` (reads `active_scene`) and the `BootstrapResult` (uses `screen`, `clock`, `font_med`, `font_large`, `ctx.profiler`, `input_mapper`).
- **Class:** `RunLoop(boot_result, router, state_machine)` with public `run() -> None` and `request_shutdown() -> None`. Also holds the overlay-dialog flags (`show_exit_dialog`, `showing_load_menu`, `showing_race_setup`, `showing_new_game_setup`) that are read by `_forward_event_to_scene` — these are **run-loop state**, not router state, because they gate event dispatch.
- **Symbols:** `RunLoop` class, `BG_COLOR` constant, `FPS` constant.
- **Estimated LOC:** 140.
- **Depends on:** pygame, `game.exit_dialog`, `game.core.input_actions.InputAction`, `game.services.llm.background.shutdown_all_calls`, `game.ui.screens.battle_results_screen` (lazy import — currently lazy in `_handle_battle_action`), and the router/boot/state_machine handles passed in.

The overlay-flag ownership question (run loop vs router) is a real design call — see Open Questions §1.

### 5. `game/__main__.py` (new) or kept inside `app.py` — Entry point — **~30 LOC**
- **Responsibility:** `main()` function: `configure_logging`, `parse_args`, `bootstrap`, instantiate `Game`/`ScreenRouter`/`RunLoop`, `freeze_registry`, run inside the crash-handler, save profiler history.
- **Two options:**
  - **5a.** Keep `main()` inside `app.py`. Then `app.py` ends at ~150 LOC (Game shell + main + `_SCREEN_TRANSITIONS`). `launcher.py` continues to `from game.app import main`. Simplest.
  - **5b.** Move `main()` to a new `game/__main__.py` so `python -m game` Just Works. Then `launcher.py` becomes `from game.__main__ import main`. Slightly cleaner but adds a file move.
- **Recommendation:** 5a. The `main()` function is small and conceptually belongs to the same "entry" concept as the `Game` class. Don't split for the sake of splitting.

### LOC budget summary
| Module | LOC | Notes |
|---|---|---|
| `game/app.py` | ~150 | `Game` shell + `_SCREEN_TRANSITIONS` + `main()` |
| `game/app_bootstrap.py` | ~180 | Pure init sequence + `BootstrapResult` |
| `game/screen_router.py` | ~340 | All scene start/return/action methods |
| `game/run_loop.py` | ~140 | Main loop + event/draw dispatch |
| **Total** | ~810 | (current 855; minor reduction from removed boilerplate / docstrings) |

All four modules are <500 LOC, satisfying the project goal.

---

## Public API surface

`from game.app import …` is used in only **5 places** in the source tree:

| Caller | Imports | Usage |
|---|---|---|
| `launcher.py:8` | `from game.app import main` | Production entry point |
| `tests/integration/test_app_integration.py` (3 sites) | `from game.app import Game` | Mocks `pygame.display.Info`, instantiates `Game`, asserts attributes |
| `tests/unit/systems/test_main_integration.py` (2 sites) | `from game import app` | Smoke import + `app.Game()` instantiation |
| `tests/unit/ui/screens/test_strategy_menu_actions.py:266` | `from game.app import Game` | Asserts handler-method existence |
| `tests/regression/test_deprecated_code_removed.py` (4 sites) | `from game import app` | Regression checks |

**Symbols required externally:**
- `main` (callable)
- `Game` (class — tests probe `.battle_scene`, `.battle_scene.engine`, `._start_quickstart`, `.start_quickstart_1p`, `.start_quickstart_2p`, the constructor signature)

Both stay top-level in `game/app.py` post-split, so **all current call sites continue to work unchanged**.

---

## Caller-update strategy

**Choice: Option B (caller migration, but trivially so).**

**Justification:** Only 5 call sites import from `game.app`, and **none of them need to change** because the two externally-required symbols (`Game` and `main`) remain in `game/app.py`. The "caller migration" is a no-op — yet this is genuinely Option B (clean public API, no shim) rather than Option A (re-export shim) because:

- `Game` keeps its public method surface (`start_quickstart_1p`, `start_battle`, etc.) by **delegating** to `ScreenRouter` internally. The class is still defined in `app.py`. We're not re-exporting it from elsewhere.
- Bootstrap, run-loop, and router classes are net-new modules with their own clean APIs. They are not part of the current public API at all, so there's nothing to "preserve".
- No transitional shim, no graveyard module, no deprecation cycle — the System Migration Policy is satisfied immediately.

The internal restructure is large; the external diff is zero. This is exactly the pattern that justifies Option B even when the file is heavily used.

### Method-delegation contract on `Game`

To preserve test-asserted methods:

```python
class Game:
    def __init__(self, args=None):
        self._boot = bootstrap(args)
        self.state_machine = ScreenStateMachine(GameState.MENU, _SCREEN_TRANSITIONS)
        self._router = ScreenRouter(self._boot, self.state_machine, self._request_shutdown)
        self._loop = RunLoop(self._boot, self._router, self.state_machine)

    # Test-asserted public methods — delegate to router
    def start_quickstart_1p(self): self._router.start_quickstart_1p()
    def start_quickstart_2p(self): self._router.start_quickstart_2p()
    def _start_quickstart(self, player_count: int): self._router._start_quickstart(player_count)
    def start_battle(self, spec, *, headless=False): self._router.start_battle(spec, headless=headless)

    # Test-asserted attributes — properties forwarding to router
    @property
    def battle_scene(self): return self._router.battle_scene

    def run(self): self._loop.run()
```

This keeps every existing test green without rewriting. Once tests are updated to read from `_router` / `_boot` directly (or, better, to test `ScreenRouter` directly), the delegation methods can be deleted.

---

## Test plan

### Existing app-level tests
- `tests/integration/test_app_integration.py` — instantiates `Game`, exercises `_start_quickstart` signature, mocks `pygame.display.Info`. **Must still pass with zero edits** (delegation contract).
- `tests/unit/systems/test_main_integration.py::test_import_main` — bare import smoke. **Trivially passes** (module still exists, still imports cleanly).
- `tests/unit/systems/test_main_integration.py::test_game_instantiation` — `app.Game()` + asserts `battle_scene` and `battle_scene.engine`. **Passes via delegation property.**
- `tests/unit/ui/screens/test_strategy_menu_actions.py::test_…` — asserts handler method existence on `Game`. **Passes via delegation methods.**
- `tests/regression/test_deprecated_code_removed.py` — confirms certain old names are gone. **Unrelated to this split.**

### New targeted tests
- `tests/unit/test_app_bootstrap.py`
  - `test_detect_resolution_force_flag` — `--force-resolution` returns `(2560, 1600)`.
  - `test_detect_resolution_4k_monitor` — large monitor returns `(3840, 2160)`.
  - `test_detect_resolution_2k_monitor` — mid monitor returns `(2560, 1600)`.
  - `test_detect_resolution_small_monitor` — small monitor returns `(0.9 * w, 0.9 * h)`.
  - `test_bootstrap_returns_complete_result` — assert every field of `BootstrapResult` is non-None after `bootstrap()`.
  - `test_bootstrap_initializes_pygame_first` — patch `pygame.init` and assert it is called before `pygame.font.init` and before `ApplicationContext.create_production` (init-order regression test — see Risks §1).
- `tests/unit/test_screen_router.py`
  - `test_router_start_quickstart_1p_transitions_to_strategy` — already covered by integration tests; mirror at unit level for speed.
  - `test_router_handle_battle_action_show_results` — covers `_handle_battle_action("show_results")`.
  - `test_router_handle_strategy_action_quit_game_calls_shutdown_hook` — verify the new shutdown-hook injection works.
- `tests/unit/test_run_loop.py`
  - `test_run_loop_exits_on_shutdown_request` — feed a `pygame.QUIT` event, assert `running=False` and `pygame.quit` called once.
  - `test_run_loop_calls_llm_shutdown_on_exit` — assert `shutdown_all_calls(timeout=5.0)` invoked.
  - `test_handle_resize_forwards_to_active_scene` — verify resize plumbing.

### Manual smoke (mandatory — `app.py` is the highest-risk split)
1. `python launcher.py` → main menu renders, all 10 buttons present and styled.
2. Click "Quickstart 1P" → strategy screen appears, galaxy renders, fleets visible.
3. From strategy: click "Battle Setup" path → battle setup screen → start battle → battle screen renders, ships visible, simulation ticks.
4. End battle → returns to battle setup.
5. Return to menu.
6. Click "Design Workshop" → workshop loads with components and ship preview.
7. Return to menu.
8. Click "Combat Lab" → test lab UI loads, run a single test → result displayed.
9. Click "Race Setup" → wizard appears, all panels render.
10. Click "Load Game" with an existing save → save selection, load, strategy resumes at the saved turn.
11. From strategy, open keybindings → editor appears, change a binding, save → return to strategy without crash.
12. Press the profiler-toggle key → log shows "Profiling ENABLED" / "DISABLED".
13. Press window close (X) → exit dialog appears → confirm exits cleanly with no traceback.
14. Trigger an exception in a scene (manually inject via `raise` in a callback) → confirm `crash.log` is written and the process re-raises (top-level handler still works).
15. Run sharded test suite: `python Tools/test_sharded/test_sharded.py` — must remain at **15405 passed, 2 skipped** baseline.

### Edge cases worth probing manually
- Resize the window mid-battle. (Currently `_handle_resize` updates surface + dispatches — must still work after extraction.)
- Open keybindings from strategy, save, return → strategy tooltips re-applied (the `_apply_tooltips` callback in `on_keybindings_return`).
- Open Design Workshop from strategy → return → strategy resumes (state stack `push_and_transition` / `pop_and_return`).

---

## Risks

### 1. Bootstrap order changes (HIGH)
The current `__init__` runs steps in a precise order that is not commented but matters:

- `pygame.init()` MUST run before any `pygame.display.Info()` / `pygame.display.set_mode()` / pygame_gui surface creation.
- `pygame.font.init()` MUST run before `get_font(…)` is called (the menu scene calls fonts in its constructor).
- `ApplicationContext.create_production()` populates module-level `_default_*` accessors. `get_default_registry_provider()` is called immediately after for `load_components` — if the order flips, the provider returns the wrong (or empty) registry.
- `load_components` / `load_modifiers` MUST run before `initialize_ship_data` (ship-data loader resolves component refs).
- `ResourceCatalog.from_json()` is called **twice** currently — once at line 160 to populate `ctx.registry_manager.resources`, then again at line 182 inside `GameRegistries(...)` to provide `resource_catalog`. The second call is wasteful but might be load-bearing if one mutates state. The bootstrap extraction is the right time to fix this — call once, pass twice.
- `SpriteManager.load_sprites` is called **after** registries are loaded but **before** scene constructors that may resolve sprite references in their constructors.
- `MenuScene` constructor uses `get_font(…)` and the `menu_ui_manager` it builds is shared with overlay dialogs (load menu, race setup, new-game setup). It must be constructed before any code path that opens those overlays.

**Mitigation:** the `bootstrap()` function preserves the **exact** current order, with comments calling out each ordering invariant. New unit test `test_bootstrap_initializes_pygame_first` locks one invariant in place. A code review checklist for the extraction PR explicitly confirms each step's relative position.

### 2. Module-level side effects on import
`game/app.py` currently has `logger = logging.getLogger(__name__)` at module level (harmless) and a long list of UI-screen imports at module top. Those imports trigger pygame/pygame_gui module init. Splitting must NOT change which modules are imported on `from game.app import Game`. The current top-of-file import block is what tests rely on.

**Mitigation:** `app.py` keeps its current top-level imports of `Game`-class-required types. `screen_router.py` owns the heavier imports (workshop, test_lab, etc.) — these get loaded the first time `Game()` is constructed, same as today (since `Game.__init__` constructs them). No on-import-of-`game.app` regression.

### 3. Pygame initialization order
A bug here means a black screen, a `pygame.error`, or font corruption on startup. Pygame's `display.set_mode` cannot be called before `pygame.init()`; pygame_gui's `UIManager` cannot be constructed before `display.set_mode`. Currently this is enforced by sequence-in-a-method; post-split it must be enforced by `bootstrap()`'s contract.

**Mitigation:** `bootstrap()` is a single linear function with explicit ordering. No conditional branches that could reorder steps. Failing fast on missing prerequisites (e.g., `assert pygame.display.get_init()` before `set_mode`).

### 4. Overlay-dialog flag ownership (MEDIUM)
The `showing_load_menu` / `showing_race_setup` / `showing_new_game_setup` flags are written by router methods (`show_load_menu`, `start_race_setup`, `start_strategy_layer`) and **read** by run-loop methods (`_forward_event_to_scene`). Split blindly and you get cross-module mutation, which is a code smell.

**Mitigation:** the flags live on `RunLoop` (since they gate event dispatch — run-loop concern). `ScreenRouter` flips them via `loop.set_overlay(name, active)` or similar minimal protocol. Alternatively, encapsulate as `OverlayState` shared object passed to both. Decide at execution time based on which feels least awkward — both work.

### 5. Test attribute coupling
The integration tests assert `game.battle_scene is not None` and `game.battle_scene.engine is not None`. These are currently direct attributes on `Game`. After split, `battle_scene` lives on `ScreenRouter`. We expose it via `@property` on `Game` (delegation contract above). This works but couples test API to internal layout — an opportunity to update tests to use `game._router.battle_scene` or, better, drop the test in favour of dedicated `ScreenRouter` tests. Not in scope for this split; flag as follow-up.

### 6. Profiler shutdown order
`main()` calls `game.ctx.profiler.save_history()` AFTER `game.run()` returns. Currently this works because `run()` returns when the loop exits (after `pygame.quit()`). Post-split, `RunLoop.run()` must still return — not call `sys.exit()` — so `save_history()` continues to fire. Easy to break by accident.

**Mitigation:** test `test_run_loop_returns_after_shutdown_request` explicitly asserts return; `main()` still calls `save_history()` after.

### 7. Crash-handler scope
The top-level `try/except` in `main()` catches everything from `Game(args)` and `game.run()`. If we move `main()` (option 5b), preserve the same scope. If we keep it (option 5a, recommended), no risk.

---

## Open questions

1. **Where do overlay-dialog flags belong** — `RunLoop` or `ScreenRouter`? See Risks §4. Defer to execution time; both are workable. Lean toward `RunLoop` because event dispatch is a run-loop concern, but a shared `OverlayState` dataclass might be cleanest.
2. **Should `_SCREEN_TRANSITIONS` move?** Currently a module-level frozenset in `app.py`. Could move to `game/core/state_machine.py` (next to `ScreenStateMachine`) or `game/core/constants.py` (next to `GameState`). Decision: **leave in `app.py`** — it's app-policy, not core data, and `ScreenStateMachine` is intentionally generic. But this is a coin-flip.
3. **Should `Game` even survive?** Strictly, post-split, `Game` is a thin facade over `(boot, router, loop)`. We could delete the class entirely and have `main()` instantiate the three directly. The only reason to keep `Game` is the test-attribute coupling (Risks §5). Recommendation: **keep `Game` for now**, mark it for deletion in a follow-up once tests are updated.
4. **Single bootstrap-like function or scattered init?** Currently scattered — `__init__` does everything inline. Post-split: ONE bootstrap function, returning a dataclass. This is the right answer; no debate.
5. **Move `main()` to `game/__main__.py`?** Option 5a (keep) vs 5b (move). Recommendation: 5a — smaller diff, `launcher.py` continues to work. Revisit if the codebase grows a `python -m game` workflow.
6. **`ResourceCatalog.from_json()` called twice** — should the bootstrap fix this duplication? Yes, opportunistically. Call it once, reuse for both registry hydration and `GameRegistries`.

---

## Execution sequencing notes

When this design is implemented:

1. Land `app_bootstrap.py` first (lowest risk — pure extraction, no behavior change).
2. Add `BootstrapResult` and migrate `Game.__init__` to call `bootstrap()`. Run full suite + manual smoke #1 (launch).
3. Land `screen_router.py` next. Migrate `start_*` / `on_*_return` / `_handle_*_action` methods one cluster at a time, with delegation methods on `Game` keeping tests green. Full suite after each cluster.
4. Land `run_loop.py` last (highest coupling to `Game`'s internal state).
5. Manual smoke (full 15-step list) after each landing — `app.py` is the bootstrap, a broken split = unlaunchable game.
6. Final commit: trim `app.py` to its slim shell. Re-read `docs/01_ARCHITECTURE.md §Entry Point` and update if the description no longer matches.
