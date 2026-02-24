# PROJ-167: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized | Starting point for Centralize UI Color Palette Constants |
| 2026-02-23 | Full color audit scope (abilities + UI panels + renderers) | User chose broadest scope to consolidate ALL hardcoded colors, not just ability hints |
| 2026-02-23 | Ability hint colors → `game/simulation/components/abilities/ui_colors.py` | Simulation layer cannot import from game/ui (hard boundary). Abilities already import from game/core. Keeping in same package is cleanest. |
| 2026-02-23 | UI-layer colors → extend existing `game/ui/colors.py` | PROJ-113 established this as the canonical UI color file. Extend with semantic categories. |
| 2026-02-23 | Two-file architecture (sim + ui) | Respects layer boundary. Each file owns its domain's colors. No new cross-layer imports needed. |
| 2026-02-23 | Phase 1 = ability hints (highest duplication), Phase 2 = UI panels, Phase 3 = renderers/misc | Ability hints have 25 unique colors × 51 inline references + 27 test assertions. Highest ROI first. |
| 2026-02-23 | Use flat module-level constants (not dicts/classes) for ability colors | Simpler to import: `from ...ui_colors import HINT_DAMAGE`. Matches existing constant patterns in game.core.constants. |
| 2026-02-23 | Naming convention: `HINT_` prefix for ability color_hint constants | Clearly distinguishes from RGB rendering colors. Examples: `HINT_DAMAGE`, `HINT_SHIELD_CAP`, `HINT_THRUST`. |
