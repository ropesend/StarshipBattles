# PROJ-302: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for Star Intrinsic Ability Sources |
| 2026-04-26 | **Stars project mostly system-scope abilities** (radiation field, stellar heat, gravitational lensing) | A star physically affects its entire system, not just the central hex. The framework's `system` scope is the right fit. Sector-scope is reserved for star-hex-only effects (e.g. a future "coronal flare" hot spot). |
| 2026-04-26 | **Stars are ownerless (`owner_id=None`)** | Same rationale as planet intrinsic abilities: the radiation damages friend and foe equally. |
| 2026-04-26 | **`source_label` format: `"<star.name> (<star_type>)"`** e.g. `"Sol (G-class)"` | Matches PROJ-301 planet pattern. |
| 2026-04-26 | **Pulsar `ShieldModifier scope: system`** affects all combat in pulsar systems with stacking reduction | Intentional balance lever — pulsar systems are dangerous to fight in. Combat aggregation through `_entries_from_sector_effects` (PROJ-300 Phase 6c) already handles system-scope provider entries; no new wiring needed. |
| 2026-04-26 | **Reuse PROJ-301's `roll_intrinsic_abilities` helper** rather than reimplement | Promote to a shared module is appropriate now that two projects use it. If PROJ-301 hasn't landed, ship it here. |
