# PROJ-24: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Project created from LPA-01 finding | ShipControllableAdapter delegation blocks interface migration completion |
| 2026-01-27 | Include both AI implementations | UI layer uses `core/system.py`, simulation uses `controller.py` - both must migrate |
| 2026-01-27 | Add `set_rotation()` method | FormationBehavior needs direct angle setting for angle snapping (`ship.angle = master.angle`) |
| 2026-01-27 | Add `adjust_position()` method | FormationBehavior needs position mutation for drift correction (`ship.position += correction`) |
| 2026-01-27 | Add `get_layers()` method | `core/system.py` directly accesses ship.layers for component inspection |
| 2026-01-27 | Defer consolidation to PROJ-25 | Focus PROJ-24 on interface migration only; consolidating dual implementations is separate work |
| 2026-01-27 | `formation_master` returns raw Ship | Intentional - master is not wrapped in adapter, code chains to master properties directly |
