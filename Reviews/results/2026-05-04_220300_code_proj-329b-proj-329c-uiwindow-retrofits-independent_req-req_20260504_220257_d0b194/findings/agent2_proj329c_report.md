# PROJ-329C Refactor Review — Agent 2 Report

## PlanetAbilitiesWindow — Behavioral Parity

### __init__ order

**PASS** — `planet_abilities_window.py:199-228`

Stage 1 (lines 199-211) sets all cheap state (planet, facade, component_registry,
_on_open_editor, _on_close_callback, _toggle_buttons, _editor_buttons,
_status_labels, _widgets, controller) before `super().__init__` (line 214).
Stage 3 (lines 223-228) branches on `_window_init_bypassed` then delegates to
the builder. The ordering matches the canonical two-stage pattern exactly.

No facade I/O occurs in `__init__`. The `self.facade = facade` assignment at
line 201 is pure object storage.

### Controller construction: no facade I/O

**PASS** — `planet_abilities_controller.py:65-68`

`PlanetAbilitiesController.__init__` is three pure attribute assignments
(`self.planet`, `self.facade`, `self.component_registry`). No facade calls,
no model traversal, no I/O of any kind.

### process_event — toggle_ability flow

**PASS** — `planet_abilities_window.py:249-271`

The window calls `self.controller.toggle_ability()` at line 250, dispatches the
result correctly:
- If `result and not result.is_valid` → logs a warning (line 257).
- Otherwise → flips `_is_active`, updates button text (lines 259-263), and
  refreshes the status label via `self.controller.get_component_status()` (line 267).

The controller's `toggle_ability` at `planet_abilities_controller.py:192-208`
builds an `IssuePlanetOrderCommand` and dispatches via `self.facade.handle_command(cmd)`.
Behavior is equivalent to the original inline facade call.

### kill() — on_close_callback ordering

**PASS** — `planet_abilities_window.py:230-233`

`_on_close_callback` fires at line 232 *before* `super().kill()` at line 233.
Matches the canonical pattern and the StrategyModalWindow base class contract.

### ui_builder → controller delegation

**PASS** — `planet_abilities_window.py:52,53,83,123,135`

All five builder queries route through `screen.controller`:

| Builder call | Controller method | Facade I/O? |
|---|---|---|
| `screen.controller.get_available_editors()` | `planet_abilities_controller.py:78-99` | No — iterates planet.facilities + registry lookup |
| `screen.controller.should_show_food_editor()` | `planet_abilities_controller.py:72-76` | No — reads planet.populations |
| `screen.controller.scan_abilities()` | `planet_abilities_controller.py:101-150` | No — iterates planet.facilities + registry lookup |
| `screen.controller.get_component_status()` | `planet_abilities_controller.py:152-174` | No — reads facility.get_activation_state() |
| `screen.controller.is_component_active()` | `planet_abilities_controller.py:176-188` | No — reads facility.get_activation_state() |

**OBSERVATION** — `planet_abilities_window.py:201`, `planet_abilities_controller.py:65-68`
`self.facade` is stored on the PlanetAbilitiesWindow instance during Stage 1
but never referenced again after init — all post-init facade access goes through
the controller. This is dead state on the window (non-breaking, no behavioral
impact).

**OBSERVATION** — `planet_abilities_controller.py:78-99,101-150,152-174,176-188`
Four of the five controller query methods (`get_available_editors`, `scan_abilities`,
`get_component_status`, `is_component_active`) do not call the facade at all —
they read the planet/facility model objects directly. Only `toggle_ability`
(line 208) calls `self.facade.handle_command(...)`. The controller is acting
as a general data-access delegate rather than a pure facade-wrapper. This does
not violate the spec (controllers own "facade queries + command dispatch" and
"should NOT own widget construction" — both are satisfied), but blurs the
stated boundary intent.

---

## PlanetListWindow — Behavioral Parity

### __init__ order

**PASS** — `planet_list_window.py:224-326`

Stage 1 (lines 225-310) sets all cheap state (selected_planet, registries,
facade, galaxy, empire, layout constants, all_planets via `gather_planets`,
columns, effect_keys, filter state, controller) before `super().__init__`
(line 313). `gather_planets` at `planet_list_filters.py:33-62` is a pure
data function (iterates galaxy.systems, caches computed values) — no facade
I/O. Likewise `compute_planet_effect_keys` and `build_effect_columns` are
pure data transformations on the already-gathered planet list.

Stage 3 (lines 321-326) branches correctly on `_window_init_bypassed`.

### Controller construction: no facade I/O

**PASS** — `planet_list_controller.py:31-33`

`PlanetListController.__init__` is two pure attribute assignments
(`self.facade`, `self.on_navigate_callback`). No facade calls.

### _resolve_demographic_view fallback

**PASS — equivalent paths** — `planet_list_window.py:687-701`, `planet_list_controller.py:35-40`

Controller path (line 696-697):
```python
controller = getattr(self, 'controller', None)
if controller is not None:
    return controller.resolve_demographic_view(planet)
```
→ `controller.resolve_demographic_view` (planet_list_controller.py:35-40):
```python
if planet.owner_id is None or self.facade is None:
    return None
return self.facade.get_colony_demographic_view(planet.id)
```

Legacy fallback (lines 699-701):
```python
if planet.owner_id is None or self._facade is None:
    return None
return self._facade.get_colony_demographic_view(planet.id)
```

Both paths test `planet.owner_id is None` → `None`, then `facade is None` →
`None`, then call `facade.get_colony_demographic_view(planet.id)`. The
only difference is `self.facade` (controller attribute) vs `self._facade`
(window attribute). In production these are the same object (both bound from
the `facade` parameter in `__init__` at lines 238 and 308). In tests with a
custom mock controller, the controller path uses the mock's facade — which is
the intended override behavior.

**OBSERVATION** — `planet_list_window.py:690-693`, `planet_list_controller.py:42-45`
The fallback comment says "Bypass-init tests construct the window via `__new__`
and set `self._facade` directly without going through `__init__`." Under the
current `bypass_init` context manager, `__init__` *does* run — Stage 1 constructs
the controller (line 307-310), so `getattr(self, 'controller', None)` will find
it and the fallback never fires. The fallback guards a pre-existing test pattern
(`__new__` + manual attr set) that may be distinct from bypass_init. The check
is harmless and correctly handles both construction styles.

### Public methods

**PASS** — all three public methods preserve original behavior.

- **process_event** (`planet_list_window.py:411-525`): Handles UI_BUTTON_PRESSED
  (filter toggles, Save Preset, Apply, Build Queue, Navigate), MOUSEBUTTONUP
  (row click → `_on_planet_selected` which calls `_resolve_demographic_view`),
  UI_TEXT_ENTRY_FINISHED (range text inputs), MOUSEWHEEL (scrolling). No direct
  facade I/O — the only facade path is through `_resolve_demographic_view`.

- **update** (`planet_list_window.py:527-558`): Scrollbar refresh, slider text
  sync, header sort/swap, preset dropdown polling. No facade I/O. Correct.

- **kill** (`planet_list_window.py:720-739`): Cleans up VirtualTable,
  planet_detail_panel, buttons, fires `on_close_callback` (line 737-738)
  before `super().kill()` (line 739). Correct ordering.

**OBSERVATION** — `planet_list_window.py:424,618-625`, `planet_list_controller.py:42-45`
The Navigate button event handler at line 424 calls `self._navigate_to_selected()`,
which at line 625 calls `self.on_navigate_callback(loc)` directly — it does NOT
route through `self.controller.navigate_to(location)`. The controller's
`navigate_to` method is defined (planet_list_controller.py:42-45) but never
called from the window. Dead code in the controller.

---

## Controller Boundary (PlanetAbilitiesController)

### Owns facade queries + command dispatch

**PASS** — `planet_abilities_controller.py:55-208`

The controller owns five query methods (all read-only, no widget construction)
and one command-dispatch method (`toggle_ability` → `facade.handle_command`).

### Does NOT own widget construction

**PASS** — `planet_abilities_controller.py`

Zero imports from `pygame_gui`. Zero references to UIButton, UILabel, or any
widget class. All widget construction lives in `PlanetAbilitiesUiBuilder`
(`planet_abilities_window.py:37-153`).

### Facade calls isolated in controller

**PASS** — `planet_abilities_window.py:249-270`

The window's `process_event` calls `self.controller.toggle_ability()` (line 250)
and `self.controller.get_component_status()` (line 267) — both well-isolated.
The window's `__init__` never calls any facade method (only stores the facade
reference at line 201).

### Window __init__ does not call facade methods

**PASS** — `planet_abilities_window.py:199-228`

Stage 1 lines are all attribute assignments. No method calls on `self.facade`.

---

## CargoQuickDialog — Light-Touch Verification

### Two-stage construction

**PASS** — `cargo_quick_dialog.py:228-258`

- Stage 1 (lines 229-243): fleet, hex_coord, direction, scene, `scene.facade`
  (property read — no facade I/O call; correctly called out in the comment at
  line 233-235), _mapper, cargo_items (list), controller. All before
  `super().__init__` (line 247).
- Stage 2 (lines 247-250): `super().__init__` with window_display_title and
  window_manager.
- Stage 3 (lines 253-258): `_window_init_bypassed` guard → `ui_builder.build()`
  or default `CargoQuickDialogUiBuilder().build()`.

Matches the canonical pattern.

### Controller wraps facade calls without breaking existing tests

**PASS** — `cargo_quick_dialog_controller.py:35-111`

All facade I/O is in the controller:
- `get_unload_items` (line 43) → `CargoTransferService.resolve_colonies` +
  `CargoTransferService.get_unload_items`
- `get_load_items` (line 51) → same pattern
- `issue_orders` (line 69) → `CargoTransferService.build_transfer_command` +
  `self.facade.handle_command(cmd)`

`issue_orders` at line 69 iterates `cargo_items`, reads `item['slider']`
(`pygame_gui` widget reference passed from the dialog's own list), builds
commands, and dispatches them. The controller touches the slider widget only
to read its current value (`item['slider'].get_current_value()` at line 78) —
which is a pragmatic data-access pattern that does not constitute widget
construction. This matches how the original inline code accessed slider values
before the refactor.

The test fixture at `tests/fixtures/cargo_quick_dialog_ui_builder.py` provides
`MockCargoQuickDialogUiBuilder` that populates widget slots with MagicMocks.
Tests using `bypass_init` + this mock builder will not invoke the real
controller's facade methods. Tests using real `pygame_gui` UIManager +
production `__init__` go through the normal (non-bypassed) path and exercise
the real controller. Both paths coexist without conflict.

### bypass_init path is present and correct

**PASS** — `cargo_quick_dialog.py:253-256`

The guard checks `getattr(self, '_window_init_bypassed', False)`, then calls
the provided `ui_builder.build(self)` if non-None. The
`MockCargoQuickDialogUiBuilder` at `tests/fixtures/cargo_quick_dialog_ui_builder.py:48-77`
verifies Stage 1 attrs exist (`cargo_items`, `fleet`, `direction`) before
populating widget slots — confirming the bypass path works end-to-end.

---

## PlanetListWindow — Legacy Fallback Analysis

### Equivalence of controller path vs legacy fallback

**PASS** — `planet_list_window.py:687-701`

Both paths produce identical results for all input cases:

| Input condition | Controller path | Legacy fallback |
|---|---|---|
| `planet.owner_id is None` | `None` | `None` |
| `facade is None` (either ref) | `None` | `None` |
| Normal colonized planet | `facade.get_colony_demographic_view(planet.id)` | `facade.get_colony_demographic_view(planet.id)` |

The facade references — `self.facade` (controller attribute) and `self._facade`
(window attribute) — are the same object in every production code path (both
bound from the same constructor parameter). In tests with mock controllers, the
divergence is intentional (the mock controller's facade is the test-controlled
facade).

### Fallback necessity

**PASS** — The fallback is necessary. `planet_list_window.py:690-693` documents
that tests may construct the window via `__new__` without running `__init__`,
leaving `controller` unset. In that scenario `getattr(self, 'controller', None)`
returns `None` and the legacy path correctly uses `self._facade` (which was set
manually). Under bypass_init, the controller *is* constructed (Stage 1 runs),
so the `controller` path fires — also correct, and equivalent.

### Potential subtlety

**OBSERVATION** — `planet_list_window.py:307-310`, `planet_list_controller.py:31-33`
The controller stores `on_navigate_callback` at construction time but the
window *never* calls `controller.navigate_to(location)` — it calls
`self.on_navigate_callback(loc)` directly at line 625. If a test passes a
custom controller with a different `on_navigate_callback` from the window's
own, the window would bypass the controller's callback. However, the default
controller construction at line 308 uses the same `on_navigate_callback`
parameter, so production behavior is correct. The custom-controller override
case (`controller=my_controller`) would need the test author to also handle
the navigate callback independently — this is a design choice for the test
seam, not a behavioral regression.
