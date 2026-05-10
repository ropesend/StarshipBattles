# PROJ-354A: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Origin

This project implements C1–C3 of the consensus plan at:
`AgentCoordination/Scratchpad/Discussion/20260505T034554Z_replay-end-state-verification/plans/replay_end_state_verification_r003.md`

That plan was the output of a 5-message inter-agent discussion between Claude and Codex (arc01_001 through arc01_005), with two corrections applied during the discussion:

1. **Trigger location**: Codex caught that verification belongs at the post-capture/post-persist path (live battle end) rather than the user-clicks-Replay path. Out of scope for PROJ-354A; informs PROJ-354B.
2. **`ComponentStatus` enum members**: Codex caught that the actual enum is `ACTIVE`/`DAMAGED`/`NO_CREW`/`NO_POWER`/`NO_FUEL`/`NO_AMMO` (with `auto()` numeric values), not `ACTIVE`/`DAMAGED`/`DESTROYED` as the original plan claimed. Serialize via `.name`, not `.value`. **This correction directly drives PROJ-354A's design.**

## Initial Analysis

### What's wrong today

The `_extract_component_states` function (`game/simulation/battle_runner.py:622-643`) emits a `ComponentStateSpec` per component with only four fields: `component_id`, `instance_index`, `current_hp`, `is_active`. Two limitations:

- **`max_hp` is dropped**: only ship-level `max_hp` is captured (in `ShipOutcome` display fields). Per-component max_hp is design-time information, technically reconstructible from spec — but expensive to look up at compare-time, and a moddable game where components might have run-time-modified max_hp (via stat modifiers) makes the "look it up from design" approach unreliable.
- **`status` collapses to `is_active`**: `Component.status` carries 6 distinct enum values; `is_active=True/False` collapses (`ACTIVE`, `DAMAGED`) → True and (`NO_CREW`, `NO_POWER`, `NO_FUEL`, `NO_AMMO`) → False. Two damage scenarios that produce different statuses but same `is_active` would be invisible to verification.

### What end-state verification needs (per consensus plan)

PROJ-354B will compare `record.outcome.data` (captured live battle outcome) byte-for-byte against `battle_outcome_to_dict(replayed_outcome)` (the replay's outcome). For that comparison to be both **diagnostic** (mismatch tells you which field differs) and **complete** (catches all per-component state divergence), the captured per-component state must include `max_hp` and `status`.

PROJ-354A is the prerequisite work: capture more per-component data so the verifier (PROJ-354B) has something fine-grained to compare.

## Swarm Findings Summary

Three Explore agents ran during planning. Reports in `findings/` (not yet generated).

### Architecture

- `ComponentStateSpec` lives in the simulation layer (`game/simulation/battle_spec.py`). Adding fields does not violate `docs/01_ARCHITECTURE.md` layer rules. Consumers are simulation, replay (sub-package), and strategy's post-battle hook (allowed direction).
- `Component.status` is mutated only by `ComponentHealthManager`. Reading it during `_extract_component_states` is safe — by the time the extractor runs, the battle has ended and the engine is settled.
- The strategy-side persistent `ComponentState` (`game/core/component_state.py:54-99`) already has `max_hp` (default 0.0) but no `status`. **Out of scope for this project** — adding `status` to the persistent type is a separate concern that would also require save-format migration.

### Key Patterns to Reuse

- **Pattern #17 Serializable Protocol** (`docs/02_PATTERNS.md`): Free-function `to_dict`/`from_dict` pairs preserve frozen dataclass status. The existing `_component_state_to_dict` / `_component_state_from_dict` follow this; we extend in place.
- **Pattern #18 Per-Battle RNG** (PROJ-252/PROJ-312): Determinism contract is unchanged; we're only adding capture fidelity.
- **PROJ-307 Documentation Freshness Timestamps**: Phase 3 includes the `> **Last verified:**` blockquote update on `docs/systems/combat_simulation.md`.
- **PROJ-311 Return Type Annotation Backfill**: Any new helpers added (none planned) must have return-type annotations.

### Dependencies & Risks

1. **R1: Schema bump invalidates existing user replays.** Mitigation: project convention (CLAUDE.md Rule 3) — no save/replay compat shims. `ReplayResolver.resolve()` (`replay_resolver.py:103-104`) already returns `version_drift` reason for old records, surfaced by UI as a "different game version" dialog. Pre-release moddable game; acceptable.
2. **R2: Test fixtures with hand-built component dicts.** Swarm confirmed no JSON schema files for replays; all test construction uses Python literal `ComponentStateSpec(...)` calls. Phase 2 Task 2.2 updates all 5 test sites.
3. **R3: Post-battle hook bridge breakage.** Swarm confirmed `_apply_survivor_outcome` (`post_battle_hook.py:150-158`) reads named fields — backward-compatible. Phase 2 Task 2.3 verifies.
4. **R4: `Component.max_hp` or `Component.status` missing.** Swarm confirmed both are direct instance attributes set in `Component.__init__` (`component.py:114, 124`). Defensive `hasattr(status_obj, "name")` check in extractor protects against unexpected status types.

### Opportunities Discovered

- **Persistent state can become more accurate**: Today the post-battle hook reconstructs `ComponentState` from `ComponentStateSpec` (which lacks `max_hp`), so persistent state's `max_hp` defaults to 0.0 unless set elsewhere. After PROJ-354A, the bridge has access to actual battle-end `max_hp` if a future change wants to use it. **Out of scope here**, but unblocked.
- **Verification diagnostic granularity**: With `status` captured, mod-induced divergence at the ACTIVE↔DAMAGED↔NO_FUEL boundary becomes visible to the verifier — useful diagnostic for the moddable game use case.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

Key decisions:

- **Serialize `ComponentStatus.name` (string), not `.value` (int)**: enum uses `auto()`; numeric values are not stable across Python versions. String names are. Codex r002 correction.
- **No `DESTROYED` synthesized status**: enum has no such member; destruction is `current_hp == 0` + `is_active == False`. Codex r002 correction.
- **No migration shim for old replays**: project convention (CLAUDE.md Rule 3). `version_drift` graceful degradation already exists.
- **Bump to `"2.0.0"`** (major version): the schema is backward-incompatible. Use semantic versioning even though there's no formal compatibility contract.
