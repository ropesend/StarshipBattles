# PROJ-FMS-C File Manifest

| File | Type | Action | Phase | Notes |
|------|------|--------|-------|-------|
| `game/simulation/components/abilities/launch.py` | Production | Skeleton classes from PROJ-FMS-A (data-only — no `apply()` method on `Ability`) | 1 | |
| `game/simulation/components/abilities/recovery.py` | Production | Skeleton class from PROJ-FMS-A (data-only) | 3 | |
| `game/strategy/engine/order_handlers/launch_fighters.py` (new) | Production | `LaunchFightersOrderHandler(BaseOrderHandler)` — mirrors [`colonize.py`](../../../game/strategy/engine/order_handlers/colonize.py) | 1 | |
| `game/strategy/engine/order_handlers/recover_fighters.py` (new) | Production | `RecoverFightersOrderHandler(BaseOrderHandler)` | 3 | |
| `game/strategy/engine/handlers/<launch_command>.py` | Production | `IssueLaunchFightersCommand` + handler; mirrors `IssueMoveCommand` at [`movement.py:87-225`](../../../game/strategy/engine/handlers/movement.py#L87) | 1 | |
| `game/strategy/engine/handlers/<recover_command>.py` | Production | `IssueRecoverFightersCommand` + handler | 3 | |
| `game/simulation/combat/weapon_firing_system.py:115-141` | Production | Replace auto-launch with design-instance deploy | 1 | |
| `game/simulation/systems/attack_processor.py:68-97` | Production | Accept design-instance payload, not class string | 1 | |
| `game/simulation/systems/battle_engine.py` | Production | End-of-battle reboard + overflow-to-sector-group hook | 3 | |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | Verify `fighter_group` inclusion in combat manifest | 2 | Should be free with `group_kind` |
| `game/simulation/entities/stat_contributors/launch.py:29-61` | Production | Update for new launch ability shape | 1 | |
| `game/ai/controller.py` | Production | Minimal fighter AI controller | 2 | |
| `game/ui/screens/<tactical_action_menu>.py` | Production | Tactical launch action UI | 1 | |
| `game/ui/screens/<sector_action_menu>.py` | Production | Strategic launch + recovery UI | 1, 3 | |
| `tests/unit/simulation/components/abilities/test_strategic_fighter_launch.py` | Test | Add | 1 | |
| `tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py` | Test | Add | 1 | Including design-instance deploy and tagging |
| `tests/unit/simulation/components/abilities/test_recover_fighters.py` | Test | Add | 3 | Including partial recovery + HP preservation |
| `tests/unit/ai/test_fighter_controller.py` | Test | Add | 2 | |
| `tests/integration/test_fms_c_e2e.py` | Test | Add | 4 | Full strategic launch → battle → strategic recovery |
| `tests/integration/test_fms_c_launch_in_battle_e2e.py` | Test | Add | 4 | Tactical launch + auto-reboard + overflow |
| `docs/systems/fighters.md` | Docs | Add | 4 | New system doc |
| `docs/systems/ability_reference.md` | Docs | Edit | 4 | Document new abilities |
