# Review Scope: PROJ-364 Superweapon Spec Table Refactor
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_070825_e838b1
**Scope:**
- `game/strategy/services/superweapon_registry.py` (new — Phase 2)
- `game/strategy/engine/superweapon_order_processor.py` (Phase 3 dispatcher)
- `game/strategy/engine/order_processor.py` (lines 706-725 superweapon dispatch table)
- `tests/unit/strategy/services/test_superweapon_registry_contract.py`
- Phase 1 characterization tests under `tests/unit/strategy/engine/`
- `Projects/active_projects/PROJ-364/decisions.md`

**Instructions:**
- Verify all 5 strategic superweapons (IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE) have correct `SuperweaponSpec` entries
- Confirm SELF_DESTRUCT remains structural outlier and is not in the spec table
- Check the `precheck_fn` extension (added beyond the plan) is justified — it preserves error-message ordering
- LOC target was ≤ 30 per `process_*` but actual is 34–96. Is this a real concern or acceptable given effect-closure complexity?
- Audit the `DYSON_SPHERE_CREATED` event missing `planet_id`/`planet_name` fields — minor, but is replay capture affected?
- Confirm Phase 2 files (`superweapon_registry.py`, contract test) made it into HEAD and are tested even though they're attributed to PROJ-359's commit

**Context:**
Phase 2 was attributed to PROJ-359's commit `a8a2fc10b` due to concurrent-agent race. Phase 3 commit `3890fa921`. Sharded 17645 passed.
