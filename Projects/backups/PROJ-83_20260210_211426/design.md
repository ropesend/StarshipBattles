# PROJ-83: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Warning Categories (from test baseline: 7353 passed, 299 warnings)

| Category | ~Count | Root Cause | Fix Strategy |
|---|---|---|---|
| Label Rect Too Small | ~200+ | StatRow labels at 50% width overflow at test resolution | Abbreviate label text |
| BattleEngine Deprecation | ~15 | Tests call engine.start() without ai_factory | Add AIControllerFactory |
| Font Not Preloaded | ~50+ | pygame_gui lazy-loads noto_sans bold/italic variants | Filter in pytest.ini |
| Shadow/Border Clamping | ~18 | Small test windows can't fit theme border/shadow values | Filter in pytest.ini |
| Slider Value Out of Range | ~1 | set_current_value() called before value_range updated | Swap order |

## Swarm Findings Summary

### Architecture

**StatRow label sizing** (`game/ui/panels/design_stats_panel.py:49-59`):
- Labels use `int(width * 0.50)` of the column width
- Column width = `(container_width - 30) // 2`
- In tests with 800x600 windows and ~300px panels: `col_w ≈ 135`, `lbl_w ≈ 67px`
- At font size 14, most label texts exceed 67px width
- Fix: Abbreviate labels rather than change ratio (user decision)

**BattleEngine deprecation path** (`game/simulation/systems/battle_engine.py:268-291`):
- `start()` accepts optional `ai_controllers` or uses `_ai_factory` attribute
- When neither provided, falls back to legacy path with deprecation warning
- `AIControllerFactory` (`game/simulation/factories/ai_factory.py`) is the simulation-layer tool
- `BattleOrchestrator` (`game/ui/orchestration/battle_orchestrator.py`) is for UI layer
- Tests should use `AIControllerFactory` since they're simulation-layer code

**Slider bug** (`game/ui/screens/transfer_dialog.py:217-222`):
- `_update_amount_ui()` sets value BEFORE range, triggering "value not in range" warning
- Simple fix: swap the two lines

### Key Patterns to Reuse
- **AIControllerFactory**: `game/simulation/factories/ai_factory.py` — already exists from PROJ-43
- **create_battle_engine()**: `tests/fixtures/battle.py:40-54` — shared fixture factory
- **pytest filterwarnings**: Standard pytest.ini feature for warning management

### Dependencies & Risks
1. **Label abbreviation readability** — shortened labels must remain understandable in context (values + units provide context). Mitigation: Keep abbreviations recognizable (e.g., "Maneuver Pts" not "MP").
2. **Build queue truncation** — reducing from 15 to 12 chars means "mining_complex_mk1" becomes "mining_compl". Mitigation: acceptable since full name visible on hover/selection.
3. **AIControllerFactory grid dependency** — factory needs engine.grid, but grid is created in BattleEngine.__init__(), so create engine first, then factory, then assign `engine._ai_factory = factory`.

### Opportunities Discovered
- Adding `error::DeprecationWarning` to pytest.ini will catch future deprecation regressions automatically

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
