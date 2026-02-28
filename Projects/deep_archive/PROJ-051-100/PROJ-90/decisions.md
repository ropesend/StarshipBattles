# PROJ-90: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for Untangle Circular Dependencies and Layer Violations |
| 2026-02-09 | Comprehensive scope (all 5 issues) | User selected full scope including protocol formalization |
| 2026-02-09 | Extract `reload_all_from_directory` to simulation layer (Option A) | The function logically belongs in simulation since it calls simulation loading functions. Moving it eliminates the Core → Simulation violation. Simpler than callback/plugin patterns. |
| 2026-02-09 | Extract BattleConfig/BattleMode to `battle_config.py` (no re-export shim) | Per project's "eradicate old systems" policy. All importers updated immediately. |
| 2026-02-09 | Move all 4 Ship.py late imports to module level | Deep analysis confirmed none are real circular dependency cycles. WeaponAbility, ModifierService, and ShipCombatEngine have no transitive Ship dependency. ShipSerializer is safe because `ship_serialization.py` doesn't import Ship at module level. |
| 2026-02-09 | Name protocol `IPostBattleShip` not `ISimulationShip` | The protocol is specifically for the post-battle readback scenario. A generic name would be misleadingly broad. |
| 2026-02-09 | Keep `layers` typed as `Dict` (bare) in protocol | The complex nested structure (`Dict[LayerType, Dict[str, List[Component]]]`) would over-couple the protocol to specific types. Duck typing handles the iteration pattern. |
| 2026-02-09 | Separate `IResourceReader` protocol | Resources are accessed through a sub-object with `get_value`/`get_max_value`. A separate small protocol is cleaner than embedding in IPostBattleShip. |
| 2026-02-09 | Accept TurnEngine lazy properties as-is | 9 lazy property imports are a legitimate service locator/DI pattern, not a problem. Allows constructor injection for tests and avoids unnecessary import overhead. |
| 2026-02-09 | Accept App.py lazy imports as-is | Startup optimization for UI screens. Legitimate pattern for an application entry point. |
| 2026-02-09 | Leave ShipInstance.to_ship()/from_ship() ShipSerializer late imports | These are intentional cross-layer calls in the allowed direction (Strategy → Simulation). The late import is for load-time decoupling. |
| 2026-02-09 | Add protective comment in ship_serialization.py | When moving ShipSerializer import to module level in ship.py, the runtime import of Ship in `from_dict()` at line 133 must remain as-is. A comment documents this constraint. |
