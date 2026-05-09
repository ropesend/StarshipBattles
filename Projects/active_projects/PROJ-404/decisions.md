# PROJ-404: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Project initialized | Starting point for Tier 1 B-05: Eradicate save-format compatibility (Rule 3 follow-on) |
| 2026-05-09 | `consumable_levels` contract: absent → `{}` (the `resource_levels` rename fallback is deleted; `consumable_levels` is the only accepted key, and it remains optional). | Canonical `to_dict` always emits `consumable_levels` (line 38 in serializer). The `resource_levels` fallback was a Rule 3-violating field-rename shim. Keeping the optional default `{}` matches `ShipInstance.__init__`'s default-empty contract for ships created without prior consumables; making it required would break `to_dict` of fresh ships that never populated the dict (still emits `{}`, so it round-trips, but new construction paths should not be forced to materialize the key). |
| 2026-05-09 | Missing `components` now routes through `require_keys()` (raises `PersistenceException`, code `CORRUPT_DATA`). | Documented `Raises` section in `from_dict` doc says `PersistenceException`. Raw `KeyError` violates the contract and bypasses the canonical error envelope used for save-load surface area. |
| 2026-05-09 | `BattleSetupSide.from_dict` no longer tolerates missing `*_complex_toggles`. Calls `require_keys(...)` for `system_complex_toggles` and `sector_complex_toggles`. | Rule 3: old saves are disposable. The "tolerate legacy" branch and its docstring framing are deleted. The PROJ-282 Phase 2 contract is now strictly enforced for any save the loader sees. |
| 2026-05-09 | Scope limit: did NOT expand to other save-format tolerance. `battle_state.py` `resource_levels` is a separate, live concept (not a field-rename shim) — out of scope. `ship_instance_bridge._capture_resource_levels` is a method name on a runtime helper — also unrelated. | Brief says "Don't expand scope beyond the two named files." |
