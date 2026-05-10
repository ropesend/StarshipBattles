# Duplication & Fragmentation Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 24
- **Total Issues Found:** 10
- **Critical:** 0 | **Major:** 4 | **Minor:** 5 | **Info:** 1

## Findings

#### MAJOR: Duplicated ID-Based Expansion Tracking Pattern in Battle Panels
**ID:** DUP-UI2-001
**Location:** `game/ui/panels/battle_panels.py:59-86` AND `game/ui/panels/battle_panels.py:263-286`
**Issue:** `ShipStatsPanel` and `SeekerMonitorPanel` each implement nearly identical patterns for ID-based expansion tracking. Both have:
- `_get_*_id()` method to extract string IDs from objects
- `_is_*_expanded()` method checking if ID is in a set
- `_toggle_*_expanded()` method to toggle set membership

```python
# ShipStatsPanel (lines 59-86):
def _get_ship_id(self, ship):
    ship_id = getattr(ship, 'id', None)
    if isinstance(ship_id, str):
        return ship_id
    ship_name = getattr(ship, 'name', None)
    if isinstance(ship_name, str):
        return ship_name
    return str(id(ship))

def _is_expanded(self, ship):
    return self._get_ship_id(ship) in self.expanded_ships

def _toggle_expanded(self, ship):
    ship_id = self._get_ship_id(ship)
    if ship_id in self.expanded_ships:
        self.expanded_ships.discard(ship_id)
    else:
        self.expanded_ships.add(ship_id)

# SeekerMonitorPanel (lines 263-286) - nearly identical:
def _get_projectile_id(self, proj):
    proj_id = getattr(proj, 'id', None)
    if isinstance(proj_id, str):
        return proj_id
    return str(id(proj))
# ... same _is_seeker_expanded and _toggle_seeker_expanded pattern
```
**Impact:** Maintenance risk - if ID extraction logic changes, must update in multiple places. ~27 lines duplicated.
**Recommendation:** Extract a generic `ExpansionTracker` mixin class or standalone helper that provides `get_id()`, `is_expanded()`, `toggle_expanded()` methods.
**Effort:** Simple

#### MAJOR: Duplicated Font Creation in Battle Panels
**ID:** DUP-UI2-002
**Location:** `game/ui/panels/battle_panels.py:99-101` AND `game/ui/panels/battle_panels.py:307-309`
**Issue:** Font objects are created inline with identical sizes in multiple panel `draw()` methods:
```python
# ShipStatsPanel.draw() (lines 99-101):
font_title = pygame.font.Font(None, UIConfig.FONT_TITLE)  # 28
font_name = pygame.font.Font(None, UIConfig.FONT_NAME)    # 22
font_stat = pygame.font.Font(None, UIConfig.FONT_STAT)    # 18

# SeekerMonitorPanel.draw() (lines 307-309):
font_title = pygame.font.Font(None, 28)  # Same size but hardcoded!
font_name = pygame.font.Font(None, 22)
font_stat = pygame.font.Font(None, 18)
```
Additionally, `BattleControlPanel.draw()` creates fonts at lines 514, 519, 537.
**Impact:** Font creation is not cached between frames, causing potential performance overhead. Also, `SeekerMonitorPanel` uses hardcoded values instead of UIConfig constants.
**Recommendation:** Create fonts once in `BattlePanel.__init__()` as instance variables or use a font caching utility. Ensure all panels use UIConfig constants consistently.
**Effort:** Simple

#### MAJOR: Duplicated Ship Cloning Logic in Battle Factories
**ID:** DUP-UI2-003
**Location:** `game/ui/services/battle_factories.py:161-166` AND `game/ui/services/battle_factories.py:168-173`
**Issue:** The same ship cloning logic is repeated twice in `create_hypothetical_battle()`:
```python
cloned1 = []
for ship in ships1:
    data = ShipSerializer.to_dict(ship)
    cloned = ShipSerializer.from_dict(data, registries=ship.registries)
    cloned.x, cloned.y = ship.x, ship.y
    cloned1.append(cloned)

cloned2 = []
for ship in ships2:
    data = ShipSerializer.to_dict(ship)
    cloned = ShipSerializer.from_dict(data, registries=ship.registries)
    cloned.x, cloned.y = ship.x, ship.y
    cloned2.append(cloned)
```
**Impact:** Copy-paste pattern that could drift. If cloning logic needs to preserve additional fields, both blocks must be updated.
**Recommendation:** Extract a `_clone_ships(ships: List[Ship]) -> List[Ship]` helper function.
**Effort:** Simple

#### MAJOR: Duplicated Directory Creation Pattern in Ship IO
**ID:** DUP-UI2-004
**Location:** `game/ui/services/ship_io.py:50-51` AND `game/ui/services/ship_io.py:89-90`
**Issue:** Both `save_ship()` and `load_ship()` methods independently check and create the ships folder:
```python
# save_ship() lines 50-51:
if not os.path.exists(ships_folder):
    os.makedirs(ships_folder)

# load_ship() lines 89-90:
if not os.path.exists(ships_folder):
    os.makedirs(ships_folder)
```
**Impact:** Minor duplication, but shows fragmentation of directory initialization responsibility.
**Recommendation:** Extract to a private `_ensure_ships_folder()` method or perform initialization once in a class-level setup.
**Effort:** Simple

#### MINOR: Registry Provider Lazy Resolution Pattern Duplication
**ID:** DUP-UI2-005
**Location:** `game/ui/services/component_service.py:46-50` AND `game/ui/services/vehicle_class_service.py:50-52`
**Issue:** Both services implement similar `_get_provider()` patterns for lazy registry resolution:
```python
# ComponentService:
def _get_provider(self) -> IRegistryProvider:
    if self._provider is None:
        self._provider = get_default_registry_provider()
    return self._provider

# VehicleClassService:
def _get_provider(self) -> IRegistryProvider:
    return self._provider  # Strict DI - no fallback
```
And `ShipFactory` has a similar `_get_registries()` method (line 49-56).
**Impact:** Low risk - the pattern is intentionally slightly different (strict vs optional DI). However, the services could share a base class or mixin.
**Recommendation:** Consider a `RegistryAwareService` base class if more services are added.
**Effort:** Medium

#### MINOR: get_bounding_rect Pattern with Different Alpha Thresholds
**ID:** DUP-UI2-006
**Location:** `game/ui/utils.py:110` AND `game/ui/assets/ship_theme_manager.py:155,189` AND `game/ui/screens/design_image_helper.py:165`
**Issue:** Multiple files call `surface.get_bounding_rect()` with different `min_alpha` thresholds (10, 20, 1) without clear rationale for the differences:
```python
# utils.py:110 - uses 10
bbox = surface.get_bounding_rect(min_alpha=alpha_threshold)  # default 10

# ship_theme_manager.py:155 - uses 20
rect = surf.get_bounding_rect(min_alpha=20)

# ship_theme_manager.py:189 - uses 1
rect = surf.get_bounding_rect(min_alpha=1)

# design_image_helper.py:165 - uses 10
bbox = loaded_img.get_bounding_rect(min_alpha=10)
```
**Impact:** Inconsistent behavior when determining visible bounds. Different thresholds could cause subtle visual differences.
**Recommendation:** Define a UI constant for standard alpha threshold and document when/why different values are needed.
**Effort:** Simple

#### MINOR: Singleton Managers Follow Similar Pattern Without Base Class
**ID:** DUP-UI2-007
**Location:** `game/ui/services/screenshot_manager.py:11-27` AND `game/ui/assets/ship_theme_manager.py:11-43` AND `game/ui/renderer/sprites.py:8-26`
**Issue:** Three managers use `SingletonMeta` metaclass but each implements their own initialization and clear/reset patterns:
- `ScreenshotManager.__init__()` calls `_setup()`
- `ShipThemeManager.__init__()` initializes multiple caches with a `clear()` method
- `SpriteManager.__init__()` has simple attribute initialization

**Impact:** Low - the metaclass handles thread-safe instantiation. Minor inconsistency in reset/clear patterns.
**Recommendation:** Consider a `ClearableSingletonMixin` that standardizes cache clearing behavior.
**Effort:** Medium

#### MINOR: Scale Image Pattern Repeated in Multiple Files
**ID:** DUP-UI2-008
**Location:** Multiple files use `pygame.transform.scale()` or `pygame.transform.smoothscale()` with similar patterns
**Issue:** The pattern of calculating new dimensions and scaling images appears many times across the codebase (40+ occurrences in panels/screens). While `game/ui/utils.py` provides helper functions (`scale_and_rotate_image`, `scale_image_to_fit`, `scale_image_by_visible_portion`), many call sites still perform inline scaling without using these utilities.
**Impact:** The utilities exist but aren't consistently used. New code might not discover them.
**Recommendation:** Document the utility functions in `game/ui/utils.py` more prominently and consider adding code review guidance to prefer these helpers.
**Effort:** Medium (gradual migration)

#### MINOR: AIControllerFactory Created Multiple Times
**ID:** DUP-UI2-009
**Location:** `game/ui/services/battle_factories.py:21-28` AND `game/ui/screens/battle_screen.py:73`
**Issue:** `AIControllerFactory()` is instantiated in multiple places:
```python
# battle_factories.py:
def _create_default_ai_factory():
    return AIControllerFactory()

# battle_screen.py:
self._ai_factory = AIControllerFactory()
```
The factory functions in `battle_factories.py` create new factories for each call, while `BattleScreen` creates one at init.
**Impact:** Minor - factory is lightweight. But pattern is inconsistent.
**Recommendation:** Consider whether a shared factory instance could be used, or document why separate instances are preferred.
**Effort:** Simple

#### INFO: Similar Ship Loading Patterns Between Services
**ID:** DUP-UI2-010
**Location:** `game/ui/services/ship_io.py:100` AND `game/ui/services/ship_factory.py:84`
**Issue:** Two services load ships from dict data:
```python
# ship_io.py: Uses Ship.from_dict directly
new_ship = Ship.from_dict(data)

# ship_factory.py: Wraps Ship.from_dict with registries
return Ship.from_dict(design_data, registries=self._get_registries(registry_provider))
```
**Impact:** Informational - these serve different purposes (file I/O vs factory pattern). The `ship_io.py` version doesn't explicitly pass registries, relying on defaults.
**Recommendation:** Consider whether `ShipIO.load_ship()` should accept or use explicit registries for consistency.
**Effort:** Simple

## Top 5 Priority Issues
1. **DUP-UI2-001** (Major): ID-based expansion tracking pattern is duplicated and could be extracted to reduce code and ensure consistent behavior across panels.
2. **DUP-UI2-002** (Major): Font creation happens every frame in draw() methods - should be cached for performance and consistency (use UIConfig constants everywhere).
3. **DUP-UI2-003** (Major): Ship cloning logic is copy-pasted and should be extracted to a helper function for maintainability.
4. **DUP-UI2-004** (Major): Directory creation pattern is fragmented between save/load operations.
5. **DUP-UI2-006** (Minor): Inconsistent alpha thresholds for bounding rect calculations could cause subtle visual inconsistencies.
