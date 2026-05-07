# Review Scope: PROJ-354A Review: Replay Component End-State Fidelity

**Type:** code (delegated by Claude Code)

**Request ID:** req_20260505_055832_23a2f0

**Scope:**
- `game/simulation/battle_spec.py` (`ComponentStateSpec`)
- `game/simulation/battle_runner.py` (`_extract_component_states`)
- `game/simulation/replay/replay_serialization.py` (round-trip + schema version)
- `game/strategy/combat/spec_compiler.py` (2nd constructor — added during execution, not in original plan)
- `tests/unit/simulation/replay/test_serialization.py` and 4 other updated test files
- `docs/systems/combat_simulation.md` § 11

**Instructions:**
- Verify `max_hp` and `status` (`ComponentStatus.name` string) round-trip correctly
- Confirm REPLAY_SCHEMA_VERSION is exactly `2.0.0` and existing replays surface as `version_drift` (no compat shims per CLAUDE.md Rule 3)
- Check that `spec_compiler.py`'s `status='ACTIVE'` default is correct given persistent strategy state has no per-component status — is this assumption safe?
- Are there OTHER constructors of `ComponentStateSpec` the agent's expanded inventory still missed?
- Confirm the post-battle-hook bridge (`_apply_survivor_outcome`) still works — does it ignore the new fields gracefully?

**Context:**
Just-completed project commit `cd8ebf5e5`. Phase A of replay-end-state verification consensus. PROJ-354B (verifier + coordinator) is the dependent phase B, not yet started.
