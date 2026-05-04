# PROJ-325 PoC Findings — 4 pattern refinements discovered during RaceSetupScreen refactor

**Date:** 2026-05-04 (extracted 2026-05-04 audit-remediation S1.7 — backported here from `Projects/active_projects/PROJ-328/phase_1_checklist.md` so future readers of PROJ-325 don't miss them)

The PROJ-325 Phase 3 PoC (RaceSetupScreen two-stage refactor, commit `92a7490b6`) discovered 4 refinements to the headline pattern from the original Codex–Claude consensus refactor plan (`findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`). All 4 were applied verbatim to PROJ-328 Phases A/B/C and remain authoritative for any future UIWindow-subclass refactor.

---

## Finding 1 — `self.rect` is a `pygame_gui` descriptor on UIWindow subclasses

**Symptom:** the headline pattern wrote `self.rect = rect` in the bypass branch. This raises an exception inside the bypass path because `pygame_gui`'s `GUISprite` base class makes `rect` a descriptor that mutates `self.blit_data` on write — and `blit_data` is initialized only by the `pygame.sprite.Sprite.__init__` chain that `bypass_init` deliberately skips.

**Root cause:** `pygame.sprite.Sprite` lazy-allocates `blit_data` only inside its own `__init__`. Skipping that init via the `bypass_init` guard leaves `self.blit_data` unbound, which the `rect` descriptor's setter then fails to access.

**Workaround:**
- **PoC chose:** drop the `self.rect = rect` assignment in the bypass branch entirely. Works because no test in the suite reads `screen.rect` against a bypassed instance.
- **Alternative (if a test ever does need `rect`):** `object.__setattr__(self, 'rect', rect)` bypasses the descriptor. Carries its own risks because the Sprite machinery later assumes the descriptor was used; only reach for this if the simpler "drop the assignment" path doesn't suffice.

**Canonical implementation:** [`game/ui/screens/race_setup/screen.py`](../../../../game/ui/screens/race_setup/screen.py) — see the bypass branch in `__init__` (no `self.rect = rect` line). Same pattern in `game/ui/screens/strategy_modal_window.py` Task A.1 base shell update.

---

## Finding 2 — Bypass branch must invoke `ui_builder.build(self)` when one is explicitly supplied

**Symptom:** the consensus headline pattern returned from the bypass branch immediately. With this shape, `Mock{Foo}UiBuilder` instances passed by tests would never run — and the whole point of having a Mock builder is to let tests populate widget slots without the real shell.

**Root cause:** `Mock{Foo}UiBuilder` exists to fill widget-reference attributes (`screen.btn_save`, `screen.step_panels`, etc.) that the production `_create_ui()` would have filled. If the bypass returns before invoking the builder, every test still has to wire those slots by hand — defeating the purpose of the builder pair.

**Workaround:** invoke the builder when (and only when) one was explicitly supplied:

```python
if getattr(type(self), 'bypass_init', False):
    self.ui_manager = manager
    self._window_init_bypassed = True
    if ui_builder is not None:  # PoC finding 2
        ui_builder.build(self)
    return
```

When `ui_builder is None`, the bypass branch stays a no-op — placeholders set by `_init_widget_refs()` remain `None` / empty.

**Canonical implementation:** [`game/ui/screens/race_setup/screen.py`](../../../../game/ui/screens/race_setup/screen.py) bypass branch. Phase A modal classes (BuildQueueListWindow, OrdersWindow, FleetReportWindow) use the same pattern through their `_window_init_bypassed` check after `super().__init__()`.

---

## Finding 3 — Mirror delegate refs to legacy attribute names

**Symptom:** existing tests read delegate attributes directly via legacy names (`screen._view_model`, `screen._renderer`, `screen._controller`, etc.). Renaming them to namespaced names (`screen._delegates.view_model`) during the refactor would have broken hundreds of test sites.

**Root cause:** the back-compat surface that production code AND tests both depend on is the per-attribute name, not the bundle. Existing callers in `_create_ui()`, event handlers, and tests all assume `self._view_model` is a direct attribute, not a path through a bundle.

**Workaround:** after building the bundle, mirror each delegate to its legacy attribute name:

```python
self._delegates = (delegate_factory or DefaultRaceSetupDelegateFactory()).build(self)
# Mirror to legacy attribute names for back-compat:
self._view_model = self._delegates.view_model
self._renderer = self._delegates.renderer
self._controller = self._delegates.controller
# ... etc
```

**Don't** try to migrate callers to the namespaced form in the same pass — that's a separate refactor with its own risk surface. The mirror is cheap (~5 lines per class) and preserves the test surface 1:1.

**Canonical implementation:** [`game/ui/screens/race_setup/screen.py`](../../../../game/ui/screens/race_setup/screen.py) — see the delegate-mirror block immediately after the factory call.

---

## Finding 4 — Look for renderer-internal widget reach-throughs

**Symptom:** during PoC implementation, several tests were observed reaching into the renderer's widget tree (e.g., `screen._renderer.save_update_dialog`) to assert on widget state. Those reach-throughs survive the refactor IF the `MockUiBuilder` reproduces them.

**Root cause:** the production `_create_ui()` flow constructs widgets and assigns them to renderer-internal attributes as a side effect, not just to the screen instance. Tests that exercise dialogs, popups, or modal sub-widgets often grabs these via the renderer rather than the screen.

**Workaround:** before refactoring each test file, grep for `screen._renderer.<attr>` (and equivalent reach-throughs through any other delegate) and record the full set of attributes the test relies on. The `MockUiBuilder` then explicitly writes those attributes onto the renderer (Stage 1 has already constructed the real `RaceSetupRenderer` instance, so the writes land on a real object):

```python
class MockRaceSetupUiBuilder:
    def build(self, screen):
        # Standard widget slots
        screen.btn_save = MagicMock()
        screen.btn_load = MagicMock()
        # ...
        # Renderer-internal reach-throughs (PoC finding 4):
        screen._renderer.save_update_dialog = MagicMock()
        # ... and any other renderer attributes tests touch
```

**Canonical implementation:** [`tests/fixtures/race_setup_ui_builders.py`](../../../../tests/fixtures/race_setup_ui_builders.py) — see the `MockRaceSetupUiBuilder.build()` method for the full set of renderer reach-throughs.

---

## Why these findings live here AND in PROJ-328

These 4 findings were originally only documented in [`Projects/active_projects/PROJ-328/phase_1_checklist.md`](../../PROJ-328/phase_1_checklist.md) (lines 27-37) because PROJ-328 Phase A was the first downstream consumer that needed them. The original PROJ-325 design.md captured the consensus plan (which they refine) but not the refinements themselves.

Future agents reading PROJ-325 to learn the canonical pattern need these findings — without them, applying the consensus plan headline verbatim would re-discover all 4 issues from scratch. PROJ-325 audit-remediation S1.7 (2026-05-04) backported them here as a dedicated findings file.

The PROJ-328 phase_1_checklist.md copy is preserved verbatim for historical context; this file is the authoritative reference for any future UIWindow-subclass refactor that uses the two-stage construction pattern.

## See also

- [`design.md`](../design.md) — high-level design + GO/NO-GO decision tree
- [`findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`](consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md) — original plan these findings refine
- [`Projects/active_projects/PROJ-328/phase_1_checklist.md`](../../PROJ-328/phase_1_checklist.md) — original location (preserved)
- `docs/02_PATTERNS.md` §32 (Compositional Construction) + §33 (UI Widget Test Factory) — canonical pattern docs
