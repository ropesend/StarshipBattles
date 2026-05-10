# PROJ-214: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis
The strategy map renderer (`game/ui/screens/strategy_renderer.py`) draws the galaxy with grid, warp lanes, systems, and fleets. It already has a `_draw_hover_hex()` method that draws a hex outline using the 6-corner polygon pattern. The Galaxy class maintains spatial indexes for O(1) lookups of planets, zones (stars/Dyson Spheres/storms), and warp points by global hex coordinate.

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
- `StrategyRenderer` delegates to `self.scene` (StrategyScreen) for all data access
- Galaxy spatial indexes: `_global_hex_planets`, `_global_hex_zones`, `_global_hex_warp_points` provide O(1) lookups
- Player identification: `self.scene.session.player_empire.id`
- Turn tracking: `self.scene.session.turn_number` increments on turn processing

### Key Patterns to Reuse
- **Hover hex polygon**: `strategy_renderer.py:165-176` - 6-corner hex outline with `hex_to_pixel` + `camera.world_to_screen`
- **Viewport culling**: `strategy_renderer.py:178-196` - screen-space bounds check with margin
- **Owner lookup**: `strategy_renderer.py:379,611` - `next((e for e in self.empires if e.id == owner_id), None)`

### Dependencies & Risks
1. **Performance** - Iterating all occupied hexes each frame mitigated by: turn-based caching, viewport culling, sparse iteration (only hexes with objects)
2. **Dyson Sphere dual registration** - Dyson Spheres appear in both `_global_hex_planets` and `_global_hex_zones`; handled by checking `owner_id` attribute presence on zone objects

### Opportunities Discovered
- The existing `_draw_hover_hex` method provided a perfect template for `_draw_inner_hex`

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
