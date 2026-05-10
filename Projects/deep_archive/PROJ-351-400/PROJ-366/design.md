# PROJ-366: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

PROJ-354B planned a full background replay verification pipeline in 6 phases. Phases 1-4 (verifier, sidecar, listener API, coordinator) landed at commits `9dabe9042` → `ef20ea35d`, with audit-remediation `27e297815`. Phases 5-6 (composition root wiring, integration tests, Combat Lab fallback, docs) were marked **Blocked** because PROJ-354B's plan asserted "the user is handling the prereq sink wiring with codex separately." The user has now clarified that codex is NOT handling this. PROJ-366 owns the prereq + the originally-planned Phase 5-6 work.

## Today's State

### What's wired
- `ReplayStore` exists at `game/strategy/services/replay_store.py` and implements `IReplayCaptureSink`. Constructor accepts `settings` (defaults via `load_replay_settings()`), `save_root` (Optional, set later via `set_save_root`), `json_writer`, `clock`.
- `set_default_capture_sink(sink)` exists at `game/simulation/replay/replay_capture.py:118`. Called by tests; never called in production. Default sink is `NullCaptureSink` (no-op).
- `set_replay_store(store)` exists at `game/strategy/systems/save_game_service.py:33`. Called by tests; never called in production. `_notify_replay_store_save_or_load` and `_notify_replay_store_save_deleted` route save lifecycle to the registered store but no-op when none is registered.
- `ReplayVerificationCoordinator` exists at `game/strategy/services/replay_verification_coordinator.py:151`. Construction takes `replay_store`, `ai_factory`, `registry_provider`, `settings`, `fallback_ship_builder`, `clock`, with test-injection seams for `replay_runner` and `ship_builder_factory`. `start()` registers the listener on the store and spawns the worker thread (idempotent).
- `shutdown_all_coordinators(timeout)` module-level helper exists at `replay_verification_coordinator.py:74`, mirroring `shutdown_all_calls` in `game/services/llm/background.py:345`.
- `AIControllerFactory` is the production AI factory, instantiated freshly in `screen_router.py` for combat. The coordinator can do the same.
- `get_default_registry_provider()` (`game/core/registry.py`) is the module-level registry source.
- `build_replay_ship_builder` lives at `game/strategy/services/replay_ship_builder.py` (extracted from `replay_player.py` in audit-remediation `27e297815` to fix the simulation→strategy layer violation).

### What's NOT wired
- `game/app_bootstrap.py` does not call `set_default_capture_sink(...)` or `set_replay_store(...)`.
- `game/app_bootstrap.py` does not construct `ReplayStore` or `ReplayVerificationCoordinator`.
- `game/run_loop.py` does not call `shutdown_all_coordinators(timeout=...)`.
- No integration tests exist for the end-to-end live-battle → sidecar flow.
- No headless-vs-visual equivalence test exists.
- No Combat Lab fallback test exists.
- `docs/systems/combat_simulation.md` § 11, `docs/systems/strategy_layer.md`, and `docs/01_ARCHITECTURE.md` don't yet document the verification coordinator.

## Architecture

### Layer compliance check

PROJ-354B audit-remediation `27e297815` already moved `build_replay_ship_builder` out of `game/simulation/replay/` into `game/strategy/services/` to fix a simulation→strategy layer violation (finding AR-001). The verifier (`replay_verifier.py`) imports only stdlib + simulation/replay DTOs. The coordinator imports from `game.simulation.replay`, `game.strategy.services.replay_*`, and `game.simulation.battle_outcome` (TYPE_CHECKING only). All within layer rules.

PROJ-366 only modifies `game/app_bootstrap.py` (the composition root, allowed to import everything) and `game/run_loop.py` (also a top-level orchestrator). No new layer crossings introduced.

### Bootstrap sequence (after PROJ-366)

```
bootstrap():
    pygame.init()
    ctx = ApplicationContext.create_production()        # Existing — Invariant 3
    pygame.font.init() / preload                         # Existing — Invariant 2
    ... display, registry loading, ship loading ...      # Existing — Invariants 4, 5
    sprite_manager.load_sprites(...)                     # Existing
    InputMapper.load(...)                                # Existing

    # NEW (Phase 1) — sink wiring
    replay_store = ReplayStore()                         # Constructor uses load_replay_settings() default
    set_default_capture_sink(replay_store)               # Replaces NullCaptureSink
    set_replay_store(replay_store)                       # Routes SaveGameService hooks to the store

    # NEW (Phase 2) — coordinator construction + start
    coordinator = ReplayVerificationCoordinator(
        replay_store=replay_store,
        ai_factory=AIControllerFactory(),
        registry_provider=get_default_registry_provider(),
        settings=load_replay_settings(),
        fallback_ship_builder=load_combat_lab_design,    # Combat Lab fallback (Phase 4)
    )
    coordinator.start()                                  # Subscribes to listener + spawns worker thread

    # Existing return — extended with two new fields
    return BootstrapResult(
        ctx=ctx, screen=..., width=..., height=..., clock=..., registries=...,
        input_mapper=..., font_small=..., font_med=..., font_large=...,
        replay_store=replay_store,                       # NEW
        replay_verification_coordinator=coordinator,     # NEW
    )
```

### Shutdown sequence (after PROJ-366)

```
RunLoop.run():
    while self.running:
        ... frame pump ...

    shutdown_all_calls(timeout=5.0)                      # Existing PROJ-296 LLM cleanup
    shutdown_all_coordinators(timeout=5.0)               # NEW — drain verification work
    pygame.quit()
```

Order remains `shutdown_all_calls` -> `shutdown_all_coordinators` ->
`pygame.quit()` because the current code has no LLM dependency in the
replay verification path (`AIControllerFactory` constructs local AI
controllers directly per `game/ai/ai_factory.py:21-29,83-110`), and this
preserves the existing LLM shutdown invariant before adding the coordinator
drain. If a future verifier path invokes LLM work, revisit this order.
The ordering test in `test_run_loop_shutdown_ordering.py` pins the
current invariant by name so any future flip is loud.

`shutdown_all_coordinators` is idempotent and bounded by the timeout. Note
that a stuck non-daemon worker can still hold the process alive after a
timed join — PROJ-354B accepted no process-boundary timeout, so the
lifecycle docs do not overclaim termination guarantees.

### Failure isolation

- If `ReplayStore()` constructor raises (load_replay_settings malformed JSON), the existing `replay_store.py:87` already catches it with a broad except and returns defaults. Bootstrap should not need defensive error handling — defaults are guaranteed.
- If `set_default_capture_sink(...)` or `set_replay_store(...)` raised (they don't — both are simple module-level assignments), bootstrap would crash, which is correct behavior for a startup invariant.
- If `coordinator.start()` raises, bootstrap should crash — a coordinator that can't subscribe is a wiring bug. The store and coordinator construction should land before any battle code can run.
- If the verifier worker raises mid-record, the existing audit-remediated worker loop (commit `27e297815`, finding ERR-354B-001) catches the exception and writes an `ERROR` sidecar without killing the worker. Subsequent records still process.

## Test Strategy

### Phase 3 integration tests

**`test_verification_queue_integration.py`**
- **Setup:** temp save dir; construct `ReplayStore` + register sink + register store + construct coordinator + `start()`.
- **Pass case:** run a deterministic small battle via `run_battle` with a `ReplayCaptureContext`. Wait for sidecar with bounded timeout (poll for file existence, max 30s). Assert sidecar exists; load and assert `status=PASSED`.
- **Skip case:** rebuild coordinator with `settings=ReplaySettings(verification_enabled=False)`. Run battle. Wait for sidecar. Assert `status=SKIPPED_DISABLED`.
- **Cleanup:** `coordinator.shutdown(timeout=5.0)`; `reset_default_capture_sink()`; `set_replay_store(None)`.

**`test_headless_visual_equivalence.py`**
- **Setup:** Build a deterministic battle via `run_battle`; capture replay record; obtain `replay_record_to_spec(record)`.
- **Path A:** `outcome_a = run_replay_headless(record, ai_factory=..., ship_builder=builder, registry_provider=...)`.
- **Path B:** `controller = BattleController(...); controller.start_from_spec(spec, config=BattleConfig(replay_mode=True), ai_factory=..., ship_builder=the_same_builder, registry_provider=...)`. Drive `controller.update(0.016)` until `controller.is_battle_over()`. `outcome_b = controller.get_outcome()`.
- **Assert:** `battle_outcome_to_dict(outcome_a) == battle_outcome_to_dict(outcome_b)`.
- **Boundary:** `BattleController` only — no `BattleScreen`, no Pygame UI dependency.

**`test_verification_uses_production_materializer.py`**
- **Setup:** as `test_verification_queue_integration` but inject a spy around `build_replay_ship_builder` (monkeypatch + counter).
- **Run:** trigger one battle; wait for sidecar.
- **Assert:** `build_replay_ship_builder` was called by the coordinator (call count ≥ 1); sidecar `status=PASSED`.

**`test_combat_lab_verification.py`**
- **Pass case:** Construct a Combat Lab synthetic record (`instance_snapshot=None` for all ships); coordinator wired with `fallback_ship_builder=load_combat_lab_design`; trigger verification; assert sidecar `status=PASSED`.
- **Error case:** Same record but coordinator wired with `fallback_ship_builder=None`; trigger verification; assert sidecar `status=ERROR` with a diagnostic message indicating "no fallback builder and no instance snapshots".

### Phase 4 lint test

**`test_replay_verifier_imports.py`**
```python
import ast
from pathlib import Path

def test_verifier_has_no_upward_imports():
    src = Path("game/simulation/replay/replay_verifier.py").read_text()
    tree = ast.parse(src)
    forbidden_prefixes = ("game.strategy.", "game.ui.", "game.ai.")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = node.module if isinstance(node, ast.ImportFrom) else None
            for alias in node.names:
                target = mod or alias.name
                assert not any(target.startswith(p) for p in forbidden_prefixes), \
                    f"replay_verifier.py imports forbidden module: {target}"
```

## Risks

### R1: Test-time global state pollution
`set_default_capture_sink` and `set_replay_store` are module-level assignments. Tests that construct their own `ReplayStore` and use `reset_default_capture_sink()` in cleanup are fine; tests that don't may pollute the global. Mitigation: every Phase 3 integration test must teardown via `reset_default_capture_sink()` and `set_replay_store(None)`. Add `addfinalizer` (or `try/finally`) explicitly. Existing `tests/integration/replay/test_replay_store.py` is a reference for the cleanup pattern.

### R2: Coordinator started before save_root is set
`bootstrap()` runs before any save is loaded. The store's `save_root` is initially `None`; `_replay_dir()` returns `None`; persist is a no-op. Once a save is loaded, `_notify_replay_store_save_or_load` calls `store.set_save_root(save_path)` and persistence is active. The coordinator subscribes at bootstrap; it doesn't need to wait for save load. The first battle that runs after a save loads will produce a record that fires the listener as expected. **No bootstrap-vs-save-load ordering issue.**

### R3: AIControllerFactory constructed before policies are loaded
`PolicyManager` is set up in `ApplicationContext.create_production()` (line 90). `AIControllerFactory()` is constructed AFTER that point, so policies are available. No ordering issue.

### R4: Headless replay recursion
Established in PROJ-354B as solved: `run_replay_headless` passes `capture_context=None` to `run_battle`, so `battle_runner.py:180`'s capture-path check is False, and the headless run does not itself produce a replay record. PROJ-354B Phase 4 (Task 4.5) added a no-recursion regression test. PROJ-366 does not need a new test — it relies on PROJ-354B's existing one. **Not a new risk.**

### R5: Combat Lab record verification with no instance snapshots
Combat Lab records have `instance_snapshot=None` for all ships. Without a fallback, `build_replay_ship_builder` raises `ValueError`. The coordinator's worker catches the exception (audit-remediated ERR-354B-001) and writes an `ERROR` sidecar. The fallback `load_combat_lab_design` is the explicit synthetic builder. **Phase 4 wires this; Phase 4 tests it.**

### R6: Existing test fixtures that pre-call `set_default_capture_sink`
Tests like `tests/integration/replay/test_replay_store.py` already wire a sink for testing. PROJ-366 doesn't change the test sink path; the production wiring is additive. Conflict only if tests rely on `_default_sink == NullCaptureSink()` at import time, which they don't (every test that needs a specific sink calls `set_default_capture_sink(...)` itself). **Not a conflict.**

## Implementation Notes

### `BootstrapResult` extension

```python
@dataclass(frozen=True)
class BootstrapResult:
    # ... existing fields ...
    replay_store: "ReplayStore"
    replay_verification_coordinator: "ReplayVerificationCoordinator"
```

These can be forward-referenced via string types so the dataclass module doesn't grow new top-level imports. The `bootstrap()` function imports the concrete types lazily inside its body, like the existing pattern.

### Profiler timing

The existing pattern in `bootstrap()` wraps each step in a `_timed_phase("name", ctx.profiler)` context manager. PROJ-366's wiring should follow the same:

```python
with _timed_phase("replay.construct_store", ctx.profiler):
    replay_store = ReplayStore()
    set_default_capture_sink(replay_store)
    set_replay_store(replay_store)

with _timed_phase("replay.start_coordinator", ctx.profiler):
    coordinator = ReplayVerificationCoordinator(...)
    coordinator.start()
```

Two short timed phases keep launch diagnostics aware of the new work.
