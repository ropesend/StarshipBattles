# PROJ-212: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-27_211243_general_circular-dependency-deferred-imports](../../Reviews/results/2026-02-27_211243_general_circular-dependency-deferred-imports/)
- **Type:** General Review — Architecture Focus
- **Date:** 2026-02-27
- **Report:** [View Full Report](../../Reviews/results/2026-02-27_211243_general_circular-dependency-deferred-imports/report.md)

## Initial Analysis
- 33 validated findings (35 original, 2 rejected, 14 downgraded)
- **Critical:** 0, **Major:** 9, **Minor:** 18, **Info:** 6
- **Selected for remediation:** 9 Major findings across 3 phases
- **Deferred to PROJ-87:** IIA-006 (strategy data layer internal coupling)

## Architecture Context

### Current State
The codebase has **zero top-level layer violations** — architectural discipline is strong. The ~325 deferred imports (excluding TYPE_CHECKING) break down as:
- ~171 circular avoidance (the core problem)
- ~45 redundant duplicates (can delete)
- ~109 intentional lazy loading / conditional (acceptable)

### Key Insight: Phantom Circular Dependencies
Many deferred imports exist defensively but have no actual circular dependency chain. Validators confirmed that `command_handlers.py`, `strategy_fleet_ops.py`, and `strategy_build_queue_manager.py` all defer imports that could safely be top-level. The original developer was cautious; the architecture has evolved past the need.

### The fleet.py Bottleneck
`fleet.py` contains `OrderType` (enum), `FleetOrder` (data class), and `Fleet` (heavyweight class with many dependencies). Because these live together, importing just `OrderType` transitively pulls in `Fleet` and all its dependencies. This single design decision causes 15+ files to defer their fleet imports.

**Solution:** Extract `OrderType`, `FleetOrder`, and order-type sets into `game/strategy/data/order_types.py`.

### Existing Patterns to Leverage
- **StrategySessionFacade** with CQRS-lite commands — already in place, just inconsistently used
- **DI via RegistryManager/DefaultRegistryProvider** — 24 files already use this
- **Lazy property pattern** in TurnEngine — intentional DI fallback, not a defect

## Selected Findings Summary

### Phase 1: Quick Wins
| ID | Finding | File | Effort |
|----|---------|------|--------|
| RS-002 | 11 identical deferred FleetOrder/OrderType imports | `command_handlers.py` | Simple |
| CA-002 | 3 duplicate imports across 3 methods | `strategy_build_queue_manager.py` | Simple |
| IIA-003 | 7x inline formula_system imports | `weapons.py` | Simple |
| RS-003 | Unnecessary deferred command imports | `strategy_fleet_ops.py` | Simple |
| RS-004 | Facade bypass (`session.handle_command`) | `strategy_build_queue_manager.py` | Simple |

### Phase 2: OrderType/FleetOrder Extraction
| ID | Finding | File | Effort |
|----|---------|------|--------|
| RS-001 | OrderType/FleetOrder in monolithic fleet.py | `fleet.py` | Medium |

### Phase 3: DI & Service-Locator
| ID | Finding | File | Effort |
|----|---------|------|--------|
| RS-007 | Service-locator anti-pattern | `fleet_capability_calculator.py` | Medium |
| IIA-005 | Registry deferred in 12 files | `game/core/registry` consumers | Complex (audit) |

## Key Patterns to Reuse
- **Facade pattern**: `game/ui/screens/strategy_screen.py` — how other UI delegates use `self.facade.handle_command()`
- **DI fallback**: `game/strategy/engine/turn_engine.py` — `if self._xxx is None: import and create`
- **Registry injection**: `game/core/registry.py` — `DefaultRegistryProvider` / `TestRegistryProvider`

## Dependencies & Risks
1. **PROJ-87 overlap**: Phase 2's OrderType extraction is complementary to PROJ-87's fleet.py decomposition. Coordinate if both active simultaneously.
2. **Import order sensitivity**: Promoting deferred imports to top-level could expose previously-hidden import order issues. Run full test suite after each task.
3. **Test registry setup**: Some tests may depend on specific import timing for registry initialization. Watch for `set_default_registries()` ordering issues (see MEMORY.md).

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
