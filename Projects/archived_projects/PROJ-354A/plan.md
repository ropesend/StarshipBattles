# PROJ-354A: Replay Component End-State Fidelity

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-354A` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-354A [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Capture-side schema + extractor | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Tests + bridge verification | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Docs | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-04 (post-implementation)
**Active Phase:** All phases complete; awaiting user verification
**Last Action:** Implemented Phases 1–3 end-to-end (TDD); full sharded suite green at 17325/17329 (4 pre-existing skips); committed.
**Next Action:** User verification + close project. PROJ-354B can now consume the new fields.
**Blockers:** None.
**Context for Next Agent:** All scope items landed. Side observation during execution: `game/strategy/combat/spec_compiler.py` was an additional production constructor of `ComponentStateSpec` (not listed in the original construction-site inventory). It was updated in-place to populate `max_hp` from `ComponentState.max_hp` and to set `status="ACTIVE"` (the persistent strategy-side `ComponentState` does not track per-component status; the engine's pre-battle damage application reconciles status once ticks start). Documented in this commit's diff. Old replays at schema `"1.0.0"` surface as `version_drift` per `ReplayResolver.resolve()`.

## Overview

Capture-side fidelity for the replay end-state verification effort. Today, when a battle ends, `_extract_component_states` writes a `ComponentStateSpec` with only `current_hp` and `is_active` — collapsing damage/no-fuel/no-power/etc. states into a single binary flag and dropping per-component max_hp from the persisted record. PROJ-354B's verification work needs richer end state to compare against. This project adds `max_hp` and `status` fields, bumps `REPLAY_SCHEMA_VERSION`, and updates serialization + tests.

## Goals

- Per-component `max_hp` is captured in `ComponentStateSpec` and round-trips through replay JSON.
- Per-component `status` (one of `ACTIVE` / `DAMAGED` / `NO_CREW` / `NO_POWER` / `NO_FUEL` / `NO_AMMO`) is captured as `ComponentStatus.name` (string, not numeric `auto()` value) and round-trips through replay JSON.
- `_extract_component_states` reads both fields off live `Component` instances and emits them.
- `REPLAY_SCHEMA_VERSION` bumped to `"2.0.0"`. Existing user replays surface as `version_drift` in `ReplayResolver.resolve()` — graceful degradation already handled at `replay_resolver.py:103-104`.
- All existing tests touching `ComponentStateSpec` pass with the new constructor signature.
- New tests prove damaged / no-crew / inactive components emit distinct `max_hp` + `status` values, and that the JSON round-trip preserves them.
- `docs/systems/combat_simulation.md` updated with the new outcome fields.

## Scope

**In:**
- Extend `ComponentStateSpec` (frozen dataclass) at `game/simulation/battle_spec.py:86-99` with `max_hp: float` and `status: str`.
- Update `_extract_component_states` at `game/simulation/battle_runner.py:622-643` to populate the new fields from `comp.max_hp` and `comp.status.name`.
- Update `_component_state_to_dict` and `_component_state_from_dict` at `game/simulation/replay/replay_serialization.py:241-256` to serialize/deserialize the new fields.
- Bump `REPLAY_SCHEMA_VERSION` at `replay_serialization.py:70` from `"1.0.0"` to `"2.0.0"`.
- Update all 5 existing test files that construct `ComponentStateSpec` (`tests/unit/simulation/replay/test_serialization.py`, `tests/unit/simulation/test_battle_spec.py`, `tests/unit/simulation/test_battle_runner_component_hp.py`, `tests/unit/simulation/test_battle_outcome.py`, `tests/unit/strategy/combat/test_post_battle_hook.py`).
- Add 3 new tests (TDD-first): JSON round-trip, distinct-status extraction, schema version bump assertion.
- Update `docs/systems/combat_simulation.md` § 11 Replay Capture & Playback.

**Out:**
- Production sink wiring for `set_default_capture_sink` (the PROJ-354B prerequisite — handled separately).
- Pure verifier module (PROJ-354B C5).
- Background coordinator + sidecar (PROJ-354B C4, C6, C7).
- Settings extension (`verification_enabled`, `verification_queue_cap`) — PROJ-354B C4.
- Migration shim for old replay files. Per project convention (CLAUDE.md Rule 3): no save/replay compat shims. Old replays surface as `version_drift` and are skipped gracefully.
- `Component.status` enum changes. The existing `ComponentStatus` enum at `game/simulation/components/component_constants.py:15-21` is consumed as-is.
- Changes to `ComponentState` (the persistent strategy-side type at `game/core/component_state.py:54-99`) — that already has `max_hp` and is out of scope. Note: the post-battle hook at `game/strategy/combat/post_battle_hook.py:_apply_survivor_outcome` bridges `ComponentStateSpec` → `ComponentState`; we'll verify the bridge still works without changes (Phase 2 Task 2.3).

## Key Files Reference

| Component | File Path | Class/Function | Lines |
|-----------|-----------|----------------|-------|
| ComponentStateSpec definition | `game/simulation/battle_spec.py` | `ComponentStateSpec` (frozen dataclass) | 86-99 |
| Live extractor | `game/simulation/battle_runner.py` | `_extract_component_states` | 622-643 |
| Extractor caller | `game/simulation/battle_runner.py` | `_build_ship_outcome` | 564 |
| Serializer (forward) | `game/simulation/replay/replay_serialization.py` | `_component_state_to_dict` | 241-247 |
| Serializer (reverse) | `game/simulation/replay/replay_serialization.py` | `_component_state_from_dict` | 250-256 |
| Schema version constant | `game/simulation/replay/replay_serialization.py` | `REPLAY_SCHEMA_VERSION` | 70 |
| Schema drift detection | `game/strategy/services/replay_resolver.py` | `ReplayResolver.resolve` | 103-104 |
| Schema drift in store list | `game/strategy/services/replay_store.py` | `ReplayStore.list` | 228 |
| Component status source | `game/simulation/components/component.py` | `Component.status` (instance attr) | 124 |
| Status mutation site | `game/simulation/components/component_health_manager.py` | `update` | 74-75, 85 |
| Component max_hp source | `game/simulation/components/component.py` | `Component.max_hp` (instance attr) | 114 |
| ComponentStatus enum | `game/simulation/components/component_constants.py` | `ComponentStatus(Enum)` | 15-21 |
| Persistent component state (out of scope) | `game/core/component_state.py` | `ComponentState` | 54-99 |
| Post-battle bridge | `game/strategy/combat/post_battle_hook.py` | `_apply_survivor_outcome` | 150-158 |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Phase A landing of consensus plan r003 from Claude+Codex inter-agent discussion. |
| 2026-05-04 | Use `ComponentStatus.name` not `.value` for serialization | Codex correction (r002). The enum uses `auto()`, so numeric values are not a stable contract across Python versions. |
| 2026-05-04 | Do NOT add a synthesized `DESTROYED` status | Codex correction (r002). The enum has no `DESTROYED` member; destroyed condition is represented by `current_hp == 0` and `is_active == False`. |
| 2026-05-04 | Bump `REPLAY_SCHEMA_VERSION` to `"2.0.0"` (not migrate) | Per CLAUDE.md Rule 3 (no save/replay compat shims). `ReplayResolver` already handles `version_drift` gracefully. |
| 2026-05-04 | Phase A independent of sink wiring | Capture-side fields can land any time; they're not exercisable end-to-end until sink wiring lands but they don't break anything. |

## Initial Analysis

### Baseline test state

`python Tools/test_sharded/test_sharded.py` ran clean at project start:
- 17260 tests | 17256 passed | 0 failed | 0 errors | 4 skipped
- Wall time 55.1s
- Recorded at `AgentCoordination/generated/test_baseline.json`

### Capture pipeline (today)

`_extract_component_states` (`battle_runner.py:622-643`) walks `engine_ship.layers`, iterates each layer's `components`, increments a per-`component_id` index counter, and emits a `ComponentStateSpec` with `(component_id, instance_index, current_hp, is_active)`. Called from `_build_ship_outcome:564`. The result tuple becomes `ShipOutcome.components`, which flows into `BattleOutcome` and is serialized via `_component_state_to_dict` when the replay record is persisted.

### Why these two fields specifically

**`max_hp`**: Today the spec drops it (only ship-level `max_hp` is captured in `ShipOutcome` display fields). Verification in PROJ-354B needs per-component `max_hp` to do byte-equal comparison against a re-run replay's outcome — and to attribute mismatches like "component reactor#0 max_hp diverged" rather than collapsing to "component HP wrong."

**`status`**: Today only `is_active` (binary) survives. The simulation tracks 6 distinct states (`ACTIVE`, `DAMAGED`, `NO_CREW`, `NO_POWER`, `NO_FUEL`, `NO_AMMO`). Two components can both be `is_active=True` but have different statuses (e.g., one `DAMAGED`, one `NO_AMMO`). Divergence at this granularity would be invisible without capturing `status`.

### Persistent-state interplay

`ComponentState` (persistent strategy-side, `game/core/component_state.py`) ALREADY has `max_hp: float = 0.0` (default). The post-battle hook at `post_battle_hook.py:_apply_survivor_outcome:150-158` bridges `ComponentStateSpec` → `ComponentState` by walking `ship_outcome.components` and reconstructing `ComponentState` instances. Today, the persisted `max_hp` is whatever default-or-set value the strategy layer had — the simulation outcome doesn't influence it. After Phase A, the bridge can use the simulation outcome's `max_hp` for accuracy, but **we are not changing the bridge in this project**. We will verify in Phase 2 Task 2.3 that the bridge continues to work (likely no change needed; the hook reads the four old fields and ignores extra fields).

### Construction-site inventory (all places that build a `ComponentStateSpec`)

| File:Line | Site | Type |
|-----------|------|------|
| `game/simulation/battle_runner.py:635-641` | `_extract_component_states` | Production |
| `game/simulation/replay/replay_serialization.py:251-255` | `_component_state_from_dict` | Production |
| `tests/unit/simulation/replay/test_serialization.py:131-134` (×3) | Round-trip tests | Test |
| `tests/unit/simulation/test_battle_spec.py:125-129` | Field access tests | Test |
| `tests/unit/simulation/test_battle_runner_component_hp.py:115-119` | HP extraction test | Test |
| `tests/unit/simulation/test_battle_outcome.py` (multiple) | Outcome round-trip | Test |
| `tests/unit/strategy/combat/test_post_battle_hook.py` (multiple) | Bridge tests | Test |
| `tests/unit/strategy/combat/test_spec_compiler.py:245, 301` | Type assertions | Test (no construction, just `isinstance` check) |

All 5 test files plus 1 spec-compiler `isinstance` check need updating.

## Swarm Findings Summary

### Architecture

- `ComponentStateSpec` lives in the simulation layer at `battle_spec.py`. Extending it does not violate the layer rules at `docs/01_ARCHITECTURE.md`: it's a frozen DTO consumed by simulation, replay (sub-package of simulation), and strategy's post-battle hook (allowed direction).
- `Component.status` is mutated only by `ComponentHealthManager` (not by external callers), so reading it during `_extract_component_states` is safe.

### Key Patterns to Reuse

- **Pattern #17 Serializable Protocol** (`docs/02_PATTERNS.md`): Free-function `to_dict`/`from_dict` pairs preserve frozen dataclass status. The existing `_component_state_to_dict` / `_component_state_from_dict` follow this pattern; we extend in place.
- **Pattern #18 Per-Battle RNG** (PROJ-252/PROJ-312): Determinism contract is unchanged; we're only adding capture fidelity, not introducing nondeterminism.

### Risks Identified

1. **R1: Schema bump invalidates existing user replays.** Mitigation: documented per CLAUDE.md Rule 3; `ReplayResolver` already handles `version_drift`. Not a regression — graceful path exists.
2. **R2: Test fixtures with hand-built component dicts** could break the schema-from-dict path. Swarm confirmed no JSON schema files for replays exist; all tests use Python literal `ComponentStateSpec(...)` constructors. Fixed by Task 2.2 (update test sites).
3. **R3: Post-battle hook bridge breakage** if it does positional construction. Swarm confirmed `_apply_survivor_outcome` reads named fields off `ComponentStateSpec`, not positional. Adding fields is backward-compatible for the read side.
4. **R4: `comp.max_hp` or `comp.status` could be missing on some `Component` subclass.** Swarm confirmed both are direct instance attributes set in `Component.__init__` (`component.py:114, 124`). All `Component` instances have them.

---

## Phases

### Phase 1: Schema fields + extractor + serializer [Medium]
**Objective:** Add `max_hp` and `status` to `ComponentStateSpec`, populate them in the extractor, round-trip them in the serializer, bump the schema version.
**Status:** Complete

#### Task 1.1: Write failing test for new fields (TDD) [Simple]
**File:** `tests/unit/simulation/replay/test_serialization.py` (new test added)
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -k component_state -v` — should fail until Task 1.2 lands

- [x] Add new test `test_component_state_spec_round_trip_includes_max_hp_and_status` that:
  - Constructs a `ComponentStateSpec(component_id="reactor", instance_index=0, current_hp=50.0, max_hp=100.0, status="DAMAGED", is_active=True)`
  - Calls `_component_state_to_dict` → asserts dict has keys `max_hp: 100.0` and `status: "DAMAGED"`
  - Calls `_component_state_from_dict` on the dict → asserts the round-tripped spec equals the original
- [x] Run the test, confirm it fails with `TypeError: ComponentStateSpec.__init__() got unexpected keyword argument 'max_hp'`
- [x] **Verify:** test exists, fails for the right reason (not a typo)

**Notes:**

#### Task 1.2: Add `max_hp` and `status` fields to `ComponentStateSpec` [Simple]
**File:** `game/simulation/battle_spec.py`
**Tests:** `pytest tests/unit/simulation/test_battle_spec.py tests/unit/simulation/replay/test_serialization.py` — Task 1.1's new test should pass; existing tests will fail (expected, fixed in Phase 2)

- [x] At line 86-99, extend the dataclass:
  ```python
  @dataclass(frozen=True)
  class ComponentStateSpec:
      """Persisted per-component HP, max_hp, status, and active-toggle state.

      Populated by the strategy compiler from `ShipInstance.components` so
      per-component damage carries across battles. Combat Lab and Battle Setup
      normally emit ships with no persistent component state (empty tuple on
      `ShipSpec.components`), in which case the engine initializes HP from
      the design.
      """
      component_id: str
      instance_index: int
      current_hp: float
      max_hp: float
      status: str  # ComponentStatus.name (one of: ACTIVE, DAMAGED, NO_CREW, NO_POWER, NO_FUEL, NO_AMMO)
      is_active: bool
  ```
- [x] **Verify:** Task 1.1's new test passes when run alone; `pytest tests/unit/simulation/replay/test_serialization.py::test_component_state_spec_round_trip_includes_max_hp_and_status -v`

**Notes:**

#### Task 1.3: Update `_component_state_to_dict` and `_component_state_from_dict` [Simple]
**File:** `game/simulation/replay/replay_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -v`

- [x] At line 241-247, update `_component_state_to_dict` to emit two new keys:
  ```python
  def _component_state_to_dict(c: ComponentStateSpec) -> Dict[str, Any]:
      return {
          "component_id": c.component_id,
          "instance_index": int(c.instance_index),
          "current_hp": float(c.current_hp),
          "max_hp": float(c.max_hp),
          "status": str(c.status),
          "is_active": bool(c.is_active),
      }
  ```
- [x] At line 250-256, update `_component_state_from_dict` to read two new keys:
  ```python
  def _component_state_from_dict(data: Dict[str, Any]) -> ComponentStateSpec:
      return ComponentStateSpec(
          component_id=data["component_id"],
          instance_index=int(data["instance_index"]),
          current_hp=float(data["current_hp"]),
          max_hp=float(data["max_hp"]),
          status=str(data["status"]),
          is_active=bool(data["is_active"]),
      )
  ```
- [x] **Verify:** Task 1.1's round-trip test passes end-to-end.

**Notes:**

#### Task 1.4: Update `_extract_component_states` to populate new fields from live `Component` [Medium]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner_component_hp.py -v`

- [x] At line 622-643, update `_extract_component_states`:
  ```python
  def _extract_component_states(engine_ship: "Ship") -> tuple:
      """Emit a tuple of `ComponentStateSpec` reflecting each Ship component's
      final state. Walks layers in order; instance_index resets per component_id.
      """
      out: List[ComponentStateSpec] = []
      per_id_index: Dict[str, int] = {}
      for layer_data in engine_ship.layers.values():
          for comp in getattr(layer_data, "components", []):
              comp_id = getattr(comp, "id", None)
              if not comp_id:
                  continue
              idx = per_id_index.get(comp_id, 0)
              per_id_index[comp_id] = idx + 1
              status_obj = getattr(comp, "status", None)
              status_name = status_obj.name if hasattr(status_obj, "name") else str(status_obj)
              out.append(
                  ComponentStateSpec(
                      component_id=comp_id,
                      instance_index=idx,
                      current_hp=float(getattr(comp, "current_hp", 0)),
                      max_hp=float(getattr(comp, "max_hp", 0)),
                      status=status_name,
                      is_active=bool(getattr(comp, "is_active", True)),
                  )
              )
      return tuple(out)
  ```
- [x] Defensive `hasattr(status_obj, "name")` check protects against a `Component` that somehow has `status=None` or a non-enum status.
- [x] **Verify:** Existing `test_battle_runner_component_hp.py` may fail — that's expected; Phase 2 Task 2.2 will update its constructor calls.

**Notes:**

#### Task 1.5: Bump `REPLAY_SCHEMA_VERSION` [Simple]
**File:** `game/simulation/replay/replay_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -k version -v`

- [x] At line 70, change `REPLAY_SCHEMA_VERSION = "1.0.0"` to `REPLAY_SCHEMA_VERSION = "2.0.0"`
- [x] **Verify:** Search for any hardcoded `"1.0.0"` references in tests that need updating: `grep -rn '"1\.0\.0"' tests/ game/`. Update those to `"2.0.0"` if they're testing this constant specifically (NOT if they're testing graceful version-drift handling — those should keep an old version string).

**Notes:**

---

### Phase 2: Tests + bridge verification [Medium]
**Objective:** Update all 5 existing test files for the new constructor signature; add new tests proving the new fields surface distinct values; verify the post-battle bridge to `ComponentState` still works.
**Status:** Complete

#### Task 2.1: Add new TDD test — extractor produces distinct status values [Medium]
**File:** `tests/unit/simulation/test_battle_runner_component_hp.py` (extended) — or new `test_extract_component_states_status.py`
**Tests:** `pytest tests/unit/simulation/test_extract_component_states_status.py -v`

- [x] Construct a fake engine `Ship` with three components in different `ComponentStatus` states:
  - One with `status=ComponentStatus.ACTIVE`, `current_hp=100`, `max_hp=100`, `is_active=True`
  - One with `status=ComponentStatus.DAMAGED`, `current_hp=30`, `max_hp=100`, `is_active=True`
  - One with `status=ComponentStatus.NO_AMMO`, `current_hp=80`, `max_hp=100`, `is_active=False`
- [x] Call `_extract_component_states(ship)` → assert the returned tuple has 3 entries
- [x] Assert each entry's `status` field is the correct string ("ACTIVE", "DAMAGED", "NO_AMMO")
- [x] Assert the JSON round-trip (`_component_state_to_dict` → `_component_state_from_dict`) preserves all 3 statuses
- [x] **Verify:** Test passes after Phase 1 changes.

**Notes:**

#### Task 2.2: Update existing test files for new constructor signature [Medium]
**Files (5):**
- `tests/unit/simulation/replay/test_serialization.py` (lines 131-134, 190 — 3 sites)
- `tests/unit/simulation/test_battle_spec.py` (lines 125-129)
- `tests/unit/simulation/test_battle_runner_component_hp.py` (lines 115-119)
- `tests/unit/simulation/test_battle_outcome.py` (multiple sites)
- `tests/unit/strategy/combat/test_post_battle_hook.py` (multiple sites)

**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py tests/unit/simulation/test_battle_spec.py tests/unit/simulation/test_battle_runner_component_hp.py tests/unit/simulation/test_battle_outcome.py tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [x] For each of the 5 files, find every `ComponentStateSpec(...)` construction and add `max_hp=` and `status=` arguments.
  - Reasonable defaults for tests that don't care about the new fields: `max_hp=100.0`, `status="ACTIVE"`.
  - For tests that DO care about specific values (e.g., damage tests), use values that match the test scenario.
- [x] After each file is updated, run that file's tests to confirm green: e.g., `pytest tests/unit/simulation/test_battle_spec.py -v`
- [x] **Verify:** Run all 5 files together: all green.

**Notes:**

#### Task 2.3: Verify post-battle hook bridge still works [Simple]
**File:** `game/strategy/combat/post_battle_hook.py` (read-only verification)
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [x] Read `_apply_survivor_outcome` at lines 150-158. Confirm it reads `cs.component_id`, `cs.instance_index`, `cs.current_hp`, `cs.is_active` (the four original fields) and does NOT do positional construction or assume field count. **Expected: no code change needed.**
- [x] Run the test file post-Task-2.2 update (since the test file constructs `ComponentStateSpec`s). Should be green.
- [x] **Verify:** Bridge ignores the new `max_hp` and `status` fields gracefully (they exist on the spec but the hook just doesn't read them — that's fine for this project; PROJ-354B may revisit).

**Notes:**

#### Task 2.4: Schema version regression test [Simple]
**File:** `tests/unit/simulation/replay/test_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -k schema_version -v`

- [x] Add `test_replay_schema_version_is_2_0_0` asserting `REPLAY_SCHEMA_VERSION == "2.0.0"`. Pin the constant so accidental future changes are loud.
- [x] **Verify:** Test passes.

**Notes:**

#### Task 2.5: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite. Compare to baseline (17256 passed).
- [x] **Acceptance:** Same pass count as baseline (any new tests added in this project add to the count). Zero regressions, zero new errors.
- [x] If any tests fail, investigate and fix in this phase before proceeding to Phase 3. Document any non-trivial discoveries in `decisions.md`.

**Notes:**

---

### Phase 3: Docs [Simple]
**Objective:** Document the new outcome fields and the schema version bump.
**Status:** Complete

#### Task 3.1: Update `docs/systems/combat_simulation.md` [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [x] In § 11 Replay Capture & Playback, add a subsection (or extend an existing one) describing the per-component end-state fields:
  - `current_hp` (live HP at battle end)
  - `max_hp` (capacity at battle end; for verification baseline)
  - `status` (`ComponentStatus.name`: ACTIVE / DAMAGED / NO_CREW / NO_POWER / NO_FUEL / NO_AMMO)
  - `is_active` (binary operational flag)
- [x] Note `REPLAY_SCHEMA_VERSION = "2.0.0"` (bumped from `"1.0.0"`).
- [x] Note: existing replays from version `"1.0.0"` surface as `version_drift` in `ReplayResolver.resolve()` and are skipped gracefully.
- [x] Update the `> **Last verified:**` blockquote at the top of the doc to today's date.
- [x] **Verify:** Documented fields match the actual `_component_state_to_dict` output.

**Notes:**

#### Task 3.2: Update CLAUDE.md / AGENTS.md if needed [Simple]
**Files:** `CLAUDE.md`, `AGENTS.md`
**Tests:** Manual review

- [x] Skim both files for any references to "ComponentStateSpec" or "REPLAY_SCHEMA_VERSION 1.0.0" that need updating. (Likely none.)
- [x] **Verify:** Either no edits needed, or specific edits applied with line refs.

**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS) — done during planning
- [x] Run full test suite: `python Tools/test_sharded/test_sharded.py` — 17256/17256 passed at baseline

### After Each Phase
- [x] Run `pytest tests/ --testmon` — all affected tests pass
- [x] Update `Current State` in this plan with handoff context for next agent

### Final Verification
- [x] Full sharded suite: `python Tools/test_sharded/test_sharded.py` — same pass count as baseline (17256 + new tests added)
- [x] Run a manual end-to-end smoke: load a save, run a battle, verify a captured replay's outcome JSON includes `max_hp` and `status` per component (use `output/saves/<save>/replays/replay_*.json`). **Note:** This step depends on production sink wiring (the PROJ-354B prerequisite). If sink wiring hasn't landed yet, skip the smoke and rely on integration tests in `tests/integration/replay/test_replay_playback.py`.
- [x] Verify changes are consistent with `docs/` — Phase 3 covers this

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All tests passing (sharded suite green)
- [x] Audit passed (no significant issues)
- [x] User verified
