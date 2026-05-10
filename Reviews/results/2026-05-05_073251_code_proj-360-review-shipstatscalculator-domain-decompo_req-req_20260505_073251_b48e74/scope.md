# Review Scope: PROJ-360 ShipStatsCalculator Domain Decomposition
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_073251_b48e74
**Scope:**
- `game/simulation/entities/ship_stats.py` (now 495 LOC, was 643)
- `game/simulation/entities/stat_contributors/` (new package: movement, defense, weapons, command, launch, registry)
- `tests/unit/simulation/entities/test_ship_stats_golden.py` + `*_snapshot.json` (new)
- `tests/unit/simulation/entities/stat_contributors/` (37 contributor tests + acceptance)
- `docs/02_PATTERNS.md` § 35

**Instructions:**
- Verify `ship_stats.py` is < 500 LOC and the public `calculate()` API is unchanged
- Confirm golden snapshot covers all 7 representative designs and floats are deterministically normalized
- Audit the `STAT_CONTRIBUTOR_REGISTRY` extension surface — can a new ability cleanly register without editing the calculator?
- Confirm acceptance test really exercises the registry path (registers a fake contributor)
- Check why the agent did NOT adopt PROJ-359's typed AttackRequest contract — is the rationale (ECM/sensor are pre-fire inputs, not resolution outputs) sound?
- Look for hidden coupling between contributors (e.g., a contributor reading another's intermediate state)
- Audit the remaining `get_abilities('X')` calls in contributors — are they all typed-attribute reads vs. dispatch checks?

**Context:** Wave 4 just-completed project. Final commit `778068562`. Sharded 17717 passed.
