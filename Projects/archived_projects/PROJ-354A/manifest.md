# PROJ-354A File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/battle_spec.py` | Production | Extend `ComponentStateSpec` with `max_hp: float` and `status: str` (lines 86-99) |
| `game/simulation/battle_runner.py` | Production | Update `_extract_component_states` (lines 622-643) to populate new fields from live `Component` |
| `game/simulation/replay/replay_serialization.py` | Production | Update `_component_state_to_dict` / `_component_state_from_dict` (lines 241-256); bump `REPLAY_SCHEMA_VERSION` (line 70) from `"1.0.0"` to `"2.0.0"` |
| `tests/unit/simulation/replay/test_serialization.py` | Test | New round-trip test for new fields; update existing 3 `ComponentStateSpec` constructions (lines 131-134, 190); new schema-version regression test |
| `tests/unit/simulation/test_battle_spec.py` | Test | Update existing `ComponentStateSpec` construction (lines 125-129) |
| `tests/unit/simulation/test_battle_runner_component_hp.py` | Test | Update existing construction (lines 115-119); possibly add distinct-status extractor test (or new file) |
| `tests/unit/simulation/test_battle_outcome.py` | Test | Update existing constructions (multiple sites) |
| `tests/unit/strategy/combat/test_post_battle_hook.py` | Test | Update existing constructions (multiple sites); verify bridge still works |
| `tests/unit/simulation/test_extract_component_states_status.py` | Test (NEW, optional) | Distinct-status extractor test if not folded into `test_battle_runner_component_hp.py` |
| `docs/systems/combat_simulation.md` | Docs | Phase 3: document new outcome fields + schema version bump in § 11 |
| `CLAUDE.md` | Docs | Phase 3: skim for stale references (likely no change) |
| `AGENTS.md` | Docs | Phase 3: skim for stale references (likely no change) |

## Files NOT touched (out of scope)

| File | Why excluded |
|------|--------------|
| `game/core/component_state.py` | Persistent strategy-side `ComponentState` is out of scope; it already has `max_hp`. Adding `status` to it would be a separate change. |
| `game/strategy/combat/post_battle_hook.py` | Bridge reads named fields; ignores new fields gracefully. No code change needed. Phase 2 Task 2.3 verifies. |
| `game/simulation/components/component.py` | Read-only access of `comp.max_hp` and `comp.status`. No mutations. |
| `game/simulation/components/component_constants.py` | `ComponentStatus` enum consumed as-is; no changes. |
| `game/simulation/components/component_health_manager.py` | Read-only; existing status mutations are unchanged. |
