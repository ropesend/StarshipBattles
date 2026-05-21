# Cross-Layer Error Propagation Report

## Summary
- Error Boundaries Mapped: 10
- Critical Paths Traced: 4
- Total Findings: 8
- Critical: 1 | Major: 3 | Minor: 4

---

## Error Boundary Audit

### Boundary 1: Simulation → Strategy (`simulation_adapter.py`)
**File:** `game/strategy/adapters/simulation_adapter.py:316-341`
**Summary:** `SimulationBattleResolver._run_simulated_battle()` catches `SimulationException` and `ValidationException` from `run_battle()`, wraps as `BattleResolutionError` with fleet_ids, empire_ids, hex_coord, and preserves chaining via `from e`.
**Verdict:** PASS — Correct domain-specific wrapping with full battle context. One gap: only `SimulationException`/`ValidationException` are caught; any other exception from `run_battle` (e.g., `RuntimeError`, `KeyError`) bypasses this wrapper and surfaces as a raw exception. The TurnEngine `_time_phase()` will catch it, but without battle-specific context. (See MINOR-3.)

### Boundary 2: Turn Engine Phase Boundary (`turn_engine.py`)
**File:** `game/strategy/engine/turn_engine.py:286-335`
**Summary:** `_time_phase()` wraps any non-`EnginePhaseError` exception as `EnginePhaseError(T001)` with `phase_name`, `tick`, `turn_number`, `save_path`, `original_error`, `original_type`. `process_turn()` catches `EnginePhaseError`, writes crash snapshot, restores state from snapshot, invalidates caches, and re-raises.
**Verdict:** PASS — Fail-fast with snapshot rollback is well-executed. Context is rich for diagnostics. Broad-catch comment is justified per docs/05_ERROR_HANDLING.md.

### Boundary 3: Strategy → Facade (`strategy_session_facade.py`)
**File:** `game/strategy/facade/strategy_session_facade.py:215-252`
**Summary:** `process_turn()` catches `EnginePhaseError`, re-raises as `TurnFailedError` with context copied from the original via `dict(e.context or {})` and `from e` chaining. Properties on `TurnFailedError` tolerate missing context keys with sentinel values.
**Verdict:** PASS — Clean conversion with preserved context. The `PROJ-409 MAJ-014` secondary `except EnginePhaseError` block was correctly removed per CLAUDE.md Rule 4.

### Boundary 4: Facade → UI (`strategy_game_state_manager.py`)
**File:** `game/ui/screens/strategy_game_state_manager.py:352-380`
**Summary:** `process_full_turn()` catches `TurnFailedError`, logs the failure, and surfaces a `TurnFailedDialog` (a `StrategyModalWindow` subclass registered with `StrategyWindowManager` for input-blocking per Pattern #31). The UI never sees a domain-engine exception type.
**Verdict:** PASS — Proper modal UX with input blocking. Falls back to `StrategyGameStateManager._show_turn_failed_dialog()` which reads `phase_name`, `tick`, `turn_number`, `original_type` from context with sentinel fallbacks.

### Boundary 5: GameSession Initialization → Strategy (bootstrap)
**File:** `game/strategy/engine/session/bootstrap.py:263-278`
**Summary:** `SessionBootstrap.new_game_state()` catches `Exception` from `GameInitializer.initialize()`, logs, and re-raises as `SessionInitializationError` with `original_type` context and `from e` chaining. `GameSession.__init__()` catches `SessionInitializationError`, sets deterministic null-object state (galaxy=None, empires=[]), and re-raises.
**Verdict:** PASS — Null-object substitution preserves the invariant that a session is never partially constructed. The caller (UI layer) must catch `SessionInitializationError` to surface a user-facing error. (See CRITICAL-1.)

### Boundary 6: AssetManager → UI (`asset_manager.py`)
**File:** `game/assets/asset_manager.py:69-92, 265-337`
**Summary:** `load_image()` catches `FileNotFoundError` and `pygame.error`, returns missing texture. `load_planet_image()` catches `(FileNotFoundError, pygame.error, ValueError)` across a resolution fallback chain, returns missing texture on exhaustion. `load_star_image()` catches `(FileNotFoundError, pygame.error, ValueError, OSError)` — an extra `OSError` not present in the planet path. All methods degrade gracefully for non-critical assets.
**Verdict:** PASS with note — Graceful degradation is correct for optional assets. The `OSError` asymmetry between planet and star loading is noted as MINOR-4.

### Boundary 7: LLM Provider → Service (`deepseek.py`)
**File:** `game/services/llm/deepseek.py:84-237`
**Summary:** `DeepSeekProvider.complete()` maps every HTTP status code and network error to a specific `LLMException` subclass. Security: API key read per-request, redacted in repr, never in context. Retry policy: 5xx only with exponential backoff; 429 never retried. Timeout, SSL, and cancellation all handled. Context always safe (provider, model, status_code, attempt, latency).
**Verdict:** PASS — Exemplary provider error mapping. All documented contracts satisfied.

### Boundary 8: LLM Background Call → Consumer (`background.py`)
**File:** `game/services/llm/background.py:248-337`
**Summary:** `LLMBackgroundCall._run()` catches `LLMCancelled` (→CANCELLED), `LLMException` (→ERROR), and broad `Exception` (→LLMUnexpectedError→ERROR). All terminal branches set `_finished_at` and release the in-flight slot under `_in_flight_lock`. The outer `finally` sets `_done_event` outside all locks for deterministic `wait()` unblocking.
**Verdict:** PASS — Worker-thread error containment is thorough. `LLMUnexpectedError` correctly prevents the `_status=RUNNING` lockup that PROJ-321..328 fixed.

### Boundary 9: Image Background Call → Consumer (`background.py`)
**File:** `game/ui/services/image/background.py:193-259`
**Summary:** Mirrors LLM pattern with `ImageUnexpectedError` wrap for non-`ImageException` escapes. One threading nuance: `_active_workers.discard(current)` runs outside `_in_flight_lock` (line 252) whereas the LLM version does it inside (line 331). In CPython, `set.discard()` is atomic, so this is harmless but inconsistent. (See MINOR-5.)
**Verdict:** PASS — Symmetric error containment with LLM pattern. Thread-safe in practice.

### Boundary 10: Game Initializer → Caller (`game_initializer.py`)
**File:** `game/strategy/engine/game_initializer.py:50-136`
**Summary:** `GameInitializer.initialize()` retries up to 10 times for planet-shortage at N=1, then raises `ValidationException(V001)` with system_count, num_empires, attempts, and last_error in context. No internal broad-catch masking.
**Verdict:** PASS — Clean domain exception with actionable context.

---

## Critical Path Analysis

### Path 1: Battle Simulation Failure → Strategy Turn → UI
**Trace:** `run_battle()` → `SimulationBattleResolver._run_simulated_battle()` → `ConflictResolutionEngine._resolve_combat_at_hex()` → `TurnEngine._time_phase()` → `TurnEngine.process_turn()` → `GameSession.process_turn()` → `StrategySessionFacade.process_turn()` → `StrategyGameStateManager.process_full_turn()` → `TurnFailedDialog`

**Files checked:**
- `game/simulation/battle_runner.py` (referenced)  
- `game/strategy/adapters/simulation_adapter.py:316-341`  
- `game/strategy/engine/conflict_resolution_engine.py:414-556`  
- `game/strategy/engine/turn_engine.py:286-703`  
- `game/strategy/engine/game_session.py:329-362`  
- `game/strategy/facade/strategy_session_facade.py:215-252`  
- `game/ui/screens/strategy_game_state_manager.py:352-392`  
- `game/ui/screens/turn_failed_dialog.py:32-55`

**Findings:**

- **MAJOR-1: BattleResolutionError context not surfaced in UI.** The `SimulationBattleResolver` wraps simulation failures as `BattleResolutionError` with fleet_ids, empire_ids, hex_coord in context. At the `_time_phase` boundary, this becomes `EnginePhaseError(T001)` where `original_error=str(e)` carries only the message, and `original_type="BattleResolutionError"`. The `TurnFailedDialog._format_body()` reads `phase_name`, `tick`, `original_type`, `turn_number` — none of which include battle-specific IDs. The crash dump (`dump_crash_snapshot`) writes only `EnginePhaseError.context`, not the nested `BattleResolutionError.context`. A developer debugging a crash dump will see the phase failed at tick N but won't know which fleets or hex was involved.
  - **File:** `game/strategy/engine/turn_engine.py:322-333` (EnginePhaseError construction)
  - **Impact:** Diagnostic context loss — crash dumps lack battle-identifying information.
  - **Recommendation:** When constructing `EnginePhaseError` in `_time_phase()`, inspect `e.__cause__` for `BattleResolutionError` and merge relevant keys (`fleet_ids`, `hex_coord`) into the `EnginePhaseError.context` dict.

- **MINOR-1: ConflictResolutionEngine does not wrap resolver errors.** The call `self._battle_resolver.resolve_battle(...)` at `conflict_resolution_engine.py:516` has no try/except. The current design relies on `_time_phase()` to catch all exceptions, which is correct for rollback safety but means a non-`SimulationException`/non-`ValidationException` from `run_battle` bypasses the `BattleResolutionError` wrapper entirely and surfaces as an opaque exception in the crash dump.
  - **Recommendation:** Consider a narrow `except (SimulationException, ValidationException) as e: raise BattleResolutionError(...) from e` directly in `_resolve_combat_at_hex()` so battle-specific context is always captured regardless of the exception path.

### Path 2: Galaxy Generation Error → Session Initialization → UI
**Trace:** `GameInitializer.initialize()` → `SessionBootstrap.new_game_state()` → `GameSession.__init__()` → `screen_router._on_new_game_start()` / `_start_quickstart()` → UI crash handler

**Files checked:**
- `game/strategy/engine/game_initializer.py:50-136`  
- `game/strategy/engine/session/bootstrap.py:227-278`  
- `game/strategy/engine/game_session.py:96-155`  
- `game/screen_router.py:199-240, 246-289`  
- `game/ui/screens/new_game_setup_controller.py:152-187`  
- `game/app.py:508-525`

**Findings:**

- **CRITICAL-1: No error boundary at GameSession construction sites in screen_router.** Both `_on_new_game_start()` (line 209) and `_start_quickstart()` (line 266) call `GameSession(config=...)` without a try/except. If `GameInitializer.initialize()` raises (e.g., planet shortage at N=1 after all retries), the error chain is:
  1. `ValidationException` → caught by `SessionBootstrap.new_game_state()` → re-raised as `SessionInitializationError` (with `from e` chaining)
  2. `GameSession.__init__()` → caught, null-object state set, re-raised
  3. `screen_router._on_new_game_start()` → **NO CATCH** → propagates

  The exception bubbles up through the pygame event handler pipeline (the `_on_start_clicked` UI callback at `controller.py:186` also has no catch), eventually reaching the top-level `main()` crash handler at `app.py:518` which logs a "CRITICAL CRASH" and writes `crash.log`. The user sees a hard application crash rather than an error dialog with a retry option (e.g., "try a different seed").

  **Files:** `game/screen_router.py:209`, `game/screen_router.py:266`, `game/ui/screens/new_game_setup_controller.py:186`  
  **Impact:** User-facing hard crash instead of recoverable error UX.  
  **Recommendation:** Wrap both `GameSession(...)` constructor calls in `except SessionInitializationError as e:` and surface a user-friendly error message. For `_on_new_game_start`, show an error on the setup screen's error label. For `_start_quickstart`, display a `UIMessageWindow` error dialog.

- **MAJOR-2: NewGameSetupController.on_start_clicked() has no exception guard around callback.** Line 186: `self._on_start_callback(config)` is called bare. While the controller validates inputs before this point, the callback itself (session construction) can fail for reasons the controller cannot predict (generation randomness). The controller kills the setup window after the callback (`self._screen.kill()` at line 187), so even a caught error would leave the session in an indeterminate state.
  - **Recommendation:** Catch `SessionInitializationError` around the callback, keep the setup window alive, and surface the error via `self._screen.error_label.set_text(...)`.

### Path 3: Asset Loading Failure → Fallback → UI Rendering
**Files checked:**
- `game/assets/asset_manager.py:69-92, 131-337`  

**Findings:**

- **MINOR-2: Missing manifest silently returns no error.** `AssetManager.load_manifest()` at line 53-67 logs an error for a missing file but returns `None` rather than raising. Callers that don't check the return value will get `get_missing_texture()` (hot-pink placeholder) for every subsequent `load_image()` call. This is a graceful degradation pattern but the caller has no way to distinguish "manifest not loaded at all" from "specific asset not in manifest."
  - **Recommendation:** Consider raising `MissingResourceException` for a missing manifest (it's configuration, not optional art). Or ensure `load_manifest` is always called during initialization.

- **MINOR-4: Inconsistent exception catching between planet and star loading.** `AssetManager.load_planet_image()` catches `(FileNotFoundError, pygame.error, ValueError)` while `load_star_image()` catches `(FileNotFoundError, pygame.error, ValueError, OSError)`. The extra `OSError` in the star path was added by PROJ-381 Phase 2 (ERR-02-001) but not mirrored to the planet path. The document at `asset_manager.py:154` notes the narrowing was intentional against `MemoryError`/`KeyboardInterrupt`, but `OSError` (permission denied, disk full) could also affect planet images.
  - **Recommendation:** Add `OSError` to `load_planet_image()`'s except clause for consistency, or remove the `OSError` from `load_star_image()` if the PROJ-381 narrow was specifically for a star-only edge case.

### Path 4: LLM Provider Failure → Service Layer → UI Feedback
**Files checked:**
- `game/services/llm/deepseek.py:84-237`  
- `game/services/llm/background.py:248-337`  
- `game/ui/services/image/background.py:193-259`  
- `game/ui/screens/race_setup/llm_dialog_service.py:49-80`

**Findings:**

- **PASS:** The LLM error propagation chain is complete and well-designed. Every provider error maps to a specific `LLMException` subclass. `LLMBackgroundCall._run()` catches escapes as `LLMUnexpectedError`. The `LLMDialogService` in the race setup reads per-error-type status from the controller and surfaces appropriate user-facing messages. No information is lost at any boundary.

- **MINOR-3: ImageBackgroundCall._active_workers.discard() outside lock.** At `game/ui/services/image/background.py:252`, the `_active_workers.discard(current)` runs outside the `_in_flight_lock`. Compare with `game/services/llm/background.py:331-333` where both `_in_flight_calls` decrement and `_active_workers.discard` are under the lock. In CPython, `set.discard()` is atomic (single GIL-protected bytecode), so this is harmless in practice. However, the structural inconsistency could be a maintenance hazard.
  - **Recommendation:** Move `_active_workers.discard(current)` inside `_in_flight_lock` in `ImageBackgroundCall._run()` for consistency with the LLM pattern.

---

## Prioritized Recommendations

| # | Severity | Finding | File(s) | Effort |
|---|---|---|---|---|
| CRITICAL-1 | Critical | No SessionInitializationError catch at GameSession creation | `screen_router.py:209,266`, `controller.py:186` | Low |
| MAJOR-1 | Major | BattleResolutionError context lost in UI/crash dump | `turn_engine.py:322-333` | Low |
| MAJOR-2 | Major | No exception guard around on_start_callback in controller | `new_game_setup_controller.py:186` | Low |
| MINOR-1 | Minor | ConflictResolutionEngine doesn't wrap resolver errors with battle context | `conflict_resolution_engine.py:516` | Low |
| MINOR-2 | Minor | Missing manifest silently returns None, all assets become missing-texture | `asset_manager.py:53-67` | Low |
| MINOR-3 | Minor | ImageBackgroundCall thread cleanup lock asymmetry vs LLM pattern | `image/background.py:252` | Trivial |
| MINOR-4 | Minor | Inconsistent OSError handling between planet/star image loading | `asset_manager.py:153,319` | Trivial |

**Remediation Order (by impact/effort):**

1. **CRITICAL-1 + MAJOR-2** (same root cause): Add `except SessionInitializationError` around `GameSession(...)` in `screen_router.py` and around `on_start_callback` call in `new_game_setup_controller.py`. ~10 lines total.
2. **MAJOR-1**: In `TurnEngine._time_phase()`, before constructing `EnginePhaseError`, check if `e.__cause__` is a `BattleResolutionError` and merge its context keys into the error context dict. ~8 lines.
3. **MINOR-1**: Add narrow `try/except (SimulationException, ValidationException)` in `ConflictResolutionEngine._resolve_combat_at_hex()` for defense-in-depth. ~6 lines.
4. **MINOR-2, MINOR-3, MINOR-4**: Cleanup items, each ~2-5 lines.
