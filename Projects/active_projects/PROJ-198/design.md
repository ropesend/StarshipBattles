# PROJ-198: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Problem Statement
The UI layer contains ~223 actionable `hasattr()`/`getattr()` instances that represent implicit duck typing. This is the last layer to be addressed after PROJ-190 (Core), PROJ-191 (Strategy), PROJ-192 (AI), PROJ-193 (UI Data Binding), and PROJ-194 (Builder/Workshop).

### Key Finding: Overengineering Risk
The original plan proposed ViewModels, ISelectable/IRenderable adapters, and IUIComponentData protocols. Deep analysis revealed this is unnecessary because:

1. **~70% of instances are unnecessary defensive guards** on attributes that always exist. No protocol needed — just delete the guard.
2. **`self.scene` in strategy UI is always `StrategyScreen`** — single concrete type, no polymorphism.
3. **`self.scene.ui` is always `StrategyUI`** — single concrete type.
4. **Projectile, Component, Ship** all have their checked attributes initialized in `__init__`.

### What Actually Needs Protocols
Only a handful of cases genuinely involve polymorphism:
- `battle_panels.py` scenes (BattleScreen vs DTO-based testing)
- `build_queue_screen.py` build_context (Planet vs Fleet)
- `builder/detail_panel.py` selection_data (tuple vs Component)

## Swarm Findings Summary

### Architecture
- **Strategy UI files** all reference `self.scene: StrategyScreen` as their parent
- **StrategyScreen** delegates to `StrategyUI`, which delegates to `StrategyWindowManager`
- **BattleScreen** has `ui_service` (BattleUIService), `test_mode`, `is_battle_over()`
- **Galaxy** does NOT store empires — those live on `GameSession`
- **Ship** and **Projectile** lack explicit `id` attributes; code uses `id(obj)` fallback

### Key Patterns to Reuse
- **PROJ-194**: Initialize attrs in `__init__` → remove hasattr (used for builder buttons)
- **PROJ-193**: TYPE_CHECKING imports for type hints without runtime cost
- **PROJ-191**: Direct `x.attr` access replacing `getattr(x, 'attr', default)`

### Dependencies & Risks
1. **Monkey-patch removal (Phase 3)** changes event dispatch logic in `design_selector_window.py` and `build_queue_selector.py`. Button click handling must work identically after migration to dict lookups.
2. **Bug fixes (Phase 4)** enable previously-dead code paths. The code inside those blocks may have its own issues once it actually runs.
3. **`empire_build_queue_formatter.py` L112** may surface a coordinate-system bug (local vs global hex) that was previously masked.
4. **Ship.id / Projectile.id** — adding `id` attributes could conflict with test mocks or serialization that doesn't expect them.

### Opportunities Discovered
- Fixing the `planet_list_filters.get_owner_name` dead code will actually make the planet list show owner names correctly
- Implementing `show_confirmation_dialog` and `show_ship_picker` in StrategyUI will unblock superweapon features

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Phase Organization Rationale

Phases are organized by **fix type** (not by file) to maximize velocity:

| Phase | Why This Order |
|-------|----------------|
| 1. Trivial Guards | ~90 one-line changes, zero risk, immediate progress |
| 2. Init Declarations | ~15 changes, low risk, unblocks further removals |
| 3. Monkey-Patches | Medium risk — changes event dispatch patterns |
| 4. Bug Fixes | Medium risk — enables dead code paths, needs new tests |
| 5. Type Annotations | Medium effort — needs understanding of polymorphic points |
| 6. Stub Methods | Highest complexity — new UI implementations needed |
