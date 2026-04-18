# PROJ-282: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Project initialized | Starting point for FleetBattleSetupScreen MVVM Decomposition |
| 2026-04-17 | Approach: Full MVVM matching TestLab pattern | User chose "Full MVVM". Codebase consistency: TestLab already uses ViewModel+Renderer+InputHandler+Controller. Future contributors learn one pattern, apply it across UI |
| 2026-04-17 | Move `_complex_toggles` from screen onto BattleSetupState | It's data, not UI presentation. Belongs to the model. Save/load gets it for free |
| 2026-04-17 | Extract `FleetHierarchyEditor` as a separate helper | TF/SQ clone duplication is a structural issue independent of MVVM. Solving it in the same project reinforces anti-rebloat principle and demonstrates the decomposition pattern |
| 2026-04-17 | Anti-rebloat: line-budget convention in docs/03_CONVENTIONS.md | Without documented limits, future contributors will pile UI logic back into the screen. Convention gives reviewers grounds to push back. Soft limit (≤300 lines for screens) — the goal is visibility, not brittle enforcement |
| 2026-04-17 | Per-panel files (left/center/right) under panels/ subpackage | Each panel renderer focused on one panel keeps each file small. Future panel additions land naturally in their own file |
| 2026-04-17 | Sequencing: LAST in the 5-project arc | Largest project; benefits from momentum and learnings. Independent of others technically, but cognitive grouping (Combat Lab cluster → UI cleanup cluster) is cleaner |
| 2026-04-17 | Preserve N-team support (PROJ-275) — 2 to 8 sides | Decomposition is structural; behavior must be unchanged. Smoke checklist explicitly tests 2/3/8-side cases |
| 2026-04-17 | Spec compiler stays unchanged | `game/ui/screens/battle_setup/spec_compiler.py` is already well-structured. Touching it would be scope creep |
