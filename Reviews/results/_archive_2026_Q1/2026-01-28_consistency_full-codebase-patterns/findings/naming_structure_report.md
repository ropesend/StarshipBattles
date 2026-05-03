# Naming and File Organization Pattern Analysis

**Agent:** Naming & Structure Analyst
**Date:** 2026-01-28
**Scope:** game/, ui/ directories (excluding tests)

---

## Summary
- Total pattern variants found: 18
- Critical inconsistencies: 0
- Major inconsistencies: 1
- Minor inconsistencies: 3
- Dominant pattern: Strong suffix conventions, snake_case methods

---

## Class Naming Patterns

### Class Suffixes

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Service (business logic) | BattleService, ResearchService | 40% | Dominant for logic |
| Manager (resource management) | AssetManager, ResourceManager | 27% | Singletons, collections |
| Panel (UI components) | BattlePanel, ShipStatsPanel | 20% | UI regions |
| Controller (orchestration) | AIController, InteractionController | 13% | Input handling |

### Other Class Patterns

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Engine suffix | BattleEngine, ShipCombatEngine | 2 classes | Core processors |
| Scene suffix | BattleScene, TestLabScene | 3 classes | Screen-level |
| Mixin suffix | ShipCombatMixin | 1 class | Compatibility |
| No suffix (data) | ComponentRef, ShipPanel | ~10% | Data holders |

---

## Method Naming Patterns

### Method Prefixes

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| `get_` (queries) | get_position(), get_velocity() | 60% | Read operations |
| `_` (private) | _calculate_firing_solution() | 70% | Internal methods |
| `is_` (boolean) | is_alive(), is_battle_over() | 40% | State checks |
| `set_` (mutations) | set_throttle(), set_value() | 35% | Property changes |
| `on_` (events) | on_selection_changed() | 15% | Event handlers |

### Verb Patterns (no prefix)

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| create_, add_, remove_ | create_battle(), add_ship() | 20% | CRUD operations |
| update(), reset() | Various managers | 15% | State changes |
| draw(), handle_ | UI components | 10% | UI operations |

---

## File Organization Patterns

### Module Structure

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Single class per file | BattleService.py, AssetManager.py | 80% | Standard |
| Related classes grouped | battle_panels.py (4 classes) | 15% | UI components |
| Many classes per file | test_lab_scene.py (10-40+) | 5% | Problematic |

### Directory Structure

```
game/
├── core/           # Utilities, config (good)
├── engine/         # Physics, spatial (good)
├── simulation/     # Battle logic (good)
│   ├── services/   # Business logic
│   ├── systems/    # Manager systems
│   └── entities/   # Domain objects
├── ai/             # AI behaviors (good)
├── strategy/       # Strategy layer (good)
└── research/       # Research system (good)

ui/ (root)          # INCONSISTENT - should be in game/ui/
├── builder/        # Ship builder
└── test_lab_scene.py
```

---

## Import Organization Patterns

### Import Ordering

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| stdlib → 3rd party → local | BattleService.py, most game/ | 90% | Standard |
| Mixed ordering | detail_panel.py (json after pygame) | 10% | Inconsistent |

### Import Styles

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Absolute `from game.*` | game/ directory | 85% | Dominant |
| Mixed `from ui.builder.*` | ui/ directory | 15% | Inconsistent |

---

## Key Inconsistencies

### NS-01: Dual UI Directory Structure
**Severity:** Major
**ID:** NS-01
**Location:** `game/ui/` and `ui/` (root level)
**Issue:** UI code split between two locations
**Impact:** Confusing organization, inconsistent import paths
**Recommendation:** Consolidate all UI code to `game/ui/`
**Effort:** Complex

### NS-02: Multi-Class Files
**Severity:** Minor
**ID:** NS-02
**Location:** `ui/test_lab_scene.py`, `ui/builder/` files
**Issue:** Some files contain 10-40+ classes
**Impact:** Harder to navigate, potential circular imports
**Recommendation:** Extract to single-class-per-file pattern
**Effort:** Medium

### NS-03: Mixed Import Paths
**Severity:** Minor
**ID:** NS-03
**Location:** `ui/builder/detail_panel.py`, others
**Issue:** Mix of absolute (`game.*`) and root-relative (`ui.*`) imports
**Impact:** Inconsistent import style
**Recommendation:** Standardize on absolute imports
**Effort:** Simple

### NS-04: Import Order Inconsistency
**Severity:** Info
**ID:** NS-04
**Location:** ~10 files in ui/builder/
**Issue:** stdlib imports not always first
**Impact:** Minor readability issue
**Recommendation:** Use isort or similar tool
**Effort:** Simple

---

## Recommended Standard

### Class Naming
```python
class ComponentManager:    # For resource/collection management
class BattleService:       # For business logic operations
class ShipStatsPanel:      # For UI components
class AIController:        # For input/orchestration
```

### Method Naming
```python
def get_component(self) -> Component:  # getter
def is_active(self) -> bool:           # boolean check
def _calculate_internal(self):         # private method
def on_button_clicked(self):           # event handler
def create_ship(self, config):         # factory method
```

### Import Organization
```python
# Standard library
import os
import json
from dataclasses import dataclass
from typing import Optional, List

# Third-party
import pygame
import pygame_gui

# Local (absolute)
from game.core.logger import log_error
from game.simulation.entities import Ship
```

---

## Top 5 Priority Issues

1. **NS-01:** Consider consolidating `ui/` into `game/ui/` (Major)
2. **NS-03:** Standardize import paths in ui/builder/ (~15 files)
3. **NS-04:** Apply import sorting to inconsistent files (~10 files)
4. **NS-02:** Consider splitting large multi-class files
5. Document naming conventions in coding standards
