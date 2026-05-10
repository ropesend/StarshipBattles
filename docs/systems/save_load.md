# Save / Load Compact Reference

> **Last verified:** 2026-05-08 - Balanced compact replacement checked against `docs/systems/save_load.md`, the compact alternate, `SaveGameService`, `GameSession` serialization, replay bootstrap wiring, and current save/load tests.

`SaveGameService` owns strategy save/load persistence. Saves are disposable, turn-based snapshots of the current `GameSession`; the service supports exactly one current schema and rejects incompatible versions instead of migrating them.

## Scope

| Area | Current contract |
|---|---|
| Service | `game/strategy/systems/save_game_service.py::SaveGameService` |
| Method style | Static methods; module-level replay-store accessors sit beside the class. |
| Schema version | `SaveGameService.SAVE_VERSION = "3.0.0"`; exact match only. |
| Save root | `Paths.SAVES_DIR`, normally `output/saves/`. |
| Snapshot payload | One full `GameSession.to_dict()` per saved turn. |
| JSON I/O | `game/core/json_utils.py::save_json`, `load_json`, `load_json_required`. |
| Replay coupling | `game/strategy/services/replay_store.py`, wired in `game/app_bootstrap.py`. |

`GameSession.to_dict()` currently writes `turn_number`, `save_path`, `config`, `galaxy`, `empires`, `human_player_ids`, and `event_log`. `GameSession.from_dict()` reconstructs config first, resolves registries, rebuilds the turn engine and event bus, loads the galaxy before empires, resolves fleet order references, rebuilds pursuer tracking, and restores active/enemy empire pointers.

## Public API

All entry points are static methods on `SaveGameService`.

| Method | Contract |
|---|---|
| `save_game(game_session, save_name: Optional[str] = None)` | Returns `(success: bool, message: str, save_path: Optional[str])`. Reuses `game_session.save_path` when it is a non-empty string; otherwise creates a save folder under `Paths.SAVES_DIR`. On success, sets `game_session.save_path`, writes the current turn file and metadata, then points the replay store at the save folder. |
| `load_game(save_path: str, turn_number: Optional[int] = None, ai_factory=None)` | Returns `(session: Optional[GameSession], message: str)`. Accepts absolute paths or save-folder names relative to `Paths.SAVES_DIR`. `turn_number=None` loads `latest_turn_number`, falling back to metadata `turn_number`, then `1`. Reconstructed sessions get `session.save_path = resolved_path`. |
| `list_saves()` | Returns metadata dictionaries for folders under `Paths.SAVES_DIR` whose `save_metadata.json` can be parsed, sorted by metadata `timestamp` descending. Adds `save_name` and `save_path`. It is a UI listing helper, not a full version validator. |
| `list_turns(save_path: str)` | Returns turns sorted ascending by `turn_number`. Each entry has `turn_number`, `filename`, `path`, `timestamp`, and `size`. |
| `delete_save(save_path: str)` | Resolves relative paths, deletes the save folder with `shutil.rmtree`, then clears the replay store root. Returns `(success: bool, message: str)`. |
| `get_save_info(save_path: str)` | Returns raw metadata plus `save_name` and `save_path`, or `None` when metadata cannot be read or parsed. It does not enforce `SAVE_VERSION`. |

Playable loaded sessions should pass `ai_factory` when combat may occur after load. `GameSession.from_dict(..., ai_factory=None)` is tolerated during reconstruction, but later battle resolution needs an injected AI factory or battle resolver.

## Disk Layout

```text
output/saves/
+-- <player_name>_<YYYYMMDD_HHMMSS>/
    +-- save_metadata.json
    +-- turns/
    |   +-- turn_1.json
    |   +-- turn_2.json
    |   +-- ...
    +-- designs/
        +-- empire_0/
        +-- empire_1/
        +-- ...
```

Rules:

- `turns/turn_N.json` stores the full game-session snapshot for turn `N`.
- `designs/empire_<id>/` folders are created during save for the current empires; new saves do not copy old temp designs.
- All save files are human-readable JSON.
- All save writes must stay on the `save_json()` path.

Current `save_metadata.json` shape:

```json
{
  "version": "3.0.0",
  "timestamp": "<ISO 8601>",
  "player_name": "<first player>",
  "empire_count": 4,
  "empire_names": ["Terrans", "Romulans"],
  "latest_turn_number": 12,
  "turn_number": 12,
  "galaxy_radius": 25,
  "system_count": 60
}
```

`turn_number` duplicates `latest_turn_number` for current list/detail consumers. The current key is `timestamp`; `save_timestamp` is stale.

Required load-time metadata fields are `version`, `timestamp`, and `player_name`. Required turn-state fields are `turn_number`, `config`, `galaxy`, and `empires`.

## Atomic Persistence

`save_json()` serializes to a sibling `.tmp` file, then replaces the target via `Path.replace()`. The invariant is that a crash can leave the previous valid target or a `.tmp` orphan, but not a torn JSON target.

`SaveGameService` load helpers convert read failures into user-facing messages:

- `_load_json_safe()` catches `JSONDecodeError`, `FileNotFoundError`, `PermissionError`, and `OSError`.
- `_load_save_metadata()` resolves relative paths, validates folder shape, checks required metadata fields, and enforces exact `SAVE_VERSION`.
- `_load_turn_data()` resolves the requested turn file and checks required game-state fields.
- `_reconstruct_game_session()` catches corrupt or incompatible domain data and returns `"Save file corrupted: ..."` instead of leaking internal exceptions.

Save operations return clean failures for `PermissionError`, `OSError`, and `ValidationException`. Delete/list/info helpers also degrade gracefully on permission and OS errors so one bad save does not break the whole save browser.

## Versioning

`_is_compatible_version(save_version)` is an exact equality check against `SaveGameService.SAVE_VERSION`.

Forbidden:

- Migration tables.
- Field-rename shims.
- Fallback loaders.
- Compatibility paths for old save formats.
- Copying legacy temp designs or old save data into new saves.

If the persisted schema changes, bump `SAVE_VERSION`, update strict-version tests, and write only the new shape. Old saves are intentionally invalid.

## Replay Store Coupling

`SaveGameService` coordinates with replay sidecar persistence through module-level hooks:

| Hook | When it runs | Effect |
|---|---|---|
| `set_replay_store(store)` / `get_replay_store()` | Process setup and tests | Registers or clears the optional replay store object. |
| `_notify_replay_store_save_or_load(save_path)` | After successful `save_game()` and `load_game()` | Calls `ReplayStore.set_save_root(Path(save_path))`, so sidecars live under the active save's `replays/` folder. |
| `_notify_replay_store_save_deleted()` | After successful `delete_save()` | Calls `ReplayStore.clear_save_root()`, preventing later battles from writing into a deleted or stale folder. |

Production wiring happens in `game/app_bootstrap.py`: it constructs `ReplayStore`, installs it as the default replay capture sink, and calls `set_replay_store(replay_store)`. Tests can inject a spy/mock or leave `_replay_store = None`; notifications are no-ops without a store.

Hook failures are logged and swallowed with intentional broad catches because replay sidecars must not crash save/load/delete.

Related subsystem docs:

- Strategy replay persistence: `docs/systems/strategy_layer.md`
- Simulation replay capture/playback: `docs/systems/combat_simulation.md`

## Extension Guidance

When adding persisted data:

- Add the field to the owning domain object's `to_dict()` and `from_dict()` pair.
- Keep the service snapshot model as `GameSession.to_dict()` per turn; do not add parallel persistence paths.
- Update metadata only for data needed by save listing/detail UI.
- Use `Paths` constants for paths and `save_json()` for writes.
- Preserve relative-path handling for public APIs that currently support save-folder names.
- Preserve replay-store notifications when changing save, load, or delete flow.
- Preserve graceful failure for corrupt JSON, permission errors, OS errors, and invalid domain data.
- Add round-trip coverage for the exact serialization path.
- If changing the schema, bump `SAVE_VERSION` and keep old saves rejected.

When changing reconstruction:

- Keep galaxy loading before empire loading so planet/fleet references can resolve.
- Keep registries resolved before `Empire.from_dict(...)` and turn-engine construction.
- Keep `event_log` restoration and event-bus wiring aligned with `GameSession.from_dict()`.
- Preserve fleet order-reference resolution and pursuer-tracker rebuild after empires load.

## Tests And Commands

Targeted commands:

```sh
pytest tests/unit/strategy/save_game_service/
pytest tests/integration/save_load/
pytest tests/unit/ui/test_save_selection.py
pytest tests/integration/replay/test_replay_store.py -k SaveGameServiceHooks
```

Canonical full-suite command:

```sh
python Tools/test_sharded/test_sharded.py
```

Primary unit coverage:

- `tests/unit/strategy/save_game_service/test_save_load_ops.py` - folder structure, per-turn files, metadata, version rejection, latest/specific turn loading, turn listing.
- `tests/unit/strategy/save_game_service/test_error_handling.py` - no temp-design migration, logging, friendly errors, path resolution, permission/OS/corrupt JSON handling, delete/list/info failures.
- `tests/unit/strategy/save_game_service/test_load_helpers.py` - helper-level metadata, turn-data, and reconstruction failure contracts.
- `tests/unit/ui/test_save_selection.py` - save browser uses `list_saves()`, `list_turns()`, timestamp parsing, latest/specific turn callbacks, delete flow.

Primary integration coverage:

- `tests/integration/save_load/test_full_roundtrip.py` - end-to-end session save/load identity and turn advancement.
- `tests/integration/save_load/test_live_verification.py` plus `tests/infrastructure/state_snapshot.py` - QA round-trip verifier and deep state comparison.
- `tests/integration/save_load/test_save_creation.py`, `test_save_edge_cases.py`, `test_load_restoration.py` - save layout, malformed saves, missing turns, relative paths, and restoration basics.
- `tests/integration/save_load/test_reference_integrity.py`, `test_registry_injection.py` - restored references and registry injection.
- Domain round trips: `test_roundtrip_config.py`, `test_roundtrip_designs.py`, `test_roundtrip_empire.py`, `test_roundtrip_events.py`, `test_roundtrip_fleet.py`, `test_roundtrip_galaxy.py`, `test_roundtrip_orders.py`, `test_roundtrip_planet.py`, `test_roundtrip_research.py`, `test_roundtrip_ships.py`, `test_roundtrip_stars.py`, and `test_resupply_persistence.py`.
- Replay lifecycle coupling: `tests/integration/replay/test_replay_store.py::TestSaveGameServiceHooks`.

## Stale Reference Corrections

- Current metadata uses `timestamp`, not `save_timestamp`.
- Current `list_turns()` entries include `path`.
- Current production replay wiring lives in `game/app_bootstrap.py`, not `ApplicationContext.create_production()`.
- Current atomic replacement is implemented with `Path.replace()` after writing `.tmp`.
- `SAVE_VERSION = "3.0.0"` is authoritative even where older source comments still mention earlier save-format labels.
