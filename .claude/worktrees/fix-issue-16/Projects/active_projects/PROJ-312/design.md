# PROJ-312: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis (Phase A)

### Test baseline
- Sharded suite: **15672 / 15672 passed** in 56s. Establishes a clean starting point. Document reference: `Tools/test_sharded/test_sharded.py`.

### RNG determinism audit (Phase A, Agent 1)
The simulator's hot-path RNG is largely seeded:

- **Seeded provider:** `random.Random(seed)` instance owned by
  `BattleEngine.rng`. Set in `_initialize_start_state(seed)` at
  `game/simulation/systems/battle_engine.py:359`. Threaded to
  `DamageCalculator.rng` and `CollisionSystem.rng` via explicit DI at
  `battle_engine.py:359-362`. PROJ-252 is the canonical pattern, formalized as
  Pattern #18 in `docs/02_PATTERNS.md`.
- **Seed plumbing:** `BattleSpec.seed: int` flows into
  `engine.start_teams(..., seed=spec.seed)` via
  `start_engine_from_spec()` at `game/simulation/battle_runner.py`.
  `BattleOutcome.seed` echoes the seed back for reproducibility — the spec
  was already designed for replay-style usage even though no replay system
  yet consumes it.
- **Combat Lab proof-of-concept:** `tests/integration/fleet_combat/test_battle_determinism.py:63-106` already
  asserts that two battles run with the same seed produce identical
  `(winner, tick_count, survivors)` tuples — and that *global* `random.seed()`
  contamination doesn't perturb the seeded battle. PROJ-312's regression
  suite extends this with a state-hash assertion.
- **Blocker — ErraticBehavior:** `game/ai/behaviors.py:330-331, 370-371` call
  `random.choice(...)` and `random.uniform(...)` against the **module-level
  `random` module**, not `engine.rng`. Four call sites total. Battle replays
  cannot ship until this is fixed.
- **Combat Lab unseeded fallback (lower priority):**
  `combat_lab/services/ui_state_service.py:188` falls back to
  `random.randint(...)` when run mode is "random". Documented during the
  audit; not a production blocker but worth tightening.

### Battle entry/exit (Phase A, Agent 2)
Two visible entry points, **one shared lower-level codepath**:

- **Headless:** `run_battle(spec, *, ai_factory, ship_builder=None,
  registry_provider=None, headless=True, per_tick_callback=None,
  pre_tick_loop_callback=None) -> BattleOutcome` at
  `game/simulation/battle_runner.py:226-326`.
- **Visual-mode:** `BattleController.start_from_spec(spec, *, ai_factory,
  ship_builder=None, registry_provider=None, config=None) ->
  tuple[BattleServiceResult, Dict[str, 'Ship']]` at
  `game/simulation/battle_controller.py:242-321`.
- **Both route through `start_engine_from_spec(spec, ...)`** at
  `game/simulation/battle_runner.py` (the line ~143 helper). This is the
  natural single hook point for input capture.
- `extract_outcome(engine, spec)` at `game/simulation/battle_runner.py:370-443`
  is the single hook point for output capture.

`BattleSpec` is a frozen dataclass at `game/simulation/battle_spec.py:183-220`
with these fields:
`seed`, `telemetry_level`, `boundary`, `end_condition`, `absolute_max_ticks`,
`teams: Tuple[TeamSpec, ...]`, `modifier_stack`, `post_battle_hook`.

**Non-JSON-safe fields (4):** `post_battle_hook` (callable), `instance_ref`
(per-`ShipSpec`, opaque strategy ref), `modifier_stack` (object), `end_condition`
(object).

**Per-tick state hash hook:** `run_battle` already accepts a
`per_tick_callback: Callable[[BattleEngine], None]` that's called after each
`engine.update()`. Replay determinism debugging can hook here without engine
modification.

### Save / load architecture (Phase A, Agent 3)
- **Saves are folder-based** at `output/saves/<player_name>_<timestamp>/` with
  established sub-structure: `save_metadata.json`, `turns/turn_N.json`,
  `designs/empire_N/`. Replays will live alongside in a new `replays/`
  subfolder.
- **Atomic writes** via `.tmp + os.replace` are already implemented in
  `save_json()` at `game/core/json_utils.py:184-189`. Replays adopt the same
  pattern.
- **Lifecycle hooks** for replay store integration:
  - `SaveGameService.save_game()` at
    `game/strategy/systems/save_game_service.py:62-74` — first call creates
    folder + subfolders. Replay store ensures `replays/` exists.
  - `SaveGameService.load_game()` at
    `game/strategy/systems/save_game_service.py:117-148` — replay store
    re-points to the loaded save's `replays/` directory.
  - `SaveGameService.delete_save()` at
    `game/strategy/systems/save_game_service.py:239-270` — `shutil.rmtree`
    removes the entire save folder, replays follow automatically.
- **Settings file:** `output/settings/` directory pattern already exists for
  user-overridable configs (keybindings precedent). New file:
  `output/settings/replay_settings.json` — lazy-init, defaults to `cap: 50`
  when missing.
- **Schema versioning:** Saves use a strict-match version (currently `3.0.0`).
  Replays adopt the same strict-match policy via a `replay_schema_version`
  field on each replay file. Mismatches → silent skip + debug log.
- **Disk math:** ~150–300 KB per replay × 50 cap = ~15 MB sidecar overhead
  per save. Acceptable.

## Swarm Findings Summary (Phase B)

Combined analysis from individual agent reports in `findings/` (those are
per-agent — this is the synthesis).

### Architecture
- The codebase is **already replay-shaped**: `BattleSpec` carries the seed,
  `BattleOutcome` echoes it, `start_engine_from_spec` is the single capture
  hook for both visual and headless callers, `BattleScreen` has no
  player-input-driven engine mutations, pause/speed already exist.
- The remaining work is therefore mostly **serialization plumbing + a
  persistence layer + a thin UI surface**. Phase 1 (determinism) is the only
  blocker that actually changes simulation behavior.

### Key Patterns to Reuse
- **Pattern #13 (Spec Compiler + run_battle):** `docs/02_PATTERNS.md:963` —
  the unified-entry pattern PROJ-312 is built on top of.
- **Pattern #18 (Per-Battle RNG):** `docs/02_PATTERNS.md:1182` — every new
  RNG consumer must take its rng via DI. Phase 1's `ErraticBehavior` fix
  follows this pattern.
- **Pattern #17 (Serializable Protocol):** `docs/02_PATTERNS.md:1154` —
  static `to_dict(obj) -> dict` + `@classmethod from_dict(cls, data) -> obj`
  is the codebase standard. Phase 2's serialization additions follow this
  pattern.
- **`ShipInstanceSerializer`:** `game/strategy/data/ship_instance_serializer.py:21-177` —
  already covers components, modifiers, cargo, HP, name, design_id, role,
  experience. Phase 2 reuses verbatim for `instance_ref` capture.
- **`IEndCondition.to_dict / end_condition_from_dict`:**
  `game/simulation/systems/battle_end_conditions.py:91-496` — full bidirectional
  serialization with type discriminator. Phase 2 wraps without modification.
- **`ComponentState.to_dict / from_dict`:**
  `game/core/component_state.py:62-79` — canonical per-component HP shape.
- **Atomic save writes:** `game/core/json_utils.py:184-189` — `.tmp + os.replace`
  pattern. Phase 4 uses verbatim.
- **Existing battle determinism harness:**
  `tests/integration/fleet_combat/test_battle_determinism.py:63-106` — Phase 1
  extends with a state-hash regression test.
- **Combat Lab visual replay precedent:**
  `game/ui/screens/test_lab/test_executor.py:225-237` already drives a captured
  `BattleSpec` through `BattleController.start_from_spec()` for visual
  rendering. Phase 5 reuses this exact path with a replay-mode flag.

### Dependencies & Risks (from Phase B Risk Assessor)
1. **Component schema drift (HIGH).** A replay captured under
   `data/components.json` v1 may fail to re-materialize if v2 renames or
   removes a component. `_apply_spec_components_to_ship()` silently skips
   unmatched components (`battle_runner.py:558`), producing a divergent
   replay. *Mitigation:* `replay_schema_version` field + components.json hash
   stored in the replay metadata; UI surfaces "data drift" warning on load
   and either skips the replay or plays best-effort with a banner.
2. **Mid-battle crash → no replay (HIGH).** `BattleOutcome` is only extracted
   at `engine.is_battle_over()`. A 4-hour campaign battle that crashes
   mid-tick produces no replay record. *Mitigation:* explicitly out of scope
   for v1 — replays only exist for *completed* battles. Eager partial-record
   capture is rejected (added complexity, low value).
3. **Strategy state staleness (MEDIUM).** Player's mental model is "view the
   battle that happened at sector X, turn N". The galaxy moves on; sector X
   may not exist anymore. *Mitigation:* replay metadata header carries
   `sector_name`, `turn_number`, participating empires, timestamp so the
   browser UI can display context independent of the live galaxy.
4. **AI policy drift (MEDIUM).** `CombatPolicy` IDs (`"aggressive"` etc.) are
   looked up at runtime from `data/targeting_policies.json`. If the policy
   file changes between capture and replay, behavior drifts even though seed
   matches. *Mitigation:* document divergence behavior; future work could
   pin a policy snapshot in the replay.
5. **Telemetry mismatch (MEDIUM).** Capture spec might be DETAILED but replay
   spec might be NORMAL (or vice versa). *Mitigation:* the replay sidecar
   pins the captured `telemetry_level` in metadata; on load, default to the
   captured level. UI exposes a "view at NORMAL/DETAILED" toggle that warns
   on divergence.
6. **N-team team-id ordering (LOW).** N-team battles allow non-sequential
   `team_id`s (e.g., {1, 3, 5}). *Mitigation:* `ShipSpec.team_id` is already
   serialized in the existing dataclass — confirmed. Round-trip tests in
   Phase 2 cover this.
7. **Ring buffer atomicity (LOW).** Eviction must be **write-then-evict**,
   never the reverse. *Mitigation:* `ReplayStore.persist_replay()` enforces
   the order; tested in Phase 4.

### Opportunities Discovered
- **Combat Lab tooling becomes more useful as a side-effect.** Once `BattleSpec`
  has full `to_dict / from_dict`, Combat Lab scenarios can be saved/loaded
  generically — useful for regression-test capture.
- **Future "shared replay" feature** is unblocked. Replays as standalone JSON
  files become a natural artifact for bug reports and community sharing.
  Out of scope for v1 (sidecar-only) but the data structures don't preclude it.
- **Fleet battle headless tests** could use captured replays as fixtures
  rather than rebuilding scenarios in code. Out of scope for v1.

## Architecture

### Capture pipeline
```
caller (Strategy / Combat Lab / Battle Setup)
       │
       ▼
build_*_battle_spec → BattleSpec  (frozen, has runtime objects + post_battle_hook)
       │
       ▼
run_battle(spec, ...)  -or-  BattleController.start_from_spec(spec, ...)
       │
       ▼
start_engine_from_spec(spec)  ────────────►  ReplayCapture.snapshot_input(spec, context)
                                                     │
                                                     ▼
                                               ReplaySpec  (JSON-safe, post_battle_hook stripped,
                                                            instance_ref → ShipInstance snapshot,
                                                            boundary/modifier_stack/end_condition serialized)
       │
       ▼
... tick loop ...
       │
       ▼
extract_outcome(engine, spec) ─────────────►  ReplayCapture.snapshot_outcome(outcome, replay_spec)
                                                     │
                                                     ▼
                                               ReplayRecord = ReplaySpec + ReplayOutcome + metadata
                                                     │
                                                     ▼
                                               ReplayStore.persist(record)
                                                     │
                                                     ▼
                                               output/saves/<save>/replays/replay_<id>.json
                                               (atomic write, ring-buffer eviction)
```

### Replay playback pipeline
```
EventLogWindow → user clicks Replay button on a battle event entry
       │
       ▼
ReplayStore.load(replay_id)  →  ReplayRecord
       │
       ▼
ReplaySpec.to_battle_spec() → BattleSpec (post_battle_hook = no-op,
                                          instance_ref = ShipInstance from snapshot)
       │
       ▼
BattleScreen.start_from_spec(spec, ai_factory, registry_provider,
                             config=BattleConfig(replay_mode=True,
                                                 captured_telemetry=record.telemetry_level))
       │
       ▼
[same combat renderer, pause/speed/exit affordances, "REPLAY MODE" badge]
```

### Module layout
```
game/simulation/replay/                           # NEW (Phase 2-3)
├── __init__.py
├── replay_spec.py                                # ReplaySpec + nested DTOs (mirror BattleSpec)
├── replay_outcome.py                             # ReplayOutcome (mirror BattleOutcome) — likely just a wrapper
├── replay_record.py                              # ReplayRecord = spec + outcome + metadata + version
├── replay_capture.py                             # snapshot_input / snapshot_outcome + glue to start_engine_from_spec
└── replay_serialization.py                       # to_dict / from_dict for Boundary, ModifierStack, ModifierEntry

game/strategy/services/                           # Phase 4
└── replay_store.py                               # NEW: write / list / load / evict + ring buffer

game/ui/screens/                                  # Phase 5-6
├── battle_screen.py                              # MOD: replay-mode flag, badge, exit
└── event_log_window.py                           # MOD: Replay button per battle event row

output/settings/replay_settings.json              # NEW (Phase 4, lazy-init): {"max_replays_per_save": 50}
output/saves/<save>/replays/replay_<uuid>.json    # NEW per-replay sidecar (Phase 4)
```

### `ReplaySpec` shape (sketch)
```python
@dataclass(frozen=True)
class ReplayShipSpec:
    instance_id: str
    design_id: str
    theme_id: Optional[str]
    name: str
    position: Tuple[float, float]
    angle: float
    velocity: Tuple[float, float]
    components: Tuple[ReplayComponentStateSpec, ...]
    instance_snapshot: Optional[Dict[str, Any]]   # ShipInstanceSerializer.to_dict() output
    scenario_role: Optional[str]
    team_id: int

@dataclass(frozen=True)
class ReplaySpec:
    schema_version: str                            # "1.0.0", strict-match
    seed: int
    telemetry_level: str                           # IntEnum.name
    boundary: Dict[str, Any]                       # serialized Boundary
    end_condition: Dict[str, Any]                  # uses end_condition_from_dict
    absolute_max_ticks: int
    teams: Tuple[ReplayTeamSpec, ...]
    modifier_stack: Dict[str, Any]                 # serialized ModifierStack
    # post_battle_hook: NOT serialized — replay attaches a no-op
```

### `ReplayRecord` metadata
```python
@dataclass(frozen=True)
class ReplayRecord:
    schema_version: str
    replay_id: str                                 # uuid4
    captured_at: str                               # ISO 8601
    sector_name: Optional[str]
    sector_coords: Optional[Tuple[int, int]]
    turn_number: Optional[int]
    participating_empires: Tuple[str, ...]
    components_registry_hash: str                  # for drift detection
    spec: ReplaySpec
    outcome: ReplayOutcome
```

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
