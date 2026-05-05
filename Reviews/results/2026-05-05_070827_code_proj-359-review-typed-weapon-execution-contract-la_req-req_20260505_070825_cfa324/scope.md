# Review Scope: PROJ-359 Review: Typed Weapon Execution Contract (large refactor)
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_070825_cfa324
**Scope:**
- `game/simulation/combat/attack_contract.py` (new)
- `game/simulation/combat/weapon_registry.py` (new + `FAMILY_METADATA`)
- All weapon family handler modules (Beam, Projectile, Seeker, PDC) under `game/simulation/combat/`
- `game/simulation/combat/process_beam_attack.*` and projectile/firing/targeting paths
- `game/engine/collision.py` (dict-carrier removal)
- `tests/unit/simulation/combat/test_weapon_dispatch_golden.py` (new) and family-handler tests
- `docs/02_PATTERNS.md` § 34, `docs/systems/combat_simulation.md`
- Commits: 157264456, a8a2fc10b, b112742e0, 93a2fa8b0, fe5d4a724, a1c1c158b, bd8b48d51

**Instructions:**
1. Verify zero remaining `has_ability('BeamWeaponAbility')` / `'SeekerWeaponAbility'` string branches in firing/targeting
2. Confirm Beam and Projectile damage event/telemetry shapes have converged (per goal)
3. Audit `game/engine/collision.py` — no simulation semantics in dict carriers anymore
4. Verify `BeamHandler` and `PDCHandler` near-duplicates are intentional and `FAMILY_METADATA` correctly distinguishes them
5. Check `_get_pdc_valid_targets` still calls `comp.has_ability('BeamWeaponAbility')` — agent argues this is data-fetch not dispatch; verify the rule's spirit
6. Test the extensibility claim: can a hypothetical 5th weapon family be added with one registration call + one family module? Examine `WeaponRegistry` extension points
7. LAUNCH dict path retained as out-of-scope: confirm this is not a regression
8. Audit Seeker arc-check logic: agent reports it was bit-for-bit replicated to keep golden tests green

**Context:** Just-completed LARGE refactor across 7 commits. Final commit `bd8b48d51`. Sharded 17650 passed.
**Review Mode:** normal
**Limitations:** No parent review to verify against. Phase 3.4 PDC handler review limited to on-disk code; no runtime behavior verification beyond golden tests.
