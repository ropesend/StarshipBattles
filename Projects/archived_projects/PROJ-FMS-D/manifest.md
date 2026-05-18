# PROJ-FMS-D File Manifest

| File | Type | Action | Phase | Notes |
|------|------|--------|-------|-------|
| `game/simulation/components/abilities/launch.py` | Production | Skeleton classes from PROJ-FMS-A (data-only — no `apply()` method on `Ability`) | 1 | |
| `game/simulation/components/abilities/recovery.py` | Production | Skeleton class from PROJ-FMS-A (data-only) | 2 | |
| `game/strategy/engine/order_handlers/launch_satellites.py` (new) | Production | `LaunchSatellitesOrderHandler(BaseOrderHandler)` | 1 | |
| `game/strategy/engine/order_handlers/recover_satellites.py` (new) | Production | `RecoverSatellitesOrderHandler(BaseOrderHandler)` | 2 | |
| `game/strategy/engine/handlers/<launch_command>.py` | Production | `IssueLaunchSatellitesCommand` + handler | 1 | |
| `game/strategy/engine/handlers/<recover_command>.py` | Production | `IssueRecoverSatellitesCommand` + handler | 2 | |
| `game/simulation/components/abilities/cargo.py` (or `vehicle_bay.py`) | Production | Add `allowed_types` filter to `VehicleBayAbility` (if option (a) chosen) | 1 | |
| `data/components.json` | Data | Add `satellite_bay_*` components; possibly retro-tag fighter bays | 1 | |
| `game/ai/controller.py` | Production | Stationary satellite AI variant | 1 | Existing satellite ref at lines 361-363 |
| `game/simulation/entities/stat_contributors/launch.py` | Production | Aggregate satellite-specific stats separately | 1 | |
| `game/simulation/systems/battle_engine.py` | Production | Extend end-of-battle reboard to handle satellites | 2 | |
| `game/ui/screens/<sector_action_menu>.py` | Production | Strategic launch + recovery UI for satellites | 1, 2 | |
| `tests/unit/simulation/components/abilities/test_strategic_satellite_launch.py` | Test | Add | 1 | |
| `tests/unit/simulation/components/abilities/test_tactical_satellite_launch.py` | Test | Add | 1 | |
| `tests/unit/simulation/components/abilities/test_recover_satellites.py` | Test | Add | 2 | Including bay-type isolation |
| `tests/unit/ai/test_satellite_controller.py` | Test | Add | 1 | Verify stationary |
| `tests/integration/test_fms_d_e2e.py` | Test | Add | 3 | |
| `tests/integration/test_fms_d_launch_in_battle_e2e.py` | Test | Add | 3 | |
| `tests/integration/test_fms_cd_isolation.py` | Test | Add | 3 | Cross-type ability gate isolation |
| `docs/systems/satellites.md` | Docs | Add | 3 | New system doc |
| `docs/systems/ability_reference.md` | Docs | Edit | 3 | Document new abilities |
