# PROJ-404 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/data/ship_instance_serializer.py | Production | Delete `resource_levels` fallback; route `components` through `require_keys()`. |
| game/ui/screens/battle_setup_state.py | Production | Delete `*_complex_toggles` legacy tolerance + docstring framing. |
| tests/unit/strategy/ship_instance/test_ship_instance_serializer.py | Test | Add positive new-shape + negative legacy-shape tests. Delete tests that encode legacy success. |
| tests/unit/ui/screens/test_battle_setup_state.py | Test | Delete legacy-tolerance test; add negative regression. |
| tests/integration/save_load/test_roundtrip_ships.py | Test (read + maybe edit) | Should still pass; update if it relies on legacy shapes. |
