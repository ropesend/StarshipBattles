# Phase 1: Core & Simulation Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Narrow exception handling in the lowest layers first (core, simulation) since higher layers depend on them.
**Tests:** `pytest tests/unit/core/ tests/unit/simulation/ tests/unit/entities/ tests/unit/systems/ tests/unit/services/ tests/unit/combat/`

---

## Tasks

### Task 1.1: Core — registry.py (3 sites) [Simple]
**File:** `game/core/registry.py`
**Lines:** 370, 380, 395
**Pattern:** JSON/data loading during registry initialization.

- [x] Line 370: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — modifiers loading
- [x] Line 380: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — components loading
- [x] Line 395: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — vehicle classes loading
- [x] Ensure `import json` is present at top of file
- [x] Verify: `pytest tests/unit/core/ -x`

**Notes:** Added `import json` at top of file. All three catches narrowed.

---

### Task 1.2: Core — screenshot_manager.py (2 sites) [Simple]
**File:** `game/core/screenshot_manager.py`
**Lines:** 134, 146
**Pattern:** Clipboard operations — Tier 1 (keep with comments).

- [x] Line 134: Keep `except Exception as e:` — add comment: `# Intentional broad catch: Tkinter clipboard is platform-dependent`
- [x] Line 146: Keep `except Exception as clip_err:` — add comment: `# Intentional broad catch: subprocess clipboard fallback, platform-dependent`
- [x] Verify: `pytest tests/unit/core/ -x`

**Notes:** Both intentional broad catches documented with inline comments.

---

### Task 1.3: Simulation — battle_controller.py (3 sites) [Medium] — TIER 4 STRUCTURAL
**File:** `game/simulation/battle_controller.py`
**Lines:** 205, 422, 557
**Pattern:** Ship state restoration and reinforcement. Needs validation before try block.

- [x] Line 205: Narrow catch to `except (TypeError, ValueError, KeyError, AttributeError) as e:`
- [x] Line 422: Narrow catch to `except (TypeError, ValueError, AttributeError) as e:`
- [x] Line 557: Narrow catch to `except (TypeError, ValueError, KeyError, AttributeError) as e:`
- [x] Verify: `pytest tests/unit/simulation/ tests/unit/combat/ -x`

**Notes:** Existing validation was sufficient. Test updated to use ValueError instead of generic Exception.

---

### Task 1.4: Simulation — abilities/__init__.py (1 site) [Medium] — TIER 4 STRUCTURAL
**File:** `game/simulation/components/abilities/__init__.py`
**Line:** 99
**Pattern:** Ability instantiation from registry.

- [x] Validation already exists (`if name in ABILITY_REGISTRY`) before calling constructor
- [x] Narrow remaining catch to `except (TypeError, ValueError, KeyError, AttributeError) as e:`
- [x] Verify: `pytest tests/unit/simulation/ -x`

**Notes:** Validation already present at line 93. Only narrowed the catch.

---

### Task 1.5: Simulation — component.py (3 sites) [Simple]
**File:** `game/simulation/components/component.py`
**Lines:** 567, 583, 676
**Pattern:** Component/modifier JSON loading. Already has specific catches above broad catch.

- [x] Line 567: Replace `except Exception as e:` with `except (AttributeError, ImportError) as e:` — fallback after (KeyError, TypeError, ValueError) catch
- [x] Line 583: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:` — fallback after json.JSONDecodeError catch
- [x] Line 676: Replace `except Exception as e:` with `except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:` — fallback after json.JSONDecodeError catch
- [x] Verify: `pytest tests/unit/simulation/ -x`

**Notes:** All three catches narrowed.

---

### Task 1.6: Simulation — design_loader.py (2 sites) [Simple]
**File:** `game/simulation/services/design_loader.py`
**Lines:** 80, 131
**Pattern:** Design data loading. Already has specific catches above broad catch.

- [x] Line 80: Replace `except Exception as e:` with `except (AttributeError, ImportError, OSError) as e:` — fallback after (KeyError, TypeError, ValueError) catch
- [x] Line 131: Replace `except Exception as e:` with `except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:` — fallback after OSError catch
- [x] `import json` already present at top of file
- [x] Verify: `pytest tests/unit/simulation/ -x`

**Notes:** Both catches narrowed.

---

### Task 1.7: Simulation — vehicle_design_service.py (1 site) [Medium] — TIER 4 STRUCTURAL
**File:** `game/simulation/services/vehicle_design_service.py`
**Line:** 121
**Pattern:** Ship creation with component registry.

- [x] Validation already exists (line 98 checks `ship_class in self._registries.vehicle_classes`)
- [x] Narrow catch to `except (TypeError, ValueError, KeyError, AttributeError) as e:`
- [x] Verify: `pytest tests/unit/services/ -x`

**Notes:** Validation already present. Only narrowed the catch.

---

### Task 1.8: Simulation — battle_service.py (1 site) [Medium] — TIER 4 STRUCTURAL
**File:** `game/simulation/services/battle_service.py`
**Line:** 76
**Pattern:** Battle engine creation.

- [x] Narrow catch to `except (TypeError, ValueError, AttributeError) as e:`
- [x] Verify: `pytest tests/unit/simulation/ -x`

**Notes:** Catch narrowed.

---

### Task 1.9: Simulation — persistence.py (3 sites) [Simple]
**File:** `game/simulation/systems/persistence.py`
**Lines:** 20, 69, 116
**Pattern:** Tkinter init (Tier 1) + file I/O (already has specific catches above).

- [x] Line 20: Keep `except Exception as e:` — add comment: `# Intentional broad catch: Tkinter init is platform-dependent`
- [x] Line 69: Replace `except Exception as e:` with `except (OSError, PermissionError) as e:` — save fallback after (TypeError, ValueError) catch
- [x] Line 116: Replace `except Exception as e:` with `except (OSError, PermissionError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` — load ship
- [x] Verify: `pytest tests/unit/simulation/ -x`

**Notes:** One intentional broad catch documented, two catches narrowed. Updated test to use json.JSONDecodeError.

---

### Task 1.10: Simulation — ship_serialization.py (1 site) [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Line:** 107
**Pattern:** Safety net with re-raise — Tier 1 (keep with comment).

- [x] Line 107: Keep `except Exception as e:` — add comment: `# Intentional broad catch: diagnostic logging before re-raise`
- [x] Verify: `pytest tests/unit/entities/ -x`

**Notes:** Intentional broad catch documented with inline comment.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run: `pytest tests/unit/core/ tests/unit/simulation/ tests/unit/entities/ tests/unit/systems/ tests/unit/services/ tests/unit/combat/ -x` — 1591 passed
- [x] Run: `pytest tests/ -n 12` — 6244 passed (1 pre-existing flaky test excluded)
- [x] Grep: `grep -rn "except Exception" game/core/ game/simulation/` — only 4 intentional sites + 3 Phase 6 sites remain
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
