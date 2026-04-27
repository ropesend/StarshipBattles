# PROJ-304: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for Star System Archetype Ability Sources |
| 2026-04-26 | **Archetype is OPTIONAL** — most systems have `archetype = None` | Adds variety without making every system feel themed. Archetype rolling is configurable (default ~15%). |
| 2026-04-26 | **System archetype effects are system-scope** (apply to every hex in the system) | A nebula isn't localized; its sensor degradation reaches every corner of the system. Sector-scope archetype effects don't make conceptual sense (they'd be storms, not archetypes). |
| 2026-04-26 | **System archetypes are ownerless** (`owner_id=None`) | Same rationale as planet/star intrinsic. Empire ownership of a system doesn't change its physical nature. |
| 2026-04-26 | **`source_label` format: `"<system.name> (<Archetype Title Case>)"`** e.g. `"Sol System (Nebula System)"` | Consistent with PROJ-301/302/303 — descriptive, identifies both instance and archetype. |
| 2026-04-26 | **`void` archetype with empty `abilities` dict is valid** | A useful no-op explicit archetype if any future logic needs to distinguish "rolled an archetype but it's plain" from "no archetype assigned." Optional — can be omitted from registry. |
| 2026-04-26 | **Archetype assignment percentage configurable in galaxy generation config** | Lets the user balance how often archetypes appear without code changes. |
| 2026-04-26 | **Reuse `roll_intrinsic_abilities` from PROJ-301** | Shared helper across all five intrinsic-source projects. |
