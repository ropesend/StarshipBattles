# Phase 2: ReplaySpec Serialization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-312 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build a JSON-safe parallel data model that mirrors `BattleSpec`
and `BattleOutcome`. Add `to_dict` / `from_dict` to every existing simulation
DTO that doesn't already have them, and create a new
`game/simulation/replay/` package containing `ReplaySpec`, `ReplayOutcome`,
and `ReplayRecord` (the persisted form). Phase 2 produces no behavior change
— it only adds serialization.

**Depends on:** Phase 1 (determinism baseline) complete and passing.

---

## Tasks

### Task 2.1: Serialize boundary types [Simple]
**File:** `game/simulation/combat/boundary.py`
**Tests:** `pytest tests/unit/simulation/replay/test_boundary_serialization.py`

Add `to_dict` / `from_dict` to the three concrete boundary classes plus a
discriminator-based load helper.

- [ ] Add `to_dict(self) -> Dict[str, Any]` to `RectBoundary` (line 104). Include
      `"type": "rect"`, dimensions, center, and `exit_policy.value`.
- [ ] Add `to_dict` to `CircleBoundary` (line 155). Include `"type": "circle"`,
      `center`, `radius`, `exit_policy.value`.
- [ ] Add `to_dict` to `UnboundedRegion` (line 189). Include `"type":
      "unbounded"`, `exit_policy.value`.
- [ ] Add a module-level `boundary_from_dict(data) -> BoundaryRegion` dispatch
      function keyed off `"type"`. Mirror the pattern in
      `end_condition_from_dict` at
      `game/simulation/systems/battle_end_conditions.py:482-496`.
- [ ] Add `from_dict` `@classmethod`s to each concrete class.
- [ ] Update `game/simulation/__init__.py` to export `boundary_from_dict`.

**Notes:** [Filled during implementation]

### Task 2.2: Serialize ModifierStack and ModifierEntry [Simple]
**File:** `game/simulation/combat/modifier_stack.py`
**Tests:** `pytest tests/unit/simulation/replay/test_modifier_stack_serialization.py`

`ModifierEffect.to_dict` already exists at
`game/simulation/combat/modifier_effects.py:82`. Wrap it.

- [ ] Add `to_dict(self) -> Dict[str, Any]` to `ModifierEntry` (line 33).
      Shape: `{"source": ..., "stack_group": ..., "effect": effect.to_dict()}`.
- [ ] Add `from_dict(cls, data, *, ...) -> ModifierEntry` classmethod. Use the
      existing `ModifierEffect.from_dict`.
- [ ] Add `to_dict(self) -> Dict[str, Any]` to `ModifierStack` (line 53).
      Shape: `{"per_team": {team_id: [entry, ...]}, "global_": [entry, ...]}`.
- [ ] Add `from_dict(cls, data) -> ModifierStack` classmethod.
- [ ] Verify `ModifierEffect.from_dict` exists; if not, add it (mirroring
      `to_dict`).

**Notes:** [Filled during implementation]

### Task 2.3: Serialize BattleSpec + nested DTOs [Medium]
**File:** `game/simulation/battle_spec.py`
**Tests:** `pytest tests/unit/simulation/replay/test_battle_spec_serialization.py`

Add static `to_dict` / classmethod `from_dict` to every spec DTO. Strip
`post_battle_hook` (always serializes to `None`); serialize `instance_ref`
to `None` (Phase 3 fills it from `ShipInstance` at capture time).

- [ ] Add `to_dict` / `from_dict` to `EntryVector` (line 56).
- [ ] Add `to_dict` / `from_dict` to `CombatPolicies` (line 68). Reuse
      existing `CombatPolicy.to_dict` / `from_dict` at
      `game/strategy/data/fleet_hierarchy.py:71-89`.
- [ ] Add `to_dict` / `from_dict` to `ComponentStateSpec` (line 86). Delegate
      to `ComponentState.to_dict` / `from_dict` at
      `game/core/component_state.py:62-79` where shapes match.
- [ ] Add `to_dict` / `from_dict` to `ShipSpec` (line 103). **Treat
      `instance_ref` as opaque — set to `None` on `to_dict`, expect `None` on
      `from_dict`. Phase 3 introduces a separate `ReplayShipSpec` carrying
      the captured `ShipInstance` snapshot.**
- [ ] Add `to_dict` / `from_dict` to `SquadronSpec` (line 140).
- [ ] Add `to_dict` / `from_dict` to `TaskForceSpec` (line 149).
- [ ] Add `to_dict` / `from_dict` to `TeamSpec` (line 164).
- [ ] Add `to_dict` / `from_dict` to `BattleSpec` (line 183).
      `post_battle_hook` always serializes to `None`. `boundary` /
      `modifier_stack` / `end_condition` use the helpers added in 2.1 / 2.2 /
      existing `IEndCondition`. `telemetry_level` serializes via
      `TelemetryLevel.name` (IntEnum).
- [ ] Round-trip test: build a representative `BattleSpec` using
      `tests/fixtures/battle.py::make_minimal_spec`,
      `to_dict → json.dumps → json.loads → from_dict`, assert structural
      equality (all fields except hook + instance_ref match).

**Notes:** [Filled during implementation]

### Task 2.4: Serialize BattleOutcome + nested DTOs [Medium]
**File:** `game/simulation/battle_outcome.py`
**Tests:** `pytest tests/unit/simulation/replay/test_battle_outcome_serialization.py`

- [ ] Add `to_dict` / `from_dict` to `ModifierApplication` (line 70).
- [ ] Add `to_dict` / `from_dict` to `HitRecord` (line 83).
- [ ] Add `to_dict` / `from_dict` to `WeaponSummary` (line 98).
- [ ] Add `to_dict` / `from_dict` to `ShipStats` (line 108).
- [ ] Add `to_dict` / `from_dict` to `ShipOutcome` (line 123). Serialize
      `ShipStatus` (line 35) and `EndReason` (line 44) via `.name`.
- [ ] Add `to_dict` / `from_dict` to `TeamOutcome` (line 156).
- [ ] Add `to_dict` / `from_dict` to `BattleOutcome` (line 170). Serialize
      `telemetry_level` via `.name`.
- [ ] Round-trip test: capture a real `BattleOutcome` from a known seeded
      battle, `to_dict → json → from_dict`, assert deep equality.

**Notes:** [Filled during implementation]

### Task 2.5: Create the `game/simulation/replay/` package [Medium]
**File:** `game/simulation/replay/__init__.py`, `replay_spec.py`,
`replay_outcome.py`, `replay_record.py`, `replay_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_replay_spec_roundtrip.py
tests/unit/simulation/replay/test_replay_outcome_roundtrip.py`

The replay package wraps the simulation DTOs with replay-specific
extensions (notably the `ShipInstance` snapshot replacing `instance_ref`).

- [ ] Create `game/simulation/replay/__init__.py`. Export `ReplaySpec`,
      `ReplayOutcome`, `ReplayRecord`, schema-version constant.
- [ ] Create `replay_serialization.py` housing helpers shared across the
      package (e.g., a `serialize_optional_enum`, `current_components_hash`
      hash helper, version-string constant `REPLAY_SCHEMA_VERSION = "1.0.0"`).
- [ ] Create `replay_spec.py` containing:
      - `ReplayComponentStateSpec` mirroring `ComponentStateSpec` (no
        change but kept locally for forward evolution).
      - `ReplayShipSpec` mirroring `ShipSpec` but with
        `instance_snapshot: Optional[Dict[str, Any]]` (output of
        `ShipInstanceSerializer.to_dict`) replacing `instance_ref`. Includes
        `team_id`.
      - `ReplaySquadronSpec`, `ReplayTaskForceSpec`, `ReplayTeamSpec` mirrors.
      - `ReplaySpec` with `schema_version`, `seed`, `telemetry_level: str`,
        `boundary: Dict`, `end_condition: Dict`, `absolute_max_ticks`,
        `teams: Tuple[ReplayTeamSpec, ...]`, `modifier_stack: Dict`. **No
        `post_battle_hook`.**
      - `to_dict` / `from_dict` on every class.
      - Conversion helpers: `from_battle_spec(spec, ship_instance_lookup) ->
        ReplaySpec` and `to_battle_spec(replay_spec, *, registries) ->
        BattleSpec`. The lookup callable resolves a ShipSpec.instance_ref to
        a serialized `ShipInstance` snapshot dict at capture time.
      - On reconstruction (`to_battle_spec`), `instance_ref` is rebuilt from
        the snapshot via `ShipInstanceSerializer.from_dict(...)`. The
        rebuilt `BattleSpec` carries a no-op `post_battle_hook`.
- [ ] Create `replay_outcome.py` with `ReplayOutcome` — likely thin wrapper
      around `BattleOutcome.to_dict / from_dict` with explicit
      `schema_version`. Justify either re-using `BattleOutcome` directly or
      mirroring it.
- [ ] Create `replay_record.py` with `ReplayRecord`:
      ```python
      @dataclass(frozen=True)
      class ReplayRecord:
          schema_version: str
          replay_id: str          # uuid4
          captured_at: str        # ISO 8601
          sector_name: Optional[str]
          sector_coords: Optional[Tuple[int, int]]
          turn_number: Optional[int]
          participating_empires: Tuple[str, ...]
          components_registry_hash: str
          spec: ReplaySpec
          outcome: ReplayOutcome
      ```
      Add `to_dict` / `from_dict` covering every field.
- [ ] Round-trip test: `ReplayRecord` ↔ JSON ↔ `ReplayRecord` with deep
      equality. Include a generated `ShipInstance` snapshot through the
      `instance_snapshot` field.

**Notes:** [Filled during implementation]

### Task 2.6: Determinism contract — replay_spec → battle_spec → engine [Medium]
**File:** `tests/integration/replay/test_replay_spec_determinism.py` (NEW)
**Tests:** `pytest tests/integration/replay/test_replay_spec_determinism.py`

Prove the round-trip preserves the determinism contract.

- [ ] Build a representative `BattleSpec` (2-team scenario via
      `make_minimal_spec`).
- [ ] Snapshot ship instances into a synthetic
      `ship_instance_lookup` fixture.
- [ ] `ReplaySpec.from_battle_spec(...)` → JSON → `from_dict` →
      `to_battle_spec(...)`.
- [ ] Run both the original and the reconstructed spec through `run_battle`.
- [ ] Assert the two `BattleOutcome`s have identical `seed`, `duration_ticks`,
      `end_reason`, and per-ship `final_position`/`final_angle` (allow ε for
      float drift if needed; ideally bit-identical).

**Notes:** [Filled during implementation]

### Task 2.7: Phase 2 sharded suite verification [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes. Record new test count in plan.md "Current
      State Snapshot".

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Round-trip tests cover every new `to_dict` / `from_dict`
- [ ] Determinism re-run test (Task 2.6) is green
- [ ] No simulation hot-path code paths changed (Phase 2 is serialization-only)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
