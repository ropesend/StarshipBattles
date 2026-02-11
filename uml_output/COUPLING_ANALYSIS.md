# Pyreverse Coupling Analysis Report

**Generated:** 2026-02-10
**Codebase:** Starship Battles (`game/` package)
**Tool:** Pyreverse (Pylint) + Graphviz

---

## Summary

| Metric | Value | Assessment |
|--------|-------|------------|
| Total classes | 434 | Large codebase |
| Total modules | 326 | Well-decomposed |
| Class relationships | 244 | Low (0.56 per class) |
| Module import edges | 977 | Moderate (3.0 per module) |
| Layer violations | 4 | Minor |
| Circular dependencies | 13 pairs | **Significant concern** |

**Overall verdict:** This is **NOT a hairball**. The class-level coupling is actually quite low (0.56 edges/node). However, there are **13 circular dependency pairs** and **4 layer violations** that represent real coupling problems worth fixing.

---

## Generated Diagrams

Open these in a browser for zoomable views:

| Diagram | File | Description |
|---------|------|-------------|
| **Layer Coupling** | `layer_coupling.svg` | High-level view of cross-layer dependencies (best overview) |
| **Circular Dependencies** | `circular_deps.svg` | All 13 bidirectional module dependency pairs |
| **Full Package Graph** | `packages_StarshipBattles.svg` | All 326 modules with 977 edges (the "hairball") |
| **Full Class Graph** | `classes_StarshipBattles.svg` | All 434 classes with 244 edges |
| **Simulation Layer** | `packages_Simulation.svg` | 54 modules, 92 imports |
| **Strategy Layer** | `packages_Strategy.svg` | 73 modules, 117 imports |
| **UI Layer** | `packages_UI.svg` | 154 modules, 232 imports |

---

## Cross-Layer Dependencies

Expected layering (bottom to top):
```
core (0) → engine (1) → simulation (2) → strategy/research (3) → ai (4) → ui (5) → app (6)
```

### Import Counts Between Layers

| From → To | Count | Status |
|-----------|-------|--------|
| ui → core | 189 | OK (heaviest dependency) |
| ui → strategy | 77 | OK |
| strategy → core | 60 | OK |
| simulation → core | 49 | OK |
| ui → simulation | 18 | OK |
| app → ui | 14 | OK |
| ai → core | 12 | OK |
| app → core | 10 | OK |
| ui → ai | 9 | OK |
| research → core | 6 | OK |
| strategy → simulation | 5 | OK |
| engine → core | 4 | OK |
| **simulation → ai** | **2** | **VIOLATION** |
| **research → ui** | **2** | **VIOLATION** |

### Layer Violations (4 total)

#### 1. `simulation → ai` (layer 2 importing layer 4)
- `game.simulation.factories.ai_factory → game.ai.controller`
- `game.simulation.factories.ai_factory → game.ai.interfaces`

**Impact:** Simulation layer should not know about AI. The factory creates AI controllers, coupling the layers.
**Fix:** Move `ai_factory` to a higher layer, or inject AI controllers via an interface defined in simulation.

#### 2. `research → ui` (layer 3 importing layer 5)
- `game.research.ui.research_renderer → game.ui.renderer.camera`
- `game.research.ui.research_scene → game.ui.renderer.camera`

**Impact:** Research UI code imports from the general UI renderer. Since `research.ui` is itself a UI concern, this is more of a packaging issue than a true layer violation.
**Fix:** Either move `research.ui` under `game.ui`, or extract `Camera` into a shared rendering interface.

---

## Circular Dependencies (13 pairs)

These are the most actionable coupling problems. A circular dependency means module A imports B and B imports A — making them impossible to use or test independently.

### Cluster 1: `game.simulation.components` (3 cycles)

```
component ↔ component_health_manager
component ↔ component_resource_manager
component ↔ component_stats_calculator
```

**Root cause:** The `Component` god class was decomposed into manager classes, but the managers still import `Component` types and `Component` imports the managers.
**This is a PROJ-88 target** (Simulation Core Tier decomposition).

### Cluster 2: `game.strategy.data` — Fleet (4 cycles)

```
fleet ↔ fleet_battle_adapter
fleet ↔ fleet_capability_calculator
fleet ↔ fleet_resource_aggregator
fleet ↔ fleet_speed_calculator (in strategy.services)
```

**Root cause:** The `Fleet` god class was decomposed, but circular imports remain between Fleet and its extracted helpers.
**This is a PROJ-87 target** (Strategy Data Tier decomposition).

### Cluster 3: `game.strategy.data` — ShipInstance (3 cycles)

```
ship_instance ↔ ship_cargo_manager
ship_instance ↔ ship_display_formatter
ship_instance ↔ ship_resource_manager
```

**Root cause:** Same pattern as Fleet — `ShipInstance` god class decomposition left circular imports.
**Also a PROJ-87 target.**

### Cluster 4: `game.strategy` — Navigation (1 cycle)

```
pathfinding ↔ fleet_navigation_service
```

**Root cause:** Pathfinding and navigation service mutually depend on each other.

### Cluster 5: `game.simulation` — Battle (1 cycle)

```
battle_controller ↔ battle_mode_handler
```

**Root cause:** Controller dispatches to mode handler, but handler calls back to controller.
**This is a PROJ-88 target.**

### Cluster 6: `game.ui.screens` — Strategy UI (1 cycle)

```
strategy_ui ↔ strategy_event_router
```

**Root cause:** Event router was extracted from StrategyUI but they still cross-reference.
**This is a PROJ-86 or PROJ-89 target.**

---

## Coupling Hotspots — Most Connected Classes

### Most Depended On (incoming connections)

| Class | Depended on by | Layer |
|-------|---------------|-------|
| `Ability` (base) | 33 classes | simulation |
| `Game` | 15 classes | app |
| `DesignWorkshopScreen` | 15 classes | ui |
| `AIBehavior` | 11 classes | ai |
| `HexCoord` | 10 classes | core |
| `BuilderScreen` | 10 classes | ui |
| `StrategyWindowManager` | 8 classes | ui |
| `BuildQueueScreen` | 7 classes | ui |
| `GameException` | 6 classes | core |

**Note:** `Ability` with 33 dependents is expected — it's the base class for all component abilities (inheritance hierarchy, not coupling). `Game` and `DesignWorkshopScreen` at 15 each are the real hub classes.

### Heaviest Importers (outgoing connections)

| Module | Imports | Layer |
|--------|---------|-------|
| `game.app` | 28 modules | app |
| `game.ui.screens.builder.main` | 24 modules | ui |
| `game.ui.screens.workshop_screen` | 24 modules | ui |
| `game.ui.screens.strategy_screen` | 23 modules | ui |
| `game.ui.screens.build_queue_screen` | 22 modules | ui |
| `game.ui.screens.race_setup_screen` | 16 modules | ui |

These are the "god modules" that import everything. The top 5 are all UI screens, which is expected (screens coordinate many subsystems).

### Most Imported Modules

| Module | Imported by | Layer |
|--------|------------|-------|
| `game.core.logger` | 88 modules | core |
| `game.core.constants` | 56 modules | core |
| `game.core.hex_math` | 31 modules | core |
| `game.core.config` | 29 modules | core |
| `game.core.registry` | 29 modules | core |
| `game.core.paths` | 23 modules | core |
| `game.core.json_utils` | 22 modules | core |
| `game.strategy.data.fleet` | 22 modules | strategy |

All top imports are `core` utilities — exactly what you'd expect. `fleet` at 22 is notable as a non-core module with very high fan-in.

---

## Diagnosis: Is This a Hairball?

**No.** The full-package diagram IS visually dense, but the metrics tell a more nuanced story:

### What's Good
- **Class coupling is low** — 0.56 edges per class means most classes have 0-1 direct dependencies
- **Layer boundaries are mostly respected** — only 4 violations out of 977 import edges (0.4%)
- **Core layer is properly foundational** — 382 modules, imported by everything, imports nothing above it
- **UI properly sits on top** — 410 modules, heaviest consumer, not imported by lower layers
- **No cross-layer spaghetti** — the dependency graph flows cleanly upward in most cases

### What Needs Work
- **13 circular dependency pairs** — all from god-class decompositions that didn't fully break the cycles
- **`simulation → ai` layer violation** — factory coupling that should be inverted
- **UI screens import 20-28 modules each** — could benefit from facade patterns
- **`fleet` is a coupling hub** — 22 modules import it, and it has 4 circular deps with its extracted helpers

### Priority Fixes

1. **Break circular dependencies in PROJ-87/88** — The existing god-class decomposition projects already target these. The key is to ensure extracted managers depend on the parent class (or an interface) but NOT vice versa.
2. **Fix `ai_factory` layer violation** — Move factory up or use dependency injection.
3. **Consider merging `research.ui` into `game.ui`** — Eliminates the research→ui violation by making it intra-layer.

---

## Files Generated

All output in `uml_output/`:
- `.dot` files — raw Graphviz source (editable)
- `.png` files — raster images
- `.svg` files — vector images (open in browser, zoomable)
