# PROJ-357 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/combat/fleet_aura_manager.py` | Production | Add component/ability identity to `AuraProvider`; rewrite `_scan_ship` to record identity; rewrite `_recalculate` to read live `value` from the live ability instance, not cached `provider.value`. |
| `game/simulation/entities/ability_aggregator.py` | Production (read-only) | Aggregator contract MUST be preserved bit-for-bit; no edits expected. |
| `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py` | Test (new) | Characterization + new behavior: same-class multi-provider disable, ship-disable-removes-all, single-provider unchanged. |
| `tests/unit/simulation/combat/test_fleet_aura_manager.py` | Test (existing) | Re-run unchanged; locks single-provider semantics. |
| `tests/unit/simulation/combat/test_fleet_aura_unknown_stat_key_warning.py` | Test (existing) | Re-run unchanged; verifies external-modifier path is untouched. |
