# PROJ-105: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Battle Panel Architecture
Three `BattlePanel` subclasses in `game/ui/panels/battle_panels.py`:
- **ShipStatsPanel** (right side, 450px wide) — ship roster with expandable details
- **SeekerMonitorPanel** (left side, 300px wide) — missile tracking with expandable details
- **BattleControlPanel** (overlay) — end battle button + victory screen

All inherit from `BattlePanel(scene, x, y, w, h)` and implement `draw(screen)`.

### Data Flow: Two Rendering Paths
1. **Collapsed view**: Uses `_get_ships()` → `ui_service.get_ships()` → `List[ShipDTO]`. Only accesses: `id`, `team_id`, `name`, `is_alive`, `is_derelict`.
2. **Expanded view**: Calls `ship_stats_renderer.py` functions that expect **domain Ship objects** (not DTOs). Accesses: `ship.resources.get_all_resources()`, `ship.layers.get(LayerType.OUTER)`, `ship.current_target.is_alive`, `comp.has_ability('WeaponAbility')`.

### Key Dependencies for Rendering
- `StrategyManager.instance().strategies` — needed by `draw_ship_info_header()` (line 243 of ship_stats_renderer.py). Hydrated by root conftest `reset_game_state` fixture.
- `pygame.mouse.get_pos()` — called by SeekerMonitorPanel for button hover (line 333). Returns `(0, 0)` in headless mode (deterministic).
- `screen.get_size()` — called by BattleControlPanel for victory text centering (line 487).

### Existing Infrastructure
- Headless Pygame: `SDL_VIDEODRIVER=dummy` + `enforce_headless` session fixture
- Test resolution: 1440x900 via `DisplayConfig.test_resolution()`
- MockBattleUIService in `tests/unit/ui/mocks/`
- JSON snapshot regression pattern in `tests/regression/modifier_ability_snapshots/`
- `pygame.image.save()` works in headless mode (proven by ScreenshotManager)
- Pillow already installed (v9.5.0)

## Swarm Findings Summary

### Architecture
- Visual regression module fits cleanly at `tests/visual_regression/`
- No circular import risks — UI depends on Core/Sim/AI, never the reverse
- Root conftest `reset_game_state` hydrates StrategyManager before each test, cleans after
- `_get_ships()` guard (line 39) requires `get_ships()` to return a real `list`, not a MagicMock auto-attribute

### Key Patterns to Reuse
- **Snapshot test pattern**: `tests/regression/modifier_ability_snapshots/conftest.py` — `load_snapshot()`, `save_snapshot()`, `compare_snapshots()` with auto-create on first run
- **Mock ship fixtures**: `tests/unit/ui/services/battle_ui_service/conftest.py` — `mock_ship`, `mock_battle_service`
- **MockBattleUIService**: `tests/unit/ui/mocks/mock_battle_ui_service.py` — implements `IBattleUI` protocol
- **Display reset fixture**: `tests/unit/ui/conftest.py` — `pygame_display_reset` (autouse)

### Dependencies & Risks
1. **xdist race conditions** — `pytest.ini` defaults to `-n 4`. Baseline updates must use `-n 1` to avoid file corruption. Add warning in `--update-baselines` implementation.
2. **Font determinism** — `pygame.font.Font(None, size)` uses SDL default font, deterministic on same machine + same Pygame-CE version. Baselines invalid after Pygame-CE upgrade.
3. **Expanded view mocking** — `ship_stats_renderer.py` expects domain-like objects. Need `MagicMock` with explicit attributes, not auto-mocking.
4. **Scroll offset** — ShipStatsPanel has `scroll_offset`. Must set to 0 for deterministic rendering.

### Opportunities Discovered
- Could extend to pygame_gui panels in Phase 2 (needs UIManager + theme)
- Image comparison engine is reusable for any future visual testing
- Panel registry pattern makes adding new panels trivial

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
