# TD-02: GameSession is both session model and composition root

**Status:** VERIFIED
**Source:** `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/report.md`, TD-02
**Target file:** `game/strategy/engine/game_session.py` (599 LOC)

---

## Verification Findings

### File-line evidence

`game/strategy/engine/game_session.py:77-199` — `__init__` performs the entire composition-root job:

1. Lines 79-84: config defaulting, `turn_number`, `save_path`
2. Lines 87-88: `EventLog` + `EventBus` construction with closure handler
3. Line 91: `_resolve_registries()` (provider + `ResourceCatalog.from_json()`)
4. Lines 98: lazy `_race_registry` slot
5. Lines 104-123: import + construction of five mutator services (`FleetNavigationService`, `FleetWriteService`, `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService`)
6. Lines 130-146: `TurnEngineConfig.create_default(...)` + `TurnEngine(...)`
7. Line 147: `create_default_registry()` (command dispatch)
8. Lines 159-184: `GameInitializer.initialize(config, ...)` wrapped in null-object substitution + `SessionInitializationError` re-raise (PROJ-381 / PROJ-395)
9. Lines 185-190: `systems` list materialisation, `human_player_ids` from `config.players` `is_human` flag
10. Lines 198-199: `active_empire` / `enemy_empire` seed (BUG-125)

`game/strategy/engine/game_session.py:432-598` — `from_dict` bypasses `__init__` via `cls.__new__(cls)` (line 456) and **manually re-implements steps 1, 2, 3, 5, 6, 7** plus six rehydration-only operations:

- Line 472: re-calls `_resolve_registries` (the only step extracted to a shared helper)
- Lines 481-482: `EventLog.from_dict(...)` + new `EventBus`
- Line 488: `_race_registry = None`
- Lines 498-517: **literally re-imports** the five mutator-service modules and re-constructs the five services in the same order as `__init__` (the comment at lines 490-497 documents that this is mirrored from `__init__` lines 104-123 by hand under PROJ-396 CRIT-002)
- Lines 519-535: `TurnEngineConfig.create_default(...)` + `TurnEngine(...)` again
- Line 536: `_command_registry`
- Lines 538-560: two-phase galaxy/empire deserialisation
- Lines 562-573: galaxy back-references + fleet registration loop (no equivalent in `__init__`)
- Lines 575-592: `resolve_order_references` + pursuer-tracker rebuild (no equivalent in `__init__`)
- Lines 594-596: `active_empire` / `enemy_empire`

### Confessed drift

The PROJ-396 CRIT-002 comment block (lines 490-497) is self-documenting evidence: *"deserialized sessions MUST construct the same mutator services as `__init__` (lines 104-123). Without these, any command handler that pulls `session.fleet_mutator` ... raises `AttributeError`."* This regression has already happened once and was fixed by hand-mirroring; nothing structurally prevents the next addition from drifting again.

### Concrete drift examples (already present today)

1. **`human_player_ids` semantics differ.** `__init__` (line 188-190) derives `[i for i, p in enumerate(config.players) if p.is_human]`. `from_dict` (line 563) falls back to `[0, 1]`. A two-human / one-AI config that round-trips through save without `human_player_ids` in the dict gets the wrong human set.
2. **`_event_log` handling.** `__init__` constructs a fresh `EventLog()`. `from_dict` does `EventLog.from_dict(data.get('event_log', {'events': []}))`. The fallback shape is a private detail of `EventLog`; if its schema changes the default leaks.
3. **`SessionInitializationError` null-object substitution exists only in `__init__`.** A `from_dict` failure mid-way leaves a partially-constructed object on the caller's stack (e.g. galaxy set but empires missing) — no parallel safety net.
4. **Initialization-only steps.** `GameInitializer.initialize` does homeworld seeding, colony reset, population seeding through the mutator surface (lines 160-164). None of this runs on load — by design, but it means the two paths can never share a single bootstrap until those concerns are factored out.
5. **Load-only steps.** Galaxy back-references (lines 566-567), fleet registration (lines 570-573, PROJ-219), order reference resolution (lines 579-581, PROJ-207), pursuer tracker rebuild (lines 586-592, PROJ-222). These have no `__init__` counterpart because fresh games don't need them, but they expand the surface that `from_dict` must keep in sync with whatever shape the live runtime requires.

### Public surface count

`game/strategy/engine/game_session.py` exposes:

- **6 public methods:** `process_turn` (line 299), `preview_fleet_path` (line 334), `get_fleet_path_projection` (line 359), `handle_command` (line 373), `to_dict` (line 416), `from_dict` classmethod (line 432)
- **7 public properties:** `event_log`, `registries`, `fleet_mutator`, `planet_mutator`, `empire_mutator`, `ship_mutator`, `race_registry` (lines 218-273)
- **1 static helper:** `_resolve_registries` (line 201)
- **2 private helpers:** `_create_event_handler` (line 275), `_get_fleet_by_id` (line 388), `_get_planet_by_id` (line 401)

These public members fan out across **five separable responsibilities** that the report calls out:

| Responsibility | Surface |
|---|---|
| Owned domain state | `config`, `turn_number`, `save_path`, `galaxy`, `empires`, `systems`, `human_player_ids`, `active_empire`, `enemy_empire`, `_event_log` |
| Runtime services | 5 mutator properties, `registries`, `race_registry`, `turn_engine`, `_command_registry`, `_event_bus` |
| Command dispatch | `handle_command` |
| Preview helpers | `preview_fleet_path`, `get_fleet_path_projection` |
| Persistence | `to_dict`, `from_dict` (+ all hand-mirrored bootstrap inside it) |

### Verdict

**VERIFIED.** `__init__` and `from_dict` are two parallel composition pipelines with shared steps performed in-line in each (mutator construction, turn-engine construction, event-bus construction). The PROJ-396 CRIT-002 comment is a confession of the drift mechanism. Public-method count and responsibility tally match the report's "session model + composition root + persistence" framing.

---

## Executor Guardrails

- Keep the public API stable in this remediation: `GameSession(config=..., ai_factory=...)`, `GameSession.from_dict(data, ai_factory=...)`, and `GameSession.to_dict()` remain the supported entry points. Do **not** mass-migrate production or test call sites to a new factory in this plan.
- Preserve save schema and current load semantics unless a dedicated failing test explicitly requires a change. This is a structural split, not a behavior-cleanup pass.
- Preserve the current lazy `race_registry` behavior. Do not make it eager just because other services move into a bag.
- Do not use `self.__dict__.update(...)`, and do not duplicate bootstrap logic in two places. The whole point of this remediation is to eliminate the duplicated init/load construction path.
- The `game/strategy/engine/session/` package does **not** exist yet. Creating it is part of the plan.
- Before each phase, re-run:

```bash
rg -n "GameSession\(|GameSession\.from_dict\(|SessionBootstrap|SessionPersistenceAdapter|SessionRuntimeServices" game tests docs
rg -n "fleet_mutator|planet_mutator|empire_mutator|ship_mutator|TurnEngineConfig\.create_default|create_default_registry|GameInitializer\.initialize" game/strategy/engine/game_session.py
```

The first command tells you whether new external call sites appeared while parallel work was happening. The second confirms `game_session.py` is actually shrinking.

---

## Affected Code

### Production files to edit

- `game/strategy/engine/game_session.py`
- `game/strategy/systems/save_game_service.py` — only if `from_dict` delegation changes require a docstring or tiny call-site adjustment; do not change API shape

### New production files to add

- `game/strategy/engine/session/__init__.py`
- `game/strategy/engine/session/runtime_services.py`
- `game/strategy/engine/session/bootstrap.py`
- `game/strategy/engine/session/persistence_adapter.py`

### Existing tests that must stay green

High-signal current coverage includes:

- `tests/unit/strategy/test_game_session.py`
- `tests/unit/strategy/test_game_session_events.py`
- `tests/unit/strategy/test_game_session_save_load_registries.py`
- `tests/unit/strategy/engine/test_game_session_from_dict.py`
- `tests/integration/save_load/`
- `tests/integration/strategy/test_event_log_integration.py`
- `tests/integration/strategy/test_fleet_registration_wiring.py`
- `tests/integration/strategy/test_fleet_registration_lifecycle.py`
- `tests/integration/strategy/test_game_session_strategy.py`
- `tests/integration/gameplay_loop/`
- `tests/integration/quickstart/`
- `tests/integration/test_app_integration.py`

There are many additional `GameSession(...)` and `GameSession.from_dict(...)` call sites across tests. That is why this plan preserves the public API and avoids broad call-site churn.

### New tests to add

- `tests/unit/strategy/engine/session/test_runtime_services.py`
- `tests/unit/strategy/engine/session/test_bootstrap.py`
- `tests/unit/strategy/engine/session/test_persistence_adapter.py`
- `tests/unit/strategy/engine/test_game_session_shape.py`

### Save schema constraint

The serialized dict shape stays:

```text
{turn_number, save_path, config, galaxy, empires, human_player_ids, event_log}
```

No migration, no compatibility layer, no field rename.

---

## Goal / End State

`GameSession` becomes a thin owned-state object with a small behavior shell. Construction and rehydration share one internal bootstrap pipeline, but the public API seen by callers does not change.

### Target package layout

```text
game/strategy/engine/
    game_session.py
    session/
        __init__.py
        runtime_services.py
        bootstrap.py
        persistence_adapter.py
```

### Required collaborators

```python
@dataclass(frozen=True)
class SessionRuntimeServices:
    registries: GameRegistries
    event_log: EventLog
    event_bus: EventBus
    fleet_mutator: IFleetMutator
    planet_mutator: IPlanetMutator
    empire_mutator: IEmpireMutator
    ship_mutator: IShipInstanceMutator
    turn_engine: TurnEngine
    command_registry: Any
```

`race_registry` intentionally stays **outside** this bag and remains lazy on `GameSession`. It is not part of the drift problem and changing its lifetime here would create unnecessary behavior risk.

**Cross-plan coupling with TD-05:** If TD-05 has already landed when TD-02 starts, the `DesignRepository` and per-empire `DesignCatalog` ownership that TD-05 placed directly on `GameSession` should be absorbed into `SessionRuntimeServices` (or into `SessionBootstrapState` for the catalogs, since they are per-empire runtime state) as part of TD-02 Phase 1. Leaving them on `GameSession` while every other service migrates into the frozen services bag creates a second service-injection convention that future plans would have to bridge. If TD-05 has not yet landed, no action is required here; TD-05 lands its accessor on `GameSession` and a later cleanup migrates it.

```python
@dataclass(frozen=True)
class SessionBootstrapState:
    config: GameConfig
    services: SessionRuntimeServices
    galaxy: Galaxy | None
    empires: list[Empire]
    turn_number: int
    save_path: str | None
    human_player_ids: list[int]
```

`SessionBootstrapState` is the single internal payload both init and load paths hand to `GameSession`.

### Required `GameSession` structure

```python
class GameSession:
    def __init__(
        self,
        config: GameConfig | None = None,
        ai_factory: Any | None = None,
        *,
        _state: SessionBootstrapState | None = None,
    ) -> None:
        state = _state or SessionBootstrap.new_game_state(
            config or GameConfig(),
            ai_factory=ai_factory,
        )
        self._apply_bootstrap_state(state)

    @classmethod
    def from_dict(cls, data: dict, ai_factory: Any | None = None) -> "GameSession":
        state = SessionPersistenceAdapter.rehydrate_state(data, ai_factory=ai_factory)
        return cls(_state=state)
```

The private `_apply_bootstrap_state(...)` method is the single assignment path. This avoids both `cls.__new__(cls)` reconstruction logic in `from_dict` and the risky `self.__dict__.update(...)` shortcut.

---

## Remediation Plan

Strict TDD throughout. Each phase ends with focused green tests before moving on.

### Phase 0 — Preflight and contract freeze

**Purpose:** capture the external API and current semantics before extracting internals.

**Touch list:** none.

**Actions:**

1. Run the two `rg` commands from **Executor Guardrails**.
2. Confirm that production callers still use `GameSession(...)` / `GameSession.from_dict(...)` directly.
3. Record the current `human_player_ids` load fallback and current `race_registry` laziness as behaviors to preserve in this refactor.

**Exit criteria:**

- You have a current call-site inventory.
- You have explicitly decided that API and behavior are preserved during the split.

### Phase 1 — Add `SessionRuntimeServices` and `SessionBootstrapState`

**Purpose:** introduce the internal value objects first, with no caller-visible change.

**Touch list:**

- Add `game/strategy/engine/session/__init__.py`
- Add `game/strategy/engine/session/runtime_services.py`
- Edit `game/strategy/engine/game_session.py`
- Add `tests/unit/strategy/engine/session/test_runtime_services.py`

**Red tests first:**

- `test_runtime_services_is_frozen_dataclass`
- `test_runtime_services_exposes_current_service_members`
- `test_bootstrap_state_captures_session_owned_state`
- `test_game_session_services_property_returns_runtime_services`

**Implementation rules:**

1. Add `SessionRuntimeServices`.
2. Add `SessionBootstrapState`.
3. `GameSession.__init__` still uses the old construction path in this phase, but it assembles `self._services` and exposes a `services` property.
4. Keep existing private attributes and service properties unchanged for now.

**Validation:**

```bash
pytest tests/unit/strategy/engine/session/test_runtime_services.py -x
pytest tests/unit/strategy/test_game_session.py tests/unit/strategy/test_game_session_events.py tests/unit/strategy/test_game_session_save_load_registries.py -x
```

**Exit criteria:**

- The two internal dataclasses exist and are covered by tests.
- `GameSession` exposes `services` without behavior drift.

### Phase 2 — Extract canonical service construction into `SessionBootstrap`

**Purpose:** eliminate duplicated service wiring between `__init__` and `from_dict`.

**Touch list:**

- Add `game/strategy/engine/session/bootstrap.py`
- Edit `game/strategy/engine/game_session.py`
- Add `tests/unit/strategy/engine/session/test_bootstrap.py`

**Red tests first:**

- `test_build_services_returns_fully_wired_runtime_services`
- `test_build_services_reuses_injected_event_log`
- `test_init_and_from_dict_use_identical_service_classes`
- `test_new_game_state_builds_human_player_ids_exactly_as_today`

**Implementation rules:**

1. Move service construction into `SessionBootstrap._build_services(...)`.
2. Add `SessionBootstrap.new_game_state(...) -> SessionBootstrapState`.
3. Preserve current init failure behavior by keeping the `SessionInitializationError` wrapping in the new-game path only.
4. Do **not** change load-path exception behavior in this phase.

**Validation:**

```bash
pytest tests/unit/strategy/engine/session/test_bootstrap.py -x
pytest tests/unit/strategy/engine/test_game_session_from_dict.py -x
pytest tests/unit/strategy/ tests/integration/strategy/ -k "game_session or from_dict" -x
```

**Exit criteria:**

- Both fresh and loaded sessions use the same service-construction function.
- The anti-drift test comparing service classes passes.

### Phase 3 — Extract `SessionPersistenceAdapter`

**Purpose:** move save/load serialization and rehydration logic out of `GameSession.from_dict`.

**Touch list:**

- Add `game/strategy/engine/session/persistence_adapter.py`
- Edit `game/strategy/engine/game_session.py`
- Add `tests/unit/strategy/engine/session/test_persistence_adapter.py`

**Red tests first:**

- `test_serialize_preserves_existing_save_schema`
- `test_rehydrate_wires_galaxy_back_refs`
- `test_rehydrate_registers_loaded_fleets`
- `test_rehydrate_resolves_order_references`
- `test_rehydrate_rebuilds_pursuer_trackers`

**Implementation rules:**

1. `SessionPersistenceAdapter.serialize(session)` must return the exact current dict shape.
2. `SessionPersistenceAdapter.rehydrate_state(data, ai_factory=...)` returns `SessionBootstrapState`, not `GameSession`.
3. Preserve the current `human_player_ids` fallback semantics exactly as implemented today. Do **not** “clean them up” during this refactor.
4. `GameSession.to_dict()` and `GameSession.from_dict()` become thin delegates.

**Validation:**

```bash
pytest tests/unit/strategy/engine/session/test_persistence_adapter.py -x
pytest tests/integration/save_load/ -x
pytest tests/integration/strategy/test_event_log_integration.py tests/integration/strategy/test_fleet_registration_wiring.py tests/integration/strategy/test_fleet_registration_lifecycle.py -x
python Tools/test_sharded/test_sharded.py
```

**Exit criteria:**

- `GameSession.from_dict()` no longer reconstructs services inline.
- Save/load integration coverage stays green.

### Phase 4 — Collapse `GameSession` to a thin shell

**Purpose:** finish the separation after bootstrap and persistence are external.

**Touch list:**

- Edit `game/strategy/engine/game_session.py`
- Add `tests/unit/strategy/engine/test_game_session_shape.py`

**Red tests first:**

- `test_game_session_no_longer_constructs_mutator_services_inline`
- `test_game_session_no_longer_constructs_turn_engine_inline`
- `test_game_session_keeps_lazy_race_registry`
- `test_game_session_file_loc_budget`

**Implementation rules:**

1. Add `_apply_bootstrap_state(...)` and route both public entry paths through it.
2. Convert service properties to forward through `self._services`.
3. Keep `race_registry` lazy on `GameSession`.
4. Remove inline service/turn-engine/bootstrap imports from `game_session.py`.
5. Do **not** migrate external call sites.

**Validation:**

```bash
pytest tests/unit/strategy/engine/test_game_session_shape.py -x
pytest tests/unit/strategy/test_game_session.py tests/unit/strategy/test_game_session_events.py tests/unit/strategy/engine/test_game_session_from_dict.py -x
pytest tests/integration/gameplay_loop/ tests/integration/quickstart/ tests/integration/test_app_integration.py -x
python Tools/test_sharded/test_sharded.py
```

**Exit criteria:**

- `game_session.py` is a thin shell.
- Public constructor/from_dict behavior is unchanged.

### Phase 5 — Docs update

**Touch list:**

- `docs/01_ARCHITECTURE.md`
- `docs/02_PATTERNS.md`
- `docs/systems/strategy_layer.md`
- `docs/systems/save_load.md`

**Implementation rules:**

1. Document `SessionRuntimeServices`, `SessionBootstrap`, and `SessionPersistenceAdapter` as internal collaborators.
2. Explicitly state that the public API remains `GameSession(...)` / `GameSession.from_dict(...)`.
3. Document that save schema is unchanged.

**Validation:**

```bash
pytest tests/unit/strategy/engine/test_game_session_shape.py -x
python Tools/test_sharded/test_sharded.py
```

**Exit criteria:**

- Docs match the new lifecycle split.

---

## Test Strategy

### New focused tests

```text
tests/unit/strategy/engine/session/test_runtime_services.py
tests/unit/strategy/engine/session/test_bootstrap.py
tests/unit/strategy/engine/session/test_persistence_adapter.py
tests/unit/strategy/engine/test_game_session_shape.py
```

### Required regression coverage

```bash
pytest tests/unit/strategy/test_game_session.py -x
pytest tests/unit/strategy/test_game_session_events.py -x
pytest tests/unit/strategy/test_game_session_save_load_registries.py -x
pytest tests/unit/strategy/engine/test_game_session_from_dict.py -x
pytest tests/integration/save_load/ -x
pytest tests/integration/strategy/test_event_log_integration.py tests/integration/strategy/test_fleet_registration_wiring.py tests/integration/strategy/test_fleet_registration_lifecycle.py -x
pytest tests/integration/strategy/test_game_session_strategy.py tests/integration/gameplay_loop/ tests/integration/quickstart/ tests/integration/test_app_integration.py -x
```

### Final gates

- After phase 3: `python Tools/test_sharded/test_sharded.py`
- After phase 4: `python Tools/test_sharded/test_sharded.py`

---

## Risks & Mitigations

| Risk | Likelihood | Required mitigation |
|------|------------|---------------------|
| A weak executor “helpfully” rewrites all `GameSession(...)` call sites | High | Keep public API stable. Do not add a call-site migration phase. |
| Accidentally changing `race_registry` lifetime while extracting services | Medium | Keep it lazy on `GameSession`; cover this with a dedicated shape test. |
| Accidentally changing load semantics while moving logic | Medium | Preserve current `human_player_ids` fallback and existing load exception behavior unless a dedicated failing test approves a change. |
| Replacing duplicated logic with `self.__dict__.update(...)` | Medium | Use `SessionBootstrapState` plus `_apply_bootstrap_state(...)`; never bulk-copy `__dict__`. |
| Save schema drift | Low | Keep `SessionPersistenceAdapter.serialize()` byte-for-byte equivalent to the old `to_dict()` shape and pin it with tests. |

### Save compatibility statement

This refactor does not change the on-disk schema. Old saves are disposable per project rules, but this plan should still keep existing round-trip tests green because the serialized shape remains identical.

---

## Dependencies / Order

### Verified cross-plan constraints

- **TD-02 should stay before TD-05.** The extracted runtime-services seam is the cleaner injection point for TD-05.
- **TD-02 should stay before TD-08.** The facade cleanup is easier once session construction is no longer in `GameSession` itself.
- **TD-02 is independent of TD-01 and TD-03.**

### Impact on `EXECUTION_ORDER.md`

No required change. The current order document already places TD-02 before TD-05 and TD-08, and this validation did not introduce a new dependency on TD-01 or TD-03.

---

## Estimated Scope

| Phase | Primary work | Validation cost |
|-------|--------------|-----------------|
| 0 | grep baseline only | negligible |
| 1 | add runtime-services/state dataclasses | focused unit tests |
| 2 | extract bootstrap | focused unit/integration tests |
| 3 | extract persistence adapter | one sharded run |
| 4 | thin `GameSession` shell | one sharded run |
| 5 | docs | low |

Expected wall-clock remains under one hour, dominated by the two sharded test runs.

---

## Completion Criteria

- [ ] `game/strategy/engine/session/` exists with `runtime_services.py`, `bootstrap.py`, and `persistence_adapter.py`
- [ ] `GameSession.__init__` and `GameSession.from_dict()` both route through `SessionBootstrapState` + `_apply_bootstrap_state(...)`
- [ ] `game_session.py` no longer imports `FleetNavigationService`, `FleetWriteService`, `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService`, `TurnEngineConfig`, `TurnEngine`, `GameInitializer`, `EventBus`, or `create_default_registry`
- [ ] `race_registry` remains lazy on `GameSession`
- [ ] `SessionPersistenceAdapter.serialize()` preserves the existing save schema
- [ ] `python Tools/test_sharded/test_sharded.py` passes after phase 3 and again after phase 4
