# PROJ-243: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Project initialized | Starting point for Mid-Battle Ship Addition Fix |
| 2026-04-05 | Declare fleet bonus attributes in `Ship.__init__` with default `0.0` | Dynamically-set attributes are fragile. Declaring makes the contract explicit and prevents `AttributeError` if accessed before aura manager runs. |
| 2026-04-05 | Extract `_initialize_ship()` helper from `start()` | The 5-step init sequence (event bus, component update, recalculate, derelict check) is shared between `start()` and `add_ship_mid_battle()`. Extract once, call from both. DRY. |
| 2026-04-05 | Add `register_ship()` method to `FleetAuraManager` | `initialize()` clears all state and rescans everything — too heavy for adding one ship. A targeted `register_ship()` that scans one ship and triggers `_recalculate()` is the clean solution. |
| 2026-04-05 | Refactor fighter launch to use `add_ship_mid_battle()` | Fighter launch (lines 478-511) duplicates ship-addition logic and skips all init. It should call `add_ship_mid_battle()` to inherit the fix. |
| 2026-04-05 | 4 phases instead of 3 | Separating the helper extraction (Phase 2) from the fix application (Phase 3) keeps each phase focused and testable. Fighter launch refactor folded into Phase 3. |
| 2026-04-10 | Project review (Protocol 09) conducted | 17 findings: 8 stale line refs (Low), 2 stale refs (Medium), 1 scope gap (High — `remove_ship()` aura cleanup → PROJ-268), 2 doc gaps (Low), 4 minor observations (Informational). Changes: Key Files table updated, decisions.md populated, design.md annotated, minor observations recorded. |

## Known Issues (from review)

These items were identified during the 2026-04-10 project review but are outside PROJ-243's scope:

- **`collision.py` dead `getattr` on `source_ship`**: Line 115 uses `getattr(source_ship, 'fleet_attack_bonus', None)` which is now unnecessary since the attribute is declared. The `target` side (line 120) still needs `getattr` because targets can be Projectiles. Cleanup is simple.
- **`register_ship()` fingerprint cache**: Doesn't update `_last_fingerprint`, causing one redundant `_recalculate()` on the next tick after a mid-battle addition. Negligible performance impact.
- **Mid-tick fighter timing**: Fighters launched mid-tick can't fire until next tick (pre-existing, not introduced by PROJ-243). Undocumented timing behavior.
- **Fleet bonus asymmetry**: Fleet bonuses only affect beam hit chance (via `collision.py`), not projectile collision (geometric in `projectile_manager.py`). May be intentional design; undocumented.
