# Phase 3: Extract Colony Marker

**Objective:** Extract the 3-level nested colony marker block to a helper method.

**Target:** `game/ui/screens/strategy_renderer.py` lines 325-336

---

## Implementation

- [x] **3.1** Add new method `_draw_colony_marker` to `StrategyRenderer` class
  - Location: After `_get_star_asset_key` (from Phase 2)
  - Signature: `def _draw_colony_marker(self, screen, sys, world_pos):`
  - Use early returns to flatten nesting
  ```python
  def _draw_colony_marker(self, screen, sys, world_pos):
      """Draw colony ownership marker at low zoom levels.

      Only draws when zoom < 0.5 and system has owned planets.
      Uses first owned planet's owner color.

      Args:
          screen: pygame.Surface to draw on
          sys: StarSystem object
          world_pos: pygame.math.Vector2 - system center in world coords
      """
      if self.camera.zoom >= 0.5:
          return

      owned_planets = [p for p in sys.planets if p.owner_id is not None]
      if not owned_planets:
          return

      first_owner_id = owned_planets[0].owner_id
      owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
      if not owner_emp:
          return

      offset_world = pygame.math.Vector2(-0.75 * self.hex_size, -0.75 * self.hex_size)
      marker_world = world_pos + offset_world
      marker_screen = self.camera.world_to_screen(marker_world)

      pygame.draw.circle(screen, owner_emp.color, (int(marker_screen.x), int(marker_screen.y)), 5)
      pygame.draw.circle(screen, WHITE, (int(marker_screen.x), int(marker_screen.y)), 6, 1)
  ```

- [x] **3.2** Replace inline code in `_draw_systems` with method call
  - Remove lines 325-336 (the nested if block)
  - Replace with: `self._draw_colony_marker(screen, sys, world_pos)`
  - Place call right after the viewport culling continue (line 321)

---

## Verification

- [x] **3.3** Run colony marker tests: `pytest tests/unit/ui/screens/test_strategy_renderer.py -v -k "colony_marker"`
- [x] **3.4** Run full renderer tests: `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`
- [x] **3.5** Measure complexity: `radon cc game/ui/screens/strategy_renderer.py -s -a`
  - Actual `_draw_systems` CC: 13 (down from 20, better than expected!)

---

## Completion Criteria

- New `_draw_colony_marker` method added
- `_draw_systems` calls the new method
- All tests pass
- CC reduced by ~3
