# Phase 2: Major — Pattern #2 / #10 / #31 + naming collision + convention cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-382 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Tighten the major pattern erosions identified in the audit: one Pattern #2 TypeGuard miss, four Pattern #10 dual-path event-logging blocks, one Pattern #31 modal-window base-class miss, the long-standing `EventBus` naming collision, the hardcoded superweapon list that duplicates the registry, and an empty package `__init__.py`.

---

## Tasks

### Task 2.1: Replace `isinstance(obj, Planet)` with `is_planet()` TypeGuard
**File:** `game/strategy/data/galaxy_spatial_index.py`
**Pattern:** #2 (Protocol + TypeGuard)
**Tests:** `pytest tests/ -k galaxy_spatial_index --testmon`

- [ ] Drop the `from game.strategy.data.planet import Planet` import; add `from game.core.protocols import is_planet` instead (TypeGuard lives at `game/core/protocols/strategy_entities.py:424`).
- [ ] At line 37: replace `isinstance(obj, Planet)` with `is_planet(obj)`.
- [ ] Verify: existing tests pass; the module no longer pulls a concrete strategy data class for runtime narrowing.

### Task 2.2: Collapse dual-path event logging in `Empire`
**File:** `game/strategy/data/empire.py`
**Pattern:** #10 (Event Bus)
**Tests:** `pytest tests/ -k empire --testmon`

- [ ] At lines 107-127, remove the `if event_bus: ... else: log_event(...)` fallback block; emit only via the injected `event_bus`.
- [ ] If callers exist that legitimately have no `event_bus`, identify them and inject one rather than restoring the fallback.
- [ ] Verify: empire-event tests pass; no regressions in event-log UI surface.

### Task 2.3: Collapse dual-path event logging in `Fleet`
**File:** `game/strategy/data/fleet.py`
**Pattern:** #10 (Event Bus)
**Tests:** `pytest tests/ -k fleet --testmon`

- [ ] At lines 408-427 (first emission block), remove the `if event_bus: ... else: log_event(...)` fallback.
- [ ] At lines 437-454 (second emission block), remove the same fallback.
- [ ] Verify: fleet event-emission tests pass; manual end-turn smoke shows event log entries still produced.

### Task 2.4: Inject `EventBus` into `projectile.py` (remove module-level shim usage)
**File:** `game/simulation/entities/projectile.py`
**Pattern:** #10 (Event Bus)
**Tests:** `pytest tests/ -k "projectile or seeker" --testmon`

- [ ] Remove `from game.core.event_logging import log_event` import.
- [ ] Pass an `EventBus` (or compatible callable) into the projectile lifecycle so the `log_event(...)` calls at lines 97 and 116 dispatch through the injected bus rather than the module-level shim.
- [ ] Verify: SEEKER-* simulation tests still record `SEEKER_EXPIRE` events; projectile spawn/expire events still appear in the event log.

### Task 2.5: Convert `DesignSelectorWindow` to subclass `StrategyModalWindow`
**File:** `game/ui/screens/design_selector_window.py`
**Pattern:** #31 (Strategy Modal Window Base Class)
**Tests:** `pytest tests/ -k design_selector --testmon`

- [ ] At line 45, change `class DesignSelectorWindow(UIWindow):` → `class DesignSelectorWindow(StrategyModalWindow):`.
- [ ] Add the required `window_manager` keyword argument to `__init__` per Pattern #31's signature.
- [ ] Confirm `StrategyEventRouter.has_modal_open()` correctly observes the window during click-handling.
- [ ] Verify: open/close/click-blocking smoke; existing `_registered_subclasses` set in `StrategyWindowManager` includes `DesignSelectorWindow`.

### Task 2.6: Replace hardcoded `_SUPERWEAPON_ABILITIES` with iteration over `SUPERWEAPONS` registry
**File:** `game/ui/screens/builder/stat_getters.py`
**Pattern:** Convention §6.5 "No Hardcoded Type Lists"
**Tests:** `pytest tests/ -k "stat_getters or workshop" --testmon`

- [ ] At lines 288-291: replace the literal `_SUPERWEAPON_ABILITIES = ['DestroyPlanet', ...]` list with an iteration deriving the names from `SUPERWEAPONS` at `game/strategy/services/superweapon_registry.py` (filter out entries whose `ability_name is None`, e.g. `STELLERATE_STAR`).
- [ ] At lines 293-300: derive `_SUPERWEAPON_LABELS` from `SuperweaponSpec.display_name` (or whichever field carries the user-visible name).
- [ ] Verify: builder UI shows the same superweapon entries it did before; no labels lost.

### Task 2.7: Resolve `EventBus` naming collision — rename builder variant to `WorkshopEventBus`
**File:** `game/ui/screens/builder/event_bus.py` (+ ~15 importers)
**Pattern:** #10 (Event Bus) / Pattern #6 naming hygiene
**Tests:** `pytest tests/ -k "workshop or builder or build_queue" --testmon`

- [ ] Rename the class at `game/ui/screens/builder/event_bus.py:12` from `EventBus` → `WorkshopEventBus`.
- [ ] Update every importer named in the cross-shard report: `workshop_screen.py`, `weapons_viewmodel.py`, `weapons_panel.py`, `test_lab/screen.py`, `empire_build_queue_window.py`, `empire_build_queue_viewmodel.py`, `empire_build_queue_sidebar.py`, `build_queue_viewmodel.py` (search for `from game.ui.screens.builder.event_bus import EventBus` and `from game.ui.screens.builder import event_bus`).
- [ ] Verify: workshop pub/sub smoke; build-queue UI still receives events; no remaining `EventBus` import resolves to the workshop variant under that name.

### Task 2.8: Empty `simulation/components/__init__.py` — add canonical re-exports or delete
**File:** `game/simulation/components/__init__.py`
**Pattern:** Convention — package `__init__.py` either re-exports or is removed
**Tests:** `pytest tests/ -k components --testmon`

- [ ] Inspect external consumers — does anyone do `from game.simulation.components import X`? If yes: add canonical re-exports for those names. If no: leave the file empty intentionally and add a single-line comment documenting it as a namespace marker.
- [ ] Verify: package imports still work; no circular-import regressions introduced.

### Task 2.9: Phase verification
**File:** N/A
**Pattern:** #2/#10/#31
**Tests:** Full suite

- [ ] `pytest tests/ --testmon` passes.
- [ ] Sharded baseline holds.
- [ ] Re-run pattern audit — Pattern #2 / #10 / #31 violation counts for the cited sites all drop to 0; `EventBus` naming collision no longer flagged.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220452_pattern-audit/`. See `findings/source_audit.md` for the link._
