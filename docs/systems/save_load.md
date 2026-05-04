# Save / Load System

> **Last verified:** 2026-05-04 — Initial coverage backfill (T3-25). Documents `SaveGameService` (PROJ-276 v3.0.0 format), the on-disk turn-based layout, the strict no-migration policy, atomic-write guarantees via `save_json`, and the PROJ-312 replay-store integration hook.

---

## 1. Overview

**File:** `game/strategy/systems/save_game_service.py`
**Class:** `SaveGameService` (all methods are `@staticmethod`).
**Format version:** `SAVE_VERSION = "3.0.0"` — strict match. Old saves
are rejected with a clear error; saves are **disposable** per
`CLAUDE.md` Rule 3 / `AGENTS.md`. There is no migration code path.

Saves are **turn-based**: every `process_turn()` writes a new
`turn_N.json` into the save's `turns/` folder; `save_metadata.json`
tracks `latest_turn_number`. The same save can be re-loaded at any
recorded turn.

---

## 2. Public API

All entry points are static methods on `SaveGameService`.

| Method | Signature | Returns |
|--------|-----------|---------|
| `save_game` | `(game_session, save_name: Optional[str] = None)` | `(success: bool, message: str, save_path: Optional[str])` |
| `load_game` | `(save_path: str, turn_number: Optional[int] = None, ai_factory=None)` | `(session: Optional[GameSession], message: str)` |
| `list_saves` | `()` | `List[dict]` — all saves under `Paths.SAVES_DIR`, sorted newest first. |
| `list_turns` | `(save_path: str)` | `List[dict]` — turn metadata `(turn_number, filename, timestamp, size)`. |
| `delete_save` | `(save_path: str)` | `(success: bool, message: str)` |
| `get_save_info` | `(save_path: str)` | `Optional[dict]` — metadata for one save (or `None` if missing/invalid). |

`save_game()` reuses `game_session.save_path` if it is set (so repeated
saves on the same session append turn files). When `save_path` is empty
and no `save_name` is provided, a timestamped name
(`<player_name>_<YYYYMMDD_HHMMSS>`) is generated under `Paths.SAVES_DIR`.

`load_game(turn_number=None)` loads the latest turn. Pass an explicit
`turn_number` to time-travel to an earlier state. The returned
`GameSession` is fully reconstructed (empires, fleets, planets, orders,
events, registries) — see `_reconstruct_game_session()` for the path.
Versioned reconstruction failure (`SAVE_VERSION` mismatch) returns
`(None, "Incompatible save version: <old> (requires 3.0.0)")`.

---

## 3. On-Disk Format

```
output/saves/
└── <player_name>_<YYYYMMDD_HHMMSS>/
    ├── save_metadata.json       # version, timestamp, latest turn, galaxy params
    ├── turns/
    │   ├── turn_1.json          # full GameSession.to_dict() at turn 1
    │   ├── turn_2.json
    │   └── …                    # one file per turn processed
    └── designs/
        ├── empire_0/            # per-empire design folders (allocated lazily)
        ├── empire_1/
        └── …
```

`Paths.SAVES_DIR` resolves to `output/saves/` at the repo root. All
files are JSON, human-readable, written via `save_json()`.

**`save_metadata.json` shape** (written every `save_game()` call):

```json
{
  "version": "3.0.0",
  "save_timestamp": "<ISO 8601>",
  "player_name": "<first player>",
  "empire_count": 4,
  "latest_turn_number": 12,
  "turn_number": 12,
  "galaxy_radius": 25,
  "system_count": 60
}
```

The `turn_number` field is a duplicate of `latest_turn_number`,
preserved for backward-compatibility with `list_saves()` consumers.

---

## 4. Atomic Write Guarantee

Every JSON file written by the service goes through `save_json()`
(`game/core/json_utils.py:184`), which writes to a `.tmp` sibling and
then `os.replace()`s the original file. A crash mid-write leaves either
the previous valid file or the `.tmp` orphan — never a half-written
target. This is the same mechanism `ReplayStore` uses for replay
sidecars and `EventLog` snapshots use for the persisted event log; the
project-wide invariant is "never a torn JSON write."

`load_game()`'s helpers (`_load_json_safe`, `_load_save_metadata`,
`_load_turn_data`) catch `JSONDecodeError`, `PermissionError`, and
`OSError` and return `(None, message)` rather than raising — so a
corrupt file fails the load gracefully, and the rest of the saves on
disk are unaffected.

---

## 5. Versioning Policy — No Migration

`SAVE_VERSION` is checked exact-match in `_is_compatible_version()`.
There is no migration table, no field-rename shim, no fallback path.
Bumping the version (e.g. PROJ-276 Phase 5: `2.0.0` → `3.0.0` to drop
the legacy `component_damage` dict in favor of per-instance
`components`) immediately invalidates every previously-written save.

This is intentional. The project rule (`AGENTS.md`, `CLAUDE.md`,
`docs/03_CONVENTIONS.md` § 6.6) is:

> **No save-file migration.** Old saves are disposable. When a system
> is replaced, remove the old path and update all callers.

If the format changes, write a fresh save. The benefit is that schema
evolution code never accumulates in the codebase — every load path
deals with exactly one schema.

---

## 6. PROJ-312 Replay Integration

`SaveGameService` participates in the replay system's save-coupling
contract via two module-level hook helpers:

- `_notify_replay_store_save_or_load(save_path)` — fires on every
  successful `save_game()` / `load_game()`. Calls
  `ReplayStore.set_save_root(Path(save_path))` so the replay sidecars
  always live under the active save's `replays/` folder.
- `_notify_replay_store_save_deleted()` — fires on `delete_save()`.
  Calls `ReplayStore.clear_save_root()` so subsequent battles do not
  write replays into a stale folder.

The hook is registered via the module-level
`set_replay_store(store)` / `get_replay_store()` accessors (lines 33-42).
`ApplicationContext.create_production` (PROJ-312 Phase 4) wires the
production `ReplayStore` as part of bootstrap; tests can either pass a
mock or leave `_replay_store = None` (every notification is a no-op).

Hook errors are logged with `logger.exception` and swallowed
(`# Intentional broad catch: store hooks must not crash save/load`,
per `docs/05_ERROR_HANDLING.md` convention). A misbehaving
`ReplayStore` will not corrupt the save flow.

For the read side, see [strategy_layer.md § Replay Persistence](strategy_layer.md);
for the simulation-side capture/playback engine, see
[combat_simulation.md § 11 Replay Capture & Playback](combat_simulation.md).

---

## 7. Test Coverage

**Unit tests** — `tests/unit/strategy/save_game_service/`:
- `test_save_load_ops.py` — folder-structure creation (`turns/`,
  `designs/empire_N/`), per-turn versioning, metadata correctness,
  strict-version rejection of older `SAVE_VERSION` strings.
- `test_error_handling.py` — `PermissionError`, `OSError`, corrupt JSON,
  missing required metadata fields.
- `test_load_helpers.py` — metadata validation, turn-file resolution,
  `GameSession` reconstruction edges.

**Integration tests** — `tests/integration/save_load/` (19 files):
- `test_full_roundtrip.py` — end-to-end `GameSession` → save → load →
  identity check (PROJ-223 Phase 5).
- Per-domain round-trips: `test_save_creation.py`,
  `test_save_edge_cases.py`, `test_load_restoration.py` cover empires,
  fleets, planets, galaxy, stars, designs, orders, events, research.
- `test_resupply_persistence.py`, `test_roundtrip_ships.py` — ship
  instance + component serialization integrity.
- `test_reference_integrity.py`, `test_registry_injection.py` — race
  registry and external data injection during load.

The integration suite is the practical contract test for the v3.0.0
format. New fields added to any `to_dict()` / `from_dict()` pair must
include a round-trip case here, or the next refactor will lose the
field silently.
