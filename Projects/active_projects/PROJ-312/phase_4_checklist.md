# Phase 4: Sidecar Persistence

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-312 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (worktree-proj-312-battle-replay; 21/21 store tests + lifecycle hooks)
**Objective:** Persist captured replays to per-save sidecar files at
`output/saves/<save>/replays/replay_<uuid>.json`. Apply atomic write +
write-then-evict ring buffer governed by
`output/settings/replay_settings.json`. Hook into `SaveGameService`
lifecycle so replays follow the save through create / load / delete.

**Depends on:** Phase 3 (`IReplayCaptureSink` Protocol + capture pipeline)
complete.

---

## Tasks

### Task 4.1: Replay settings file + loader [Simple]
**File:** `game/strategy/services/replay_settings.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_replay_settings.py`

`output/settings/replay_settings.json` is user-editable JSON; lazy-init on
first need; missing file → defaults.

- [x] Add a frozen `ReplaySettings` dataclass with `max_replays_per_save:
      int` (default 50). Open to extension fields.
- [x] Add `load_replay_settings(settings_path: Optional[Path] = None) ->
      ReplaySettings`. When the file is missing, return defaults without
      raising; log a debug message ("missing replay_settings.json — using
      defaults").
- [x] Add `save_replay_settings(settings, path)` using existing atomic
      `save_json`. Lazy-creates `output/settings/` if missing.
- [x] Path constant: extend `game/core/paths.py` with
      `Paths.REPLAY_SETTINGS_FILE = output/settings/replay_settings.json`.

**Notes:** [Filled during implementation]

### Task 4.2: ReplayStore service [Complex]
**File:** `game/strategy/services/replay_store.py` (NEW)
**Tests:** `pytest tests/integration/replay/test_replay_store.py`

Single owner of replay file IO. Strategy-layer service (not Simulation —
Simulation must not touch the save filesystem).

- [x] Create `ReplayStore` class with:
      - `__init__(self, save_root: Optional[Path] = None, *, settings:
        ReplaySettings, json_writer=save_json)`.
      - `set_save_root(self, save_root: Path) -> None` — called on save
        create / load. Lazy-creates `<save_root>/replays/` if missing.
      - `clear_save_root(self) -> None` — called when no save is loaded
        (main menu state). Returns store to a no-op state.
      - `persist(self, record: ReplayRecord) -> Path` — writes
        `<save_root>/replays/replay_<replay_id>.json` atomically via
        `save_json`. Returns the file path. After write, calls
        `_evict_excess()`.
      - `list(self) -> List[ReplayRecord]` — returns all records sorted by
        `captured_at` descending (newest first). Skips corrupt /
        version-mismatched files with a debug log (mirrors
        `race_caption_loader.py` graceful-degradation precedent).
      - `load(self, replay_id: str) -> Optional[ReplayRecord]` — loads a
        single record; returns None if missing / corrupt.
      - `delete(self, replay_id: str) -> bool` — removes the file (used by
        a future "Delete replay" UI). Returns True on success.
      - `_evict_excess(self) -> int` — deletes oldest replays beyond
        `settings.max_replays_per_save`. Returns count deleted. **Must run
        AFTER successful write, never before.**
- [x] Implement `IReplayCaptureSink` interface (Phase 3 Task 3.1) on
      `ReplayStore`:
      - `on_battle_started(replay_spec, *, context) -> str`: generate a uuid4,
        cache `(replay_id, replay_spec, context)` in memory.
      - `on_battle_ended(replay_id, replay_outcome) -> None`: assemble
        `ReplayRecord` from cached spec/context + outcome, call
        `self.persist(record)`, drop the cache entry.
- [x] Drop in-memory cache entries that haven't received an outcome within
      a "reasonable" window (e.g., 1 hour) to prevent memory leaks if a
      battle fails to reach exit. Acceptable to ignore for v1 — document
      decision in `decisions.md`.

**Notes:** [Filled during implementation]

### Task 4.3: Wire ReplayStore into SaveGameService [Medium]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/integration/replay/test_save_lifecycle.py`

Hook the three save lifecycle entry points so the store points at the
correct directory.

- [x] Locate `SaveGameService.save_game()` (around line 62-74). After the
      save folder is created/confirmed, call
      `replay_store.set_save_root(save_path)` if a store is registered.
- [x] Locate `SaveGameService.load_game()` (around line 117-148). After
      successful load, call `replay_store.set_save_root(save_path)`.
- [x] Locate `SaveGameService.delete_save()` (around line 239-270). The
      `shutil.rmtree(save_path)` already removes the `replays/` subfolder
      automatically — verify with a test. After the rmtree, also call
      `replay_store.clear_save_root()` so the in-process store doesn't
      retain a stale path.
- [x] Inject `ReplayStore` into `SaveGameService.__init__` as an optional
      dependency (defaults to `None` for backward compat with tests that
      don't care about replays). When `None`, all replay calls are no-ops.

**Notes:** [Filled during implementation]

### Task 4.4: Register ReplayStore as default capture sink [Simple]
**File:** `game/context.py` (or wherever `ApplicationContext` registers
default services)
**Tests:** `pytest tests/integration/replay/test_default_sink_registration.py`

- [x] In `ApplicationContext.create_production()`, instantiate `ReplayStore`
      (with `ReplaySettings` loaded from disk) and call
      `set_default_capture_sink(store)`.
- [x] Pass the same `ReplayStore` instance into `SaveGameService` so the
      lifecycle hooks (Task 4.3) point at the same store.
- [x] In `ApplicationContext.create_test()`, default to a no-op /
      `NullCaptureSink` to avoid filesystem writes in tests. Tests that
      want to exercise the store opt in by passing
      `set_default_capture_sink(test_store)` explicitly.

**Notes:** [Filled during implementation]

### Task 4.5: Atomic-write + ring-buffer regression tests [Medium]
**File:** `tests/integration/replay/test_replay_store.py`
**Tests:** `pytest tests/integration/replay/test_replay_store.py`

- [x] `test_persist_writes_atomically`: simulate a write that raises
      mid-serialization; assert no `replay_*.json` file exists after.
- [x] `test_ring_buffer_evicts_oldest_after_write`: configure cap=3, persist
      4 records in sequence (with controlled `captured_at` timestamps);
      assert exactly 3 remain, the oldest is gone.
- [x] `test_ring_buffer_writes_before_eviction`: monkey-patch `save_json` to
      raise on the 4th write; assert all 3 prior records are still on disk.
      (Validates write-then-evict ordering.)
- [x] `test_settings_fallback`: rename `replay_settings.json`; assert store
      loads with `max_replays_per_save=50` default.
- [x] `test_corrupt_file_skipped_in_list`: write a `replay_*.json` with
      garbage JSON; `store.list()` returns the rest without raising; debug
      log emitted.
- [x] `test_schema_version_mismatch_skipped`: write a replay with
      `schema_version="0.0.0"`; `store.list()` skips it.
- [x] `test_save_delete_cascades_to_replays`: integration test —
      `SaveGameService.delete_save(save_path)` removes the entire folder
      including `replays/`. Already true via `shutil.rmtree` but pin with
      a test.

**Notes:** [Filled during implementation]

### Task 4.6: Sharded test runner isolation [Simple]
**File:** `tests/integration/replay/conftest.py` (NEW)
**Tests:** `pytest tests/integration/replay/`

The sharded runner runs each shard in a separate process. Filesystem-touching
tests must use temp dirs.

- [x] Add a `replay_temp_dir` fixture using `tmp_path` (pytest builtin) that
      sets up `<tmp_path>/saves/` and `<tmp_path>/settings/replay_settings.json`.
- [x] Patch `Paths.SAVES_DIR` and `Paths.REPLAY_SETTINGS_FILE` at fixture
      setup; restore on teardown.
- [x] Confirm no replay test writes outside `tmp_path`. Tag any persistence
      test that needs special handling with `@pytest.mark.no_shard` only if
      strictly necessary.

**Notes:** [Filled during implementation]

### Task 4.7: Phase 4 sharded suite verification [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes. Record new test count.
- [x] Manual smoke: start a strategy save, run a battle, end turn, save
      game, inspect `output/saves/<save>/replays/`. Expect exactly one
      `replay_*.json` file.
- [x] Manual smoke: delete the save via the in-game UI; verify the
      `replays/` folder is gone.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `output/settings/replay_settings.json` is documented in
      `docs/04_SERVICES.md` (or wherever user-editable configs are catalogued)
- [x] Atomic write + ring-buffer tests are green
- [x] Save lifecycle integration tests are green
- [x] Manual smoke confirms a strategy battle produces a sidecar file
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
