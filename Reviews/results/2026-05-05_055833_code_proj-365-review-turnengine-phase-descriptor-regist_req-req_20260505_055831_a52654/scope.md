# Review Scope: PROJ-365 Review: TurnEngine Phase Descriptor Registry

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_055831_a52654
**Review mode:** normal (full-depth review)

**Scope:**
- `game/strategy/engine/turn_phase_registry.py` (new, 297 lines)
- `game/strategy/engine/turn_engine.py` (`_process_tick` and surrounding, 792 lines)
- `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` (new, 267 lines)
- `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py` (new, 84 lines)
- `Projects/active_projects/PROJ-365/decisions.md`

**Instructions:**
- Verify the 15-phase ordering is preserved exactly (golden test) — *note: request says "14-phase" but code has 15*
- Check the new `pre_exec_hook` (added beyond plan) is justified and doesn't double-fire
- Confirm `tick_gating` semantics: hooks self-gate on `ctx.tick` instead of skipping the phase entirely
- Confirm PROJ-320 `moved_fleet_ids` cross-phase state still works
- Look for any `_phase_times` keys that drifted
- Layer-boundary check (`turn_phase_registry.py` should not reach into UI/simulation)

**Context:**
Just-completed project commit `3d9519090` (shared with PROJ-361 due to concurrent-agent race).
