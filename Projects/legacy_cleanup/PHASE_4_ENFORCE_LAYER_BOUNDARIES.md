# Phase 4: Enforce Layer Boundaries

**Project:** Legacy Code Cleanup
**Phase:** 4 of 8
**Risk Level:** High
**Dependencies:** Phase 3 complete

---

## High-Level Project Context

This phase is part of a comprehensive 8-phase legacy code cleanup effort:

| Phase | Name | Status |
|-------|------|--------|
| 1 | Delete Dead Code | Complete |
| 2 | Remove Shims & Aliases | Complete |
| 3 | Consolidate Re-exports | Complete |
| **4** | **Enforce Layer Boundaries** | **THIS PHASE** |
| 5 | Standardize Registry Access | Pending |
| 6 | Type Safety via Protocols | Pending |
| 7 | Standardize Data Formats | Pending |
| 8 | Clean Up Tests & Patterns | Pending |

**Overall Goal:** Clean up legacy code, enforce architectural boundaries, and standardize patterns across the Starship Battles codebase.

---

## Phase 4 Objectives

1. Define and document the layer architecture
2. Remove pygame dependency from Simulation layer (enable headless)
3. Fix AI layer importing from Simulation layer
4. Fix Simulation layer reverse dependencies (importing from AI/Strategy)
5. Establish interface boundaries using dependency inversion

---

## Target Architecture

```
┌─────────────────────────────────────┐
│    UI Layer (game/ui/)              │  Depends on: Strategy, Simulation, AI, Core
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Strategy Layer (game/strategy/)    │  Depends on: Simulation (via interface), Core
│  - Uses IBattleResolver interface   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Simulation Layer (game/simulation/)│  Depends on: Core ONLY
│  - Defines IControllable interface  │  - NO pygame imports
│  - Accepts AI controller via DI     │  - NO strategy imports
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  AI Layer (game/ai/)                │  Depends on: Simulation interfaces, Core
│  - Implements IControllable users   │  - NO direct Simulation imports
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Core Layer (game/core/)            │  Depends on: Nothing (foundation)
│  - Vector2, math, constants         │
│  - Registry, config, logging        │
└─────────────────────────────────────┘
```

**Key Principles:**
- Lower layers define interfaces
- Upper layers implement/consume interfaces
- Dependencies flow downward only
- Cross-layer communication via interfaces and dependency injection

---

## Detailed Tasks

### 4.1 Document Architecture

Create `game/ARCHITECTURE.md` documenting:
- Layer definitions and responsibilities
- Allowed dependencies for each layer
- Interface patterns (IControllable, IBattleResolver)
- Examples of correct vs incorrect imports

### 4.2 Remove pygame from Simulation Layer

**CRITICAL:** This enables headless/server deployment of simulation.

#### 4.2.1 Ship.py pygame Import

**File:** `game/simulation/entities/ship.py` (Line 1)
```python
import pygame  # VIOLATION - remove this
```

**Issue:** pygame is used for:
- `pygame.math.Vector2` - Replace with `game.core.math.Vector2`
- Possibly color tuples or other pygame types

**Steps:**
1. Audit all pygame usages in ship.py
2. Replace `pygame.math.Vector2` with `from game.core.math import Vector2`
3. Replace any color handling with tuple types
4. Remove `import pygame`
5. Test that Ship class works without pygame

#### 4.2.2 Battle State pygame References

**File:** `game/simulation/battle_state.py`

Check for any pygame dependencies and remove them.

#### 4.2.3 Other Simulation Files

Search entire `game/simulation/` directory for pygame imports:
```bash
grep -r "import pygame" game/simulation/ --include="*.py"
grep -r "from pygame" game/simulation/ --include="*.py"
```

Fix all violations found.

### 4.3 Fix AI → Simulation Violation

**File:** `game/ai/target_evaluator.py` (Line 7)
```python
from game.simulation.components.component import LayerType  # VIOLATION
```

**Options:**

**Option A: Move LayerType to Core (Recommended)**
1. Move `LayerType` enum to `game/core/constants.py`
2. Update all imports to use `from game.core.constants import LayerType`
3. This makes LayerType available to all layers without violations

**Option B: Create AI-local enum**
1. Define a copy of LayerType in `game/ai/constants.py`
2. Only if LayerType has AI-specific values

**Option C: Pass LayerType as parameter**
1. Have callers pass LayerType values
2. AI layer never imports it directly

**Recommended:** Option A - Move to Core

### 4.4 Fix Simulation → AI Reverse Dependency

**File:** `game/simulation/systems/battle_engine.py` (Lines 60-61)
```python
from game.ai.controller import AIController  # VIOLATION
from game.ai.interfaces import ShipControllableAdapter  # Check if violation
```

**Solution: Dependency Injection**

Instead of importing AIController, accept it as a parameter:

```python
# Before (violation):
from game.ai.controller import AIController

class BattleEngine:
    def __init__(self):
        self.ai_controller = AIController()

# After (dependency injection):
class BattleEngine:
    def __init__(self, ai_controller=None):
        self.ai_controller = ai_controller  # Injected from outside
```

**Steps:**
1. Remove `from game.ai.controller import AIController`
2. Add `ai_controller` parameter to BattleEngine.__init__
3. Update all BattleEngine instantiation sites to pass AIController
4. Instantiation happens in UI or Strategy layer, not Simulation

**For ShipControllableAdapter:**
- Check if this is from `game/ai/interfaces/` or `game/simulation/`
- If it's in AI, same pattern applies - inject it
- Consider: Should IControllable interface move to Simulation?

### 4.5 Fix Simulation → Strategy Violation

**File:** `game/simulation/battle_controller.py`

Check for imports from `game.strategy`:
```bash
grep -r "from game.strategy" game/simulation/ --include="*.py"
```

**Common patterns to fix:**
- Importing Fleet type → Use interface or move to Core
- Importing configuration → Move config to Core

**Solution approaches:**
1. **Move shared types to Core** (if genuinely shared)
2. **Use adapter pattern** (Strategy adapter converts Strategy types to Simulation types)
3. **Define interfaces in Simulation** (Strategy implements them)

### 4.6 Verify Interface Boundaries

**Existing interfaces to leverage:**

**IControllable** (`game/ai/interfaces/controllable.py`)
- Defines contract for AI-controlled entities
- Ship implements this interface
- AI layer programs against interface, not Ship directly

**IBattleResolver** (`game/strategy/interfaces/battle_resolver.py`)
- Defines contract for battle resolution
- SimulationBattleResolver implements it
- Strategy layer uses interface, not Simulation directly

**Verify these patterns are correctly applied:**
1. Strategy imports IBattleResolver, not BattleController
2. AI imports IControllable, not Ship
3. All cross-layer dependencies use interfaces

---

## Verification Checklist

After completing all tasks:

- [ ] Architecture documented in `game/ARCHITECTURE.md`
- [ ] No `import pygame` in any `game/simulation/` file
- [ ] Simulation layer can be imported without pygame installed (test this!)
- [ ] LayerType moved to Core (or alternative solution implemented)
- [ ] AIController not imported in Simulation layer
- [ ] BattleEngine accepts AI controller via dependency injection
- [ ] No Strategy imports in Simulation layer
- [ ] Interface boundaries correctly applied
- [ ] No circular imports
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Application launches and runs correctly
- [ ] Headless simulation test passes (new test)

---

## Import Analysis Commands

Before and after, run these to verify:

```bash
# Find all pygame imports in simulation
grep -rn "import pygame\|from pygame" game/simulation/ --include="*.py"

# Find all AI imports in simulation
grep -rn "from game.ai" game/simulation/ --include="*.py"

# Find all strategy imports in simulation
grep -rn "from game.strategy" game/simulation/ --include="*.py"

# Find all simulation imports in AI (check for violations)
grep -rn "from game.simulation.components\|from game.simulation.entities" game/ai/ --include="*.py"

# Test headless import
python -c "import sys; sys.modules['pygame'] = None; from game.simulation.entities.ship import Ship; print('Headless OK')"
```

---

## Files Modified

- `game/ARCHITECTURE.md` (new file)
- `game/simulation/entities/ship.py` (remove pygame)
- `game/simulation/battle_state.py` (if pygame found)
- `game/ai/target_evaluator.py` (fix LayerType import)
- `game/core/constants.py` (add LayerType if moving)
- `game/simulation/systems/battle_engine.py` (dependency injection)
- `game/simulation/battle_controller.py` (fix strategy imports)
- Various files updating imports

---

## Headless Test

Create a test to verify Simulation layer works without pygame:

```python
# tests/unit/simulation/test_headless.py
import sys
import pytest

def test_simulation_layer_headless():
    """Verify simulation layer can be imported without pygame."""
    # Block pygame import
    original_pygame = sys.modules.get('pygame')
    sys.modules['pygame'] = None

    try:
        # These imports should work without pygame
        from game.simulation.entities.ship import Ship
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.battle_state import BattleState
        # Add more critical imports
    finally:
        # Restore pygame
        if original_pygame:
            sys.modules['pygame'] = original_pygame
        else:
            del sys.modules['pygame']
```

---

## Notes for Next Phase

Phase 5 (Standardize Registry Access) will:
- Define tiered access pattern (utility functions vs domain services)
- Fix ModifierService inconsistency (uses RegistryManager.instance())
- Evaluate and potentially remove thin wrapper services
- Document access patterns

Ensure layer boundaries are enforced before proceeding to Phase 5.

---

*End of Phase 4 Plan*
