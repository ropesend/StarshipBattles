# PROJ-354A Review: Replay Component End-State Fidelity

**Review Type:** code

**Review Mode:** full (not lightweight — no Coverage block)

**Scope:** `game/simulation/battle_spec.py`, `game/simulation/battle_runner.py`, `game/simulation/replay/replay_serialization.py`, `game/strategy/combat/spec_compiler.py`, 5 test files, `docs/systems/combat_simulation.md` § 11

**Parent Request:** None (not a follow-up)

**Commit:** cd8ebf5e5

**Completed:** 2026-05-05T06:15:00Z

---

## Findings

### Finding MAJ-001 — Post-battle hook ignores outcome `max_hp` and `status`; captured fidelity lost at bridge

**Severity:** MAJ

**File:** `game/strategy/combat/post_battle_hook.py:135-158`

**Description:**

`_apply_survivor_outcome` writes `ShipOutcome.components` (a `tuple[ComponentStateSpec, ...]`) back into `ShipInstance.components`. After PROJ-354A, each `ComponentStateSpec` now carries `max_hp` and `status` populated by the live extractor at battle end. However, the bridge ignores both new fields:

- `max_hp` is sourced from `prior_max_hp` — a pre-battle snapshot of `instance.components` — **not** from `cs.max_hp` in the outcome. If a modifier reshaped a component's max_hp during battle, the fidelity gain from PROJ-354A is discarded at this write-back point; the strategy-side `ShipInstance` will carry the pre-battle max_hp, not the end-state max_hp.

- `status` (the `ComponentStatus.name` string like `"DAMAGED"`, `"NO_CREW"`) is **completely discarded**. `ComponentState` (the strategy-side dataclass in `game/core/component_state.py`) has no `status` field at all — only `component_id`, `instance_index`, `current_hp`, `max_hp`, and `is_active`. So the hook cannot preserve `status` even if it wanted to.

While this doesn't crash (graceful ignore per instruction #5), it means the end-state fidelity data that PROJ-354A captures in the replay record (`max_hp` and `status`) is **not** propagated to the persistent strategy-layer `ShipInstance.components`. Only the replay file itself carries the full fidelity. PROJ-354B's verifier comparing capture vs re-run will still work (both paths read from the same outcome), but if PROJ-354B needs the strategy-side state to match for any cross-turn persistence test, the `max_hp` staleness could be a problem.

**Remediation:** Either (a) accept that the bridge intentionally ignores these fields (strategy-side `ComponentState` is damage-only, not status-aware) and document this as a deliberate design choice, or (b) add `status: str = "ACTIVE"` to `ComponentState` and read `cs.max_hp` + `cs.status` from the outcome in `_apply_survivor_outcome`. Option (b) is the correct path if PROJ-354B needs `ShipInstance` to carry end-state fidelity rather than just damage.

**Line refs:**
- `post_battle_hook.py:135-158` — `_apply_survivor_outcome` ignores `cs.max_hp`, `cs.status`
- `post_battle_hook.py:141-146` — stale comment "ComponentStateSpec doesn't carry max_hp today" (now false)
- `game/core/component_state.py:54-70` — `ComponentState` has no `status` field

---

### Finding MAJ-002 — Stale comment in `_apply_survivor_outcome` after PROJ-354A

**Severity:** MAJ

**File:** `game/strategy/combat/post_battle_hook.py:143-145`

**Description:**

The comment block in `_apply_survivor_outcome` reads:

```python
# Preserve max_hp per instance from the pre-battle state so the
# rebuilt ComponentState stays self-describing. ComponentStateSpec
# doesn't carry max_hp today, but the instance's existing dict does.
```

The claim "ComponentStateSpec doesn't carry max_hp today" is **now false** after PROJ-354A. `ComponentStateSpec` gained `max_hp` as a required field. The comment is misleading — it implies `max_hp` was intentionally sourced from `prior_max_hp` only because `ComponentStateSpec` lacked the field. Now that `cs.max_hp` exists, the hook has a choice and should document whether ignoring `cs.max_hp` is intentional or an oversight.

**Remediation:** Update the comment to explain the design choice: either "we intentionally preserve pre-battle max_hp because the strategy layer doesn't track modifier-shaped caps" or switch to using `cs.max_hp` from the outcome.

---

### Finding MAJ-003 — `max_hp` from outcome ignored at post_battle_hook (same root cause as MAJ-001)

**Severity:** MAJ

**File:** `game/strategy/combat/post_battle_hook.py:157`

**Description:**

`_apply_survivor_outcome` constructs a new `ComponentState` with `max_hp=prior_max_hp.get(key, 0.0)`. The `cs.max_hp` value from the `ShipOutcome` (populated by `_extract_component_states` reading the live engine `Component.max_hp`) is present on the `ComponentStateSpec` but never read here. The `current_hp` *is* read from `cs.current_hp` — so damage persists correctly across battles regardless. But `max_hp` fidelity (important for PROJ-354B verification of modifier-shaped caps) is lost.

**Remediation:** If PROJ-354B needs `ShipInstance` to carry post-battle `max_hp`, change line 157 to `max_hp=cs.max_hp`. If not, add a comment explaining the intentional divergence.

---

### Finding MIN-001 — `status='ACTIVE'` default in spec_compiler is safe but low-fidelity

**Severity:** MIN

**File:** `game/strategy/combat/spec_compiler.py:405`

**Description:**

The strategy spec compiler sets `status="ACTIVE"` for every component during pre-battle compilation because "the persistent strategy-side ComponentState does not track per-component status — only HP and active flag" (comment at line 394-398). This is correct: the strategy layer stores `ComponentState` which has no status field, and the engine will reconcile real `ComponentStatus` (e.g., `DAMAGED` at <50% HP) once ticks start.

However, there is one edge case: if a ship enters battle with a component at 0 HP (fully destroyed in a prior battle), the spec emits `status="ACTIVE"` for that component. The engine will immediately reconcile this on the first tick that evaluates component status, so correctness is preserved — the extractor at battle end will report the actual status. But a replay visualizer that reads the *spec's* component status during pre-tick rendering would briefly see "ACTIVE" for a 0-HP component.

This is **not** a correctness bug — the end-state extractor is authoritative — but it means the spec-level status string is a lie for components starting at 0 HP. The extractor overwrites it at capture time, so the replay record carries truth.

**Remediation:** Acceptable as-is. If desired, the compiler could set `status="DAMAGED"` when `cs.current_hp / cs.max_hp < 0.5` to give a better pre-tick approximation, but this adds complexity without a correctness gain. Document the "compile-time approximation" nature of spec-level status.

---

### Finding MIN-002 — `ComponentStateSpec` constructor inventory is complete

**Severity:** INFO (verified negative finding)

**Files:** `game/strategy/combat/spec_compiler.py:400`, `game/simulation/battle_runner.py:646`, `game/simulation/replay/replay_serialization.py:253`

**Description:**

A grep for `ComponentStateSpec(` in all production files under `game/` found exactly 3 constructors:

1. **`spec_compiler.py:400`** — Strategy pre-battle compiler (`_ship_spec_from_instance`). Sets `status="ACTIVE"` as default.
2. **`battle_runner.py:646`** — Live post-battle extractor (`_extract_component_states`). Reads actual `comp.status.name` and `comp.max_hp` from engine components.
3. **`replay_serialization.py:253`** — Deserializer (`_component_state_from_dict`). Reconstructs from JSON dict (replay load path).

All constructors are accounted for. No missed sites in production code. Tests have additional constructors but those are fixture/setup sites, not production paths.

---

### Finding NIT-001 — `REPLAY_SCHEMA_VERSION = "2.0.0"` confirmed; version_drift gate correct

**Severity:** INFO (verified negative finding)

**Files:** `game/simulation/replay/replay_serialization.py:70`, `game/strategy/services/replay_resolver.py:102-104`

**Description:**

- `REPLAY_SCHEMA_VERSION` is exactly `"2.0.0"` at `replay_serialization.py:70`.
- `ReplayResolver.resolve()` at `replay_resolver.py:102-104` compares `record.schema_version != REPLAY_SCHEMA_VERSION` and returns `ReplayLookup(found=False, reason="version_drift")`.
- `ReplayRecord.is_current_schema()` at `replay_record.py:84-90` uses the same comparison.
- `ReplayStore` at `replay_store.py:246` gates on the same check, skipping outdated records.
- The UI at `event_log_window.py:38` maps `"version_drift"` to a user-facing tooltip.
- No compat shims exist — `_component_state_from_dict` at `replay_serialization.py:252-260` expects the new shape (5 keys). Old v1.0.0 dicts missing `max_hp` or `status` would KeyError on deserialization, which is intentional per the "no compat shims" policy.

Test `test_replay_schema_version_is_2_0_0` at `test_serialization.py:579-585` asserts this constant.

---

### Finding NIT-002 — `max_hp` and `status` round-trip correctly through JSON serialization

**Severity:** INFO (verified positive finding)

**Files:** `game/simulation/replay/replay_serialization.py:241-260`

**Description:**

`_component_state_to_dict` emits both `max_hp` (as float) and `status` (as string). `_component_state_from_dict` reads both back. The round-trip preserves `max_hp` via `float()` coercion and `status` via `str()` coercion.

Tests confirming this:
- `test_component_state_spec_round_trip_includes_max_hp_and_status` at `test_serialization.py:551-576`
- `test_extract_component_states_populates_max_hp_and_status_distinctly` at `test_battle_runner_component_hp.py:276-343`

The `status` field is serialized as `ComponentStatus.name` (string, e.g. `"DAMAGED"`), not `.value` (auto() numeric). The docstring at `battle_spec.py:99-100` and the extractor at `battle_runner.py:641-644` both document this choice — `auto()` values are not stable across Python versions. Six ComponentStatus enum members exist (`ACTIVE`, `DAMAGED`, `NO_CREW`, `NO_POWER`, `NO_FUEL`, `NO_AMMO`); no `DESTROYED` member (destruction is `current_hp == 0` + `is_active is False`). All correct.

---

### Finding NIT-003 — Post-battle hook gracefully ignores new fields (no crash)

**Severity:** INFO (verified positive finding)

**Files:** `game/strategy/combat/post_battle_hook.py:149-158`

**Description:**

`_apply_survivor_outcome` iterates `ship_outcome.components` and reads only `cs.component_id`, `cs.instance_index`, `cs.current_hp`, and `cs.is_active` from each `ComponentStateSpec`. The new `cs.max_hp` and `cs.status` fields are never dereferenced in this function, so the PROJ-354A field additions do not cause any `AttributeError`, `KeyError`, or type mismatch at the bridge. The hook continues to work correctly for its existing purpose (persisting per-component HP damage).

The bridge is not *correct* in the sense of passing through full fidelity (see MAJ-001/MAJ-002/MAJ-003), but it does not regress — existing behavior is preserved.

---

### Finding MIN-003 — `battle_runner.py:688` exceeds 500 LOC ceiling

**Severity:** MIN (advisory)

**File:** `game/simulation/battle_runner.py`

**Description:**

`battle_runner.py` is 688 lines. The project convention (`AGENTS.md`) specifies a 500 LOC ceiling for production files ("When a file approaches 500 lines, split into single-responsibility sub-modules"). This file predates PROJ-354A but was not split during this change. The `_extract_component_states` function (34 lines) and `_apply_spec_components_to_ship` (30 lines) are reasonable extraction candidates.

**Remediation:** Not blocking for PROJ-354A but should be tracked for a future cleanup pass.
