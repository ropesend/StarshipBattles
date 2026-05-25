# Error Handling Guidelines

> **Last verified:** 2026-05-07 - Compared the original `docs/05_ERROR_HANDLING.md` with `AgentCoordination/Scratchpad/reports/05_ERROR_HANDLING_ALT_compact.md` and verified current contracts against the source files named below.

Compact reference for exception contracts, error codes, logging, JSON persistence, and turn-engine error boundaries. Keep this document operational: preserve current invariants and extension recipes; omit release-note archaeology and repeated prose.

## Source Files

- `game/core/exceptions.py`: custom exception hierarchy.
- `game/core/error_codes.py`: `ErrorCode` enum.
- `game/core/json_utils.py`: canonical JSON file helpers.
- `game/core/validation_helpers.py`: strict `from_dict()` validation helpers.
- `game/core/event_logging.py`: session-scoped `EventBus` (PROJ-252; PROJ-390 retired the module-level compatibility shim).
- `game/strategy/engine/turn_engine.py`: `_time_phase()` and rollback boundary.
- `game/strategy/engine/turn_state_snapshot.py`: pre-turn snapshot capture, restore, crash dump.
- `game/strategy/engine/turn_phase_registry.py`: 15 tick phases and 6 end-of-turn phases.
- `game/strategy/systems/design_repository.py`: `DesignLoadResult` result-object pattern.
- `game/services/llm/` and `game/ui/services/image/`: provider/service error mapping.

## Exception Contract

All custom exceptions inherit from `GameException`. Every game exception has:

- `message`: human-readable diagnostic, exposed through `str(exc)`.
- `code`: `str | None`, usually `ErrorCode.<NAME>.value`.
- `context`: `dict`, defaults to `{}` and must contain safe diagnostic fields only.

Do not raise `GameException`, `LLMException`, or `ImageException` directly. Prefer the narrowest domain class. `SimulationException`, `StrategyException`, `ResourceException`, and similar category bases are catch targets unless no narrower class fits.

Current hierarchy:

```text
GameException
  StateException
    FrozenStateException
  ValidationException
  ResourceException
    MissingResourceException
  PersistenceException
  StrategyException
    SessionInitializationError
    EnginePhaseError
    TurnFailedError
    BattleResolutionError
  SimulationException
    ComponentException
    FormulaException
  LLMException
    LLMConfigError
    LLMNetworkError
    LLMResponseError
    LLMRateLimited
    LLMTimeoutError
    LLMCancelled
    LLMUnexpectedError
  ImageException
    ImageConfigError
    ImageNetworkError
    ImageResponseError
    ImageRateLimited
    ImageTimeoutError
    ImageCancelled
    ImageUnexpectedError
```

Use:

- `ValidationException`: bad input, schema violation, missing entity, invalid range.
- `PersistenceException`: save/load, external serialized data, corrupt save data, snapshot capture failure.
- `StateException` / `FrozenStateException`: invalid object state or immutable-state mutation.
- `MissingResourceException` / `ResourceException`: missing required asset or other resource failure.
- `EnginePhaseError`: turn sub-engine phase failure; triggers rollback when a snapshot exists.
- `TurnFailedError`: facade-level wrapper around `EnginePhaseError` (PROJ-381 B-4) so the UI catches a single strategy-layer type. Properties: `phase_name`, `tick`, `turn_number`, `save_path`, `original_type`, `recoverable`.
- `BattleResolutionError`: simulation failure during strategy-layer battle resolution (PROJ-381 B-6); context carries `fleet_ids`, `empire_ids`, `hex_coord`.
- `SessionInitializationError`: `GameSession` constructor failure (PROJ-381 B-11); session lands in deterministic null-object state with `__cause__` preserved.
- `ImageUnexpectedError`: wraps non-`ImageException` provider escapes in `ImageBackgroundCall._run()`. Symmetric counterpart of `LLMUnexpectedError`.
- `ComponentException`: component configuration or operation failure.
- `FormulaException`: formula parse/evaluation failure.
- `LLM*`: LLM provider, factory, or background-call failure.
- `Image*`: image provider, factory, or background-call failure.

`LLMUnexpectedError` is special: it wraps non-`LLMException` provider escapes in `LLMBackgroundCall._run()`. The original exception is on `__cause__`, `context["original_exception_type"]` contains its type name, and `code` is intentionally `None`. `ImageUnexpectedError` is the symmetric wrapper for `ImageBackgroundCall._run()` (added in PROJ-381 Phase 2 / B-10): same constructor shape, same `original_exception_type` context key, same intent — keep the worker thread from leaking and `_status` from getting stuck on RUNNING when a provider raises a non-`ImageException` type.

## Error Codes

Codes live in `game/core/error_codes.py` as `ErrorCode`. Format is `X###`.

- Validation: `V001 VALIDATION_FAILED`, `V002 SCHEMA_VALIDATION_ERROR`, `V003 MISSING_ENTITY`, `V004 OUT_OF_RANGE`.
- State: `S001 STATE_FROZEN`, `S002 NOT_INITIALIZED`, `S003 INVALID_STATE`.
- Resource: `R001 RESOURCE_NOT_FOUND`, `R002 INVALID_FORMAT`, `R003 RESOURCE_LOAD_FAILED`.
- Persistence: `P001 SAVE_FAILED`, `P002 LOAD_FAILED`, `P003 CORRUPT_DATA`, `P004 VERSION_MISMATCH`, `P005 IO_ERROR`.
- Formula: `F001 FORMULA_SYNTAX_ERROR`, `F002 FORMULA_UNDEFINED_VAR`, `F003 EVAL_ERROR`, `F004 FORMULA_GENERAL_ERROR`.
- Component: `C001 COMPONENT_NOT_FOUND`, `C002 COMPONENT_INVALID`, `C003 MISSING_DEPENDENCY`, `C004 SLOT_OCCUPIED`, `C005 INCOMPATIBLE_COMPONENT`.
- Turn: `T001 PHASE_FAILED`, `T002 TURN_ROLLBACK`, `T003 SNAPSHOT_FAILED`, `T004 DUPLICATE_COMMAND`.
- LLM: `L001 LLM_CONFIG_MISSING`, `L002 LLM_NETWORK_ERROR`, `L003 LLM_BAD_RESPONSE`, `L004 LLM_RATE_LIMITED`, `L005 LLM_TIMEOUT`, `L006 LLM_CANCELLED`.
- Image: `I001 IMAGE_CONFIG_MISSING`, `I002 IMAGE_NETWORK_ERROR`, `I003 IMAGE_BAD_RESPONSE`, `I004 IMAGE_RATE_LIMITED`, `I005 IMAGE_TIMEOUT`, `I006 IMAGE_CANCELLED`.

Pattern:

```python
raise ValidationException(
    "Component damage value out of range",
    code=ErrorCode.OUT_OF_RANGE.value,
    context={"component_id": comp_id, "damage": damage, "max": 100},
)
```

Add a new `ErrorCode` only when callers need programmatic discrimination or an existing category clearly covers the condition. Otherwise a specific exception type plus context is enough.

## Service Error Hygiene

LLM and image contexts must never include API keys, `Authorization`, headers, request bodies, response bodies, prompts/messages, generated text, or image bytes. Safe fields include `provider`, `model`, `endpoint`, `status_code`, `error_code`, `request_duration_ms`, `attempt`, `attempts`, `in_flight`, and `max`.

LLM contracts:

- `LLMProvider.complete()` must return `CompletionResult` or raise an `LLMException` subclass.
- `DeepSeekProvider` reads `DEEPSEEK_API_KEY` per request, redacts `repr`, uses SSL verification and timeouts, retries 5xx only, and never retries 429.
- `LLMProviderFactory.create()` reads `LLM_PROVIDER` (default `deepseek`). Unknown provider raises `LLMConfigError(L001)` with `provider` and `registered` context. A registered provider constructor raising `LLMConfigError` returns `None` for deferred validation.
- `LLMBackgroundCall.start()` enforces `LLMConfig.MAX_CONCURRENT_CALLS` via `LLMConfigError(L001)`. `wait()` must observe terminal states only.

Image contracts:

- `ImageProvider.generate_image()` must return `ImageResult` with non-empty bytes or raise an `ImageException` subclass. Providers may return a different size than requested; callers must inspect `result.size`.
- `OpenAIImageProvider` reads `OPENAI_API_KEY` per request, redacts `repr`, uses `/v1/images/generations` or `/v1/images/edits`, retries 5xx only, and never retries 429.
- `ImageProviderFactory.create()` reads `IMAGE_PROVIDER` (default `openai`). Unknown provider raises `ImageConfigError(I001)`. A registered provider constructor raising `ImageConfigError` returns `None`, but `OpenAIImageProvider` currently validates the key on `generate_image()`, not construction.
- `NullImageProvider` always raises `ImageConfigError(I001)` from `generate_image()` and is the test-safe no-network provider.

## Logging Rules

Use standard library logging in production modules:

```python
import logging
logger = logging.getLogger(__name__)
```

- `logger.debug()`: diagnostics, state transitions, parameters, expected misses.
- `logger.info()`: normal notable events, successful initialization, completed save/load.
- `logger.warning()`: recoverable problem where execution continues with a fallback.
- `logger.error()`: failed operation, required data missing, corrupt data, unexpected exception.
- `logger.exception()`: same as error with traceback; use inside an exception handler.

Avoid `print()`, `traceback.print_exc()`, custom logger wrappers such as deleted `game.core.logger`, and silent swallowing. Log at the handling boundary; do not duplicate the same failure at every stack layer.

## Structured Events

`game/core/event_logging.py` exposes a session-scoped `EventBus` class (PROJ-252):

- `EventBus(handler=None)`: owns a per-session handler.
- `EventBus.set_handler(handler)`: replace the handler on this bus.
- `EventBus.log_event(event_type, **kwargs)`: emits structured event data through the bus's handler.
- Handler exceptions are caught with an intentional broad catch and logged so instrumentation cannot crash simulation.
- When no handler is registered, `log_event()` is a no-op. Tests rely on this; do not raise on missing handler.

Constructor injection is the only supported path: `GameSession` constructs the bus and threads it through to engines, handlers, and data classes that need to emit events (or, for projectiles, an `event_logger=` callable that closes over a session-scoped bus). PROJ-390 retired the module-level `log_event()` / `set_event_handler()` / `get_event_handler()` compatibility shim — there is no fallback path. Do not use structured events for diagnostic logging.

## JSON And Persistence

Use `game/core/json_utils.py` for normal file-based JSON operations in `game/`.

`load_json(path, default=..., encoding="utf-8")`:

- Safe loader for non-critical files.
- Returns `default` on `FileNotFoundError`, `json.JSONDecodeError`, `PermissionError`, or `OSError`.
- Logs missing files at debug and other failures at error.

`load_json_required(path)`:

- Strict loader for critical files.
- Lets `FileNotFoundError` and `json.JSONDecodeError` propagate.

`save_json(path, data, indent=2, ensure_ascii=False)`:

- Creates parent directories.
- Writes to `<file>.tmp`, then replaces the target.
- Returns `True` / `False`.
- On `PermissionError`, `OSError`, `TypeError`, or `ValueError`, logs and leaves the original file untouched.

`deserialize_list(items, deserializer, entity_name, parent_name, strict=False)`:

- `strict=False`: skip invalid children and log warning.
- `strict=True`: raise `PersistenceException(P003)` on the first invalid child, chained from the original.
- Catches `PersistenceException`, `KeyError`, `TypeError`, and `ValueError`.
- Strategy core `from_dict()` paths use strict child deserialization for state integrity.

`game/core/validation_helpers.py` is the standard `from_dict()` helper layer. `require_keys`, `validate_enum`, `validate_positive`, `validate_non_negative`, `validate_range`, and `safe_from_dict` raise `PersistenceException(P003)` because `from_dict()` is a persistence boundary, not ordinary runtime validation.

`DesignLoadResult` is the result-object pattern for non-critical design library reads:

- `success` is `data is not None`.
- Constructors: `ok`, `not_found`, `corrupt`, `invalid_schema`, `permission_denied`, `io_error`.
- Current `DesignRepository.load_design_data()` returns `ok`, `not_found`, `corrupt_json`, `permission_denied`, or `io_error`; it does not currently perform schema validation.

## Save-Restore Modifier Rejection (PROJ-498)

When ship or battle saves are restored, a serialized modifier may exist in
the modifier registry yet fail `ModifierService.check_allowance()` for the
component it was attached to (allow_types / deny_types / allow_abilities).
Both restore paths silently drop the modifier (no save migration — old saves
are disposable per the project policy) and emit `logger.warning` including
the modifier id, component id, ship identifier, and the
`AllowanceReason` name so the drift is diagnosable:

- `game/simulation/battle_state.py` `ShipState.to_ship` — battle save restore.
  Message form: `"BattleState restore: Modifier '{mid}' rejected for
  component '{cid}' on ship '{ship_id}': {REASON}; skipping"`.
- `game/simulation/entities/ship_serialization.py`
  `ShipSerializer._load_components` — ship save restore. Message form:
  `"ShipSerializer: Modifier '{mid}' rejected for component '{cid}' on
  ship '{ship_name}': {REASON}; skipping"`. Distinct from the
  pre-existing unknown-id warning (`"not found in registry, skipping"`).

The check is at the save-restore boundary, NOT inside
`Component.add_modifier()`. Builder, regression-snapshot, and UI flows
intentionally probe rejection conditions; logging there would generate
noise. See `docs/04_SERVICES.md` "Modifiers" for the `check_allowance()`
API surface and the locked reason set.

## Turn Engine Boundary

Turn processing is fail-fast with snapshot rollback.

Flow:

1. If `session` is provided, `TurnStateSnapshot.capture()` serializes all empires and the galaxy before mutation.
2. Snapshot capture failure raises `PersistenceException(T003)` from `TurnStateSnapshot.capture()` and `TurnEngine.process_turn()` aborts. It no longer continues with rollback disabled.
3. The 100-tick loop runs every `DEFAULT_TICK_PHASE_LIST` descriptor through `_time_phase()`: `harvesting`, `resources`, `fuel_gen`, `planet_energy`, `resupply`, `production`, `environmental`, `instant_orders`, `actions`, `planet_actions`, `activation_timers`, `planet_modifier_effects`, `movement_calc`, `movement_apply`, `combat`.
4. End-of-turn work also routes through `_time_phase()` with `tick=0`: `organics_consumption`, `happiness`, `population_growth`, `quality_improvement`, `atmosphere`, `water_modification`.
5. `_time_phase()` re-raises existing `EnginePhaseError`, wraps any other exception as `EnginePhaseError(T001)`, logs with `exc_info=True`, records timing, and chains the original with `raise ... from e`.
6. `process_turn()` catches `EnginePhaseError`, logs the failed tick/phase, writes crash metadata if `snapshot and save_path`, restores state if `snapshot and session`, and re-raises.
7. `GameSession.process_turn()` catches, logs, and re-raises for UI handling.

Current `_time_phase()` context keys are `phase_name`, `tick`, `original_error`, and `original_type`. Do not rely on `turn` being present unless the caller added it.

Sub-engines should validate preconditions before mutation with `_validate_tick_inputs()` and raise descriptive `ValidationException`s. The phase boundary will wrap those as `EnginePhaseError`.

## Broad Catch Rule

Prefer narrowed exception types. A broad `except Exception` in production code must be justified on the same line for new or touched code:

```python
except Exception as e:  # Intentional broad catch: <expected failures and why continuing is correct>
```

The reason must say what failures are expected and why fallback, isolation, or fire-and-forget behavior is correct.

Legitimate broad-catch areas:

- Third-party callback or subscriber dispatch.
- Platform-dependent UI initialization such as Tkinter, audio, or GPU.
- Defensive UI refresh where a redraw failure should not end the session.
- Telemetry, event emission, replay capture, and sidecar writes that must not poison the host operation.
- Registry-provider lookups that may run before app initialization in tests or CLI tools.
- Best-effort metadata/size detection where failure does not invalidate the primary result.

Invalid reasons:

- "general defensive code"
- "third-party stuff"
- "legacy"
- Any vague comment that omits expected failures and continuation rationale.

Strategy phase work is not a swallow site: raw `Exception` from a phase must become `EnginePhaseError` and re-raise.

## Required Patterns

Catch specific exceptions:

```python
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    logger.warning("Invalid JSON: %s", e)
    return default
```

Preserve causes:

```python
except json.JSONDecodeError as e:
    raise PersistenceException(
        f"Failed to parse save file: {path}",
        code=ErrorCode.CORRUPT_DATA.value,
        context={"path": str(path)},
    ) from e
```

Put actionable IDs and bounds in context:

```python
raise ValidationException(
    "Ship has invalid configuration",
    code=ErrorCode.VALIDATION_FAILED.value,
    context={"ship_id": ship.id, "errors": ship.validation_errors},
)
```

Gracefully degrade only for non-critical operations. Missing optional art can warn and use a missing texture. Corrupt save data, required config, invalid `from_dict()` state, and turn-processing failure should raise.

## Anti-Patterns

Do not:

- Use bare `except:`.
- Catch `Exception` without the required justification and logging/wrapping.
- Raise generic `Exception`.
- Wrap without `raise from` when preserving a lower-level cause matters.
- Swallow corrupt persistence data outside an explicit resilient helper such as `deserialize_list(strict=False)`.
- Use direct JSON file I/O for normal game data instead of `json_utils`.
- Put secrets, prompts, responses, headers, or image bytes in exception context.
- Use custom logger wrappers, `print()`, or `traceback.print_exc()` for diagnostics.
- Add compatibility shims or fallback systems for old save formats.

## Extension Recipes

New failure mode:

1. Choose the narrowest existing exception class.
2. Reuse an `ErrorCode` if callers need programmatic handling; add one only for a real new category/condition.
3. Include compact context: entity IDs, paths, phase names, status codes, bounds, attempts.
4. Chain wrapped exceptions with `raise ... from e`.
5. Log once at the boundary that handles or converts the failure.
6. Add focused tests for exception type, code, context, and chaining.

New `from_dict()` method:

1. Use `require_keys()` for required fields.
2. Use `validate_*()` helpers for enums and numeric constraints.
3. Use `safe_from_dict()` or `deserialize_list(..., strict=True)` for nested state that must not be skipped.
4. Raise `PersistenceException(P003)` for corrupt external data.

New turn phase or sub-engine:

1. Validate preconditions before mutation.
2. Add the descriptor to `turn_phase_registry.py` so the phase runs through `_time_phase()`.
3. Ensure failure tests assert `EnginePhaseError`, `ErrorCode.PHASE_FAILED.value`, phase context, and rollback behavior when a session snapshot exists.

New LLM provider:

1. Implement `LLMProvider.complete()`.
2. Map third-party errors to `LLMException` subclasses before returning to callers.
3. Read credentials per request, redact identity, ignore unknown opts, use timeouts, retry only 5xx, never retry 429.
4. Register via `register_provider(name, ProviderClass)`.

New image provider:

1. Implement `ImageProvider.generate_image()`.
2. Return a populated `ImageResult`; never return empty bytes as a sentinel.
3. Map third-party errors to `ImageException` subclasses inside the provider.
4. Preserve safe context only, inspect/report actual result size, retry only 5xx, never retry 429.
5. Register via `register_image_provider(name, ProviderClass)`.

## Verification Commands

Targeted references:

```bash
pytest tests/unit/core/test_exceptions.py tests/unit/core/test_error_codes.py
pytest tests/unit/core/test_json_utils.py tests/unit/core/test_validation_helpers.py
pytest tests/unit/strategy/design_repository/test_repository.py
pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py
pytest tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py
pytest tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py
pytest tests/unit/services/llm/
pytest tests/unit/ui/services/image/
```

Audit and full suite:

```bash
python Tools/error_audit/error_audit.py
python Tools/test_sharded/test_sharded.py
```
