# Decomposition Design: strategy_window_manager.py

**Current size:** 817 lines
**Target post-split:** every resulting module <500 lines

> **Last verified:** 2026-04-27 — Design produced from full read of
> `game/ui/screens/strategy_window_manager.py` (817 LOC) and grep over all
> production callers + `tests/unit/ui/screens/test_strategy_window_manager.py`.

## Current responsibilities

The file is a single class `StrategyWindowManager` whose constructor wires a
scene reference, the pygame_gui manager, screen dimensions, an InputMapper, an
asset resolver, then declares 14 window slots and a callback map. The body is
structured as 14 self-similar `# ===... # <Window Name>` banner sections, each
containing one `open_*` method and (usually) one `_on_*_closed` callback.

Concrete responsibilities, with line ranges:

- **L1-113 — Construction and resize plumbing.** `__init__` declares all
  window-slot attributes (None-initialized) plus `ui_callbacks: dict` and the
  PROJ-198 confirmation-dialog cache. `handle_resize` only writes
  `self.width`/`self.height`.
- **L115-157 — Planet List Window.** `open_planet_list`, `_on_planet_list_closed`,
  `_on_planet_navigate`. Threads `race_registry` (PROJ-290) and `facade`
  (PROJ-292 H1) through to `PlanetListWindow`.
- **L159-189 — Star List Window (PROJ-231).** `open_star_list`,
  `_on_star_list_closed`, `_on_star_navigate`.
- **L191-204 — Shared camera nav helper.** `_navigate_camera_to` —
  used by both list-window navigate callbacks.
- **L206-230 — Build Queue List Window (BUG-67).** `open_build_queue_list`,
  `_on_build_queue_list_closed`.
- **L232-267 — Empire Build Queue Window (PROJ-76).**
  `open_empire_build_queue_window`, `close_empire_build_queue_window`,
  `_on_empire_build_queue_closed`. Threads `session` + `facade`.
- **L269-336 — Event Log Window (PROJ-77).** Two openers
  (`open_event_log` pulls all events; `open_event_log_with_events` accepts a
  list — used at turn start), `_on_event_log_navigate` (with HexCoord import),
  `_on_event_log_closed`.
- **L338-370 — Empire Panel Window.** `open_empire_panel`,
  `_on_empire_panel_closed`. Threads `race_registry` (PROJ-290).
- **L372-394 — Settings Window.** `open_settings`, `_on_settings_closed`. Local
  import of SettingsWindow.
- **L396-457 — Fleet Orders Window (PROJ-238).** `open_orders_window` is the
  largest method — branches on `entity_type ∈ {fleet, planet}` and constructs
  three command-dispatch closures (`clear/delete/reorder`) per branch plus an
  `edit_order_callback` closure. Local import of `OrdersWindow`. **No `_on_*_closed`
  callback** — fleet orders are reset elsewhere.
- **L459-498 — Fleet Report Window.** `open_fleet_report_window` builds a
  `split_fleet_callback` closure dispatching `SplitFleetCommand`. Plus
  `_on_fleet_report_closed`.
- **L500-530 — Transfer Dialog (PROJ-68).** `open_transfer_dialog`. Local
  import.
- **L532-560 — Cargo Quick Dialog (PROJ-100).** `open_cargo_quick_dialog`.
  Local import.
- **L562-628 — Planet Selection Prompt + Planet Abilities Window.**
  `prompt_planet_selection`, `open_planet_abilities_window` (which does a
  registry-provider lookup with a justified broad catch), and
  `_open_planet_editor` — a dispatch table that **delegates to the
  `StrategyEventRouter`** (atmosphere/gravity/water/radiation/food editors live
  there). Note: `self.planet_abilities_window` is set without a corresponding
  None-init in `__init__` (latent bug — flagged as Open Question).
- **L630-647 — System Selection Prompt (PROJ-138).** `open_system_selection`.
- **L649-665 — Fleet Selection Prompt (FEAT-08).** `prompt_fleet_selection`.
- **L667-720 — Move Choice Prompt.** `prompt_move_choice` builds an *inline*
  pygame_gui UIWindow with two buttons and registers their callbacks into
  `self.ui_callbacks`. The only window built without a dedicated
  `*_window.py` class.
- **L722-736 — UI callback dispatcher.** `process_ui_callbacks` — pops the
  callback for `event.ui_element` from `self.ui_callbacks` if it matches a
  `UI_BUTTON_PRESSED`. Used by `StrategyEventRouter.route_event` (L113, L452).
- **L738-793 — Confirmation Dialog (PROJ-198).** `show_confirmation_dialog` +
  `process_confirmation_event` — the second is invoked by
  `StrategyEventRouter` (L145). Only one pending dialog at a time.
- **L795-817 — Ship Picker stub (PROJ-198).** `show_ship_picker` —
  currently auto-selects all ships and logs; placeholder for a real picker.

**Observation re. project sketch ("window lifecycle + event routing — two obvious
sub-concerns"):** The "event routing" surface inside this file is small (44
lines: the two dispatch helpers `process_ui_callbacks` and
`process_confirmation_event`). The bulk of strategy event routing lives in
`strategy_event_router.py` and stays there. So the natural split is **NOT
"lifecycle vs router"** — it is **"per-window-family lifecycle managers" + "a
small dispatch helper"**. The sketch is partially correct (event-dispatch is
real and separable) but the lifecycle half is itself a god-class; splitting it
further is the higher-value move.

## Proposed sub-modules

A new package `game/ui/screens/strategy_windows/` with one module per
window-family. The original `strategy_window_manager.py` becomes a thin
composition root that owns the slot attributes (so existing code reading
`window_manager.planet_list_window` keeps working) and forwards `open_*` calls
to the family modules.

| Path | Responsibility | Symbols (public) | Est. LOC | Depends on |
|---|---|---|---|---|
| `game/ui/screens/strategy_windows/__init__.py` | Package marker; re-export the registrar classes | `PlanetListRegistrar`, `StarListRegistrar`, `BuildQueueRegistrar`, `EventLogRegistrar`, `EmpirePanelRegistrar`, `OrdersRegistrar`, `FleetReportRegistrar`, `TransferRegistrar`, `SelectionPromptRegistrar`, `MoveChoiceDialog`, `ConfirmationDialogController`, `UICallbackDispatcher`, `ShipPickerStub` | 30 | (children) |
| `game/ui/screens/strategy_windows/list_windows.py` | Planet-list + star-list + the shared `_navigate_camera_to` helper. These two windows share the 90%-screen rect, the navigate-and-close idiom, and the camera-centering callback — keep them together | `PlanetListRegistrar.open(...)`, `StarListRegistrar.open(...)`, `navigate_camera_to(scene, hex)` | ~110 | scene, manager, `PlanetListWindow`, `StarListWindow` |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | Build-queue list + empire-wide build queue | `BuildQueueRegistrar.open_list(...)`, `BuildQueueRegistrar.open_empire(...)`, `BuildQueueRegistrar.close_empire(...)` | ~80 | scene, manager, `BuildQueueListWindow`, `EmpireBuildQueueWindow` |
| `game/ui/screens/strategy_windows/event_log_window_ctrl.py` | Both event-log openers + navigate/close callbacks | `EventLogRegistrar.open_all(...)`, `EventLogRegistrar.open_with_events(events)` | ~90 | scene, manager, `EventLogWindow`, `HexCoord` |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | Empire panel + Settings (small siblings, both centered modals with no command closures) | `EmpirePanelRegistrar.open(...)`, `SettingsRegistrar.open(...)` | ~80 | scene, manager, `EmpirePanelWindow`, `SettingsWindow` |
| `game/ui/screens/strategy_windows/orders_window_ctrl.py` | The 60-line `open_orders_window` with its three command-dispatch closures (fleet vs planet) | `OrdersRegistrar.open(scene, entity, entity_type)` | ~110 | `OrdersWindow`, command DTOs |
| `game/ui/screens/strategy_windows/fleet_report_ctrl.py` | Fleet report window + split-fleet command closure | `FleetReportRegistrar.open(scene, fleet)` | ~60 | `FleetReportWindow`, `SplitFleetCommand` |
| `game/ui/screens/strategy_windows/transfer_dialogs.py` | Transfer dialog + cargo quick dialog (both initiated from the same fleet right-click flow) | `TransferRegistrar.open(...)`, `TransferRegistrar.open_quick(...)` | ~70 | `TransferDialog`, `CargoQuickDialog` |
| `game/ui/screens/strategy_windows/selection_prompts.py` | Planet selection, system selection, fleet selection — three nearly-identical "modal selector" prompts | `prompt_planet(...)`, `prompt_system(...)`, `prompt_fleet(...)` | ~80 | `PlanetSelectionWindow`, `SystemSelectionWindow`, `FleetSelectionWindow` |
| `game/ui/screens/strategy_windows/planet_abilities_ctrl.py` | Planet-abilities window + the editor-dispatch table that delegates to `StrategyEventRouter` | `PlanetAbilitiesRegistrar.open(scene, planet)`, `open_planet_editor(scene, editor_type, planet)` | ~70 | `PlanetAbilitiesWindow`, `StrategyEventRouter` |
| `game/ui/screens/strategy_windows/move_choice_dialog.py` | The inline UIWindow built ad-hoc — the only window not backed by a dedicated `*_window.py`. Keeps its callback registration localized | `MoveChoiceDialog.show(...)` (registers callbacks via injected `UICallbackDispatcher`) | ~60 | `pygame_gui`, `UICallbackDispatcher` |
| `game/ui/screens/strategy_windows/dispatch.py` | The two small dispatch helpers — `UICallbackDispatcher.process_ui_callbacks(event)` and `ConfirmationDialogController.show(...)`/`.process_event(event)`. Stateful (callback map + pending-dialog refs), so they are class instances owned by the composition root | `UICallbackDispatcher`, `ConfirmationDialogController` | ~80 | `pygame_gui` |
| `game/ui/screens/strategy_windows/ship_picker.py` | The PROJ-198 placeholder. Its own file flags the TODO clearly | `ShipPickerStub.show(ships, ability_name, on_selected)` | ~25 | `logging` |
| `game/ui/screens/strategy_window_manager.py` (rewritten) | Composition root. Owns the 14 window-slot attributes (so existing reads like `wm.planet_list_window` still work). Holds one instance of each registrar + the two dispatchers. Its `open_*` methods delegate to the matching registrar and assign the returned window into the slot | `StrategyWindowManager` | ~180 | all of the above |

**Total:** ~1125 LOC across 14 files. The original was 817. The increase
(~38%) is class/imports boilerplate per module — a worthwhile cost for the
hard-to-grow constraint.

**Every resulting module is comfortably under 500 LOC** (largest is the
composition root at ~180; second-largest is `orders_window_ctrl.py` at ~110).

Possible directions evaluated:

- **Per-window-type registrar classes — CHOSEN.** Fits the structure already
  hinted at by the banner-section organization. Each registrar can be tested
  in isolation with a mock scene + mock manager. Adding a 15th window means
  adding a new registrar file, NOT growing an existing one.
- **Lifecycle manager + event router as two sibling files — REJECTED in this
  shape.** The actual event router lives elsewhere
  (`strategy_event_router.py`); the routing surface inside this file is only
  the 80-line dispatch helpers. Pulling them into a single sibling file
  produces a lopsided 750/80 split that solves nothing.
- **Window factory / pool — REJECTED.** Windows are not pooled and each has
  bespoke construction args (especially the closures inside
  `open_orders_window` and `open_fleet_report_window`). A factory would
  abstract over essentially nothing.

## Public API surface

The composition root keeps exactly the API that callers use today. Verified
caller surface (greppable):

- **`strategy_ui.py`** — calls 17 distinct methods: `handle_resize`,
  `prompt_planet_selection`, `prompt_fleet_selection`,
  `open_system_selection`, `prompt_move_choice`, `open_planet_list`,
  `open_star_list`, `open_build_queue_list`, `open_empire_build_queue_window`,
  `close_empire_build_queue_window`, `open_event_log`,
  `open_event_log_with_events`, `open_orders_window`,
  `open_fleet_report_window`, `open_transfer_dialog`,
  `open_cargo_quick_dialog`, `open_planet_abilities_window`,
  `open_empire_panel`, `show_confirmation_dialog`, `show_ship_picker`.
- **`strategy_event_router.py`** — calls `process_ui_callbacks` (twice),
  `process_confirmation_event`, and reads 14 window-slot attributes for
  modal-detection (`has_modal_open`).
- **`strategy_input_handler.py`** — reads `planet_list_window` slot.
- **`strategy_screen.py`** — reads `fleet_orders_window`, `transfer_dialog`
  slots; calls `open_settings`.
- **`tests/unit/ui/screens/test_strategy_window_manager.py`** — instantiates
  `StrategyWindowManager(scene=…, manager=…, width=…, height=…,
  input_mapper=None, asset_resolver=None)` and asserts initial slot states.

All of these continue to work unchanged after the split.

## Caller-update strategy

**Choice: Option A — re-export shim.**

**Justification:**

1. The composition root pattern makes Option A natural: the rewritten
   `strategy_window_manager.py` IS the public face. The new
   `strategy_windows/` package modules are implementation detail; nothing
   outside the file imports them.
2. 30+ caller sites across at least five files (`strategy_ui.py`,
   `strategy_event_router.py`, `strategy_input_handler.py`,
   `strategy_screen.py`, plus the test file). The diff cost of Option B is
   high while the benefit (callers see "shorter import paths") is small,
   because the composition root remains the right abstraction.
3. The 14 window-slot attributes are read directly by `strategy_event_router.has_modal_open()`. Hiding them behind sub-objects would force a rewrite of that 40-line modal-detection method (or introduce delegating properties — needless complexity). Keeping the slots on the composition root preserves zero-cost compatibility.
4. The composition root is NOT the "graveyard shim" anti-pattern flagged in
   the design — it is a real first-class object with state (the 14 slots and
   the two dispatcher instances). It does not need a follow-up deletion
   project.

**Migration plan:**

1. Add the `strategy_windows/` package and its 13 child modules.
2. Rewrite `strategy_window_manager.py` to instantiate the registrars and
   delegate. The class name `StrategyWindowManager` and every public method
   signature stays identical.
3. Run targeted `tests/unit/ui/screens/test_strategy_window_manager.py` plus
   the modal-aware tests
   (`test_sub_window_hotkeys.py`, `test_fleet_orders_refresh.py`).
4. Run full sharded suite. Baseline must hold at 15405 passed, 2 skipped.
5. Manual smoke per the test plan below.

## Test plan

**Existing automated coverage:**

- `tests/unit/ui/screens/test_strategy_window_manager.py` — direct unit tests
  for `StrategyWindowManager`. These all use mock scene + mock manager and
  exercise the public `open_*` methods. They MUST continue to pass without
  modification.
- `tests/unit/ui/screens/test_sub_window_hotkeys.py` — exercises the
  modal-detection chain through `StrategyEventRouter.has_modal_open()`,
  which reads the 14 slot attributes. Verifies the composition-root API
  preserves the slots.
- `tests/unit/ui/screens/test_fleet_orders_refresh.py` — exercises
  `fleet_orders_window` interaction.

**New automated coverage (TDD per Rule 1):**

- For each registrar file, a focused unit test that:
  1. Mocks scene + manager.
  2. Calls the registrar's `open(...)` method.
  3. Asserts the underlying window-class constructor was invoked with the
     expected args (especially the closure-built `*_callback` args for
     orders and fleet-report — a known regression risk).
- A test for `UICallbackDispatcher.process_ui_callbacks` with a fake
  `UI_BUTTON_PRESSED` event and a registered callback that does NOT exist in
  the map (must return False without raising).
- A test for `ConfirmationDialogController.process_event` covering the
  "stale dialog reference" case (dialog was killed externally).

**Manual smoke checklist:**

- [ ] Open and close: planet list, star list, build queue list, empire build
      queue, event log, empire panel, settings, fleet orders (fleet),
      fleet orders (planet), fleet report, transfer dialog, cargo quick
      dialog (load + unload), planet selection prompt, planet abilities
      window, system selection prompt, fleet selection prompt, move choice
      dialog.
- [ ] Confirm `Esc`/click-outside still closes the menu panel (regression
      check on `StrategyEventRouter`).
- [ ] Right-click planet → open abilities → click each editor button
      (atmosphere / gravity / water / radiation / food) and verify the editor
      opens (validates the `_open_planet_editor` dispatch table delegated
      cleanly to `StrategyEventRouter`).
- [ ] Trigger a superweapon to open a confirmation dialog; confirm/cancel both
      paths work (validates `ConfirmationDialogController`).
- [ ] Run a turn-end and verify the event log auto-opens via
      `open_event_log_with_events`.

## Risks

1. **Per-window state coupling.** The 14 window slots are *read* by
   `strategy_event_router.has_modal_open()`. Mitigation: keep the slots on
   the composition root as today. The registrars assign back into the
   composition root's slot after construction (or the composition root
   captures the registrar's return value into the slot itself — preferred,
   keeps registrars stateless).
2. **Closure ownership for orders/fleet-report.** The two largest methods
   build command-dispatch closures that capture `entity_type`, `owner_id`,
   `fleet_owner_id`, and `self.scene.facade`. Moving them into a registrar
   class means the closure now captures the registrar's `self`/scene
   reference instead. Behavioral parity must be verified by the targeted
   unit tests — a closure that captures the wrong scene will produce silent
   command misrouting (CQRS bug), not a visible exception.
3. **Event routing dispatch table — order-sensitive.** `route_event` in
   `strategy_event_router.py` calls `process_ui_callbacks` BEFORE
   `_handle_button_pressed` so prompt-button clicks are claimed by the
   prompt's callback rather than falling through to the global button
   handler. The `UICallbackDispatcher.process_ui_callbacks` contract MUST
   continue to return `True` and `del` the callback when consumed. The
   targeted dispatcher unit test guards this invariant.
4. **Latent bug — `planet_abilities_window` not None-initialized.** Today
   the slot is created on first open (`self.planet_abilities_window =
   PlanetAbilitiesWindow(...)`) without a corresponding `__init__`
   declaration. `StrategyEventRouter.has_modal_open()` does NOT check this
   slot — possibly intentional, possibly an oversight. The decomposition is
   a good moment to either (a) add the slot and modal-check, or (b)
   document the omission in code. Flagged as Open Question 4.
5. **Local imports inside methods.** `OrdersWindow`, `SettingsWindow`,
   `TransferDialog`, `CargoQuickDialog`, `PlanetAbilitiesWindow`, and
   `StrategyEventRouter` are imported inside methods, presumably to avoid
   import cycles at module-load time. Each registrar must preserve the
   same local-import pattern unless we verify the cycle no longer exists.
   Mitigation: in each registrar module, retain the in-method import; do
   not promote to module-level until the cycle is independently verified
   absent.
6. **PROJ-309 sequencing with strategy_renderer split.** Sibling renderer
   decomposition runs in parallel. The two files share NO code (renderer
   paints; window manager opens windows), so direct conflict is unlikely.
   Cross-check: `strategy_ui.py` is touched by both projects'
   re-export shims — coordinate the merge order.

## Open questions

1. **Should the Move Choice dialog gain its own `*_window.py` class, mirroring
   the other 13?** Currently it is built inline from `pygame_gui` primitives.
   A `MoveChoiceWindow` class would symmetric-ize the design and make the
   registrar trivial. Out of scope for this split, but flag for follow-up.
2. **Should `open_event_log` and `open_event_log_with_events` collapse into a
   single method `open_event_log(events: Optional[list] = None)`?** They
   share 100% of their body except for one line (event source). Out of
   scope; flag for follow-up.
3. **Alignment with `strategy_renderer.py` decomposition.** The renderer
   split likely produces a `strategy_render/` package; the parallel here is
   `strategy_windows/`. Confirm with the renderer designer that the package-
   per-screen-aspect convention is shared. If the renderer chooses a flat
   sibling-files layout, we may want to mirror it (or vice versa) for
   project-wide consistency. Recommend sub-package for this file because
   13 files at the screens-dir root would meaningfully clutter the
   directory listing (already 70+ files).
4. **`planet_abilities_window` slot.** Should the decomposition fix the
   missing None-init and missing `has_modal_open` entry, or preserve current
   behavior? Recommend fixing in the same commit — the cost is two lines and
   it eliminates a latent inconsistency. Flag for user decision before
   Phase 3.
5. **Should `ShipPickerStub` graduate to its own future ticket?** PROJ-198
   left it as a placeholder. Putting it in its own file makes the TODO
   visible to anyone scanning the package. Recommend filing a future ticket
   referencing the new file path.
