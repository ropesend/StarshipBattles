# PROJ-10: Design Document

## Error Handling Standards

### Pattern 1: Replace Bare Except Clauses
**Before:**
```python
try:
    do_something()
except:
    pass
```

**After:**
```python
try:
    do_something()
except (ValueError, KeyError) as e:
    log_warning(f"Operation failed: {e}")
```

### Pattern 2: Add Logging to Silent Handlers
**Before:**
```python
try:
    result = parse_data(data)
except Exception:
    result = default_value
```

**After:**
```python
try:
    result = parse_data(data)
except Exception as e:
    log_warning(f"Failed to parse data, using default: {e}")
    result = default_value
```

### Pattern 3: Include Context in Error Messages
**Before:**
```python
log_error("Failed to load design")
return None
```

**After:**
```python
log_error(f"Failed to load design '{design_id}' from '{filepath}': {e}")
return None
```

### Pattern 4: Replace print_exc() with Logger
**Before:**
```python
except Exception:
    traceback.print_exc()
```

**After:**
```python
except Exception as e:
    log_error(f"Unexpected error: {e}\n{traceback.format_exc()}")
```

## Files to Modify

### Critical Priority
| File | Issue IDs | Changes |
|------|-----------|---------|
| `game/simulation/formula_system.py` | ERR-002, ERR-003 | Add logging, whitelist validation |
| `game/ui/screens/save_selection_window.py` | ERR-001, ERR-009 | Replace bare except, add context |
| `game/strategy/systems/save_game_service.py` | ERR-004 | Replace print_exc with log_error |
| `game/strategy/systems/design_library.py` | ERR-005, ERR-010 | Add logging with context |
| `game/simulation/systems/persistence.py` | ERR-006 | Add logging, fail fast |
| `game/ui/screens/strategy_input_handler.py` | ERR-007 | Log and re-raise |
| `game/core/screenshot_manager.py` | ERR-008 | Add warning log |

### Major Priority
| File | Issue IDs | Changes |
|------|-----------|---------|
| `ui/builder/modifier_row.py` | ERR-012 | Add warning before fallback |
| `game/core/json_utils.py` | ERR-013 | Distinguish error types |
| `game/simulation/components/abilities/__init__.py` | ERR-014 | Log ability creation failures |
| `game/ui/screens/setup_data_io.py` | ERR-015 | Log skipped files |
| `game/simulation/systems/battle_engine.py` | ERR-016 | Log IOError, ensure cleanup |
| `game/core/registry.py` | ERR-017 | Validate inputs |
| `game/ui/screens/build_queue_screen.py` | ERR-011 | Track failed designs |

## Testing Strategy
1. Unit tests for each modified exception handler
2. Integration tests for save/load with corrupted data
3. Manual testing of formula evaluation with invalid formulas
4. Verify log output contains expected context
