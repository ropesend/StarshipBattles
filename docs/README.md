# Starship Battles Documentation

> **Audience:** LLM agents (Claude Code, automated workers). Optimized for machine readability.
> **Last verified:** 2026-04-28 — Documentation consistency pass: pattern count is 30 (added Registrar Close-Callback for BUG-121), `ApplicationContext` manages 9 services, broken archive links were corrected, and current layer/dependency guidance was reconciled with source.

---

## Reading Order for Agents

**Always start here.** Read docs 01-03 before doing any work. Then read task-specific docs.

### Step 1: Foundation (read for ALL tasks)

| # | Document | What you learn |
|---|----------|---------------|
| 1 | [01_ARCHITECTURE.md](01_ARCHITECTURE.md) | Layer structure, package APIs, protocols, data flow |
| 2 | [02_PATTERNS.md](02_PATTERNS.md) | 30 design patterns with file locations and code examples |
| 3 | [03_CONVENTIONS.md](03_CONVENTIONS.md) | Naming, file organization, imports, testing conventions |

### Step 2: Task-specific (read based on what you're doing)

**Working on services or business logic:**
- [04_SERVICES.md](04_SERVICES.md) — Service layer API reference

**Handling errors or logging:**
- [05_ERROR_HANDLING.md](05_ERROR_HANDLING.md) — Exception hierarchy, error codes, logging patterns

**Working on UI or rendering:**
- [06_UI_STYLE_GUIDE.md](06_UI_STYLE_GUIDE.md) — Color constants, themes, pygame_gui styling

**Working with development tools (asset processors, editors, test runners):**
- [Tools/README.md](../Tools/README.md) — Development tool catalog and creation guide

### Step 3: Domain-specific (read when working in that system)

| System | Document | Covers |
|--------|----------|--------|
| Combat/Simulation | [combat_simulation.md](systems/combat_simulation.md) | Battle modes, damage pipeline, ship architecture, abilities |
| Abilities | [ability_reference.md](systems/ability_reference.md) | All 53 component abilities: registry keys, parameters, stat bindings |
| Strategy/Turn Engine | [strategy_layer.md](systems/strategy_layer.md) | Facade, command dispatch, turn engine, fleet delegates, fleet hierarchy (task forces, squadrons), design roles, group policies, deployment zones, auto-suggestion, events |
| AI | [ai_system.md](systems/ai_system.md) | Movement behaviors, spatial behaviors, group target coordinator, strategy manager, target evaluator, adapters |
| Research | [research_system.md](systems/research_system.md) | Tech tree, research tracker, leaky bucket algorithm |
| Orders | [orders_system.md](systems/orders_system.md) | Order lifecycle, types, execution engines |
| Production | [production_system.md](systems/production_system.md) | Build queues, tick-based production, spawning, rate resolution |
| Resources | [resource_system.md](systems/resource_system.md) | Unified resource catalog (materials + consumables), resource definitions, component-driven behavior |

### Step 4: How-to guides (read when performing specific tasks)

| Task | Guide |
|------|-------|
| Understand components/abilities | [component_system.md](guides/component_system.md) |
| Add a new ability | [adding_abilities.md](guides/adding_abilities.md) |
| Understand modifiers | [modifier_system.md](guides/modifier_system.md) |
| Add a new modifier | [adding_modifiers.md](guides/adding_modifiers.md) |
| Create/modify QS complexes | [qs_complex_design.md](guides/qs_complex_design.md) |
| Write simulation tests | [simulation_testing.md](guides/simulation_testing.md) |
| Understand test infrastructure | [testing_infrastructure.md](guides/testing_infrastructure.md) |
| Profile performance | [performance_profiling.md](guides/performance_profiling.md) |

---

## Directory Structure

```
docs/
├── README.md                    <- You are here
├── 01_ARCHITECTURE.md           # Layers, packages, APIs, protocols, data flow
├── 02_PATTERNS.md               # 30 design patterns (ApplicationContext DI, Facade, CQRS, External-Stats Bridge, Scope-Driven Team Routing, Spec Compiler, Registrar Close-Callback, ...)
├── 03_CONVENTIONS.md            # Naming, file org, imports, test conventions
├── 04_SERVICES.md               # Service layer API reference
├── 05_ERROR_HANDLING.md         # Exceptions, error codes, logging
├── 06_UI_STYLE_GUIDE.md         # Colors, themes, pygame_gui
│
├── _ignore/                     # User's personal notes — NOT documentation. DO NOT READ.
│
├── guides/                      # How-to guides for common tasks
│   ├── component_system.md        Component/ability system overview
│   ├── adding_abilities.md        Step-by-step: add a new ability
│   ├── modifier_system.md         Modifier system overview
│   ├── adding_modifiers.md        Step-by-step: add a new modifier
│   ├── qs_complex_design.md       QS complex design: JSON structure, initial complexes, crew budgets
│   ├── simulation_testing.md      Simulation test scenarios
│   └── testing_infrastructure.md  DI fixtures, conftest, test helpers
│
└── systems/                     # Domain-specific architecture
    ├── ability_reference.md       All 53 abilities: keys, parameters, stat bindings
    ├── combat_simulation.md       Battle orchestration, damage pipeline
    ├── strategy_layer.md          Facade, turn engine, commands, events
    ├── ai_system.md               AI behaviors, targeting, adapters
    ├── research_system.md         Tech tree, research tracker
    ├── orders_system.md           Order lifecycle and execution
    ├── production_system.md       Build queues, production model, spawning
    └── resource_system.md         Unified resource catalog (materials + consumables)
```

## Quick Reference

- **Test command (pytest):** `python Tools/test_sharded/test_sharded.py`
- **Test command (simulation):** `python -m combat_lab.run_tests`
- **Profiling:** `python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance`
- **Minimum resolution:** 2560x1600 (optimized for 4K: 3840x2160)
- **Python:** 3.x with Pygame, Pytest, pytest-xdist
- **Historical/archived docs:** `Projects/deep_archive/` and `Projects/archived_projects/` (not in docs/ — do not read for current info)
