# Decomposition Design: race_setup_screen.py

**Current size:** 1598 lines
**Target post-split:** every resulting module <500 lines (UI screen class ≤300 per `docs/03_CONVENTIONS.md` §2.4)

> **Last verified:** 2026-04-27 — first design pass; based on the file at HEAD (1598 LOC) plus its 2 production callers (`game/app.py`, `game/ui/screens/new_game_setup_screen.py`).

---

## Pre-existing decomposition state (read this first)

The PROJ-309 design.md sketch describes this file as *"a god-screen with 4-5 logical tabs/sections"* and proposes splitting it into `genome_panel.py / traits_panel.py / preview_panel.py / controls_panel.py`. **That sketch is largely already implemented and is wrong on the remaining work.**

The seven tabs were extracted across PROJ-12 (Phase 4), PROJ-44 (Phase 7), PROJ-66 (Phase 6) and PROJ-299 into 13 sibling classes:

| Concern | Module | LOC | Imported by `race_setup_screen.py`? |
|---|---|---|---|
| Summary tab | `game/ui/panels/race_summary_panel.py` | (extracted) | yes |
| Identity tab | `game/ui/panels/race_identity_panel.py` | (extracted) | yes |
| Visuals — flag gallery | `game/ui/panels/race_flag_gallery.py` | (extracted) | yes |
| Visuals — portrait gallery | `game/ui/panels/race_portrait_gallery.py` | (extracted) | yes |
| Ships — theme gallery | `game/ui/panels/race_theme_gallery.py` | (extracted) | yes |
| Environment tab | `game/ui/panels/race_environment_panel.py` | (extracted) | yes |
| Aptitudes tab | `game/ui/panels/race_aptitudes_panel.py` | (extracted) | yes |
| Descriptions tab | `game/ui/panels/race_description_panel.py` | (extracted) | yes |
| Description LLM logic | `game/strategy/services/race_description_llm_controller.py` | 317 | yes |
| Race library load dialog | `game/ui/screens/race_browser_dialog.py` | 303 | yes |
| Validation | `game/ui/screens/race_validator.py` | 96 | yes |
| Asset I/O | `game/ui/screens/race_asset_loader.py` | 279 | yes |

So `race_setup_screen.py` is **not a god-class of business logic**. It is a god-class of *orchestration glue*: tab plumbing, navigation, event-routing, ad-hoc modals, ship preview rendering, and randomization dispatch. The remaining 1598 LOC are entirely about wiring those 13 components together. The naive sketch (`genome_panel / traits_panel / preview_panel / controls_panel`) would duplicate work already done.

The real, remaining work is to apply the **PROJ-282 MVVM split** (`battle_setup/` shape: `screen.py` thin orchestrator + `controller.py` + `view_model.py` + `input_handler.py` + `renderer.py`) to this screen, so that the orchestrator class itself drops to ≤300 lines.

---

## Current responsibilities

Mapping every distinct thing the current file does, with line ranges:

1. **Module-level imports + tab-index constants** (lines 1–73). 13 sibling-class imports + the `TAB_*` enum.
2. **Constructor and instance-field declaration** (76–181). Initializes 13 panel/gallery references, LLM-dialog state (8 fields just for the 30s/90s "still working" modal and its error popups), save-update modal state, ship-preview-element list, race library, race registry.
3. **UI tree construction** (`_create_ui`, `_create_tab_buttons`, `_create_step_panels`) (183–303). Lays out tab buttons, makes 7 tab UIPanels, dispatches per-tab content factories.
4. **Per-tab content factory wiring** (310–319, 325–360, 378–422, 558–579, 585–610, 824–833). Six small factories that each instantiate one of the extracted panel/gallery classes and store the reference. This is just glue — each factory is 5–25 lines.
5. **Ships-tab ship preview renderer** (424–552, ~130 LOC). Builds a 3×3 grid of `ship_class → (skin, portrait)` pairs in a scrolling container by reading `ShipThemeManager`. This is the only substantial *new* rendering still inside the screen class.
6. **PROJ-299 LLM "still working" dialog** (627–714, ~90 LOC). Per-frame threshold checks, modal construction (`_show_llm_dialog`), tear-down (`_close_llm_dialog`).
7. **PROJ-299 LLM error popup** (720–802, ~85 LOC). Static `_llm_error_message` mapper for `LLMException` types, `_check_llm_error_popups` per-frame check, `_show_llm_error_popup`, `_close_llm_error_popup`.
8. **Description-panel ↔ controller sync** (612–622, 804–818). Wires `attach_controller` / `set_state`, plus delegate methods for char-count and config sync.
9. **Tab navigation + button visibility** (`_show_step`, `_update_navigation_buttons`, `_update_tab_highlighting`) (889–963). Controls which tab panel is visible, when Save / Generate Random buttons appear, and tab-button highlighting.
10. **Validation-on-save dispatch** (`_validate_for_save`) (964–996). Syncs identity + aptitudes panels into `race_config`, runs budget check, delegates to `RaceValidator`.
11. **Race-library load flow** (`_on_load_race`, `_on_race_selected`, `_on_race_browser_cancelled`) (1002–1044). Opens `RaceBrowserDialog`, replaces `race_config` on selection.
12. **Cross-panel resync after race load** (`_populate_ui_from_config`) (1046–1094). After loading a race from disk, walks all 8 panels updating their `race_config` reference + calling `set_from_config()`. Plus the PROJ-299 controller resync.
13. **Per-tab randomization dispatch** (`_on_randomize`, `_randomize_identity`, `_randomize_visuals`, `_randomize_ships`, `_randomize_environment`, `_randomize_aptitudes`) (1096–1221, ~125 LOC). Six methods. Each pulls available IDs from gallery panels, calls `RaceRandomizer.randomize_*`, writes back into `race_config`, refreshes the relevant panel.
14. **Master "Randomize All"** (`_randomize_all`) (1223–1288, ~65 LOC). Calls `RaceRandomizer.randomize_all`, sprays the result across `race_config`, then `_populate_ui_from_config()` + ship-preview refresh.
15. **Save flow** (`_on_save`, `_do_save`, `_show_save_update_dialog`, `_on_overwrite_save`, `_on_save_as_new`, `_on_save_dialog_cancel`) (1296–1423, ~125 LOC). FEAT-05 overwrite-vs-save-as-new modal + actual library save call + race-registry cache invalidation.
16. **Cancel + lifecycle** (`_on_cancel`, `kill`) (1290–1294, 1438–1443). `kill()` cancels in-flight LLM calls.
17. **Per-frame update** (`update`) (1425–1436). Polls the LLM controller, runs LLM dialog/popup threshold checks.
18. **Event dispatch** (`process_event`) (1445–1598, ~150 LOC). The biggest single method: routes button presses for LLM dialog/popup, description-tab LLM buttons, tab buttons, save-update dialog buttons, main nav buttons, and gallery clicks; routes dropdown events to identity + environment panels; routes slider events to environment + aptitudes panels; routes text-entry events to identity + description panels.

That's **18 distinct concerns**. The clean MVVM split groups them into 5 modules below.

---

## Proposed sub-modules

All paths are under `game/ui/screens/race_setup/` (new package), mirroring `game/ui/screens/battle_setup/`.

### 1. `game/ui/screens/race_setup/screen.py` — orchestrator (≤200 LOC target)
- **Responsibility:** Construct the seven tab panels, hold references to delegates, forward `update()` and `process_event()` to them. No business logic, no ad-hoc modals, no direct panel mutation.
- **Symbols moved here from current file:** `RaceSetupScreen` class shell — constructor (slimmed), `_create_ui`, `_create_tab_buttons`, `_create_step_panels`, the six 5-line `_create_*_panel_content` factories, `update`, `kill`. `process_event` becomes `return self._input_handler.handle(event)`.
- **Estimated LOC:** ~180–220.
- **Depends on:** `Controller`, `InputHandler`, `Renderer`, `ViewModel`, `ShipPreviewBuilder`, `LLMDialogService`, plus the 8 extracted panel classes (unchanged imports).

### 2. `game/ui/screens/race_setup/controller.py` — mutation + lifecycle (≤450 LOC target)
- **Responsibility:** Every mutation that flows into `race_config` and every call into the race library or registry. Owns the "save flow" (FEAT-05 overwrite-vs-new), the load flow (delegating dialog construction to renderer), validation, and the randomization dispatch. No pygame imports.
- **Symbols moved here:** `_validate_for_save`, `_on_load_race` (data half — opening the dialog moves to renderer), `_on_race_selected`, `_on_race_browser_cancelled`, `_populate_ui_from_config`, `_on_randomize`, `_randomize_identity`, `_randomize_visuals`, `_randomize_ships`, `_randomize_environment`, `_randomize_aptitudes`, `_randomize_all`, `_on_save`, `_do_save`, `_on_overwrite_save`, `_on_save_as_new`, `_on_save_dialog_cancel`, `_on_cancel`. Owns the LLM controller wiring (`_on_description_controller_change`, `_update_description_char_counts`, `_update_descriptions_from_text`).
- **Estimated LOC:** ~380–440. Concentrated mutation surface — per §2.4 a controller with 15+ mutation methods can legitimately exceed 300; this one has ~17.
- **Depends on:** `RaceConfig`, `RaceLibrary`, `RaceRandomizer`, `RaceValidator`, `RacePointBudget`, `IRaceRegistry`, `RaceDescriptionLLMController`, the 8 panel classes (for config sync), `ViewModel` (for tab state).

### 3. `game/ui/screens/race_setup/view_model.py` — derived view state (≤120 LOC)
- **Responsibility:** Tab index, "is editing" flag, navigation rules ("which buttons are visible on tab X"), LLM dialog threshold state (`_bio_dialog_fired_at`, `_socio_dialog_fired_at`, `_bio_error_seen`, `_socio_error_seen`). Pure data + property functions; no pygame imports, no widgets.
- **Symbols moved here:** the `TAB_*` constants and `TAB_NAMES`, the `current_step` field, the four PROJ-299 threshold-tracking ints, plus the dispatch tables that map `tab_index → which buttons should show` (today inlined in `_update_navigation_buttons`).
- **Estimated LOC:** ~80–120.
- **Depends on:** nothing (pure data).

### 4. `game/ui/screens/race_setup/renderer.py` — modal & ship-preview construction (≤350 LOC target)
- **Responsibility:** Construct ad-hoc pygame_gui modals (save-update, LLM "still working", LLM error popup) and build the Ships-tab preview grid. All raw pygame_gui element creation that *isn't* delegated to a panel class lives here.
- **Symbols moved here:**
  - Ship preview: `_refresh_ship_preview` (~130 LOC).
  - Save-update modal: `_show_save_update_dialog`, plus its `_btn_overwrite / _btn_save_new / _btn_save_cancel` field declarations (~70 LOC).
  - LLM modal: `_show_llm_dialog`, `_close_llm_dialog` (~50 LOC).
  - LLM error popup: `_show_llm_error_popup`, `_close_llm_error_popup` (~35 LOC).
  - The factory methods stay in `screen.py` because they're 5-line panel-construction calls.
- **Estimated LOC:** ~290–340.
- **Depends on:** pygame, pygame_gui, `ShipThemeManager`. Owns its own widget-reference fields (callers go via the renderer's public API, e.g. `renderer.show_save_update_dialog()` returns the three button references).
- **Optional further split if it grows past 350:** extract `ship_preview.py` (just the 130-LOC `_refresh_ship_preview` method into a `ShipPreviewBuilder` class). I recommend doing this immediately because ship preview is unrelated to dialog-modal construction.

### 5. `game/ui/screens/race_setup/input_handler.py` — event routing (≤250 LOC target)
- **Responsibility:** `pygame.event.Event → controller method call` mapping. Owns the giant switch in today's `process_event`.
- **Symbols moved here:** `process_event` body, plus the `_on_tab_clicked` thin shim. Routes are: tab buttons, save-update dialog buttons, LLM dialog buttons, LLM error popup OK, description-tab LLM buttons (Generate/Cancel/Re-roll Bio/Socio), main nav buttons (Cancel/Save/Load/Randomize/RandomizeAll), gallery button clicks (delegated to `_flag_gallery.handle_button_click` etc.), dropdown changes, slider changes, text-entry changes.
- **Estimated LOC:** ~180–230. Currently 153 lines (1445–1598) and a few helper checks.
- **Depends on:** pygame_gui event constants, `Controller`, the panel classes (to inspect `gallery.handle_button_click`).

### 6. `game/ui/screens/race_setup/llm_dialog_service.py` — PROJ-299 modal lifecycle (≤180 LOC, OPTIONAL)
- **Responsibility:** Encapsulates the per-frame "should the still-working dialog appear?" logic plus the error-popup error-mapping. Owns the threshold state. Today this is two methods (`_check_llm_dialog_thresholds`, `_check_llm_error_popups`) plus the static `_llm_error_message` mapper, plus the four threshold-tracking fields.
- **Symbols moved here:** `_check_llm_dialog_thresholds`, `_check_llm_error_popups`, `_llm_error_message`. Holds references to the dialog windows (renders are delegated to renderer).
- **Estimated LOC:** ~110–140.
- **Depends on:** `Renderer` (to actually show modals), `RaceDescriptionLLMController`, `FieldStatus`, `LLMException` types.
- **Optional?** Yes. If renderer's LOC after extraction is comfortably under 300, this logic can stay inside `Controller` instead. **Recommendation:** extract — these checks are specific to a feature flag (`provider is not None`) and are cleaner as their own service. Without extraction, controller jumps from ~380 to ~480 LOC.

### LOC estimate summary

| Module | Est. LOC | Budget | OK? |
|---|---|---|---|
| `screen.py` (orchestrator) | 200 | ≤300 (§2.4) | yes |
| `controller.py` | 420 | ≤500 (§2.3); §2.4 explicitly permits >300 for concentrated mutation | yes |
| `view_model.py` | 100 | ≤300 | yes |
| `renderer.py` | 320 | ≤500; ≤300 if `ship_preview.py` extracted | yes (extract recommended) |
| `input_handler.py` | 210 | ≤300 | yes |
| `llm_dialog_service.py` (optional) | 130 | ≤300 | yes |
| **Total** | ~1380 | (was 1598) | -218 LOC: imports/boilerplate dedup |

Every resulting module is well under 500. The orchestrator is comfortably under 300 and contains zero business logic — that is the structural pressure against rebloat, because someone trying to add a method has to choose Controller vs Renderer vs InputHandler rather than "another method on the screen class".

---

## Public API surface

Symbols imported by callers TODAY:

| Symbol | Imported by |
|---|---|
| `RaceSetupScreen` (class) | `game/app.py:522` (lazy import inside `start_race_setup`); `game/ui/screens/new_game_setup_screen.py:433` (lazy import inside `_on_setup_race_clicked`) |
| `RaceBrowserDialog` (class — re-exported from `race_browser_dialog`) | `game/ui/screens/new_game_setup_screen.py:405` (lazy import inside `_on_load_race_clicked`) |

That's it. Tests have one symbol — `RaceSetupScreen` — imported by `tests/unit/ui/screens/test_race_setup_screen.py:36`.

`RaceBrowserDialog` is interesting — `new_game_setup_screen.py` imports it from `race_setup_screen` (line 405), but `race_setup_screen.py` doesn't even re-export it; it's accessible only because `from game.ui.screens.race_browser_dialog import RaceBrowserDialog` was left in module-level imports of `race_setup_screen.py` (line 35). This is a leaked import path. Post-split, `new_game_setup_screen.py` should import `RaceBrowserDialog` from its real home (`game.ui.screens.race_browser_dialog`).

**Public API surface is therefore: just `RaceSetupScreen`.** Two production callers, both lazy imports.

---

## Caller-update strategy

**Choice: Option A (re-export shim).**

**Justification:**

1. **Two production callers + one test caller is "few", not "many"** — Option B is genuinely viable here.
2. **However**, the project convention (per design.md "Pattern: Public API stability") prefers Option A when both work, *and* the cost of Option A is trivial: the new `screen.py` lives at `game/ui/screens/race_setup/screen.py`, and we leave a 4-line re-export shim at `game/ui/screens/race_setup_screen.py`:
   ```python
   from game.ui.screens.race_setup.screen import RaceSetupScreen
   __all__ = ["RaceSetupScreen"]
   ```
3. **Shim graveyard risk is low** because (a) only 2 callers, easy to migrate later if we want to retire the shim, and (b) no Option-B benefit lost — the new package layout (`race_setup/`) is the canonical import path going forward and PROJ-309's design.md "System Migration Policy" footnote applies: schedule shim removal in a follow-up project once both callers are touched for unrelated reasons.
4. **The leaked `RaceBrowserDialog` re-export** (described above) is fixed *during this refactor*, not preserved — `new_game_setup_screen.py:405` is updated to import from `game.ui.screens.race_browser_dialog`. This is a partial Option B for that one symbol because the import is wrong today and the cost to fix it is one-line.

So: **Option A for `RaceSetupScreen` (preserve `from game.ui.screens.race_setup_screen import RaceSetupScreen`); Option B for `RaceBrowserDialog`** (fix the leaked re-export at the same time).

---

## Test plan

### Existing tests likely affected
- `tests/unit/ui/screens/test_race_setup_screen.py` (1221 lines, bypass-init pattern). Imports `RaceSetupScreen` from `game.ui.screens.race_setup_screen`. With the shim, this import keeps working unchanged.
  - **However**, because the test patches private methods like `_validate_for_save`, `_on_save`, `_do_save`, `_show_save_update_dialog`, `_on_randomize`, `_populate_ui_from_config`, `_refresh_ship_preview`, etc., **every test that patches a private method now patches the wrong class**. After the split, those methods live on Controller / Renderer, not the screen.
  - **Mitigation:** the test file is bypass-init (`__init__` patched away, fields set manually), so it tests behaviour at the screen level. Two options:
    (a) Update the screen so it forwards each patched method as a thin shim (e.g. `def _do_save(self): return self._controller.do_save()`) — preserves test compatibility, but creates god-class drift via the back door. Reject.
    (b) Migrate the tests to patch the new sibling classes directly. ~300–500 LOC of test edits but keeps the new structure honest. Choose this.
- `tests/unit/ui/test_race_environment_panel.py` — imports the panel directly, unaffected.

### New tests required
- **Contract test:** `tests/unit/ui/screens/test_race_setup_shim.py` — assert `from game.ui.screens.race_setup_screen import RaceSetupScreen` still works post-shim, and `RaceSetupScreen.__module__` is `game.ui.screens.race_setup.screen` (proves the shim is forwarding, not duplicating).
- **Cycle test:** `tests/unit/ui/screens/race_setup/test_no_import_cycles.py` — import each new sub-module in isolation in a fresh subprocess; assert no `ImportError`.
- **Smoke test for the LLM dialog service** (only if §6 module is extracted): unit-test `LLMDialogService.check_thresholds()` against a mocked `RaceDescriptionLLMController` — currently this logic has zero dedicated test coverage.

### Sharded suite
After each migration phase: `python Tools/test_sharded/test_sharded.py`. Baseline 15405 must hold.

---

## Risks

1. **Test patching of private methods breaks en masse.** As above — `test_race_setup_screen.py` patches ~17 private methods that move to Controller/Renderer. **Mitigation:** budget time to migrate the test file in the same phase; reject the "thin-shim methods on screen" workaround because it reintroduces the god-class.
2. **Mutable state shared across delegates.** Today the screen owns `race_config`, ~13 panel references, ~10 dialog button references, ship-preview elements, and the LLM controller. Splitting into Controller + Renderer + ViewModel + InputHandler creates the question: who owns each field? **Mitigation:** clear ownership rules:
   - `race_config` — owned by Controller. Screen exposes `controller.race_config` as a read-only property if anyone needs it.
   - Panel references — owned by Controller (it's the only one that mutates them; renderer creates them but hands them over).
   - Dialog widget references — owned by Renderer (it created them; it kills them).
   - LLM threshold state — owned by ViewModel.
   - Tab state — owned by ViewModel.
3. **PROJ-299 LLM controller wiring is fragile** — it uses `set_race_config()` to keep its reference fresh after race load (line 1062–1066, with explanatory comment). After the split, the controller becomes a Controller-owned field. The "PROJ-299: silent data loss" guard must move with `_populate_ui_from_config` and stay on the Controller.
4. **The leaked `RaceBrowserDialog` import path** (`new_game_setup_screen.py:405`). Easy to miss because it's a lazy import inside a method. **Mitigation:** update the import in the same PR.
5. **No import cycles foreseen** — the package boundary is one-way: screen → controller → panels → strategy services. Controller imports `RaceDescriptionLLMController` (in `game/strategy/services/`), same direction as today.
6. **Renderer's modal-construction methods need to return widget references** so the Controller / InputHandler can wire button events to handlers. This is a clean dependency flow (caller passes callbacks; renderer returns nothing or returns a small struct of button handles). The current code stores them as fields on the screen — moving these fields to the renderer is purely mechanical.

---

## Open questions

1. **Should `LLMDialogService` (§6) be extracted, or kept inside Controller?** Recommendation: extract. The threshold-management state is feature-flagged (only relevant when `provider is not None`) and the logic is self-contained. Costs: one extra module. Benefits: Controller stays under 400 LOC and the LLM concern becomes individually testable. **Flag for cross-design review.**
2. **`_refresh_ship_preview` is the only substantive renderer responsibility unrelated to dialog construction. Should it become its own `ShipPreviewBuilder` class in `race_setup/ship_preview.py` rather than living inside `renderer.py`?** Recommendation: yes. Splits a 130-LOC method into its own module, makes it independently testable (currently has no dedicated test), and gives renderer a single concern (modal construction). **Flag for cross-design review** — minor pro/con: more files vs. cleaner SRP.
3. **The PROJ-309 sketch proposed `genome_panel / traits_panel / preview_panel / controls_panel`. Confirm the cross-design reviewer accepts the deviation.** This document explicitly refutes the sketch — the panels are already extracted, and what remains is orchestration/event-routing/modal-construction. The MVVM split is a better fit. **Flag for cross-design review.**
4. **Should the existing `race_validator.py` and `race_asset_loader.py` move under `race_setup/`?** They are currently siblings in `game/ui/screens/`. Argument for moving: they are only used by `race_setup_screen` (single consumer — confirmed by Grep). Argument against: scope creep beyond the file we were asked to decompose. **Recommendation:** leave them where they are for this PROJ-309 phase; flag as a follow-up.
5. **Test patch migration cost** — `test_race_setup_screen.py` is 1221 lines and patches many private methods. Confirm with reviewer that we accept the test-file churn rather than introducing screen-level shim methods.
