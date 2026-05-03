# Exception Catch Quality Audit Report

## Summary

Total problematic blocks found across `game/`:

- **Critical:** bare `except`, silent `Exception` swallowing
- **Major:** overly broad catches without logging, missing exception chaining
- **Minor:** inconsistent logging, silent `return None`
- **Intentional:** documented broad catches for crash isolation

---

## Critical Issues

### EXC-Q-001: Bare except in scripts

| Field | Value |
|-------|-------|
| Location | `scripts/apply_resource_costs.py` |
| Pattern | bare `except: pass` |
| Impact | Catches `SystemExit`, `KeyboardInterrupt` |
| Severity | Critical |
| Category | SEPARATE_CLEANUP |
| Effort | Simple |

---

## Major Issues

### EXC-Q-002 through EXC-Q-010: Silent swallowing patterns

| ID | Location | Pattern | Notes |
|----|----------|---------|-------|
| EXC-Q-002 | `game/ui/panels/battle_panels.py` | `except Exception` with silent fallback | ERR-004 known |
| EXC-Q-003 | `game/ui/panels/race_environment_panel.py:443` | `except Exception` with silent fallback | ERR-004 known |
| EXC-Q-004 | `game/strategy/systems/save_game_service.py:221` | Catches 11 exception types | Logs but very broad |
| EXC-Q-005 | `game/simulation/components/component.py:525,629` | Catches `(KeyError, TypeError, ValueError)` | From component loading, logs warning but may hide real errors |
| EXC-Q-006 | `game/simulation/services/design_loader.py:75,122` | Broad tuple catches | From ship init |
| EXC-Q-007 | `game/simulation/services/vehicle_design_service.py:121` | Catches 4 exception types | |
| EXC-Q-008 | `game/simulation/battle_controller.py:172,389,516` | Catches `(TypeError, ValueError, KeyError, AttributeError)` | From ship creation |
| EXC-Q-009 | `game/strategy/systems/design_library.py:182,222` | Broad catches in persistence | |
| EXC-Q-010 | `game/strategy/systems/design_library.py:261,302` | Broad catches in persistence | |

### EXC-Q-011 through EXC-Q-015: Missing exception chaining

| ID | Location | Pattern | Notes |
|----|----------|---------|-------|
| EXC-Q-011 | `game/simulation/managers/battle_state_manager.py:79` | Re-raises `ValueError` without chaining | Should use `from e` |
| EXC-Q-012 | `game/simulation/components/abilities/base.py:98` | Re-raises `ValueError` without chaining | Should use `from e` |
| EXC-Q-013 | `game/strategy/generation/density/density_map.py:208` | Catches `TypeError`, raises `ValueError` without `from e` | |
| EXC-Q-014 | `game/strategy/engine/game_session.py:294,315,329` | Catches `KeyError`, raises `PersistenceException` | Already uses `from e` - GOOD |
| EXC-Q-015 | (reserved) | | |

---

## Minor Issues

### EXC-Q-016 through EXC-Q-020: Inconsistent logging

- Some `except` blocks log warnings, while similar blocks in the same module do not
- Some blocks return `None` on exception without any logging

---

## Intentional Broad Catches (ACCEPTABLE)

### EXC-Q-021 through EXC-Q-035: Documented/justified broad catches

| ID | Location | Justification |
|----|----------|---------------|
| EXC-Q-021 | `game/app.py:692` | Top-level crash handler (commented "Intentional") |
| EXC-Q-022 | `game/simulation/formula_system.py:139` | `eval()` error handler |
| EXC-Q-023 | `game/simulation/components/modifier_effects.py:178` | `eval()` error handler |
| EXC-Q-024 | `game/core/logger.py:107` | Event handler isolation |
| EXC-Q-025-031 | `game/ui/services/tkinter_utils.py` (7 blocks) | Platform-dependent Tkinter |
| EXC-Q-032-033 | `game/ui/services/screenshot_manager.py` (2 blocks) | UI operations |
| EXC-Q-034 | `game/ui/screens/builder/event_bus.py:55` | Handler isolation |
| EXC-Q-035 | (reserved) | |

---

## Summary Table

| Category | Critical | Major | Minor | Info | Total |
|----------|----------|-------|-------|------|-------|
| FIX_DURING_MIGRATION | 0 | 8 | 3 | 0 | 11 |
| SEPARATE_CLEANUP | 1 | 2 | 2 | 0 | 5 |
| INTENTIONAL | 0 | 0 | 0 | 15 | 15 |
| **Total** | **1** | **10** | **5** | **15** | **31** |

---

## Key Recommendation

Fix exception chaining during migration (add `from e`). Fix broad catches in persistence tier during migration.
