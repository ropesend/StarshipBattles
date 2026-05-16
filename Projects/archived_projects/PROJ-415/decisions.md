# PROJ-415: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-13 | Project initialized | Starting point for Legacy removal — planet.py re-exports (PROJ-210/284 vestige) (2026-05-13) |
| 2026-05-13 | Bundled findings from `2026-05-13_194106_legacy-audit` by removal cluster `planet_reexports (PROJ-210/284)` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-14 | Caller count corrected to "61 files / 64 import statements" | Codex consult (leaf: AgentCoordination/Scratchpad/Consult/20260514T035545Z_proj-415_legacy_review) confirmed 61 distinct files / 64 import lines; per-symbol: PlanetaryFacility=53, SpeciesPopulation=12, ColonySpeciesConfig=0 external |
| 2026-05-14 | ColonySpeciesConfig removal is not a pure shim deletion — planet.py uses it at runtime | planet.py:107 (field), 187 (return annotation), 190 (constructor call) are live runtime usages. Shim line 25 serves double duty. Deletion requires a direct non-shim import to replace it. |
| 2026-05-14 | Added static zero verification as separate pre-deletion task | Line-oriented grep misses parenthesized/multiline imports; checklist now requires multiline-aware or AST scan before deletion |
| 2026-05-14 | design.md:48-49 stars.py solar constants callout is misplaced — belongs to sibling PROJ-413/414 cluster, not planet_reexports | Noted by codex; design.md is a reference-only document per its header, so no edit; flagged here for awareness |
| 2026-05-14 | No doc updates needed for this project | Pattern #36 in docs/02_PATTERNS.md does not track planet.py specifically; production/strategy docs already point at canonical modules |
