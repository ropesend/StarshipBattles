# PROJ-359 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/combat/weapon_firing_system.py` | Production | Replace `_create_attack` string-class branches (lines 198, 221, 236) with registry dispatch. |
| `game/simulation/combat/targeting_system.py` | Production | PDC / seeker rules (line 123) consume weapon-family metadata, not name lookups. |
| `game/engine/collision.py` | Production | Replace `process_beam_attack`'s dict-shaped attack input (line 68) with the typed `AttackRequest` / `AttackResolution` contract. |
| `game/simulation/projectile_manager.py` | Production | Hit-application path (line 130) routes through the typed resolution; emits the same telemetry shape regardless of family. |
| `game/simulation/combat/attack_contract.py` | Production (new) | Defines `AttackRequest`, `AttackResolution`, and the family-handler protocol. |
| `game/simulation/combat/weapon_registry.py` | Production (new) | Family registry + register/lookup; `WeaponFamily` enum or string keys (decide in Phase 2). |
| `game/simulation/combat/families/` | Production (new directory) | One module per family: `beam.py`, `projectile.py`, `seeker.py`, `pdc.py`. |
| `game/simulation/combat/telemetry.py` | Production (audit) | `HitLogRecorder._on_hit_event` may need a small update if attack metadata shape changes. |
| `tests/unit/simulation/combat/test_weapon_dispatch_golden.py` | Test (new) | Phase 1: golden damage events for each family on current behavior. |
| `tests/unit/simulation/combat/test_weapon_registry.py` | Test (new) | Phase 2: registry contract; fake `TestWeaponFamily` registers and fires. |
| `tests/unit/simulation/combat/test_weapon_family_*.py` | Test (new, one per family) | Phase 3: per-family migration tests. |
| `tests/unit/engine/test_collision.py` | Test (existing) | Verify typed-contract migration preserves collision semantics. |
