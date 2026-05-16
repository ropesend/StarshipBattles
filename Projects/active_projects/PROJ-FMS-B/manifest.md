# PROJ-FMS-B File Manifest

| File | Type | Action | Phase | Notes |
|------|------|--------|-------|-------|
| `data/balance/mines.json` | Data | Add | 1 | Warhead trigger constants, sensitivity multipliers, scatter, laserhead threshold default |
| `game/simulation/components/abilities/warhead.py` (or wherever placed in A2) | Production | Implement | 2 | Detonation via damage pipeline |
| `game/simulation/components/abilities/laserhead.py` | Production | Implement | 2 | Beam fire with consume_on_fire + threshold gate |
| `game/simulation/components/abilities/ram_target.py` | Production | Implement | 4 | Explicit target action + intercept AI + collision detonation |
| `game/simulation/components/abilities/launch.py` | Production | Verify skeleton ability classes from PROJ-FMS-A; data-bearing only — no `apply()` method (the `Ability` base class has no such hook, per [`base.py:59-227`](../../../game/simulation/components/abilities/base.py#L59)) | 1, 3 | |
| `game/strategy/data/order_types.py` | Production | `OrderType.LAY_MINES` enum value already reserved in PROJ-FMS-A Phase 5; verify | 1 | |
| `game/strategy/engine/order_handlers/lay_mines.py` (new) | Production | New `LayMinesOrderHandler(BaseOrderHandler)` — strategic execution model; mirrors [`colonize.py`](../../../game/strategy/engine/order_handlers/colonize.py) | 1 | |
| `game/strategy/engine/handlers/<lay_mines_command>.py` (new or in `movement.py`) | Production | New `IssueLayMinesCommand` + handler; mirrors `IssueMoveCommand` at [`movement.py:87-225`](../../../game/strategy/engine/handlers/movement.py#L87) | 1 | |
| `game/strategy/engine/minefield_resolver.py` | Production | New | 1, 2 | `resolve_minefield_entry()`; warhead pass Phase 1, laserhead pass Phase 2 |
| `game/strategy/engine/turn_engine.py` | Production | Edit | 1 | Wire resolver into movement phase before conflict resolution |
| `game/simulation/systems/battle_engine.py` | Production | Edit | 3 | Per-tick mine behavior; mine map placement at scatter coords |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | Verify | 3 | Confirm `mine_group` inclusion in combat manifest (should be free with PROJ-FMS-A `group_kind`) |
| `game/strategy/data/fleet.py` | Production | Edit | 1 | Add `sensitivity`, `expected_hit_chance_threshold`, `mine_positions`, `scatter_seed` fields on `mine_group` Fleets (consider a subclass or sidecar dict) |
| `game/ai/controller.py` | Production | Edit | 4 | Ram-target intercept AI |
| `game/ui/screens/<minefield_panel>.py` | Production | New/Edit | 4 | Sensitivity + threshold sliders, selective self-destruct |
| `game/ui/screens/<tactical_action_menu>.py` | Production | Edit | 4 | Set-ram-target context action |
| `tests/unit/strategy/engine/test_minefield_resolver.py` | Test | Add | 1, 2 | Warhead + laserhead pass statistics |
| `tests/unit/simulation/components/abilities/test_warhead.py` | Test | Edit | 2 | Detonation damage path |
| `tests/unit/simulation/components/abilities/test_laserhead.py` | Test | Edit | 2 | Threshold gate + beam path |
| `tests/unit/simulation/components/abilities/test_ram_target.py` | Test | Edit | 4 | Ram intercept + collision damage |
| `tests/integration/test_fms_b_e2e.py` | Test | Add | 5 | Full mine E2E |
| `tests/integration/test_ramming_e2e.py` | Test | Add | 5 | Kamikaze fighter ramming E2E |
| `docs/systems/minefields.md` | Docs | Add | 5 | New system doc |
| `docs/systems/ability_reference.md` | Docs | Edit | 5 | Document new abilities |
