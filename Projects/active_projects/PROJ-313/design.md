# PROJ-313: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### The bug class being eradicated

Four historical bugs all stem from the same architectural fragility:
- **BUG-22** — `planet_list_window` originally absent from the modal-tracking scan.
- **BUG-69** — `fleet_orders_window` / `fleet_report_window` / `transfer_dialog` close handlers wired up incorrectly.
- **BUG-121** — `planet_abilities_window` slot leaked stale references after close, permanently breaking strategy-screen mouse-wheel zoom for the rest of the session.
- **BUG-122-foodallocation** (QA Session 20260428_052952) — Organics Allocation window is not tracked at all; clicks pass through to the galaxy map.

### The 6-step manual contract that keeps failing

Every new modal window must:
1. Add `Optional[UIWindow] = None` slot field to `StrategyWindowManager`.
2. Add the slot to `StrategyEventRouter.has_modal_open()` (`is not None` check).
3. Add the slot to `StrategyEventRouter._is_blocking_ui_element_at()` (`.alive() and rect.collidepoint(point)` check).
4. Override `kill()` on the window class to invoke `on_close_callback` before `super().kill()`.
5. Wire `on_close_callback` at the spawn site (registrar).
6. Implement registrar `_on_closed` method that resets the slot to `None`.

Forgetting steps 1-3 → click-through (clicks pass to map). Forgetting steps 4-6 → BUG-121-class stale-flag leak.

### Asymmetric checks

- `has_modal_open()` uses `is not None`.
- `_is_blocking_ui_element_at()` uses `.alive() and rect.collidepoint(...)`.

This asymmetry is what produced BUG-121: clicks kept working (the `.alive()` path filtered the dead reference) but scroll did not (the `is not None` path saw the stale reference and short-circuited).

### Two parallel cleanup mechanisms

- **Mechanism 1 — `_handle_window_close`** at `game/ui/screens/strategy_event_router.py:413-446` listens for `pygame_gui.UI_WINDOW_CLOSE`, then runs an O(N) `if/elif` chain matching `event.ui_element` against tracked slots.
- **Mechanism 2 — Registrar Close-Callback** (Pattern #30, BUG-121) — `Window.kill()` invokes `on_close_callback` before `super().kill()`. The callback resets the slot directly. Synchronous and idempotent.

Six tracked windows currently use Mechanism 1 only; five use Mechanism 2 only; four use both. The mixed approach makes audits expensive and contract drift easy.

### Untracked editors

Five editor windows are spawned over the strategy screen but have **no slot**, **no `has_modal_open()` clause**, **no `_is_blocking_ui_element_at()` clause**:
- `FoodAllocationEditor` — confirmed click-through reproducible
- `AtmosphereTargetEditor`
- `GravityTargetEditor`
- `WaterTargetEditor`
- `RadiationShieldEditor`

All five already accept `on_close_callback` in their constructor — the lifecycle slot is already pre-wired; just nobody owns the slot.

## Swarm Findings Summary

Combined analysis from three Phase 1 Explore agents and one Phase 2 Plan agent. Full reports preserved in conversation transcript.

### Architecture

The migration introduces no new layer dependencies. `StrategyModalWindow` and the new `StrategyWindowManager` API live in `game/ui/screens/`, the existing UI-layer location. UI is allowed to depend on everything below it (per `docs/01_ARCHITECTURE.md`); the refactor is internal to UI.

pygame_gui's `UIWindow.kill()` (verified at `.venv/Lib/site-packages/pygame_gui/elements/ui_window.py:549-575`) is the universal funnel: every kill path posts `UI_WINDOW_CLOSE` and calls `super().kill()` to flip `.alive()` to False. Title-bar `[X]` button → `kill()`. Programmatic kill → `kill()`. Parent kill via `_window_root_container.kill()` → child sprites die without going through their own `kill()` override (parent-cascade caveat — handled by the `iter_live_modals()` GC walk).

### Key Patterns to Reuse

- **`__init_subclass__` hook** — populates a class-level registry at class definition time. More reliable than `__subclasses__()` (which depends on import order and only finds loaded classes).
- **`PlanetAbilitiesWindow.kill()`** at `game/ui/screens/planet_abilities_window.py:100-103` — current best-practice example to model the new base class's kill ordering on (callback before super, idempotent via `try/finally`).
- **`PlanetAbilitiesRegistrar._on_closed`** at `game/ui/screens/strategy_windows/planet_abilities_ctrl.py:50-55` — current example of slot-clearing logic; this is what the base class subsumes.
- **The parametrised contract test idiom** at `tests/unit/ui/screens/test_strategy_window_manager_public_api.py::TestModalSlotCleanupContract` — kept structurally but parametrisation source changes from a hardcoded slot allowlist to `StrategyModalWindow._registered_subclasses`.

### Dependencies & Risks

1. **Parent-kill cascade orphans.** If a `StrategyModalWindow` were ever a child of another `UIWindow` and the parent is killed first, pygame_gui kills children via `_window_root_container.kill()` *without* calling each child window's overridden `kill()`. Mitigation: `iter_live_modals()` GC-walks dead refs via `.alive()` filter on every iteration. Unit test pins the invariant. Not a current code path (modals are top-level) but cheap insurance.
2. **Phase 7 behaviour change.** Migrating the 5 untracked editors newly returns `has_modal_open() == True` while open. Mitigation: audit usages of `has_modal_open()` before Phase 7; document any consumer that relied on the previous (incorrect) `False` reading.
3. **Multiple `StrategyWindowManager` instances in tests.** `_modals` is instance state, not class state — per-manager isolation works correctly. The `__init_subclass__` registry is class-level (correct — it tracks classes, not instances).
4. **Modal-within-modal stacking.** `iter_live_modals` yields insertion order, not z-order. `has_modal_open` (any-True semantics) and `_is_blocking_ui_element_at` (any-hit semantics) are correct under insertion order. Documented as a constraint; future "topmost wins" features must add z-order awareness explicitly.
5. **Migration regression risk.** Each phase commit must keep 15893 tests passing. Mitigation: dual-track migration with router OR-bridge (Phase 2 introduces, Phase 8 removes). At every commit each window is on exactly one track, never both.
6. **`_pending_confirmation_dialog` asymmetry pre-dates this refactor.** Out of scope per user direction (a separate ticket).
7. **`is_blocking` flag on pygame_gui's UIWindow** controls mouse events inside the window but does NOT affect router-level event dispatch routing. Don't conflate; the strategy-side modal block must remain the source of truth.

### Opportunities Discovered

- **Test contract simplification.** Replacing the source-string-matching parametrised contract test with a structural-invariant test reduces both test count and maintenance burden. The new test instantiates each `StrategyModalWindow` subclass with a stub manager, asserts membership in `iter_live_modals()`, calls `kill()`, asserts removal — pure behaviour, no source introspection.
- **Static guard.** A second test grep-asserts that no class in `game/ui/screens/strategy_windows/` or modal-relevant `game/ui/screens/*.py` directly subclasses `pygame_gui.UIWindow` unless it's in an explicit non-modal allowlist (currently just `SettingsWindow`). Catches the "new dev forgot to subclass" case at CI time.
- **Pattern #30 retirement.** `docs/02_PATTERNS.md` §30 ("Registrar Close-Callback") becomes a historical artifact; the new pattern entry describes structural enforcement via base class. Adds a worked example for future similar refactors.
- **Per-window blocking tests for Phase 7.** Each editor migration ships with a focused regression test that opens the editor, simulates a click at strategy-map hex coordinates, and asserts the underlying map's selection did not change. Failed before, passes after.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale. Highlights:
- **Option A (base class) over Option B (registry helper) and Option C (pygame_gui native modal flag)** — only Option A makes the contract structurally unforgettable.
- **Migration via dual-track router OR-bridge** — single-PR big-bang risks un-bisectable regression; permanent shim violates Rule 3; OR-bridge during in-flight migration is allowed scaffolding.
- **`settings_window` stays as direct slot, no flag** — a `non_modal=True` flag would invert the "subclassing == modal" contract and re-introduce the manual-discipline failure mode.
- **`move_choice_window` promoted to a named subclass** — eliminates a per-window special case; brings move-choice fully under the structural contract.
- **`_handle_window_close` deleted entirely in Phase 8** — keeping it as belt-and-suspenders is a Rule-3 violation and silently absorbs future bugs.
- **Editor scope: included in PROJ-313** — closes the bug class structurally rather than leaving 5 latent click-throughs for a follow-up.
- **`_pending_confirmation_dialog` asymmetry: out of scope** — different lifecycle (UIConfirmationDialog is pygame_gui stock); separate ticket.
