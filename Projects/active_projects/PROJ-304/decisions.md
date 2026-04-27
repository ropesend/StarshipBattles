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
| 2026-04-26 | **Reuse `roll_intrinsic_abilities` from PROJ-301** *(SUPERSEDED 2026-04-27 — see D8)* | Shared helper across all five intrinsic-source projects. |
| 2026-04-27 | **D8 — Helper now imported from PROJ-300, not PROJ-301** | Per PROJ-300..305 review and PROJ-300 D15: `roll_intrinsic_abilities` and `format_intrinsic_source_label` ship in PROJ-300. PROJ-304 is a pure consumer. PROJ-301 is no longer a hard precondition. |
| 2026-04-27 | **D9 — Galaxy generator insertion point: post-system-generation, gated by `galaxy_generation_config.archetype_chance`** (default 0.15, set to 0.0 in tests) | Pinned during review. Without this, tests that rely on deterministic system attributes might break unpredictably. The 0.0-in-tests pattern is standard for similar gen-time rolls. |
