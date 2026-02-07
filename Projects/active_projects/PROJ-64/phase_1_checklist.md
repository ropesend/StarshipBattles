# Phase 1: Core & Simulation Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow exception handling in the lowest layers first (core, simulation) since higher layers depend on them.
**Tests:** `pytest tests/unit/core/ tests/unit/simulation/ tests/unit/entities/ tests/unit/systems/ tests/unit/services/ tests/unit/combat/`

---

## Tasks

### Task 1.1: Core — registry.py (3 sites) [Simple]
**File:** `game/core/registry.py`
**Lines:** 370, 380, 395
**Pattern:** JSON/data loading during registry initialization.

- [ ] Line 370: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — modifiers loading
- [ ] Line 380: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — components loading
- [ ] Line 395: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — vehicle classes loading
- [ ] Ensure `import json` is present at top of file
- [ ] Verify: `pytest tests/unit/core/ -x`

**Notes:**

---

### Task 1.2: Core — screenshot_manager.py (2 sites) [Simple]
**File:** `game/core/screenshot_manager.py`
**Lines:** 134, 146
**Pattern:** Clipboard operations — Tier 1 (keep with comments).

- [ ] Line 134: Keep `except Exception as e:` — add comment: `# Intentional broad catch: Tkinter clipboard is platform-dependent`
- [ ] Line 146: Keep `except Exception as clip_err:` — add comment: `# Intentional broad catch: subprocess clipboard fallback, platform-dependent`
- [ ] Verify: `pytest tests/unit/core/ -x`

**Notes:**

---

### Task 1.3: Simulation — battle_controller.py (3 sites) [Medium] — TIER 4 STRUCTURAL
**File:** `game/simulation/battle_controller.py`
**Lines:** 205, 422, 557
**Pattern:** Ship state restoration and reinforcement. Needs validation before try block.

- [ ] Line 205: Add validation of ship_state before `to_ship()`. Narrow catch to `except (TypeError, ValueError, KeyError, AttributeError) as e:`
- [ ] Line 422: Validate `entry_point` is a valid tuple before unpacking. Narrow catch to `except (TypeError, ValueError, AttributeError) as e:`
- [ ] Line 557: Narrow catch to `except (TypeError, ValueError, KeyError, AttributeError, OSError) as e:` — battle state restore
- [ ] Verify: `pytest tests/unit/simulation/ tests/unit/combat/ -x`

**Notes:**

---

### Task 1.4: Simulation — abilities/__init__.py (1 site) [Medium] — TIER 4 STRUCTURAL
**File:** `game/simulation/components/abilities/__init__.py`
**Line:** 99
**Pattern:** Ability instantiation from registry.

- [ ] Add check that `name` exists in `ABILITY_REGISTRY` before calling constructor (return None + log if missing)
- [ ] Narrow remaining catch to `except (TypeError, ValueError, KeyError, AttributeError) as e:`
- [ ] Verify: `pytest tests/unit/simulation/ -x`

**Notes:**

---

### Task 1.5: Simulation — component.py (3 sites) [Simple]
**File:** `game/simulation/components/component.py`
**Lines:** 567, 583, 676
**Pattern:** Component/modifier JSON loading. Already has specific catches above broad catch.

- [ ] Line 567: Replace `except Exception as e:` with `except (AttributeError, ImportError) as e:` — fallback after (KeyError, TypeError, ValueError) catch
- [ ] Line 583: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:` — fallback after json.JSONDecodeError catch
- [ ] Line 676: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:` — fallback after json.JSONDecodeError catch
- [ ] Verify: `pytest tests/unit/simulation/ -x`

**Notes:**

---

### Task 1.6: Simulation — design_loader.py (2 sites) [Simple]
**File:** `game/simulation/services/design_loader.py`
**Lines:** 80, 131
**Pattern:** Design data loading. Already has specific catches above broad catch.

- [ ] Line 80: Replace `except Exception as e:` with `except (AttributeError, ImportError, OSError) as e:` — fallback after (KeyError, TypeError, ValueError) catch
- [ ] Line 131: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:` — fallback after OSError catch
- [ ] Ensure `import json` is present at top of file
- [ ] Verify: `pytest tests/unit/simulation/ -x`

**Notes:**

---

### Task 1.7: Simulation — vehicle_design_service.py (1 site) [Medium] — TIER 4 STRUCTURAL
**File:** `game/simulation/services/vehicle_design_service.py`
**Line:** 121
**Pattern:** Ship creation with component registry.

- [ ] Add validation: check `self._registries` is not None and `ship_class` is valid before Ship construction
- [ ] Narrow catch to `except (TypeError, ValueError, KeyError, AttributeError) as e:`
- [ ] Verify: `pytest tests/unit/services/ -x`

**Notes:**

---

### Task 1.8: Simulation — battle_service.py (1 site) [Medium] — TIER 4 STRUCTURAL
**File:** `game/simulation/services/battle_service.py`
**Line:** 76
**Pattern:** Battle engine creation.

- [ ] Add validation: verify required parameters before BattleEngine construction
- [ ] Narrow catch to `except (TypeError, ValueError, AttributeError) as e:`
- [ ] Verify: `pytest tests/unit/simulation/ -x`

**Notes:**

---

### Task 1.9: Simulation — persistence.py (3 sites) [Simple]
**File:** `game/simulation/systems/persistence.py`
**Lines:** 20, 69, 116
**Pattern:** Tkinter init (Tier 1) + file I/O (already has specific catches above).

- [ ] Line 20: Keep `except Exception as e:` — add comment: `# Intentional broad catch: Tkinter init is platform-dependent`
- [ ] Line 69: Replace `except Exception as e:` with `except (OSError, PermissionError) as e:` — save fallback after (TypeError, ValueError) catch
- [ ] Line 116: Replace `except Exception as e:` with `except (OSError, PermissionError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — load ship
- [ ] Verify: `pytest tests/unit/simulation/ -x`

**Notes:**

---

### Task 1.10: Simulation — ship_serialization.py (1 site) [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Line:** 107
**Pattern:** Safety net with re-raise — Tier 1 (keep with comment).

- [ ] Line 107: Keep `except Exception as e:` — add comment: `# Intentional broad catch: diagnostic logging before re-raise`
- [ ] Verify: `pytest tests/unit/entities/ -x`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/unit/core/ tests/unit/simulation/ tests/unit/entities/ tests/unit/systems/ tests/unit/services/ tests/unit/combat/ -x`
- [ ] Run: `pytest tests/ --testmon`
- [ ] Grep: `grep -rn "except Exception" game/core/ game/simulation/` — only intentional sites remain
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
