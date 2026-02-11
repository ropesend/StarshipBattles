# Duplication & Fragmentation Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 34
- **Total Issues Found:** 5
- **Critical:** 1 | **Major:** 3 | **Minor:** 1 | **Info:** 0

## Findings

#### CRITICAL: Service Provider Initialization Pattern Duplication
**ID:** DUP-UI2-001
**Location:** `game/ui/services/component_service.py:31-43` AND `game/ui/services/validation_service.py:33-45` AND `game/ui/services/vehicle_class_service.py:36-52` AND `game/ui/services/ship_factory.py:40-56`
**Issue:** All four services implement identical lazy initialization pattern with _provider and _get_provider(). ~15-20 lines of duplicate code per instance, totaling ~60-80 lines. Inconsistent DI handling (vehicle_class_service requires provider, others optional).
**Impact:** Changes to initialization pattern must be made 4 times. Inconsistent DI semantics across services.
**Recommendation:** Extract to shared BaseUIService mixin or factory helper.
**Effort:** Simple

#### MAJOR: Cache Hit Check Pattern in ShipThemeManager
**ID:** DUP-UI2-002
**Location:** `game/ui/assets/ship_theme_manager.py` lines 167-168, 180-181, 215-216, 223-224, 281-282, 291-292
**Issue:** Identical cache-hit pattern repeated 6+ times checking nested dictionaries. Plus near-identical nested dictionary initialization pattern repeated 4+ times. ~35 lines of duplicated cache access code.
**Impact:** Maintenance burden for nested cache logic. Bug fix in one place won't automatically fix others.
**Recommendation:** Extract _get_cached(dict, theme, class) and _set_cached(dict, theme, class, value) helpers.
**Effort:** Medium

#### MAJOR: Placeholder Image Generation (3 locations)
**ID:** DUP-UI2-003
**Location:** `game/ui/utils.py:154-156` AND `game/ui/assets/ship_theme_manager.py:246-253`
**Issue:** Placeholder surface creation logic fragmented with 3 slightly different placeholder colors/sizes and inconsistent fallback behavior. ~20 lines of duplicated code.
**Impact:** Inconsistent fallback behavior. Hard to change placeholder style globally.
**Recommendation:** Create UIPlaceholder.create_empty_placeholder(width, height, color) utility.
**Effort:** Simple

#### MAJOR: Double-Checked Locking Pattern (Singleton)
**ID:** DUP-UI2-004
**Location:** `game/ui/assets/ship_theme_manager.py:28-42` AND `game/ui/renderer/sprites.py:30-44`
**Issue:** Both SpriteManager and ShipThemeManager implement identical double-checked locking singleton pattern. ~25 lines duplicated per singleton. Error messages differ slightly. Inconsistent reset/clear behavior.
**Impact:** Duplicated boilerplate across singleton classes.
**Recommendation:** Create SingletonMeta metaclass or BaseSingleton mixin.
**Effort:** Medium

#### MINOR: Scale/Rotation Utility Functions Fragmentation
**ID:** DUP-UI2-005
**Location:** `game/ui/utils.py` lines 32-63, 66-94, 130-179, 182-219
**Issue:** Four related scaling functions (calculate_ship_image_scale, scale_and_rotate_image, scale_image_by_visible_portion, scale_image_to_fit) scattered with overlapping logic. ~90 lines of scale-related code. Users might pick the wrong function.
**Impact:** High cognitive load. Bug in bounding box detection only fixed in one place.
**Recommendation:** Reorganize into scaling utility class with clear separation of concerns.
**Effort:** Simple

## Top 5 Priority Issues
1. **DUP-UI2-001: Service Provider Init Pattern** - 60-80 lines duplicated across 4 files, inconsistent DI semantics
2. **DUP-UI2-002: ShipThemeManager Cache Pattern** - 35 lines duplicated, maintains 3 separate caches with identical logic
3. **DUP-UI2-004: Double-Checked Locking** - 25+ lines per singleton, pattern could be centralized
4. **DUP-UI2-003: Placeholder Generation** - 3 different implementations, inconsistent styling
5. **DUP-UI2-005: Scale Utility Functions** - 90 lines scattered, high cognitive load
