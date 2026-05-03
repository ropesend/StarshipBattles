# DRY-CORE: Core, AI, Engine, Research, Data, Assets Report

## Summary
- **Total duplication findings:** 9
- **Critical:** 1, **Major:** 4, **Minor:** 3, **Info:** 1

## Findings

### CRITICAL: Singleton Service State Management Duplication
**ID:** CQ-001
**Location:** `game/core/registry.py:122-264`, `game/ai/strategy_manager.py:20-51`, `game/assets/asset_manager.py:9-35`, `game/core/logger.py:9-33`
**Issue:** Four singleton services duplicate state management patterns: clear(), _loaded flag, lazy loading. All use SingletonMeta correctly but repeat the service wrapper pattern (60+ lines duplicated).
**Recommendation:** Create abstract `BaseSingletonService` with common clear(), _loaded, lazy loading pattern.
**Effort:** Medium

### MAJOR: Data Loading and JSON Parsing Patterns
**ID:** CQ-002
**Location:** `strategy_manager.py:83-105`, `tech_tree.py:29-93`, `asset_manager.py:37-51`
**Issue:** Three independent JSON loading implementations with identical pattern: resolve path → load JSON → extract nested key → log result.
**Recommendation:** Create `load_json_with_extraction(file_path, extraction_key, default)` utility.
**Effort:** Simple

### MAJOR: AI Behavior Caching Pattern
**ID:** CQ-003
**Location:** `controller.py:133-173`, `target_evaluator.py:236-263`
**Issue:** Two independent cache-building implementations for ship capabilities.
**Recommendation:** Move to shared `CombatCache` utility in `combat_utils.py`.
**Effort:** Medium

### MAJOR: Validation Result Aggregation
**ID:** CQ-004
**Location:** `game/core/validation.py:132-145`, `tech_tree.py:191-252`
**Issue:** Research validation uses List[str] instead of canonical ValidationResult from core.
**Recommendation:** TechTree.validate() should return ValidationResult; use merge() for aggregation.
**Effort:** Medium

### MAJOR: Trait-Based Safety Access Pattern
**ID:** CQ-005
**Location:** `combat_utils.py:167-237`
**Issue:** Two specialized "safely access nested property" functions using identical defensive pattern (try/except + getattr + logging).
**Recommendation:** Document the pattern for future reuse. Functions are well-designed.
**Effort:** Info (documentation)

### Minor: Service Data Clearing Pattern
**ID:** CQ-006
**Location:** `strategy_manager.py:53-64`, `strategy_metadata.py:51-57`, `asset_manager.py:31-35`
**Issue:** Three services implement nearly identical clear() methods.
**Recommendation:** Document clear() contract in BaseSingletonService.
**Effort:** Simple

### Minor: Position/Rotation Safe Access
**ID:** CQ-007
**Location:** `combat_utils.py:66-125`
**Issue:** get_position() and get_rotation() nearly identical structure with interface-first fallback.
**Recommendation:** Document pattern for reuse. No code changes needed.
**Effort:** Info

### Minor: Serialization/Deserialization Pattern
**ID:** CQ-008
**Location:** `research_tracker.py:22-37`
**Issue:** to_dict()/from_dict() pattern only in research layer. Other layers likely have different patterns.
**Recommendation:** Consider Serializable protocol in game/core if serialization grows.
**Effort:** Complex (future)

### Info: Well-Designed combat_utils.py (Positive)
**ID:** CQ-009
**Issue:** combat_utils.py successfully consolidates 8 helper functions preventing duplication. Good design.
**Effort:** N/A

## Top 5 Priority Consolidation Opportunities
1. **CQ-001**: BaseSingletonService abstraction - 4 services, Medium, High future ROI
2. **CQ-002**: Unified JSON loading utility - 3 loaders, Simple, Quick win
3. **CQ-003**: CombatCache abstraction - 2 locations, Medium, Standardizes caching
4. **CQ-004**: ValidationResult for research - Medium, Unifies cross-layer validation
5. **CQ-005**: Document defensive access pattern - Simple, Prevents future duplication
