# Review Scope: PROJ-357 Review: Fleet Aura Provider Identity
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_055830_bbffca
**Review Mode:** normal
**Scope:**
- `game/simulation/combat/fleet_aura_manager.py`  (full file)
- `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py` (new)
- `Projects/active_projects/PROJ-357/decisions.md`

**Instructions:**
- Verify provider identity is now (ship, component, ability_instance) end-to-end
- Check stacking semantics (MAX same group / SUM across groups) are bit-identical
- Confirm 'skip non-operational, drop on real loss' policy is correct — would a destroyed/replaced component leak its registration?
- Audit other systems that key on (ship, ability_class_name) for similar bugs
- Look for any test that should have caught this earlier

**Context:** Just-completed project commit `6feda03f0`. Agent flagged the MAX-stacking test caught a subtle re-enable-after-disable case during dev.

**Limitations:** Manual single-reviewer analysis (scope is 3 files, ~770 lines). No agents were launched; findings are from direct source analysis.
