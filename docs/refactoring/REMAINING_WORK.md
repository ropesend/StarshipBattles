# Starship Battles - Refactoring Status Dashboard

**Last Updated:** 2026-02-07

---

## Completed Work

### Design Workshop Refactoring (2026-01-17)

Renamed "Ship Builder" to "Design Workshop" across 3 phases. Added dual launch modes (standalone/integrated), tech preset system, and design library with save/load/filter/search. 83 new tests, zero breaking changes.

See: [completed/REFACTORING_COMPLETE.md](completed/REFACTORING_COMPLETE.md)

### Strategy Scene Split (2026-01-16)

Split `strategy_scene.py` from 1,568 lines to 417 lines across 6 focused modules (renderer, input handler, camera navigation, fleet operations, colonization).

See: [completed/strategy_scene_split.md](completed/strategy_scene_split.md)

### Code Quality Phases 1-14 (January 2026)

Consolidation plan executed across 14 phases:

| Area | Status |
|------|--------|
| Core utilities, ship helpers, JSON migration | Complete |
| Singleton pattern, test infrastructure, layer coupling | Complete |
| Event bus, print-to-logging, layer iteration refactor | Complete |
| Test framework consolidation, service layer, validation | Complete |
| Configuration migration (AI, physics, UI constants) | Complete |
| Bare exception handlers, logger bug, fixture deduplication | Complete |
| Circular import analysis (TYPE_CHECKING pattern accepted) | Complete |
| Commented debug code removal, TODO comment cleanup | Complete |

See: [completed/originals/code_quality_refactor.md](completed/originals/code_quality_refactor.md)

---

## Active Projects

All projects tracked in `Projects/active_projects/`. Each has its own `plan.md`, `design.md`, and phase checklists.

| Project | Description | Status |
|---------|-------------|--------|
| [PROJ-57](../../Projects/active_projects/PROJ-57/plan.md) | Test Lab Screen god class decomposition | All 5 phases complete, audit passed. Awaiting user verification. |
| [PROJ-58](../../Projects/active_projects/PROJ-58/plan.md) | Eradicate backward compatibility shims | All 7 phases complete (6246 tests passing). Awaiting final audit. |
| [PROJ-60](../../Projects/active_projects/PROJ-60/plan.md) | Break down GalaxyTestScreen | Phases 1-3 complete, Phase 4 (final slim) not started. |
| [PROJ-61](../../Projects/active_projects/PROJ-61/plan.md) | Workshop Screen breakdown (943 to <500 lines) | Planned, not started. Awaiting user approval. |
| [PROJ-62](../../Projects/active_projects/PROJ-62/plan.md) | Planet List Window breakdown (1136 to <500 lines) | Planned, not started. Awaiting user approval. |
| [PROJ-63](../../Projects/active_projects/PROJ-63/plan.md) | Build Queue Screen breakdown (945 to <500 lines) | Planned, not started. Awaiting user approval. |
| [PROJ-64](../../Projects/active_projects/PROJ-64/plan.md) | Narrow exception handling (90 broad catches) | Planned, not started. Awaiting user approval. |
| [PROJ-65](../../Projects/active_projects/PROJ-65/plan.md) | Game class scene protocol refactor (app.py <300 lines) | Planned, not started. Awaiting user approval. |

---

## Ready to Start

These items have existing analysis or plans but no active PROJ-XX project yet.

### Large File Splits (Remaining)

The [LARGE_FILE_SPLIT_PLAN.md](LARGE_FILE_SPLIT_PLAN.md) identifies 14 files over 500 lines. Several now have active projects (PROJ-60 through PROJ-63, PROJ-65). Files without projects yet:

| File | Lines | Priority |
|------|-------|----------|
| `abilities.py` | 780 | HIGH |
| `controller.py` | 668 | HIGH |
| `ship.py` | 785 | MEDIUM |
| `battle_panels.py` | 694 | MEDIUM |
| `ship_stats.py` | 678 | MEDIUM |
| `component.py` | 671 | MEDIUM |
| `strategy_screen.py` | 786 | LOW |
| `setup_screen.py` | 668 | LOW |
| `planet_gen.py` | 516 | LOW |
| `builder_viewmodel.py` | 511 | LOW |

### Ability Boilerplate Reduction

20+ ability classes in `game/simulation/components/abilities.py` follow identical patterns. Consider factory pattern, base class consolidation, or configuration-driven creation. Blocked on abilities.py file split (above).

---

## Open Questions

| Item | Context |
|------|---------|
| Deprecated code in `strategy_scene.py:70`, `ship_stats.py:320`, `controller.py:154-190` | Legacy references and functions marked deprecated. Verify if PROJ-58 addressed these or if they still need removal. |
| PROJ-52 (findings only, no plan) | Directory exists with a `findings/` folder but no plan.md. Determine if this project is abandoned or was absorbed into another project. |
| Direct domain access in builder_screen.py | Lines 19, 466, 689, 701, 719 use direct registry/Ship access instead of service layer. Low priority -- may be addressed by PROJ-61 workshop breakdown. |
| Tools/ hardcoded paths | `Tools/component_manager.py`, `component_graphic_picker.py`, `resize_components.py` have hardcoded paths. Out of scope for game code refactoring. |
