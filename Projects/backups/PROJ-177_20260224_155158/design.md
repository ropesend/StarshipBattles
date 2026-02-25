# PROJ-177: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

PROJ-170 (Exception Handling Migration) introduced a domain exception hierarchy rooted at
`GameException` in `game/core/exceptions.py`. The migration strategy was:
1. Add domain exceptions to tuple catches alongside generic types (transitional safety)
2. Remove generic types once all raises are migrated

Step 2 was not completed. This project finishes it.

### Exception Hierarchy
```
GameException (base)
    StateException         - Object state errors
        FrozenStateException   - Modifying frozen objects
    ValidationException    - Input validation failures
    ResourceException      - Resource loading errors
        MissingResourceException - Resource not found
    PersistenceException   - Save/load failures
    SimulationException    - Combat engine errors
        ComponentException     - Component operation errors
        FormulaException       - Formula evaluation errors
```

### Current Usage Statistics
- **ValidationException**: 69 raises across 29 files (dominant type)
- **PersistenceException**: 19 raises across 7 files
- **FormulaException**: 10 raises across 2 files
- **StateException**: 6 raises across 4 files
- **FrozenStateException**: 3 raises in 1 file (registry.py)
- **ResourceException**: 3 raises across 3 files
- **MissingResourceException**: 1 raise in 1 file
- **ComponentException**: 0 raises (defined but unused - future extension)
- **SimulationException**: 0 raises (base class only)

## Swarm Findings Summary

### Architecture
The exception migration was 95%+ complete. The remaining work is mechanical cleanup:
- 29 except blocks with mixed generic + domain catches (audit said 24, we found 29)
- 12 docstrings with stale Raises: sections (audit said 6, we found 12)
- 4 builtin raise sites that should use domain exceptions
- 2 legitimate builtin raises (NotImplementedError in ABCs, TypeError in __init_subclass__)

### Key Patterns to Reuse
- **save_json() pattern**: `game/core/validation_helpers.py` - catches all exceptions internally,
  returns bool. Callers don't need generic catches around it.
- **load_json_required() pattern**: Returns parsed JSON but can raise `json.JSONDecodeError`
  (subclass of `ValueError`). Callers DO need `ValueError` catch for this.
- **from_dict() pattern**: Domain deserialization methods. Some still access raw dicts and can
  raise `KeyError`/`TypeError`. These should KEEP generic catches until the from_dict methods
  themselves are fully migrated to raise domain exceptions.

### Dependencies & Risks
1. **False positive on generic removal** - If a try block calls stdlib code we missed, removing
   the generic catch could let an unhandled exception crash the app. Mitigated by: conservative
   classification (only 9 of 29 blocks marked for cleanup), targeted test runs per task.
2. **Docstring-only changes causing test failures** - Zero risk; docstrings don't affect behavior.
3. **Caller mismatch on raise migration** - When changing `raise KeyError` to
   `raise ValidationException`, callers catching `KeyError` will miss it. Mitigated by: Task 3.5
   explicitly searches for affected callers.

### Opportunities Discovered
- `ComponentException` and `SimulationException` are defined but never raised. Could be
  candidates for removal in a future cleanup, but out of scope here.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
