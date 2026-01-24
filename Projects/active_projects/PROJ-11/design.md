# PROJ-11: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-01-24_general_maintainability-extensibility-health](../../Reviews/results/2026-01-24_general_maintainability-extensibility-health/)
- **Type:** General Review (Comprehensive)
- **Date:** 2026-01-24
- **Report:** [View Full Report](../../Reviews/results/2026-01-24_general_maintainability-extensibility-health/report.md)

## Initial Analysis
This project addresses architectural issues identified in the review:
- **Critical:** 5 issues (circular dependencies, god objects)
- **Major:** 13 issues (layer coupling, SRP violations)
- **Selected for remediation:** 18

## Architecture Principles

### 1. Dependency Direction
Dependencies should flow: UI → Business Logic → Core
- UI can depend on facades/viewmodels
- Business logic (Strategy, Simulation) depends on Core
- Core depends on nothing

### 2. Single Responsibility
Each class should have one reason to change:
- UI classes: layout OR state OR events (not all three)
- Entity classes: coordination, not implementation
- Service classes: one domain concern

### 3. Interface Segregation
Clients should not depend on interfaces they don't use:
- Create specific facades for UI needs
- Create specific DTOs for data transfer
- Avoid "god interfaces"

## Key Patterns to Implement

### Dependency Injection Container
```python
# game/core/container.py
class Container:
    _services = {}

    @classmethod
    def register(cls, interface, implementation):
        cls._services[interface] = implementation

    @classmethod
    def resolve(cls, interface):
        return cls._services[interface]
```

### GameFacade Pattern
```python
# game/ui/facades/battle_facade.py
class BattleFacade:
    def __init__(self, engine: BattleEngine):
        self._engine = engine

    def get_ships(self) -> List[ShipViewModel]:
        return [ShipViewModel.from_ship(s) for s in self._engine.ships]
```

### Component Extraction Pattern
```python
# Before: God object
class StrategyInterface:
    # 885 lines of everything

# After: Composed components
class StrategyInterface:
    def __init__(self):
        self.layout = StrategyUILayout()
        self.state = StrategyUIState()
        self.events = StrategyUIEventHandler(self.state)
        self.windows = StrategyUIWindowManager()
```

## Dependencies & Risks
1. **Risk: Breaking changes** - Mitigation: Small incremental changes, test after each
2. **Risk: Regression bugs** - Mitigation: Comprehensive test coverage before refactoring
3. **Dependency: PROJ-10** - Complete security fixes first (don't block on refactoring)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
