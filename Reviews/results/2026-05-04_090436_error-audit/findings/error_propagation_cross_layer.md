# Cross-Layer Error Propagation Report

## Summary
- Error Boundaries Mapped: 10
- Critical Paths Traced: 5
- Total Findings: 11
- Critical: 3 | Major: 5 | Minor: 3

---

## Error Boundary Audit

### 1. TurnEngine._time_phase() — `game/strategy/engine/turn_engine.py:260`
- **Catches:** `EnginePhaseError` (re-raise) + broad `Exception` (wrap in `EnginePhaseError`)
- **Re-raise:** `EnginePhaseError` with `code=T001`, context: `{phase_name, tick, original_error, original_type}`
- **Preservation:** Original exception chained via `from e`. Original type+message preserved in context dict.
- **Verdict:** PASS. Pattern #19 compliant. Missing justification comment on line 266 broad catch (minor).

### 2. TurnEngine.process_turn() — `game/strategy/engine/turn_engine.py:531`
- **Catches:** `EnginePhaseError` only
- **Action:** Logs error, dumps crash snapshot, restores state from snapshot, **re-raises**
- **Preservation:** Full. Original `EnginePhaseError` propagates unchanged.
- **Verdict:** PASS. Snapshot-rollback pattern correctly implemented per PROJ-251.

### 3. TurnEngine._process_tick() progress callback — `game/strategy/engine/turn_engine.py:669`
- **Catches:** Broad `Exception` with justification: "UI callback must never break turn processing (PROJ-308)"
- **Action:** Logs warning with exc_info, suppresses
- **Verdict:** PASS. Legitimate fire-and-forget.

### 4. GameSession.process_turn() — `game/strategy/engine/game_session.py:225`
- **Catches:** `EnginePhaseError`
- **Action:** Logs, **re-raises** without conversion
- **Preservation:** `EnginePhaseError` propagates unchanged; no DTO or user-facing message.
- **Verdict:** PASS for re-raise. ISSUE: No user-facing conversion (see Finding #4).

### 5. ConflictResolutionEngine._collect_team_modifiers() — `game/strategy/engine/conflict_resolution_engine.py:538`
- **Catches:** Broad `Exception` with justification: "external collector"
- **Action:** Logs warning, returns `None` (combat modifier collection is non-critical)
- **Verdict:** PASS. Legitimate optional feature degradation.

### 6. SimulationBattleResolver._build_capture_context() → ship_instance_lookup — `game/strategy/adapters/simulation_adapter.py:398`
- **Catches:** Broad `Exception` with justification: "capture must not crash a battle"
- **Action:** Returns `None` for the serialized instance
- **Verdict:** PASS. Replay capture is non-critical.

### 7. BattleRunner.start_engine_from_spec() — `game/simulation/battle_runner.py:187`
- **Catches:** Broad `Exception` with justification: "capture must not crash a battle"
- **Action:** Sets `replay_id = None`
- **Verdict:** PASS. Capture sink failure is non-critical.

### 8. TurnStateSnapshot.capture() — `game/strategy/engine/turn_state_snapshot.py:56`
- **Catches:** Broad `Exception` (missing justification comment in raw data baseline; wraps in `PersistenceException`)
- **Re-raise:** `PersistenceException` with `code=SNAPSHOT_FAILED`, chained via `from e`
- **Preservation:** `original_error` in context dict.
- **Verdict:** PASS for conversion pattern. Missing justification comment (minor).
- **CRITICAL DEPENDENCY:** The caller at `turn_engine.py:516-524` catches this and **continues without snapshot** (see Finding #2).

### 9. AssetManager.load_star_image() — `game/assets/asset_manager.py:148`
- **Catches:** Broad `Exception` (missing justification comment)
- **Action:** Logs warning, continues to next size tier, returns missing texture on exhaustion
- **Verdict:** PASS for graceful degradation. Missing justification comment (minor).

### 10. RaceDescriptionLLMController._fire_on_change() — `game/strategy/services/race_description_llm_controller.py:313`
- **Catches:** Broad `Exception` with justification: "UI callbacks must not crash the controller"
- **Action:** Logs error, suppresses
- **Verdict:** PASS.

---

## Critical Path Analysis

### Path 1: Battle Simulation Failure → Turn Processing → UI

**Entry:** Simulation error (e.g. `AttributeError`, `ZeroDivisionError`) in `BattleEngine.tick()`

**Chain:**
```
BattleEngine.tick()                                     [Simulation]
  → run_battle()                                        [Simulation]
    → SimulationBattleResolver._run_simulated_battle()  [Strategy/Adapter]
      → resolve_battle()                                [Strategy/Adapter]
        → ConflictResolutionEngine._resolve_combat_at_hex() [Strategy/Engine]
          → ConflictResolutionEngine._resolve_conflicts()   [Strategy/Engine]
            → _process_tick()                           [Strategy/Engine]
              → _time_phase('combat', ...)              [Strategy/Engine]  ← wraps in EnginePhaseError(T001)
                → process_turn()                        [Strategy/Engine]  ← snapshot rollback + re-raise
                  → GameSession.process_turn()          [Strategy]         ← logs + re-raise
                    → StrategySessionFacade.process_turn() [Strategy/Facade] ← pass-through, NO CATCH
                      → StrategyGameStateManager._process_turn() [UI]      ← try/finally, NO except
                        → pygame event loop             [UI]               ← uncaught EnginePhaseError
                          → app.py:496 try/except       [UI]               ← top-level crash log
```

**Where detail gets lost:**
1. `_resolve_conflicts()` runs multiple combats per tick (line 340-358). If one combat crashes, `_time_phase` wraps the error and stops the tick. **All remaining combats in that tick are abandoned.** After rollback, the entire tick resets, and the same combat pairs will re-engage on the next turn at the same hex (since pre-move state is restored). This creates a re-entrant crash loop if the same buggy fleet pairing exists.
2. `GameSession.process_turn()` re-raises `EnginePhaseError` unchanged. The facade pass-through (no catch) means the raw domain exception reaches the pygame event loop. `StrategyGameStateManager._process_turn()` uses `try/finally` with **no `except` clause** (line 122-124), so `EnginePhaseError` propagates to the event handler.
3. The top-level `app.py:494-503` handler catches it, logs to crash file, and re-raises — **crashing the game**. The user sees a terminal traceback, not a recoverable error dialog.

**Verdict:** CRITICAL. Error propagation chain preserves technical detail (good) but lacks a user-facing boundary at the StrategySessionFacade → UI transition. A turn-processing failure should produce an error dialog, not a game crash.

### Path 2: Galaxy Generation Error → Strategy Initialization → UI

**Entry:** Error during `GameInitializer.initialize()` (planet gen, empire creation, fleet placement)

**Chain:**
```
GameInitializer.initialize()                            [Strategy/Engine]
  → GameSession.__init__()                              [Strategy]    ← NO try/except
    → NewGameSetupScreen / SaveGameService.load_game()  [UI]
      → app.py:496 try/except                           [UI]          ← crash log
```

**Where detail gets lost:**
- `_in_system()` (line 148-151) catches broad exceptions on `hex_distance()` with justification comment — skips poisoned entries. **GOOD.**
- All other failures in `_create_empires()`, `Galaxy` construction, fleet placement propagate as-is. No intermediate error boundaries.
- A schema-validation error in planet generation produces a raw `ValidationException` or `KeyError` with no wrapping.

**Verdict:** MAJOR. Non-fatal generation errors (bad star/planet config) lack individual error isolation. Only `hex_distance` has a poison-entry guard. For `NewGameSetupScreen`, this is acceptable (user sees a crash dialog). For `SaveGameService.load_game()`, deserialization does use `PersistenceException` wrapping — so loaded saves are safer than initial generation.

### Path 3: Asset Loading Failure → UI Rendering

**Entry:** Missing file, corrupt image, or file I/O error in `AssetManager`

**Chain:**
```
AssetManager.load_star_image()                          [Assets]
  → tries size tiers 128→256→512→1024                  [Assets]    ← each try caught + warned
    → returns get_missing_texture() on exhaustion       [Assets]    ← graceful degradation
      → UI renders missing-texture placeholder          [UI]
```

**Where detail gets lost:**
- The `except Exception` at line 154 catches and logs each size attempt as warning. Falls through to next size.
- Returns `get_missing_texture()` after exhausting all sizes.
- **No detail lost.** User sees a placeholder texture; the warning log carries the exception detail.

**Verdict:** PASS. Correct graceful degradation. Missing justification comment (minor).

### Path 4: LLM Provider Failure → Service Layer → UI

**Entry:** Network error, timeout, rate limit, or auth failure in `DeepSeekProvider.complete()`

**Chain:**
```
DeepSeekProvider.complete()                             [Services/LLM]
  → LLMException subclass (TimeoutError/NetworkError/   [Services/LLM]  ← safe context, no secrets
    RateLimited/ConfigError/ResponseError/Cancelled)
    → LLMBackgroundCall._run()                          [Services/LLM]  ← stores in self._error
      → RaceDescriptionLLMController._poll_field()      [Strategy/Svc]  ← transitions state to ERROR
        → _apply_bio_transition()                       [Strategy/Svc]  ← logs type+message
          → _fire_on_change()                           [Strategy/Svc]  ← callback to UI
            → LLMDialogService.check_error_popups()     [UI/Screens]    ← maps to user message
              → LLMDialogService.error_message()        [UI/Screens]    ← user-friendly string
                → show_llm_error_popup()                [UI/Screens]    ← modal popup
```

**Where detail gets lost:**
- `LLMDialogService.error_message()` (line 137-154) maps 5 exception types to user-facing messages. Unknown types get a generic `"LLM error: {type}"` fallback. **GOOD.**
- `LLMBackgroundCall._run()` (line 238-256) correctly distinguishes `LLMCancelled` vs `LLMException` and preserves cancel-wins semantics. **GOOD.**
- `RaceDescriptionLLMController._fire_on_change()` (line 310-314) catches broad exceptions from the UI callback. **GOOD.**
- `RaceDescriptionLLMController._start_bio()` (line 207-215) catches `LLMConfigError` from `call.start()` (concurrent-call limit). **GOOD.**

**Verdict:** PASS. Complete chain with correct user-facing mapping. No information loss.

### Path 5: Turn Snapshot Capture Failure → Rollback Availability

**Entry:** `TurnStateSnapshot.capture()` fails (serialization error in `Empire.to_dict()` or `Galaxy.to_dict()`)

**Chain:**
```
TurnStateSnapshot.capture()                             [Strategy/Engine]
  → PersistenceException(SNAPSHOT_FAILED)               [Strategy/Engine]
    → turn_engine.py:522 catch                          [Strategy/Engine]  ← logs warning, CONTINUES
      → snapshot = None
        → process_turn() runs without rollback safety   [Strategy/Engine]
          → if turn fails: EnginePhaseError re-raised   [Strategy/Engine]
            → rollback check: "if snapshot and session" [Strategy/Engine]
              → snapshot is None, so ROLLBACK SKIPPED   [Strategy/Engine]
```

**Verdict:** CRITICAL. If snapshot capture fails AND the turn subsequently fails, state is **not rolled back** and the game is in a potentially inconsistent state. The `process_turn()` code at line 516-524 explicitly chooses to continue without a snapshot ("better to process the turn than abort"), but PROJ-251's design intent guarantees state integrity via mandatory rollback. This is a gap between documented contract and implementation.

---

## LLM Context Security

### Site 1: `game/services/llm/deepseek.py` — DeepSeek API calls
- **Exception context fields:** `attempt`, `model`, `status_code`, `request_duration_ms`, `error_type`, `provider`, `endpoint`, `in_flight`, `max`, `missing_field`, `attempts`
- **API key:** Not in context. Read from env per-request (`_read_api_key()`). `__repr__` redacts. Never cached on instance.
- **Request body:** Not in context. Built in `_build_body()` but only `body["model"]` flows to context.
- **Response body:** Not in context. `_parse_response()` extracts only `model`, `total_tokens`, `latency_ms` for logging.
- **Tokens:** Logged as count (`usage.total_tokens`), not token content.
- **Headers:** Not in context. `Authorization: Bearer {key}` built in `_build_headers()` but never referenced in exception paths.
- **Verdict:** PASS. Security model implemented as documented.

### Site 2: `game/ui/services/image/openai_provider.py` — OpenAI image API calls
- **Exception context fields:** `attempt`, `model`, `status_code`, `request_duration_ms`, `provider`, `endpoint`, `error_type`, `attempts`
- **API key:** Not in context. Read from env per-request (`_read_api_key()`). `__repr__` redacts. Never cached on instance.
- **Request body:** Not in context. Only `model` and `endpoint` flow to context.
- **Response body:** Not in context. `_parse_response()` extracts only `model`, `size`, `latency_ms` for logging.
- **Image data:** Base64 image bytes decoded in `_parse_response()` — not logged. `size` read from decoded image metadata.
- **Headers:** Not in context. `Authorization: Bearer {key}` never referenced in exception paths.
- **Verdict:** PASS. Security model mirrors `DeepSeekProvider`.

### Site 3: `game/strategy/services/race_description_llm_controller.py` — LLM result consumption
- **Logging on DONE:** `text_len`, `latency_seconds`, `total_tokens` — no prompt content, no response text. (lines 294-298)
- **Logging on ERROR:** `type(call.error).__name__`, `call.error` — the LLMException's context dict (verified safe above). (lines 301-305)
- **Verdict:** PASS.

### Site 4: `game/ui/screens/race_setup/llm_dialog_service.py` — Error-to-user mapping
- **`error_message()`:** Maps exception type → static user-facing string. Does not include exception message text, context, or internal details in the user-facing popup.
- **Verdict:** PASS.

---

## Prioritized Recommendations

| # | Severity | Finding | Recommendation | Effort |
|---|----------|---------|----------------|--------|
| 1 | **CRITICAL** | No UI error boundary for turn failures: `StrategyGameStateManager._process_turn()` uses `try/finally` with no `except`. Turn failures crash the game via `app.py` top-level handler. | Add `except EnginePhaseError` in `StrategyGameStateManager._process_turn()` (line 122). Show error dialog with `e.context.get('phase_name')` and `e.context.get('original_error')`. Set `turn_processing = False` and `current_tick = None` in handler. Do NOT re-raise. | Low |
| 2 | **CRITICAL** | Snapshot-capture failure silences rollback: `turn_engine.py:516-524` continues without snapshot. If turn then fails, no rollback occurs. | When snapshot capture fails, abort the turn immediately instead of continuing. Raise `EnginePhaseError` with code `SNAPSHOT_FAILED` and context from the capture error. This is safer than processing without rollback safety. | Low |
| 3 | **CRITICAL** | Per-combat error isolation missing: `_resolve_conflicts()` runs multiple combats per tick. If one crashes, all remaining combats in that tick are abandoned (though rolled back). Re-entrant crash loops possible. | Wrap `self._resolve_combat_at_hex(occupants)` in `_resolve_conflicts()` with try/except. On error: log, record as a conflict-resolution failure event, and continue to remaining combats. Do not re-raise. The `_time_phase` wrapper at `combat` level keeps its broad catch for truly fatal errors. | Medium |
| 4 | **MAJOR** | `EnginePhaseError` reaches UI without conversion: `GameSession.process_turn()` reraises the raw domain exception. `StrategySessionFacade.process_turn()` is a pass-through. | Add an error-DTO conversion in `GameSession.process_turn()`: return a `TurnResult` dataclass (success/failure with error message) instead of raising. Or add `except EnginePhaseError` in `StrategySessionFacade.process_turn()` that populates a facade-level error field the UI can poll. | Medium |
| 5 | **MAJOR** | Galaxy generation has no per-entity error isolation beyond `hex_distance`. Errors in individual planet/star/fleet creation propagate to caller. | Add per-entity try/except in `GameInitializer.initialize()` that logs individual generation failures and skips only the bad entity. Continue generating remaining entities. | Medium |
| 6 | **MAJOR** | `ConflictResolutionEngine._resolve_combat_at_hex()` (line 450) calls `resolve_battle()` without try/except. Error propagates through `_time_phase` wrapper only — individual combat failures stop the entire conflict phase. | Wrap `resolve_battle()` call in try/except inside `_resolve_combat_at_hex()`. On failure: log the crash, mark fleets as unaffected, emit an error event, and continue. | Medium |
| 7 | **MAJOR** | `turn_engine.py:516-524` snapshot capture failure silently proceeds. If the turn completes, the user never knows snapshot was unavailable. | Log at `logger.error` (not warning) when snapshot fails. Emit an event so the event log records the missing safety net. | Low |
| 8 | **MAJOR** | Missing justification comment on three broad catches: `turn_engine.py:266` (`_time_phase`), `turn_engine.py:522` (snapshot fallthrough), `turn_state_snapshot.py:56` (`capture` wrap). | Add `# Intentional broad catch: <reason>` comments per Pattern 19 convention. | Trivial |
| 9 | **MINOR** | `race_description_prompt_builder.py:200` uses `json.dumps()` directly instead of `game.core.json_utils`. | Switch to `json_utils` if file I/O is involved. For in-memory string building, this is not a violation (json_utils is for file operations per docs). | Trivial |
| 10 | **MINOR** | `asset_manager.py:154` broad `except Exception` on star image loading missing justification comment. | Add comment: `# Intentional broad catch: file I/O, image decode, and pygame errors all degrade to next size tier`. | Trivial |
| 11 | **MINOR** | `ShipInstanceSerializer.to_dict()` call in `simulation_adapter.py:399` captured with `except Exception` — same pattern as existing justified capture sites. | Add comment for consistency with nearby `capture` sites: `# Intentional broad catch: capture must not crash a battle`. | Trivial |

---

## Pattern #19 Compliance Summary

| Requirement | Status |
|-------------|--------|
| TurnEngine callback handlers have broad-except wrappers | PASS (line 669: progress_callback) |
| Snapshot-and-rollback used where documented | **GAP** (can be skipped if snapshot capture fails — Finding #2) |
| No errors bypass StrategySessionFacade without conversion | **GAP** (`EnginePhaseError` passes through facade unchanged — Finding #4) |
| Broad catches carry justification comments | **PARTIAL** (3 sites missing comments: Findings #8, #9, #10) |
| `_time_phase()` wraps failures in `EnginePhaseError` | PASS |
| `process_turn()` catches `EnginePhaseError` and rolls back | PASS (when snapshot is available) |
| Crash file dumped on failure | PASS (`dump_crash_snapshot()` at line 584) |

---

## Severity Distribution by Layer

| Layer | Critical | Major | Minor | Notes |
|-------|----------|-------|-------|-------|
| Core (snapshot) | 0 | 0 | 1 | Justification comment missing |
| Simulation (battle runner) | 0 | 0 | 0 | Capture failures isolated correctly |
| Strategy/Engine (turn engine) | 2 | 2 | 1 | Snapshot gap + no per-combat isolation |
| Strategy/Adapter | 0 | 0 | 1 | Capture isolation present |
| Strategy/Facade | 1 | 1 | 0 | Pass-through at UI boundary |
| Services/LLM | 0 | 0 | 0 | Comprehensive + context-secure |
| Assets | 0 | 0 | 1 | Graceful degradation with missing comment |
| UI (strategy screen) | 1 | 0 | 0 | No error handler for turn failures |
| UI/Services/Image | 0 | 0 | 0 | Mirror of LLM security model |
