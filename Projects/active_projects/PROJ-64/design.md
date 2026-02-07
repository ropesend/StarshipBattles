# PROJ-64: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Test Baseline:** 6248 passed, 0 failures (2026-02-06)
**Total `except Exception` occurrences:** 90 across 47 files in `game/`

The project has a well-designed custom exception hierarchy (`game/core/exceptions.py`) created during PROJ-45, but it is significantly underutilized. Of 90 broad exception catches, only ~6 use specific custom exceptions. The hierarchy defines 12 exception classes but 3 are never raised anywhere (ComponentException, TargetingException, MissingResourceException).

### Exception Hierarchy (game/core/exceptions.py)
```
GameException (base)
├── StateException         - 5 raises (singleton violations, battle state)
│   └── FrozenStateException   - 3 raises (registry mutations)
├── ValidationException    - 3 raises (projectile params)
├── ResourceException      - 1 raise (paths.py root finder)
│   └── MissingResourceException - 0 raises (UNUSED)
├── PersistenceException   - 3 raises (game_session.py)
├── SimulationException    - 0 raises (base class)
│   ├── ComponentException     - 0 raises (UNUSED)
│   └── FormulaException       - 8 raises (formula/modifier eval)
└── AIException            - 0 raises (base class)
    └── TargetingException     - 0 raises (UNUSED)
```

## Swarm Findings Summary

### Architecture
The 90 broad catches fall into 5 distinct patterns:

| Pattern | Count | Description | Action |
|---------|-------|-------------|--------|
| **Silent Fallback** | ~22 | No logging, returns default/None | Narrow + add logging |
| **Logged Degradation** | ~36 | Logs error, continues with fallback | Narrow exception types |
| **Error Collection** | ~14 | Appends to errors list, continues batch | Narrow exception types |
| **Catch-and-Convert** | ~8 | Wraps in domain exception, re-raises | Keep (correct pattern) |
| **Safety Net + Re-raise** | ~10 | Logs context, then re-raises | Keep (correct pattern) |

### Key Patterns to Reuse

- **Gold Standard (save_game_service.py)**: Catches `json.JSONDecodeError`, `FileNotFoundError`, `PermissionError`, `OSError`, `(TypeError, ValueError)` each with distinct user-facing messages. No broad `except Exception`. 15 dedicated error handling tests.
- **Folder Scanning (race_library.py, design_library.py)**: Specific exceptions first, then broad catch as iteration safety net with full traceback logging. Acceptable pattern.
- **Catch-and-Convert (formula_system.py, modifier_effects.py)**: Catches broad exceptions from `eval()` and wraps in `FormulaException` with error codes. Correct pattern for dynamic evaluation.
- **Safety Net (ship_serialization.py)**: Catches broad, logs with traceback, then `raise`. Correct for diagnostic logging.

### Dependencies & Risks

1. **Pygame errors in asset loading** - `pygame.error` is its own exception type, NOT a subclass of OSError. Must include it explicitly in image loading catches.
2. **Tkinter errors** - `tkinter.TclError` and `RuntimeError` are platform-dependent. Broad catch is appropriate for Tkinter init.
3. **Formula eval()** - Can throw essentially anything. Catch-and-convert to FormulaException is the correct pattern.
4. **Test compatibility fallbacks** - Some `except Exception` blocks exist specifically for test environments that don't set up registries. These should be narrowed to specific provider exceptions.
5. **No test coverage for test_lab_screen.py error paths** - 6 broad catches with zero error handling tests. Higher risk to modify.

### Opportunities Discovered

- 3 unused exception types (ComponentException, TargetingException, MissingResourceException) could be activated by replacing some broad catches
- 3 locations use `print()` instead of logger for error output - should be fixed
- Several locations have no logging at all when catching exceptions - debugging blind spots

## Classification of All 90 Sites

### Tier 1: KEEP AS-IS (Correct Patterns) — ~18 sites
These use broad catch correctly:
- **app.py** - Top-level crash handler (re-raises)
- **formula_system.py** - Catch-and-convert to FormulaException
- **modifier_effects.py** - Catch-and-convert to FormulaException
- **ship_serialization.py** - Safety net with re-raise
- **persistence.py:20** - Tkinter init (external library)
- **logger.py** - Event handler isolation (must not propagate)
- **event_bus.py** - Event handler isolation (must not propagate)

### Tier 2: NARROW TO SPECIFIC TYPES — ~55 sites
Replace `except Exception` with specific exception tuples:
- **File I/O operations** → `(FileNotFoundError, PermissionError, OSError, json.JSONDecodeError)`
- **Image/asset loading** → `(FileNotFoundError, OSError, pygame.error)`
- **Ship/component creation** → `(TypeError, ValueError, KeyError, AttributeError)`
- **Registry/data loading** → `(json.JSONDecodeError, KeyError, TypeError, FileNotFoundError, OSError)`
- **Clipboard operations** → Keep broad (platform-dependent)

### Tier 3: NARROW + ADD LOGGING — ~12 sites
Currently silent or using `print()`:
- **classification_config.py** - Silent fallback, no logging
- **ship_instance.py** - Silent registry fallback
- **turn_engine.py** - Silent registry fallback
- **workshop_context.py** - Silent registry fallback
- **design_selector_window.py:523** - Silent `continue`
- **detail_panel.py** - Uses `print()` instead of logger
- **right_panel.py** - Uses `print()` instead of logger
- **stats_config.py** - Uses `print()` instead of logger

### Tier 4: STRUCTURAL IMPROVEMENT — ~5 sites
Need validation/pre-checks rather than just catch narrowing:
- **battle_controller.py:205,422** - Should validate ship state before attempting creation
- **vehicle_design_service.py:121** - Should validate inputs before Ship construction
- **battle_service.py:76** - Should validate engine preconditions
- **abilities/__init__.py:99** - Should validate data before ability construction

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
