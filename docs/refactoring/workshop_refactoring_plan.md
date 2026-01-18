# Design Workshop Refactoring Plan

**Last Updated**: 2026-01-17
**Status**: Planning Complete - Ready for Implementation

## Overview

This plan refactors the "Ship Builder" into a flexible "Design Workshop" that can operate in two modes:
1. **Standalone Mode**: For development and testing, with tech preset selection
2. **Integrated Mode**: Embedded in strategy layer with context-aware save/load and simplified UI

The implementation is divided into 3 phases to enable gradual testing and validation.

## Test-Driven Development Approach

**CRITICAL**: This refactoring MUST be test-driven at every step:

1. **Before ANY code changes**: Run the full test suite to establish baseline
2. **After EACH rename batch**: Run tests to ensure no regressions
3. **For EACH new feature**: Write tests BEFORE implementation
4. **Multiple agents**: Use persistent naming document (see below) for coordination

### Test Execution Commands

```bash
# Full test suite
python -m pytest tests/

# Builder-specific tests only
python -m pytest tests/unit/builder/ -v

# Service layer tests
python -m pytest tests/unit/services/test_ship_builder_service.py -v

# Strategy integration tests
python -m pytest tests/strategy/ -v

# Quick smoke test (runs in ~30 seconds)
python -m pytest tests/unit/builder/test_builder_logic.py tests/unit/services/test_ship_builder_service.py -v
```

### Testing Checkpoints

Each phase has explicit test checkpoints:
- **Phase 1**: After each rename batch, run builder tests
- **Phase 2**: Write new tests for WorkshopContext before implementation
- **Phase 3**: Write DesignLibrary tests before implementation

---

## Naming Convention Reference

**Purpose**: This document ensures all agents working on this refactor use consistent naming.

### Current Names → New Names

| Category | Old Name | New Name | Status | Notes |
|----------|----------|----------|--------|-------|
| **Main Scene Class** | `BuilderSceneGUI` | `DesignWorkshopGUI` | Planned | Main UI class |
| **ViewModel** | `BuilderViewModel` | `WorkshopViewModel` | Planned | State management |
| **Event Router** | `BuilderEventRouter` | `WorkshopEventRouter` | Planned | Event handling |
| **Data Loader** | `BuilderDataLoader` | `WorkshopDataLoader` | Planned | Data loading |
| **Service** | `ShipBuilderService` | `VehicleDesignService` | Planned | Business logic |
| **Service Result** | `ShipBuilderResult` | `DesignResult` | Planned | Return type |
| **Persistence** | `ShipIO` | Keep as-is | No change | Legacy support |
| **File/Folder Names** | `builder_*.py` | `workshop_*.py` | Planned | Incremental |
| **UI Folder** | `ui/builder/` | `ui/workshop/` | Optional | Consider in Phase 1 |
| **Test Files** | `test_builder_*.py` | `test_workshop_*.py` | Planned | After impl rename |
| **Menu Text** | "Ship Builder" | "Design Workshop" | Phase 1 | User-facing |
| **Window Titles** | "Ship Builder" | "Design Workshop" | Phase 1 | User-facing |
| **State Constant** | `BUILDER` | `WORKSHOP` | Phase 1 | in app.py |
| **App Methods** | `start_builder()` | `start_workshop_standalone()` | Phase 2 | |
| **App Methods** | `on_builder_return()` | `on_workshop_return()` | Phase 2 | |
| **Comments/Docstrings** | "builder" / "ship builder" | "workshop" / "design workshop" | All phases | Search & replace |

### Import Statement Changes

```python
# OLD
from game.ui.screens.builder_screen import BuilderSceneGUI
from game.ui.screens.builder_viewmodel import BuilderViewModel
from game.simulation.services.ship_builder_service import ShipBuilderService

# NEW
from game.ui.screens.workshop_screen import DesignWorkshopGUI
from game.ui.screens.workshop_viewmodel import WorkshopViewModel
from game.simulation.services.vehicle_design_service import VehicleDesignService
```

### Testing Reference

Map old test names to new test names:

```python
# OLD → NEW
tests/unit/builder/test_builder_logic.py → tests/unit/workshop/test_workshop_logic.py
tests/unit/builder/test_builder_viewmodel.py → tests/unit/workshop/test_workshop_viewmodel.py
tests/unit/services/test_ship_builder_service.py → tests/unit/services/test_vehicle_design_service.py
```

---

## Phase 1: Rename to "Design Workshop" (Test-Driven)

**Goal**: Rename all references from "Ship Builder" to "Design Workshop" throughout the codebase, using TDD approach to ensure zero regressions.

### Phase 1 Overview

Rename will be done in **6 incremental batches**, with tests run after each batch:

1. **Batch 1a**: Establish test baseline
2. **Batch 1b**: User-facing text only (menu, window titles)
3. **Batch 1c**: Service layer (ShipBuilderService → VehicleDesignService)
4. **Batch 1d**: ViewModel and data loader
5. **Batch 1e**: Main screen class and event router
6. **Batch 1f**: File renames and import cleanup

---

### Batch 1a: Establish Test Baseline

**Action**: Run all tests to establish baseline before ANY changes.

```bash
# Run full test suite and save output
python -m pytest tests/ -v > test_baseline.txt 2>&1

# Run builder tests specifically
python -m pytest tests/unit/builder/ -v

# Run service tests
python -m pytest tests/unit/services/test_ship_builder_service.py -v

# Record test counts
echo "Builder tests: $(python -m pytest tests/unit/builder/ --collect-only -q | grep 'test session starts' -A 1)"
echo "Service tests: $(python -m pytest tests/unit/services/test_ship_builder_service.py --collect-only -q | wc -l)"
```

**Expected**: All tests pass (or document any existing failures to ignore).

**Checkpoint**: Document baseline test results before proceeding.

**Status**: [ ] Not Started

---

### Batch 1b: User-Facing Text Only

**Changes**: Update only user-visible strings (no code structure changes).

#### Files to Modify
1. [game/app.py](game/app.py:119)
   - Line 119: `"Ship Builder"` → `"Design Workshop"`

2. [game/ui/screens/builder_screen.py](game/ui/screens/builder_screen.py)
   - Search for any window titles containing "Ship Builder"
   - Update to "Design Workshop"

3. [game/app.py](game/app.py:127-141)
   - Update docstrings: `"""Enter ship builder."""` → `"""Enter design workshop."""`

#### Test Checkpoint 1b

```bash
# Run builder tests
python -m pytest tests/unit/builder/ -v

# Verify no regressions
# Expected: Same number of tests passing as baseline
```

**Pass Criteria**: All tests that passed in baseline still pass.

**Status**: [ ] Not Started

---

### Batch 1c: Service Layer Refactor

**Changes**: Rename `ShipBuilderService` → `VehicleDesignService` and update tests.

#### Step 1: Write New Tests First (TDD)

Create [tests/unit/services/test_vehicle_design_service.py](tests/unit/services/test_vehicle_design_service.py):

```python
"""
Tests for VehicleDesignService (renamed from ShipBuilderService).
This is a COPY of test_ship_builder_service.py with updated imports.
"""
import pytest
from game.simulation.services.vehicle_design_service import VehicleDesignService, DesignResult
from game.simulation.components.component import LayerType


@pytest.fixture
def service():
    """Create a VehicleDesignService instance with loaded data."""
    return VehicleDesignService()


class TestVehicleDesignServiceCreateShip:
    """Tests for VehicleDesignService.create_ship()."""

    def test_create_ship_returns_valid_ship(self, service):
        """create_ship() returns a Ship instance with expected properties."""
        result = service.create_ship(
            name="Test Ship",
            ship_class="Escort",
            theme_id="Federation"
        )

        assert result.success is True
        assert result.ship is not None
        assert result.ship.name == "Test Ship"
        # ... rest of tests from test_ship_builder_service.py
```

#### Step 2: Create New Service File

Create [game/simulation/services/vehicle_design_service.py](game/simulation/services/vehicle_design_service.py):

```python
"""
Vehicle Design Service (renamed from ShipBuilderService).

Provides an abstraction layer between UI and Ship domain objects,
handling vehicle creation, component management, and design validation.
"""
from dataclasses import dataclass
from typing import Optional, List
# ... imports from ship_builder_service.py


@dataclass
class DesignResult:
    """Result of a design operation (renamed from ShipBuilderResult)."""
    success: bool
    ship: Optional['Ship'] = None
    errors: List[str] = None
    warnings: List[str] = None


class VehicleDesignService:
    """Service for vehicle design operations (renamed from ShipBuilderService)."""

    def __init__(self):
        # ... same implementation as ShipBuilderService
        pass

    def create_ship(self, name: str, ship_class: str, theme_id: str = "Federation") -> DesignResult:
        # ... copy implementation from ShipBuilderService
        pass

    # ... all other methods from ShipBuilderService
```

#### Step 3: Run New Tests

```bash
# Run new service tests
python -m pytest tests/unit/services/test_vehicle_design_service.py -v

# Expected: All tests pass (same count as test_ship_builder_service.py)
```

#### Step 4: Add Backward Compatibility Aliases

Update [game/simulation/services/ship_builder_service.py](game/simulation/services/ship_builder_service.py):

```python
"""
DEPRECATED: Use vehicle_design_service.py instead.
This file provides backward compatibility aliases.
"""
from game.simulation.services.vehicle_design_service import (
    VehicleDesignService as ShipBuilderService,
    DesignResult as ShipBuilderResult
)

# Explicit re-exports for clarity
__all__ = ['ShipBuilderService', 'ShipBuilderResult']
```

#### Test Checkpoint 1c

```bash
# Run BOTH old and new tests
python -m pytest tests/unit/services/test_ship_builder_service.py -v
python -m pytest tests/unit/services/test_vehicle_design_service.py -v

# Run all builder tests (should still pass with compatibility layer)
python -m pytest tests/unit/builder/ -v
```

**Pass Criteria**:
- New tests pass
- Old tests still pass (using compatibility aliases)
- Builder tests still pass (still using old imports)

**Status**: [ ] Not Started

---

### Batch 1d: ViewModel and Data Loader

**Changes**: Rename ViewModel and DataLoader classes with TDD.

#### Step 1: Write Tests First

Create [tests/unit/workshop/test_workshop_viewmodel.py](tests/unit/workshop/test_workshop_viewmodel.py):

```python
"""Tests for WorkshopViewModel (renamed from BuilderViewModel)."""
import pytest
from game.ui.screens.workshop_viewmodel import WorkshopViewModel
from game.ui.screens.builder_utils import BuilderEvents
from game.ui.builder.event_bus import EventBus


class TestWorkshopViewModel:
    """Tests for WorkshopViewModel."""

    def test_create_default_ship(self):
        """ViewModel can create a default ship."""
        event_bus = EventBus()
        vm = WorkshopViewModel(event_bus, 1920, 1080)
        vm.create_default_ship()

        assert vm.ship is not None
        assert vm.ship.ship_class == "Escort"  # Default class

    # ... copy all tests from test_builder_viewmodel.py
```

Create [tests/unit/workshop/test_workshop_data_loader.py](tests/unit/workshop/test_workshop_data_loader.py):

```python
"""Tests for WorkshopDataLoader (renamed from BuilderDataLoader)."""
# Copy tests from test_builder_data_loader.py with updated imports
```

#### Step 2: Create New Implementation Files

Copy and rename:
- `builder_viewmodel.py` → `workshop_viewmodel.py`
- `builder_data_loader.py` → `workshop_data_loader.py`

Update class names:
- `BuilderViewModel` → `WorkshopViewModel`
- `BuilderDataLoader` → `WorkshopDataLoader`

#### Step 3: Add Backward Compatibility

Keep old files with aliases:

```python
# builder_viewmodel.py
"""DEPRECATED: Use workshop_viewmodel.py"""
from game.ui.screens.workshop_viewmodel import WorkshopViewModel as BuilderViewModel
```

#### Test Checkpoint 1d

```bash
# Run new tests
python -m pytest tests/unit/workshop/ -v

# Run old tests (should still work via compatibility)
python -m pytest tests/unit/builder/test_builder_viewmodel.py -v
python -m pytest tests/unit/builder/test_builder_data_loader.py -v

# Run all builder tests
python -m pytest tests/unit/builder/ -v
```

**Pass Criteria**: All old and new tests pass.

**Status**: [ ] Not Started

---

### Batch 1e: Main Screen Class and Event Router

**Changes**: Rename main GUI class and event router.

#### Implementation Order

1. Copy `builder_screen.py` → `workshop_screen.py`
2. Rename `BuilderSceneGUI` → `DesignWorkshopGUI`
3. Update internal references to use Workshop* classes
4. Copy `builder_event_router.py` → `workshop_event_router.py`
5. Rename `BuilderEventRouter` → `WorkshopEventRouter`
6. Add backward compatibility aliases in old files

#### Test Checkpoint 1e

```bash
# Run smoke test (interactive test that launches UI)
python -c "from game.ui.screens.workshop_screen import DesignWorkshopGUI; print('Import successful')"

# Run builder tests (via compatibility layer)
python -m pytest tests/unit/builder/ -v

# Manual test: Launch game and verify workshop opens
python game/app.py
# Click "Design Workshop" button
# Verify UI loads correctly
```

**Pass Criteria**:
- All tests pass
- Workshop launches successfully from main menu
- All functionality works identically

**Status**: [ ] Not Started

---

### Batch 1f: File Renames and Import Cleanup

**Changes**: Migrate all code to use new imports, deprecate old files.

#### Step 1: Update All Imports

Update imports in all files referencing builder classes:

```python
# OLD
from game.ui.screens.builder_screen import BuilderSceneGUI
from game.ui.screens.builder_viewmodel import BuilderViewModel

# NEW
from game.ui.screens.workshop_screen import DesignWorkshopGUI
from game.ui.screens.workshop_viewmodel import WorkshopViewModel
```

#### Step 2: Rename Test Files

```bash
# Create new test directory
mkdir tests/unit/workshop

# Copy and update test files
# test_builder_*.py → test_workshop_*.py
# Update all imports to use workshop classes
```

#### Step 3: Update app.py

```python
# game/app.py
from game.ui.screens.workshop_screen import DesignWorkshopGUI

# Rename state constant
WORKSHOP = 'workshop'  # was BUILDER

# Rename instance variable
self.workshop_scene = DesignWorkshopGUI(WIDTH, HEIGHT, self.on_workshop_return)

# Rename methods (prepare for Phase 2)
def start_workshop_standalone(self):
    """Enter design workshop in standalone mode."""
    self.state = WORKSHOP
    self.workshop_scene = DesignWorkshopGUI(WIDTH, HEIGHT, self.on_workshop_return)
```

#### Test Checkpoint 1f (FINAL)

```bash
# Run ALL tests with new structure
python -m pytest tests/ -v

# Run workshop tests specifically
python -m pytest tests/unit/workshop/ -v

# Run strategy tests (verify integration still works)
python -m pytest tests/strategy/ -v

# Manual smoke test
python game/app.py
```

**Pass Criteria**:
- All automated tests pass
- Manual testing confirms workshop works identically
- No references to "Builder" in user-facing text
- Old imports still work via compatibility layer (for safety)

**Status**: [ ] Not Started

---

### Phase 1 Summary

**Files Created**:
- `game/simulation/services/vehicle_design_service.py`
- `game/ui/screens/workshop_screen.py`
- `game/ui/screens/workshop_viewmodel.py`
- `game/ui/screens/workshop_data_loader.py`
- `game/ui/screens/workshop_event_router.py`
- `tests/unit/workshop/test_workshop_*.py`

**Files Modified** (backward compat aliases):
- `game/simulation/services/ship_builder_service.py`
- `game/ui/screens/builder_screen.py`
- `game/ui/screens/builder_viewmodel.py`
- `game/ui/screens/builder_data_loader.py`

**Files Eventually Deprecated** (Phase 2):
- All `builder_*.py` files (after Phase 2 complete)
- All `test_builder_*.py` files (after migration)

**Phase 1 Completion Status**: [ ] Not Started

---

## Phase 2: Dual Launch Modes (Test-Driven)

**Goal**: Implement two launch modes with different initialization contexts and button visibility, using TDD throughout.

### Phase 2 TDD Workflow

1. **Write tests for WorkshopContext** → Implement WorkshopContext
2. **Write tests for Tech Preset system** → Implement Tech Preset loader
3. **Write tests for button filtering** → Implement dynamic button generation
4. **Write tests for launch modes** → Update app.py integration
5. **Integration tests** → Verify end-to-end workflow

---

### A. Create Launch Context System (TDD)

#### Step 1: Write Tests First

Create [tests/unit/workshop/test_workshop_context.py](tests/unit/workshop/test_workshop_context.py):

```python
"""Tests for WorkshopContext launch configuration."""
import pytest
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode


class TestWorkshopContextStandalone:
    """Tests for standalone mode context."""

    def test_standalone_context_creation(self):
        """Can create standalone context with tech preset."""
        context = WorkshopContext.standalone(tech_preset_name="early_game")

        assert context.mode == WorkshopMode.STANDALONE
        assert context.tech_preset_name == "early_game"
        assert context.empire_id is None
        assert context.savegame_path is None

    def test_standalone_default_preset(self):
        """Standalone context defaults to 'default' preset."""
        context = WorkshopContext.standalone()

        assert context.tech_preset_name == "default"


class TestWorkshopContextIntegrated:
    """Tests for integrated mode context."""

    def test_integrated_context_creation(self):
        """Can create integrated context with empire and savegame."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/savegame1",
            available_tech_ids=["laser_cannon", "railgun"]
        )

        assert context.mode == WorkshopMode.INTEGRATED
        assert context.empire_id == 1
        assert context.savegame_path == "saves/savegame1"
        assert context.available_tech_ids == ["laser_cannon", "railgun"]
        assert context.tech_preset_name is None

    def test_integrated_context_default_tech(self):
        """Integrated context defaults to empty tech list."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/savegame1"
        )

        assert context.available_tech_ids == []


class TestWorkshopContextCallbacks:
    """Tests for callback and return state handling."""

    def test_context_stores_callbacks(self):
        """Context can store on_return callback."""
        def mock_callback():
            pass

        context = WorkshopContext.standalone()
        context.on_return = mock_callback
        context.return_state = "MENU"

        assert context.on_return is mock_callback
        assert context.return_state == "MENU"
```

#### Step 2: Implement WorkshopContext

Create [game/ui/screens/workshop_context.py](game/ui/screens/workshop_context.py)

**Run test to verify it fails** (TDD red phase):
```bash
python -m pytest tests/unit/workshop/test_workshop_context.py -v
# Expected: ImportError (workshop_context.py doesn't exist yet)
```

Now implement:

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Callable

class WorkshopMode(Enum):
    STANDALONE = "standalone"
    INTEGRATED = "integrated"

@dataclass
class WorkshopContext:
    """Configuration for how the workshop is launched"""
    mode: WorkshopMode

    # Tech system
    tech_preset_name: Optional[str] = None  # For standalone mode
    available_tech_ids: Optional[List[str]] = None  # For integrated mode

    # Strategy integration
    empire_id: Optional[int] = None  # Current empire in integrated mode
    savegame_path: Optional[str] = None  # Path to save designs in integrated

    # Return callback
    on_return: Optional[Callable] = None
    return_state: Optional[str] = None  # For app.py state management

    @classmethod
    def standalone(cls, tech_preset_name="default"):
        """Create standalone workshop context"""
        return cls(
            mode=WorkshopMode.STANDALONE,
            tech_preset_name=tech_preset_name
        )

    @classmethod
    def integrated(cls, empire_id, savegame_path, available_tech_ids=None):
        """Create integrated workshop context"""
        return cls(
            mode=WorkshopMode.INTEGRATED,
            empire_id=empire_id,
            savegame_path=savegame_path,
            available_tech_ids=available_tech_ids or []
        )
```

#### Test Checkpoint 2a

```bash
# Run WorkshopContext tests (should pass now - TDD green phase)
python -m pytest tests/unit/workshop/test_workshop_context.py -v

# Expected: All tests pass
```

**Status**: [ ] Not Started

---

### B. Tech Preset System (TDD)

#### Step 1: Create Tech Preset Data Files

Create `data/tech_presets/default.json`:

```json
{
    "name": "Default (All Tech)",
    "description": "All components available - for testing",
    "unlocked_components": ["*"],
    "unlocked_modifiers": ["*"]
}
```

Create `data/tech_presets/early_game.json`:

```json
{
    "name": "Early Game",
    "description": "Basic components only",
    "unlocked_components": [
        "hull_escort", "hull_frigate",
        "laser_cannon", "railgun",
        "basic_engine", "bridge", "crew_quarters"
    ],
    "unlocked_modifiers": [
        "simple_size_mount", "basic_armor"
    ]
}
```

#### Step 2: Write Tests First

Create [tests/unit/workshop/test_tech_preset_loader.py](tests/unit/workshop/test_tech_preset_loader.py):

```python
"""Tests for TechPresetLoader."""
import pytest
from game.simulation.systems.tech_preset_loader import TechPresetLoader


class TestTechPresetLoader:
    """Tests for loading tech presets."""

    def test_list_presets(self):
        """Can list available preset names."""
        presets = TechPresetLoader.list_presets()

        assert isinstance(presets, list)
        assert "default" in presets
        assert "early_game" in presets

    def test_load_preset(self):
        """Can load preset by name."""
        preset = TechPresetLoader.load_preset("default")

        assert preset['name'] == "Default (All Tech)"
        assert preset['unlocked_components'] == ["*"]

    def test_get_available_components_wildcard(self):
        """Wildcard preset returns all components."""
        components = TechPresetLoader.get_available_components("default")

        # Should return all component IDs from registry
        assert len(components) > 0
        assert isinstance(components, list)

    def test_get_available_components_filtered(self):
        """Filtered preset returns only specified components."""
        components = TechPresetLoader.get_available_components("early_game")

        assert "laser_cannon" in components
        assert "railgun" in components
        # Advanced weapons should not be included
        # (depends on actual component data)

    def test_load_nonexistent_preset(self):
        """Loading nonexistent preset raises error."""
        with pytest.raises(FileNotFoundError):
            TechPresetLoader.load_preset("nonexistent")
```

**Run test to verify it fails**:
```bash
python -m pytest tests/unit/workshop/test_tech_preset_loader.py -v
# Expected: ImportError or test failures
```

#### Step 3: Implement TechPresetLoader

Create [game/simulation/systems/tech_preset_loader.py](game/simulation/systems/tech_preset_loader.py):

```python
"""Tech preset loader for standalone workshop mode."""
import os
import glob
from typing import List, Dict
from game.core.json_utils import load_json_required
from game.core.registry import get_all_components


class TechPresetLoader:
    """Loads and manages tech presets for standalone mode."""

    PRESET_DIR = "data/tech_presets"

    @staticmethod
    def list_presets() -> List[str]:
        """List all available preset names."""
        presets = []
        for filepath in glob.glob(f"{TechPresetLoader.PRESET_DIR}/*.json"):
            preset_name = os.path.splitext(os.path.basename(filepath))[0]
            presets.append(preset_name)
        return sorted(presets)

    @staticmethod
    def load_preset(preset_name: str) -> Dict:
        """Load tech preset from data/tech_presets/{name}.json."""
        filepath = os.path.join(TechPresetLoader.PRESET_DIR, f"{preset_name}.json")
        return load_json_required(filepath)

    @staticmethod
    def get_available_components(preset_name: str) -> List[str]:
        """Get component IDs available in this preset."""
        preset = TechPresetLoader.load_preset(preset_name)
        unlocked = preset.get('unlocked_components', [])

        # Wildcard means all components
        if "*" in unlocked:
            all_components = get_all_components()
            return [c.id for c in all_components]

        # Otherwise return filtered list
        return unlocked
```

#### Test Checkpoint 2b

```bash
# Run tech preset tests
python -m pytest tests/unit/workshop/test_tech_preset_loader.py -v

# Expected: All tests pass
```

**Status**: [ ] Not Started

---

### C. Dynamic Button Generation (TDD)

#### Step 1: Write Tests First

Create [tests/unit/workshop/test_workshop_buttons.py](tests/unit/workshop/test_workshop_buttons.py):

```python
"""Tests for dynamic button generation based on workshop mode."""
import pytest
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode
from game.ui.screens.workshop_screen import DesignWorkshopGUI


class TestWorkshopButtons:
    """Tests for button visibility based on mode."""

    def test_standalone_buttons(self):
        """Standalone mode includes debug buttons."""
        context = WorkshopContext.standalone()
        # Mock GUI initialization (may require pygame setup)
        gui = DesignWorkshopGUI(1920, 1080, context)

        button_names = [btn_id for btn_id, _, _ in gui._get_button_definitions()]

        # Standalone-only buttons
        assert 'hull_toggle_btn' in button_names
        assert 'std_data_btn' in button_names
        assert 'test_data_btn' in button_names
        assert 'select_data_btn' in button_names
        assert 'verbose_btn' in button_names

        # Common buttons
        assert 'save_btn' in button_names
        assert 'load_btn' in button_names

    def test_integrated_buttons(self):
        """Integrated mode excludes debug buttons."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/test"
        )
        gui = DesignWorkshopGUI(1920, 1080, context)

        button_names = [btn_id for btn_id, _, _ in gui._get_button_definitions()]

        # Debug buttons should NOT be present
        assert 'hull_toggle_btn' not in button_names
        assert 'std_data_btn' not in button_names
        assert 'test_data_btn' not in button_names
        assert 'select_data_btn' not in button_names
        assert 'verbose_btn' not in button_names

        # Integrated-only button
        assert 'obsolete_btn' in button_names

        # Common buttons still present
        assert 'save_btn' in button_names
        assert 'load_btn' in button_names
```

**Run test to verify it fails**:
```bash
python -m pytest tests/unit/workshop/test_workshop_buttons.py -v
# Expected: Test failures (buttons not filtered yet)
```

#### Step 2: Implement Dynamic Button Filtering

Update [game/ui/screens/workshop_screen.py](game/ui/screens/workshop_screen.py):

**Current** (line 220-231):
```python
button_defs = [
    ('clear_btn', "Clear Design", 110),
    ('save_btn', "Save", 80),
    ('load_btn', "Load", 80),
    ('arc_toggle_btn', "Show Firing Arcs", 140),
    ('hull_toggle_btn', "Show Hull", 100),
    ('target_btn', "Select Target", 110),
    ('std_data_btn', "Standard Data", 110),
    ('test_data_btn', "Test Data", 90),
    ('select_data_btn', "Select Data...", 110),
    ('verbose_btn', "Toggle Verbose", 120),
    ('start_btn', "Return", 100)
]
```

**New**:
```python
def _get_button_definitions(self):
    """Returns button definitions based on launch mode."""

    # Common buttons (always visible)
    buttons = [
        ('clear_btn', "Clear Design", 110),
        ('save_btn', "Save", 80),
        ('load_btn', "Load", 80),
        ('arc_toggle_btn', "Show Firing Arcs", 140),
        ('target_btn', "Select Target", 110),
        ('start_btn', "Return", 100)
    ]

    # Standalone-only buttons
    if self.context.mode == WorkshopMode.STANDALONE:
        buttons.extend([
            ('hull_toggle_btn', "Show Hull", 100),
            ('std_data_btn', "Standard Data", 110),
            ('test_data_btn', "Test Data", 90),
            ('select_data_btn', "Select Data...", 110),
            ('verbose_btn', "Toggle Verbose", 120),
        ])

    # Integrated-only buttons
    if self.context.mode == WorkshopMode.INTEGRATED:
        buttons.append(
            ('obsolete_btn', "Mark Obsolete", 130)
        )

    return buttons
```

Update button creation code to call `self._get_button_definitions()` instead of using hardcoded list.

#### Test Checkpoint 2c

```bash
# Run button tests
python -m pytest tests/unit/workshop/test_workshop_buttons.py -v

# Expected: All tests pass
```

**Status**: [ ] Not Started

---

### D. Update App.py Integration (TDD)

#### Step 1: Write Integration Tests

Create [tests/unit/test_workshop_launch.py](tests/unit/test_workshop_launch.py):

```python
"""Integration tests for workshop launch modes."""
import pytest
from unittest.mock import MagicMock, patch
from game.app import App
from game.ui.screens.workshop_context import WorkshopMode


class TestWorkshopLaunch:
    """Tests for launching workshop in different modes."""

    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_launch_standalone_from_menu(self, mock_caption, mock_display):
        """Can launch standalone workshop from main menu."""
        app = App()

        # Launch standalone
        app.start_workshop_standalone(tech_preset="default")

        assert app.state == 'workshop'  # WORKSHOP constant
        assert app.workshop_scene is not None
        assert app.workshop_scene.context.mode == WorkshopMode.STANDALONE
        assert app.workshop_scene.context.tech_preset_name == "default"

    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_launch_integrated_from_strategy(self, mock_caption, mock_display):
        """Can launch integrated workshop from strategy layer."""
        app = App()

        # Launch integrated
        app.start_workshop_integrated(
            empire_id=1,
            savegame_path="saves/test",
            return_to='strategy'
        )

        assert app.state == 'workshop'
        assert app.workshop_scene is not None
        assert app.workshop_scene.context.mode == WorkshopMode.INTEGRATED
        assert app.workshop_scene.context.empire_id == 1
        assert app.workshop_scene.context.savegame_path == "saves/test"

    def test_return_from_workshop_to_menu(self):
        """Workshop can return to main menu."""
        app = App()
        app.start_workshop_standalone()

        # Simulate return
        app.on_workshop_return()

        assert app.state == 'menu'

    def test_return_from_workshop_to_strategy(self):
        """Workshop can return to strategy layer."""
        app = App()
        app.start_workshop_integrated(
            empire_id=1,
            savegame_path="saves/test",
            return_to='strategy'
        )

        # Simulate return
        app.on_workshop_return()

        assert app.state == 'strategy'
```

**Run test to verify it fails**:
```bash
python -m pytest tests/unit/test_workshop_launch.py -v
# Expected: AttributeError (methods don't exist yet)
```

#### Step 2: Implement Launch Methods

Modify [game/app.py](game/app.py):

**Add imports**:
```python
from game.ui.screens.workshop_context import WorkshopContext
```

**Add/modify methods**:
```python
def start_workshop_standalone(self, tech_preset="default"):
    """Enter design workshop in standalone mode."""
    context = WorkshopContext.standalone(tech_preset_name=tech_preset)
    context.on_return = self.on_workshop_return
    context.return_state = MENU

    self.state = WORKSHOP
    self.workshop_scene = DesignWorkshopGUI(WIDTH, HEIGHT, context)

def start_workshop_integrated(self, empire_id, savegame_path, return_to=STRATEGY):
    """Enter design workshop from strategy layer."""
    # Future: get available_tech_ids from empire.unlocked_tech
    context = WorkshopContext.integrated(
        empire_id=empire_id,
        savegame_path=savegame_path,
        available_tech_ids=[]  # All available for now
    )
    context.on_return = self.on_workshop_return
    context.return_state = return_to

    self.state = WORKSHOP
    self.workshop_scene = DesignWorkshopGUI(WIDTH, HEIGHT, context)

def on_workshop_return(self):
    """Return from workshop to caller."""
    if self.workshop_scene.context.return_state == STRATEGY:
        self.state = STRATEGY
        if hasattr(self.strategy_scene, 'handle_resize'):
            self.strategy_scene.handle_resize(WIDTH, HEIGHT)
    else:
        self.state = MENU
```

**Update menu button**:
```python
Button(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 50, "Design Workshop",
       lambda: self.start_workshop_standalone())
```

**Update strategy scene integration**:
Modify [game/ui/screens/strategy_scene.py](game/ui/screens/strategy_scene.py:324):
```python
self.app.start_workshop_integrated(
    empire_id=self.game_session.player_empire_id,
    savegame_path=self.game_session.save_path
)
```

#### Test Checkpoint 2d

```bash
# Run launch tests
python -m pytest tests/unit/test_workshop_launch.py -v

# Run all workshop tests
python -m pytest tests/unit/workshop/ -v

# Manual integration test
python game/app.py
# Test: Launch from menu → standalone mode
# Test: Enter strategy → launch workshop → integrated mode
```

**Pass Criteria**:
- All automated tests pass
- Manual testing confirms both launch modes work
- Buttons filtered correctly per mode

**Status**: [ ] Not Started

---

### Phase 2 Summary

**Files Created**:
- `game/ui/screens/workshop_context.py`
- `game/simulation/systems/tech_preset_loader.py`
- `data/tech_presets/default.json`
- `data/tech_presets/early_game.json`
- `tests/unit/workshop/test_workshop_context.py`
- `tests/unit/workshop/test_tech_preset_loader.py`
- `tests/unit/workshop/test_workshop_buttons.py`
- `tests/unit/test_workshop_launch.py`

**Files Modified**:
- `game/ui/screens/workshop_screen.py` - Dynamic button generation
- `game/app.py` - Launch methods and state management
- `game/ui/screens/strategy_scene.py` - Integration hook

**Phase 2 Completion Status**: [ ] Not Started

---

## Phase 3: Integrated Save/Load System (Test-Driven)

**Goal**: Implement strategy-aware save/load dialogs and mark obsolete functionality with comprehensive test coverage.

### Phase 3 TDD Workflow

1. **Write tests for DesignMetadata** → Implement DesignMetadata
2. **Write tests for DesignLibrary** → Implement DesignLibrary
3. **Write tests for save/load logic** → Integrate with workshop
4. **Write tests for mark obsolete** → Implement obsolete tracking
5. **Integration tests** → Full end-to-end workflow

---

### A. Design Metadata System (TDD)

#### Step 1: Write Tests First

Create [tests/unit/strategy/test_design_metadata.py](tests/unit/strategy/test_design_metadata.py):

```python
"""Tests for DesignMetadata."""
import pytest
import tempfile
import os
from datetime import datetime
from game.strategy.data.design_metadata import DesignMetadata
from game.simulation.entities.ship import Ship


class TestDesignMetadata:
    """Tests for DesignMetadata data class."""

    def test_create_from_ship(self):
        """Can create metadata from Ship object."""
        ship = Ship("Test Frigate", 0, 0, (255,255,255), ship_class="Frigate")
        ship.theme_id = "Federation"

        metadata = DesignMetadata.from_ship(ship, "test_frigate")

        assert metadata.design_id == "test_frigate"
        assert metadata.name == "Test Frigate"
        assert metadata.ship_class == "Frigate"
        assert metadata.theme_id == "Federation"
        assert metadata.is_obsolete == False
        assert metadata.times_built == 0

    def test_load_from_design_file(self):
        """Can load metadata from ship JSON file."""
        # Create temp ship file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"name": "Test Ship", "ship_class": "Escort", "theme_id": "Klingons"}')
            temp_path = f.name

        try:
            metadata = DesignMetadata.from_design_file(temp_path, "test_ship")

            assert metadata.design_id == "test_ship"
            assert metadata.name == "Test Ship"
            assert metadata.ship_class == "Escort"
        finally:
            os.unlink(temp_path)

    def test_to_dict_serialization(self):
        """Can serialize metadata to dictionary."""
        metadata = DesignMetadata(
            design_id="frigate_mk1",
            name="Frigate Mk I",
            ship_class="Frigate",
            vehicle_type="Ship",
            mass=1000.0,
            combat_power=500.0,
            resource_cost={"Metals": 100},
            created_date=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat()
        )

        data = metadata.to_dict()

        assert data['design_id'] == "frigate_mk1"
        assert data['name'] == "Frigate Mk I"
        assert data['is_obsolete'] == False
```

**Run test to verify it fails**:
```bash
python -m pytest tests/unit/strategy/test_design_metadata.py -v
# Expected: ImportError (design_metadata.py doesn't exist)
```

#### Step 2: Implement DesignMetadata

Create [game/strategy/data/design_metadata.py](game/strategy/data/design_metadata.py):

```python
"""Design metadata for vehicle designs."""
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from datetime import datetime
from game.core.json_utils import load_json_required


@dataclass
class DesignMetadata:
    """Lightweight metadata about a ship design."""
    design_id: str
    name: str
    ship_class: str
    vehicle_type: str
    mass: float
    combat_power: float
    resource_cost: Dict[str, int]

    created_date: str
    last_modified: str
    is_obsolete: bool = False
    times_built: int = 0

    theme_id: str = ""
    sprite_preview: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to JSON."""
        return asdict(self)

    @classmethod
    def from_design_file(cls, filepath: str, design_id: str) -> 'DesignMetadata':
        """Load metadata from ship JSON file."""
        data = load_json_required(filepath)

        return cls(
            design_id=design_id,
            name=data.get('name', 'Unnamed'),
            ship_class=data.get('ship_class', 'Unknown'),
            vehicle_type=data.get('vehicle_type', 'Ship'),
            mass=data.get('mass', 0.0),
            combat_power=cls._calculate_combat_power(data),
            resource_cost=data.get('resource_cost', {}),
            created_date=data.get('created_date', datetime.now().isoformat()),
            last_modified=data.get('last_modified', datetime.now().isoformat()),
            is_obsolete=data.get('is_obsolete', False),
            times_built=data.get('times_built', 0),
            theme_id=data.get('theme_id', '')
        )

    @classmethod
    def from_ship(cls, ship, design_id: str) -> 'DesignMetadata':
        """Create metadata from Ship object."""
        return cls(
            design_id=design_id,
            name=ship.name,
            ship_class=ship.ship_class,
            vehicle_type=getattr(ship, 'vehicle_type', 'Ship'),
            mass=ship.mass,
            combat_power=cls._calculate_combat_power_from_ship(ship),
            resource_cost=getattr(ship, 'resource_cost', {}),
            created_date=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            theme_id=ship.theme_id
        )

    @staticmethod
    def _calculate_combat_power(data: dict) -> float:
        """Calculate combat power metric from design data."""
        # Simplified - count weapons and total HP
        # TODO: Implement proper combat power calculation
        return 0.0

    @staticmethod
    def _calculate_combat_power_from_ship(ship) -> float:
        """Calculate combat power from ship instance."""
        # TODO: Implement proper combat power calculation
        return 0.0
```

#### Test Checkpoint 3a

```bash
# Run metadata tests
python -m pytest tests/unit/strategy/test_design_metadata.py -v

# Expected: All tests pass
```

**Status**: [ ] Not Started

---

### B. Design Library System (TDD)

#### Step 1: Write Tests First

Create [tests/unit/strategy/test_design_library.py](tests/unit/strategy/test_design_library.py):

```python
"""Tests for DesignLibrary."""
import pytest
import tempfile
import os
from game.strategy.systems.design_library import DesignLibrary
from game.simulation.entities.ship import Ship


class TestDesignLibrary:
    """Tests for design library management."""

    @pytest.fixture
    def temp_library(self):
        """Create temporary design library."""
        with tempfile.TemporaryDirectory() as tmpdir:
            library = DesignLibrary(savegame_path=tmpdir, empire_id=1)
            yield library

    def test_library_creates_designs_folder(self, temp_library):
        """Library creates designs folder if it doesn't exist."""
        designs_path = os.path.join(temp_library.savegame_path, "designs")
        assert os.path.exists(designs_path)

    def test_save_new_design(self, temp_library):
        """Can save a new ship design."""
        ship = Ship("Test Ship", 0, 0, (255,255,255), ship_class="Escort")
        ship.theme_id = "Federation"

        success, msg = temp_library.save_design(ship, "test_ship", set())

        assert success is True
        assert "Saved design" in msg
        # Verify file exists
        design_file = os.path.join(temp_library.designs_folder, "test_ship.json")
        assert os.path.exists(design_file)

    def test_cannot_overwrite_built_design(self, temp_library):
        """Cannot overwrite design that has been built."""
        ship = Ship("Test Ship", 0, 0, (255,255,255), ship_class="Escort")

        # Save initially
        temp_library.save_design(ship, "test_ship", set())

        # Try to overwrite after it's been built
        built_designs = {"test_ship"}
        success, msg = temp_library.save_design(ship, "test_ship", built_designs)

        assert success is False
        assert "has been built" in msg

    def test_can_overwrite_unbuilt_design(self, temp_library):
        """Can overwrite design that hasn't been built."""
        ship = Ship("Test Ship", 0, 0, (255,255,255), ship_class="Escort")

        # Save initially
        temp_library.save_design(ship, "test_ship", set())

        # Overwrite (not in built set)
        ship.name = "Modified Ship"
        success, msg = temp_library.save_design(ship, "test_ship", set())

        assert success is True

    def test_load_design(self, temp_library):
        """Can load design by ID."""
        ship = Ship("Test Ship", 0, 0, (255,255,255), ship_class="Escort")
        temp_library.save_design(ship, "test_ship", set())

        loaded_ship, msg = temp_library.load_design("test_ship")

        assert loaded_ship is not None
        assert loaded_ship.name == "Test Ship"

    def test_scan_designs(self, temp_library):
        """Can scan and list all designs."""
        ship1 = Ship("Ship 1", 0, 0, (255,255,255), ship_class="Escort")
        ship2 = Ship("Ship 2", 0, 0, (255,255,255), ship_class="Frigate")

        temp_library.save_design(ship1, "ship_1", set())
        temp_library.save_design(ship2, "ship_2", set())

        designs = temp_library.scan_designs()

        assert len(designs) == 2
        assert any(d.design_id == "ship_1" for d in designs)
        assert any(d.design_id == "ship_2" for d in designs)

    def test_filter_by_class(self, temp_library):
        """Can filter designs by ship class."""
        escort = Ship("Escort", 0, 0, (255,255,255), ship_class="Escort")
        frigate = Ship("Frigate", 0, 0, (255,255,255), ship_class="Frigate")

        temp_library.save_design(escort, "escort", set())
        temp_library.save_design(frigate, "frigate", set())

        filtered = temp_library.filter_designs(ship_class="Escort")

        assert len(filtered) == 1
        assert filtered[0].ship_class == "Escort"

    def test_mark_obsolete(self, temp_library):
        """Can mark design as obsolete."""
        ship = Ship("Test Ship", 0, 0, (255,255,255), ship_class="Escort")
        temp_library.save_design(ship, "test_ship", set())

        temp_library.mark_obsolete("test_ship", True)

        designs = temp_library.scan_designs()
        assert designs[0].is_obsolete == True

    def test_filter_hides_obsolete_by_default(self, temp_library):
        """Obsolete designs hidden by default in filter."""
        ship = Ship("Test Ship", 0, 0, (255,255,255), ship_class="Escort")
        temp_library.save_design(ship, "test_ship", set())
        temp_library.mark_obsolete("test_ship", True)

        filtered = temp_library.filter_designs(show_obsolete=False)

        assert len(filtered) == 0
```

**Run test to verify it fails**:
```bash
python -m pytest tests/unit/strategy/test_design_library.py -v
# Expected: ImportError or test failures
```

#### Step 2: Implement DesignLibrary

Create [game/strategy/systems/design_library.py](game/strategy/systems/design_library.py):

```python
"""Design library management for strategy layer."""
import os
import glob
from typing import List, Optional, Set, Tuple
from game.core.json_utils import load_json_required, save_json
from game.strategy.data.design_metadata import DesignMetadata
from game.simulation.entities.ship import Ship


class DesignLibrary:
    """Manages ship designs for a specific empire/savegame."""

    def __init__(self, savegame_path: str, empire_id: int):
        self.savegame_path = savegame_path
        self.empire_id = empire_id
        self.designs_folder = os.path.join(savegame_path, "designs")

        # Ensure designs folder exists
        os.makedirs(self.designs_folder, exist_ok=True)

    def scan_designs(self) -> List[DesignMetadata]:
        """Scan designs folder and build metadata list."""
        designs = []
        for filepath in glob.glob(f"{self.designs_folder}/*.json"):
            design_id = os.path.splitext(os.path.basename(filepath))[0]
            metadata = DesignMetadata.from_design_file(filepath, design_id)
            designs.append(metadata)
        return designs

    def save_design(self, ship, design_name: str, built_designs: Set[str]) -> Tuple[bool, str]:
        """
        Save design to empire's designs folder.
        Returns (success, message).
        """
        design_id = self._sanitize_design_id(design_name)
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        # Check if design exists and was ever built
        if os.path.exists(filepath) and design_id in built_designs:
            return False, f"Cannot overwrite '{design_name}' - this design has been built in-game"

        # Save design data
        data = ship.to_dict()

        # Add metadata
        from datetime import datetime
        if not os.path.exists(filepath):
            data['created_date'] = datetime.now().isoformat()
        data['last_modified'] = datetime.now().isoformat()

        save_json(filepath, data, indent=4)

        return True, f"Saved design: {design_name}"

    def load_design(self, design_id: str) -> Tuple[Optional[Ship], str]:
        """Load design by ID."""
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if not os.path.exists(filepath):
            return None, f"Design '{design_id}' not found"

        data = load_json_required(filepath)
        ship = Ship.from_dict(data)
        return ship, f"Loaded design: {ship.name}"

    def mark_obsolete(self, design_id: str, is_obsolete: bool):
        """Toggle obsolete flag on design metadata."""
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if not os.path.exists(filepath):
            return

        data = load_json_required(filepath)
        data['is_obsolete'] = is_obsolete
        save_json(filepath, data, indent=4)

    def filter_designs(self,
                      ship_class: Optional[str] = None,
                      vehicle_type: Optional[str] = None,
                      show_obsolete: bool = False) -> List[DesignMetadata]:
        """Filter designs by criteria."""
        designs = self.scan_designs()

        if ship_class:
            designs = [d for d in designs if d.ship_class == ship_class]
        if vehicle_type:
            designs = [d for d in designs if d.vehicle_type == vehicle_type]
        if not show_obsolete:
            designs = [d for d in designs if not d.is_obsolete]

        return designs

    @staticmethod
    def _sanitize_design_id(name: str) -> str:
        """Convert design name to safe filename."""
        safe = "".join([c for c in name if c.isalnum() or c in (' ', '-', '_')]).strip()
        return safe if safe else "unnamed_design"
```

#### Test Checkpoint 3b

```bash
# Run design library tests
python -m pytest tests/unit/strategy/test_design_library.py -v

# Expected: All tests pass
```

**Status**: [ ] Not Started

---

### C. Integrate Save/Load with Workshop (TDD)

*(Continuing with similar TDD pattern for remaining Phase 3 work...)*

**Due to length constraints, the rest of Phase 3 follows the same pattern:**

1. Write tests for save/load dialog integration
2. Implement DesignSelectorWindow (similar to PlanetListWindow)
3. Update workshop event router to use DesignLibrary in integrated mode
4. Test checkpoints at each step

**Status**: [ ] Not Started

---

### D. Update Empire Tracking (TDD)

Update [game/strategy/data/empire.py](game/strategy/data/empire.py) to track designed/built ships:

```python
class Empire:
    def __init__(self, empire_id, name, color, theme_path=None):
        self.id = empire_id
        self.name = name
        self.color = color
        self.theme_path = theme_path

        self.colonies = []
        self.fleets = []

        # NEW: Design library tracking
        self.designed_ships = []  # List[DesignMetadata]
        self.built_ship_designs = set()  # Set of design_ids that were ever built
```

**Status**: [ ] Not Started

---

### Phase 3 Summary

**Files Created**:
- `game/strategy/data/design_metadata.py`
- `game/strategy/systems/design_library.py`
- `game/ui/screens/design_selector_window.py`
- `tests/unit/strategy/test_design_metadata.py`
- `tests/unit/strategy/test_design_library.py`
- `tests/unit/workshop/test_workshop_save_load.py`

**Files Modified**:
- `game/ui/screens/workshop_event_router.py` - Context-aware save/load
- `game/strategy/data/empire.py` - Design tracking
- `game/strategy/data/planet.py` - Built design tracking

**Phase 3 Completion Status**: [ ] Not Started

---

## Tech Tree Future-Proofing

### Design Considerations

The current implementation prepares for future tech tree integration without implementing it now:

1. **Component Availability Filtering**:
   - `WorkshopContext.available_tech_ids` field exists but unused
   - `WorkshopViewModel.refresh_available_components()` can be extended to filter by tech IDs
   - No changes to component data files needed yet

2. **Tech Preset System**:
   - Standalone mode uses JSON presets in `data/tech_presets/`
   - Same format can be used for tech tree unlocks later
   - Easy to add `tech_tier`, `tech_requirements` fields to `components.json` later

3. **Empire Tech Tracking**:
   - Empire class can be extended with `unlocked_tech_ids: List[str]` later
   - `DesignLibrary` already empire-scoped
   - No breaking changes when tech system added

### Future Tech Tree Integration (Phase 4+)

When implementing tech tree:

1. **Component Definition Changes**:
   - Add `tech_tier` and `tech_requirements` fields to `data/components.json`
   - Example: `{"id": "advanced_railgun", "tech_tier": 2, "tech_requirements": ["kinetic_weapons_2"]}`

2. **Tech State Management**:
   - Add `Empire.unlocked_tech_ids: List[str]`
   - Create `TechTree` class to manage research and prerequisites
   - Serialize tech state in save games

3. **Workshop Integration**:
   - Pass `empire.unlocked_tech_ids` to `WorkshopContext.available_tech_ids`
   - Modify `WorkshopViewModel.refresh_available_components()` to filter components

4. **UI Indicators**:
   - Gray out locked components in palette
   - Show tooltip: "Requires: Kinetic Weapons II"
   - Add "Tech Tree" button to open research screen

---

## Critical Files Reference

### Core Workshop Files
- [game/ui/screens/builder_screen.py](game/ui/screens/builder_screen.py) → [workshop_screen.py](game/ui/screens/workshop_screen.py)
- [game/ui/screens/builder_event_router.py](game/ui/screens/builder_event_router.py) → [workshop_event_router.py](game/ui/screens/workshop_event_router.py)
- [game/ui/screens/builder_viewmodel.py](game/ui/screens/builder_viewmodel.py) → [workshop_viewmodel.py](game/ui/screens/workshop_viewmodel.py)
- [game/ui/screens/builder_data_loader.py](game/ui/screens/builder_data_loader.py) → [workshop_data_loader.py](game/ui/screens/workshop_data_loader.py)
- [game/simulation/services/ship_builder_service.py](game/simulation/services/ship_builder_service.py) → [vehicle_design_service.py](game/simulation/services/vehicle_design_service.py)

### UI Panels
- [ui/builder/left_panel.py](ui/builder/left_panel.py)
- [ui/builder/right_panel.py](ui/builder/right_panel.py)
- [ui/builder/layer_panel.py](ui/builder/layer_panel.py)
- [ui/builder/detail_panel.py](ui/builder/detail_panel.py)
- [ui/builder/weapons_panel.py](ui/builder/weapons_panel.py)

### Strategy Integration
- [game/app.py](game/app.py)
- [game/ui/screens/strategy_scene.py](game/ui/screens/strategy_scene.py)
- [game/strategy/data/empire.py](game/strategy/data/empire.py)
- [game/strategy/data/fleet.py](game/strategy/data/fleet.py)
- [game/strategy/data/ship_instance.py](game/strategy/data/ship_instance.py)

### Persistence
- [game/simulation/systems/persistence.py](game/simulation/systems/persistence.py)
- [game/core/json_utils.py](game/core/json_utils.py)

### Reference Patterns
- [game/ui/screens/planet_list_window.py](game/ui/screens/planet_list_window.py) - Filterable list UI
- [game/ui/screens/planet_list_filters.py](game/ui/screens/planet_list_filters.py) - Filter logic
- [game/ui/screens/planet_list_presets.py](game/ui/screens/planet_list_presets.py) - Presets

---

## Test-Driven Development Summary

**This refactoring MUST follow TDD principles strictly:**

### Red-Green-Refactor Cycle

Every feature follows this cycle:
1. **RED**: Write failing test first
2. **GREEN**: Implement minimum code to make test pass
3. **REFACTOR**: Clean up while keeping tests green
4. **CHECKPOINT**: Run full test suite to verify no regressions

### Test Coverage Requirements

- **Phase 1**: After each batch, all existing tests must pass
- **Phase 2**: New tests for WorkshopContext, TechPresetLoader, button filtering
- **Phase 3**: New tests for DesignLibrary, DesignMetadata, DesignSelectorWindow

### Multi-Agent Coordination

When multiple agents work on this refactor:
1. Always check this document for current status
2. Update status column when completing work
3. Run test checkpoint before claiming work complete
4. Document any test failures or workarounds

### Continuous Testing Commands

```bash
# Quick smoke test (30 seconds)
python -m pytest tests/unit/workshop/ tests/unit/services/test_vehicle_design_service.py -v

# Full workshop test suite
python -m pytest tests/unit/workshop/ -v

# Full regression test
python -m pytest tests/ -v

# Watch mode (if using pytest-watch)
ptw tests/unit/workshop/ -- -v
```

---

## Overall Progress Tracking

### Phase Completion Status

- [ ] **Phase 1**: Rename to "Design Workshop" (6 batches)
  - [ ] Batch 1a: Test baseline
  - [ ] Batch 1b: User-facing text
  - [ ] Batch 1c: Service layer
  - [ ] Batch 1d: ViewModel/DataLoader
  - [ ] Batch 1e: Screen/EventRouter
  - [ ] Batch 1f: Import cleanup

- [ ] **Phase 2**: Dual Launch Modes
  - [ ] 2a: WorkshopContext
  - [ ] 2b: Tech Preset system
  - [ ] 2c: Button filtering
  - [ ] 2d: Launch integration

- [ ] **Phase 3**: Integrated Save/Load
  - [ ] 3a: DesignMetadata
  - [ ] 3b: DesignLibrary
  - [ ] 3c: DesignSelectorWindow
  - [ ] 3d: Workshop integration

### Test Suite Health

```
Baseline test count: [To be filled in Batch 1a]
Current test count: [Update as tests added]
Tests passing: [Update at each checkpoint]
Tests failing: [Document any failures]
```

---

## Summary

This 3-phase plan progressively refactors the Ship Builder into the Design Workshop:

1. **Phase 1** (6 batches) renames user-facing elements and establishes new terminology with TDD checkpoints after each batch
2. **Phase 2** implements dual launch modes with context-aware initialization, button visibility, and tech preset system (all test-driven)
3. **Phase 3** replaces file dialogs with strategy-integrated design library and selection UI (test-first implementation)

**Key Principles**:
- Test-driven at every step
- Backward compatibility during transition
- Incremental batches with checkpoints
- Multiple agents can coordinate via this document
- Zero regressions tolerance

The design is extensible for future tech tree integration without requiring architectural changes. Each phase can be tested independently and provides value on its own.

The implementation preserves backward compatibility with standalone mode while enabling sophisticated strategy layer integration for production gameplay.
