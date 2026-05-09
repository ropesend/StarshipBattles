# Phase 3: Minor — CQRS / Pattern #7 / Pattern #12 fixes + doc drift

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-382 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Apply the minor cleanups: remove the CQRS-lite tautology guard, route the legacy `BaseCommandHandler` import through the canonical handler module, replace bare `json` usage with `json_utils` in three files plus drop one unused import, tighten `ProductionSpawner.registries` to required, and reconcile two pattern doc-drift entries (Pattern #23, Pattern #7).

---

## Tasks

### Task 3.1: Remove tautology guard in `GameSession.handle_command`
**File:** `game/strategy/engine/game_session.py`
**Pattern:** #6 (CQRS-lite Strategy Session)
**Tests:** `pytest tests/ -k "game_session or command_dispatch" --testmon`

- [x] At lines 343-355: drop the `if command.type == command.type.ISSUE_ORDER:` branch. All `Command` DTOs set `type = CommandType.ISSUE_ORDER` in `__post_init__`, so the guard is unreachable.
- [x] Replace with unconditional `return self._command_registry.dispatch(command.name, self, command)`.
- [x] Verify: command dispatch tests still pass.

### Task 3.2: Re-route `BaseCommandHandler` import to canonical path
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Pattern:** #7 (CommandHandlerRegistry)
**Tests:** `pytest tests/ -k "superweapon and command" --testmon`

- [x] At line 15, change `from game.strategy.engine.command_handlers import BaseCommandHandler, add_move_order_if_needed` to import from the canonical module: `from game.strategy.engine.handlers.base import BaseCommandHandler` (and locate the canonical home of `add_move_order_if_needed`, which may live elsewhere).
- [x] Verify: superweapon command handler tests still pass.

### Task 3.3: Replace bare `json` with `json_utils` (Pattern #12) — three files
**File:** `game/strategy/systems/race_library.py`, `game/ui/screens/builder/detail_panel.py`, `game/strategy/data/galaxy_warp_generator.py`
**Pattern:** #12 (Configuration Classes)
**Tests:** `pytest tests/ -k "race_library or workshop or galaxy_warp" --testmon`

- [x] `race_library.py:14`: replace `import json` + every `json.dump(...)`/`json.dumps(...)`/`json.loads(...)` with the appropriate `game.core.json_utils` helper (`save_json`, `load_json`, etc.).
- [x] `builder/detail_panel.py:11`: replace `import json` + `json.dumps(...)` calls with `json_utils.dumps` (or whichever helper exists; if `json_utils` lacks a `dumps` equivalent, leave a single-line note in the file recording why bare json is preserved).
- [x] `galaxy_warp_generator.py:366-369`: replace the inline `json.load(path.open(...))` with `load_json(str(path), default={})` from `game.core.json_utils`. Drop the `import json` if it has no other use after the replacement.
- [x] Verify: race library round-trip serialization, workshop detail panel rendering, and warp-point generation tests all pass.

### Task 3.4: Remove unused `import json` in `setup_data_io.py`
**File:** `game/ui/screens/setup_data_io.py`
**Pattern:** #12 (Configuration Classes)
**Tests:** `pytest tests/ -k setup_data_io --testmon`

- [x] Delete the unused `import json` at line 15. The module already imports `load_json` / `load_json_required` / `save_json` from `game.core.json_utils` for all JSON operations.
- [x] Verify: module imports cleanly; no test regressions.

### Task 3.5: Tighten `ProductionSpawner.registries` to required (Pattern #3, strategy-layer)
**File:** `game/strategy/engine/production_spawner.py`
**Pattern:** #3 (Registry DI)
**Tests:** `pytest tests/ -k production_spawner --testmon`

- [x] At line 36: change `registries: Optional['GameRegistries'] = None` → `registries: 'GameRegistries'` (required).
- [x] Convert `_get_planet_mutator()` (lines 51-57) lazy-fallback into eager constructor injection: accept a `planet_mutator` parameter or build it from `registries` in `__init__`.
- [x] Update every call site that constructs `ProductionSpawner` to pass `registries=` explicitly. Use grep across `game/` for `ProductionSpawner(` to find them.
- [x] Verify: production-spawn tests pass; turn engine still constructs the spawner cleanly via `TurnEngineConfig.create_default(registries=...)`.

### Task 3.6: Reconcile Pattern #23 (Tick Phase Registry) doc drift
**File:** `docs/02_PATTERNS.md`
**Pattern:** #23 (Tick Phase Registry)
**Tests:** N/A (doc-only)

- [x] Find Pattern #23 entry. Update the default-phases table from 5 entries to 6: `RebuildGridPhase(100)`, `AIAndShipUpdatePhase(200)`, `BoundaryEnforcementPhase(250)`, `AttackProcessingPhase(300)`, `RammingPhase(400)`, `ProjectileUpdatePhase(500)`. Add the missing `Phase` suffix to every name.
- [x] Update the `> **Last verified:**` blockquote timestamp to today's date.
- [x] Verify: doc reads correctly; phase priorities match `game/simulation/systems/tick_phase.py::create_default_phases()`.

### Task 3.7: Reconcile Pattern #7 (CommandHandlerRegistry) doc drift
**File:** `docs/02_PATTERNS.md`
**Pattern:** #7 (CommandHandlerRegistry)
**Tests:** N/A (doc-only)

- [x] Find Pattern #7 entry. Change the canonical-location reference from `game/strategy/engine/command_handlers.py` to `game/strategy/engine/handlers/base.py`. Note that `command_handlers.py` is a transitional re-export shim.
- [x] Update the `> **Last verified:**` timestamp.
- [x] Verify: doc lines up with the actual `class CommandHandlerRegistry` definition site at `handlers/base.py:399`.

### Task 3.8: Phase verification
**File:** N/A
**Pattern:** #6/#7/#12/#3/#23
**Tests:** Full suite

- [x] `pytest tests/ --testmon` passes.
- [x] Sharded baseline holds.
- [x] Re-run pattern audit — Pattern #6 tautology, Pattern #7 doc-drift, Pattern #12 bare-json, Pattern #23 doc-drift counts all drop to 0 (or as expected).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220452_pattern-audit/`. See `findings/source_audit.md` for the link._
