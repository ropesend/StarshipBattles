# Cross-Layer Error Propagation Report

## Summary
- Error Boundaries Mapped: 11
- Critical Paths Traced: 5
- Total Findings: 8
- Critical: 1 | Major: 3 | Minor: 4

---

## Error Boundary Audit

### B-1: Turn Engine `_time_phase()` — Central Phase Wrapper
**File:** `game/strategy/engine/turn_engine.py:251-296`

Every tick-phase and end-of-turn phase runs through `_time_phase()`. Catches `EnginePhaseError` (re-raise as-is) and `Exception` (wrap as `EnginePhaseError(T001)` with phase_name, tick, original_error context). This is the primary cross-layer catch — any exception from any sub-engine (Simulation, Strategy, Core) becomes `EnginePhaseError`.

**Verdict: PASS** — Correctly preserves cause with `raise ... from e` and enriches context. All 21 phases route through this.

---

### B-2: Turn Engine `process_turn()` — Rollback Boundary
**File:** `game/strategy/engine/turn_engine.py:451-585`

Catches `EnginePhaseError` from subturn loop and end-of-turn phases. Rolls back via snapshot if `session` was provided. Re-raises for the caller. Snapshot capture failure (`turn_engine.py:518-523`) raises immediately — correct per documented policy.

**Context keys in re-raised error:** `phase_name`, `tick`, `original_error`, `original_type`. Missing: `turn_number`, `save_path`, `empire_count`.

**Verdict: MINOR** — Rollback mechanics are correct. Context missing turn_number and save_path, which would help crash-dump correlation.

---

### B-3: GameSession `process_turn()` — Session Rollback Passthrough
**File:** `game/strategy/engine/game_session.py:273-306`

Catches `EnginePhaseError` from `TurnEngine.process_turn()`, logs it, and re-raises. turn_number is only incremented on success (line 302). No additional context enrichment.

**Verdict: PASS** — Correct passthrough. The log at line 305 includes turn number.

---

### B-4: StrategySessionFacade `process_turn()` — Facade Passthrough
**File:** `game/strategy/facade/strategy_session_facade.py:164-182`

Delegates directly to `session.process_turn()` with no try/except wrapping, no error conversion. Invalidates caches only on success (line 182 is after the delegate call).

**Verdict: MINOR** — Pattern #19 expects the facade to convert domain errors before UI sees them. But the facade correctly delegates and only invalidates caches on success. The real gap is in the UI layer (see B-5).

---

### B-5: StrategyGameStateManager `process_full_turn()` — **MISSING UI ERROR BOUNDARY**
**File:** `game/ui/screens/strategy_game_state_manager.py:86-167`

```python
try:
    self._screen._facade.process_turn(progress_callback=_on_tick)
finally:
    self._screen.current_tick = None
    self._screen.total_ticks = None
```

Only a `finally` cleanup block — no `except EnginePhaseError` handler. If a turn fails, the error propagates unhandled through:
- `advance_turn()` (line 53 — no except)
- `StrategyScreen.advance_turn()` (`strategy_screen.py:346` — no except)
- `StrategyInputHandler` → pygame event loop
- `app.py:main()` top-level broad catch (line 518-527)

The state rollback in TurnEngine works correctly, but the user experiences a crash with a crash log written to disk rather than an in-game error dialog.

**Verdict: CRITICAL** — No UI-level error boundary for turn processing failures. The game crashes on any `EnginePhaseError` instead of showing a modal error dialog. Every call chain that reaches `process_full_turn()` (single-turn advance, dev-mode run-n-turns) is affected.

---

### B-6: SimulationBattleResolver — Sim-to-Strategy Adapter
**File:** `game/strategy/adapters/simulation_adapter.py:236-325`

`_run_simulated_battle()` calls `_build_spec()`, `run_battle()`, and `_determine_winner()` without any try/except wrapping. If `run_battle` raises `ValidationException` (e.g., component drift detection in `battle_runner.py:_apply_spec_components_to_ships:640-661`), the error propagates unmodified to `ConflictResolutionEngine._resolve_combat_at_hex()`, then to `_time_phase()`, which wraps it as `EnginePhaseError`.

**Verdict: PASS** — Relying on `_time_phase()` as the universal wrapper is the documented pattern. The adapter itself has no responsibility to convert — `_time_phase` provides phase_name/tick context. However, battle-specific context (fleet IDs, hex coordinate) is lost before wrapping.

---

### B-7: ConflictResolutionEngine `_collect_team_modifiers()` — Silent Swallow
**File:** `game/strategy/engine/conflict_resolution_engine.py:549-565`

```python
try:
    ...
    modifiers[team_id] = collect_combat_modifiers(...)
except Exception as e:  # Intentional broad catch: external collector
    logger.warning(...)
    return None
```

Catches all exceptions from `collect_combat_modifiers` and returns None (battle proceeds without strategic modifiers). The justification ("external collector") is valid but broad — if the collector fails due to a bug (e.g., AttributeError), the battle silently loses modifier effects with only a `warning` log.

**Verdict: MAJOR** — Information loss. Modifier collection failure is silent; the battle proceeds with degraded modifier stack. Should either re-raise (letting `_time_phase` wrap it) or log at ERROR level and include the hex/empire context. At minimum the intentional-broad-catch comment should enumerate expected failure modes.

---

### B-8: AssetManager — Graceful Degradation
**File:** `game/assets/asset_manager.py`

Image loading failures return `get_missing_texture()` — a magenta fallback surface. Specific exceptions caught: `FileNotFoundError`, `pygame.error`. Resolution fallback chain handles missing sizes gracefully. Missing textures never crash rendering.

**Verdict: PASS** — Correct graceful degradation for non-critical assets. Specific catch types, consistent fallback.

---

### B-9: LLM Background Call — Correct Escape Wrapping
**File:** `game/services/llm/background.py:248-307`

`LLMBackgroundCall._run()` catches `LLMCancelled`, `LLMException`, and broad `Exception` (line 285). Non-`LLMException` provider escapes are wrapped as `LLMUnexpectedError` with original exception preserved on `__cause__` and type name in context. Status transitions to ERROR or CANCELLED in all paths. The `finally` block correctly releases the in-flight slot and signals `_done_event`.

**Verdict: PASS** — Complies with Pattern #19 and documented LLM error contracts.

---

### B-10: Image Background Call — **MISSING ESCAPE WRAPPER**
**File:** `game/ui/services/image/background.py:166-201`

`ImageBackgroundCall._run()` catches only `ImageCancelled` (line 175) and `ImageException` (line 182). **No broad `Exception` catch.** If `generate_image()` raises a non-`ImageException` (e.g., `RuntimeError`, `KeyError`, unhandled HTTP library exception), the exception:
1. Skips both except blocks
2. Still hits the `finally` block (in-flight slot released)
3. Propagates out of `_run()` — the worker thread dies with an unhandled exception
4. `self._status` remains `RUNNING` — caller's polling loop never sees a terminal state
5. The call object leaks permanently

The documentation explicitly acknowledges this gap (`05_ERROR_HANDLING.md:74`): *"There is no equivalent image unexpected wrapper today; image providers must map third-party failures to ImageException subclasses before they cross the provider boundary."*

**Verdict: MAJOR** — Mirror of the gap that `LLMUnexpectedError` closed for LLM. If any image provider fails to map a third-party exception, the background call hangs forever. The `LLMBackgroundCall` pattern should be mirrored: add an `ImageUnexpectedError` exception class and broad-catch wrapping in `_run()`.

---

### B-11: Simulation Battle Runner — Capture Hooks
**File:** `game/simulation/battle_runner.py:179-189, 357-366`

Replay capture hooks (`on_battle_started`, `on_battle_ended`) are wrapped with intentional broad catches — "capture must not crash a battle". Correct pattern for fire-and-forget instrumentation.

**Verdict: PASS** — Complies with documented pattern for telemetry/sidecar operations.

---

## Critical Path Analysis

### CP-1: Battle Simulation Failure → Battle Outcome → Strategy Turn Processing

```
run_battle() raises ValidationException [battle_runner.py:652]
  → SimulationBattleResolver._run_simulated_battle() [simulation_adapter.py:288]
    (NO try/except — propagates as-is)
  → SimulationBattleResolver.resolve_battle() [simulation_adapter.py:236]
  → ConflictResolutionEngine._resolve_combat_at_hex() [conflict_resolution_engine.py:461]
    (NO try/except — propagates as-is)
  → ConflictResolutionEngine._resolve_conflicts() [conflict_resolution_engine.py:358]
  → TurnEngine._run_phases() → _time_phase() [turn_engine.py:279]
    ✓ Wrapped as EnginePhaseError(T001) with phase_name="combat", tick=N
  → TurnEngine.process_turn() [turn_engine.py:567]
    ✓ Snapshot rollback executed
    ✓ Error re-raised
  → GameSession.process_turn() [game_session.py:303]
    ✓ Logged, re-raised
  → StrategySessionFacade.process_turn() [facade.py:181]
    ✗ No wrapping (acceptable per Pattern #19)
  → StrategyGameStateManager.process_full_turn() [strategy_game_state_manager.py:122-128]
    ✗ ONLY finally block — no except EnginePhaseError
  → propagate unhandled through advance_turn() → input handler → event loop
  → app.py main() [app.py:518-527]
    ✗ Top-level crash handler logs to crash.log and re-raises → game exits
```

**State integrity:** Rollback works. **User experience:** Game crashes silently. **Lost context:** Battle-specific data (fleet IDs, hex coordinate) is absent from `_time_phase` context; only phase_name "combat" and tick number survive.

---

### CP-2: Galaxy Generation Error → Strategy Initialization → UI Error Display

```
GameInitializer.initialize() raises exception
  → GameSession.__init__() [game_session.py:154]
    (NO try/except around initializer call — session object may be partially constructed)
  → propagates to app/scene construction
  → app.py main() top-level catch → crash.log
```

**Verdict: MAJOR** — No strategy-initialization error boundary. If galaxy generation fails (e.g., `ValidationException` from planet placement), the session may be partially initialized with unset attributes (galaxy=None, empires=[]). The top-level handler catches it, but the UI never has a chance to show a "generation failed" dialog. Compare with turn processing: there's at least a rollback mechanism there. Generation errors have no such safety net.

---

### CP-3: Asset Loading Failure → AssetManager Fallback → UI Rendering

```
AssetManager.load_image() [asset_manager.py:86-93]
  catches FileNotFoundError, pygame.error
  → returns get_missing_texture() [magenta fallback]
AssetManager.get_component_derivative() [asset_manager.py:142-158]
  resolution fallback chain → get_missing_texture()
```

**Verdict: PASS** — Correct graceful degradation. Specific catch types, consistent magenta fallback, never crashes rendering.

---

### CP-4: LLM Provider Failure → Service Layer → UI Feedback

```
LLMBackgroundCall._run() [background.py:248-307]
  catches LLMCancelled, LLMException, broad Exception
  → LLMUnexpectedError wraps non-LLMException escapes
  → status transitions to ERROR/CANCELLED
  → caller polls status/error via pygame update loop
```

**Verdict: PASS** — Full chain preserves exception type, code, context. UI polling loop sees terminal status deterministically.

---

### CP-5: Turn Engine Phase Failure → Snapshot Rollback → Game Session → UI

See CP-1. The rollback mechanics are correct but the UI-path gap means the user never sees an error. The crash dump is written to `save_path/crash_turnN_tickM_phase_X.json` but the UI never surfaces it.

**Verdict: CRITICAL** (same as B-5)

---

## Pattern #19 Validation (Error Boundary Pattern)

| Requirement | Status | Detail |
|---|---|---|
| TurnEngine callback handlers have broad-except wrappers | PASS | `_time_phase()` wraps all 21 phases. Progress callback has intentional broad catch (turn_engine.py:678) |
| Snapshot-and-rollback where documented | PASS | `TurnStateSnapshot.capture()` → `process_turn()` rollback → `restore()` on failure |
| Errors don't bypass StrategySessionFacade without conversion | PASS | Facade is a passthrough but correctly delegates. Gap is in UI layer, not facade |
| SimulationException caught and re-wrapped as StrategyException | PASS | Via `_time_phase()` universal wrapper |
| Engine errors propagate via EnginePhaseError | PASS | All sub-engines route through `_time_phase()` |
| LLM/Image errors map to domain-specific before UI | PASS (LLM), **FAIL** (Image) | LLM has correct hierarchy + escape wrapper. Image lacks `ImageUnexpectedError` |
| Validation/Persistence exceptions propagate cleanly from Core | PASS | Direct raise path; `_time_phase()` wraps if they originate in phases |

**Pattern #19 score: 6/7 requirements met.** The image unexpected-error gap is the sole documented non-compliance (acknowledged in docs). The UI error boundary gap is not a pattern-design failure but an implementation omission in the UI layer.

---

## Prioritized Recommendations

### CRITICAL

**REC-1: Add UI-level EnginePhaseError handler** (CP-1, B-5)
- **File:** `game/ui/screens/strategy_game_state_manager.py:122-128`
- **Action:** Add `except EnginePhaseError as e` after the `finally` block in `process_full_turn()`. Display a modal error dialog with the failed phase name, tick number, and a "Turn has been rolled back — state is preserved" message. Map `e.context` fields to user-facing text.
- **Also:** Wrap `advance_turn()` call in a try/except (strategy_game_state_manager.py:53) or propagate the handler into advance_turn's call chain.
- **Impact:** Prevents game crash on turn failure; user sees meaningful error instead.

### MAJOR

**REC-2: Add ImageUnexpectedError wrapper** (B-10, Pattern #19)
- **File:** `game/core/exceptions.py` — add `ImageUnexpectedError(ImageException)` class
- **File:** `game/ui/services/image/background.py:166-201` — add `except Exception` catch-all in `_run()` that wraps as `ImageUnexpectedError` (mirror `LLMBackgroundCall._run()` pattern at `background.py:285-307`)
- **Impact:** Prevents leaked worker threads and hung status polling when image providers raise non-ImageException errors.

**REC-3: Add initialization error boundary in GameSession** (CP-2)
- **File:** `game/strategy/engine/game_session.py:149-158`
- **Action:** Wrap `GameInitializer.initialize()` call in try/except. On failure, ensure session is in a null-object state (galaxy=empty, empires=empty) rather than partially initialized, and raise a descriptive `StrategyException`.
- **Impact:** Prevents partially-constructed session objects. UI can detect empty-galaxy state and show "generation failed" before crashing.

**REC-4: Enrich battle error context in SimulationBattleResolver** (B-6)
- **File:** `game/strategy/adapters/simulation_adapter.py:236-325`
- **Action:** Add try/except around `run_battle()` call at line 288 that catches `SimulationException` and re-raises as `EnginePhaseError` or a new `BattleResolutionError` with fleet_ids, hex coordinate, and empire_ids in context. This provides richer context than the generic `_time_phase` wrapper.
- **Impact:** Crash-dump files would include fleet IDs and hex location, making battle failure debugging feasible from logs alone.

### MINOR

**REC-5: Add turn_number + save_path to EnginePhaseError context** (B-2)
- **File:** `game/strategy/engine/turn_engine.py:285-294`
- **Action:** Include `"turn_number": getattr(session, 'turn_number', 0)` and `"save_path": save_path` in context dict when available.
- **Impact:** Crash-dump correlation becomes trivial.

**REC-6: Strengthen modifier collection error logging** (B-7)
- **File:** `game/strategy/engine/conflict_resolution_engine.py:563`
- **Action:** Change `logger.warning` to `logger.error` and include hex coordinate and empire order in the message. Enumerate expected failure modes in the intentional-broad-catch comment.
- **Impact:** Production debugging of silent modifier loss.

**REC-7: Add `StrategyException` conversion in facade** (B-4)
- **File:** `game/strategy/facade/strategy_session_facade.py:164-182`
- **Action:** Wrap `session.process_turn()` in try/except, catching `EnginePhaseError` and re-raising as a facade-level `TurnFailedError` with UI-formatted message fields.
- **Impact:** Cleaner separation — UI catches facade exceptions, not domain exceptions.

**REC-8: Add ImageUnexpectedError to `game.core.__all__` and docs** (docs gap)
- **File:** `game/core/exceptions.py`, `docs/05_ERROR_HANDLING.md`
- **Action:** After adding the exception class (REC-2), add it to `__all__` and update the hierarchy in docs §Exception Contract.
- **Impact:** Completeness of public API and documentation.
