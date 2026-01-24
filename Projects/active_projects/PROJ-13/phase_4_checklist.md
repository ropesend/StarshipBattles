# PROJ-13 Phase 4: UI Improvements

## Phase Overview
Establish consistent UI patterns and improve architecture.

## Tasks

### Document Builder ViewModel Pattern
- [ ] Review `game/ui/screens/workshop_viewmodel.py`
- [ ] Document pattern usage and benefits
- [ ] Create template/example for new ViewModels
- [ ] Add to ARCHITECTURE.md

### Standardize EventBus Usage (UI-005)
- [ ] Review `ui/builder/event_bus.py`
- [ ] Document event types and naming conventions
- [ ] Create EventTypes enum or constants
- [ ] Consider extending to other screens (optional)

### Address UI-003: Layout Configuration
- [ ] Create `game/ui/layout_config.py` (if not done in Phase 2)
- [ ] Document layout patterns
- [ ] Update at least one screen to use config (example)
- [ ] Note: Full migration deferred to future

### Address UI-004: Reduce getattr Usage
- [ ] Audit getattr usage in UI panels
- [ ] Document expected data contracts
- [ ] Add type hints where missing
- [ ] Consider DTO/ViewModel pattern for data

### Address UI-009: Render Method Refactoring
- [ ] Review long render methods
- [ ] Consider visitor pattern for object rendering
- [ ] Document rendering patterns
- [ ] Implement for one example (optional)

### Address UI-010: Complete builder_screen.py Removal
- [ ] Verify all references removed in Phase 1
- [ ] Update any documentation
- [ ] Close issue

### Address UI-011: Localization Preparation
- [ ] Document current string handling
- [ ] Create StringKeys enum for common strings (optional)
- [ ] Note: Full localization is future work

### Address UI-012: Surface Caching
- [ ] Document cache invalidation patterns
- [ ] Consider RenderCache helper (optional)
- [ ] Note: Full implementation is future work

### Address UI-017: Modal Window Tracking
- [ ] Review modal window tracking in strategy_screen.py
- [ ] Consider WindowManager pattern
- [ ] Document current approach
- [ ] Implement if simple (optional)

## Verification
- [ ] UI patterns documented
- [ ] EventBus usage clear
- [ ] Layout configuration exists
- [ ] At least one example of each pattern
