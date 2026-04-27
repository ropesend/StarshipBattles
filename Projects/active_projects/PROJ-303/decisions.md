# PROJ-303: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for Warp Point Intrinsic Ability Sources |
| 2026-04-26 | **Warp points project sector-scope abilities only** (no system-scope) | A warp point's effect is local to its hex. System-scope effects belong to stars (PROJ-302) and system archetypes (PROJ-304). |
| 2026-04-26 | **Warp points are ownerless** (`owner_id=None`) | Same rationale as planet/star intrinsic. The warp shear damages everyone equally. |
| 2026-04-26 | **`source_label` includes the warp_point type** e.g. `"<descriptive_name> (Unstable)"` | Lets the user see at a glance why a warp point hex is dangerous — type carries the meaning. |
| 2026-04-26 | **New `damage_type: "warp"`** introduced for warp-shear damage | Extends the existing damage_type taxonomy (plasma/radiation/thermal). Future warp-shielding components may target this damage_type specifically. |
| 2026-04-26 | **If today's codebase has only one warp_point type, defer expansion** to a follow-up project — first land the framework path with the existing type | Per Rule 3 / clean-sheet, don't over-design before the use case is proven. The framework is what matters; data can grow afterward. Verify with the user during Phase 1. |
