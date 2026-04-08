# Phase 3: Single Stat Path / Remove expected_stats Fallback

**Objective:** Remove redundant component re-scanning from `calculate_design_stats()` and eliminate the `expected_stats` fallback that serves stale data.

**Key Principle:** One canonical stat path: `Ship.from_dict()` + `recalculate_stats()`. No parallel computation, no stale fallback. If it fails, raise — don't silently degrade.

---

## Background

`calculate_design_stats()` in `ship_design_stats.py`:
1. Creates a Ship via `Ship.from_dict()` → calls `recalculate_stats()` (correct path)
2. Then re-scans all components for resource totals (lines ~80-101) — redundant, Ship already has these
3. On `AttributeError`/`TypeError`/`KeyError`, falls back to `expected_stats` from design_data — serves stale/cached values that may not reflect current modifiers, damage, or toggles

The docs (`04_SERVICES.md:443`) explicitly call this the "single source of truth" for stat calculation.

## Design

1. After `ship.recalculate_stats()`, read resource/consumption values from the ship object's existing properties
2. Delete the redundant component re-scan (lines ~80-101)
3. Remove the `expected_stats` fallback — let errors propagate
4. If callers need graceful handling, they catch the exception at their level

---

## Checklist

### Discovery
- [ ] Read `ship_design_stats.py` fully — map all computation paths
- [ ] Identify which Ship properties provide resource storage, consumption, cargo totals
- [ ] Read all callers of `calculate_design_stats()` — understand error handling expectations
- [ ] Check if any caller depends on `expected_stats` fallback behavior

### Tests First (TDD)
- [ ] Write test: `calculate_design_stats()` returns correct resource_storage values (matches Ship properties)
- [ ] Write test: `calculate_design_stats()` returns correct resource consumption values
- [ ] Write test: `calculate_design_stats()` with invalid design data raises exception (not returns stale data)
- [ ] Write test: `calculate_design_stats()` with component_damage returns correct damaged stats
- [ ] Write test: `calculate_design_stats()` with component_toggles returns correct toggled stats
- [ ] Run tests — confirm fallback test fails (current code returns stale data instead of raising)

### Implementation
- [ ] Replace component re-scan for resource totals with reads from Ship properties
- [ ] Replace component re-scan for consumption rates with reads from Ship properties
- [ ] Remove `expected_stats` fallback (the `except (AttributeError, TypeError, KeyError)` block)
- [ ] Let exceptions propagate naturally to callers
- [ ] Update any callers that relied on the fallback to handle the exception explicitly
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python Tools/test_sharded/test_sharded.py`) — no regressions
- [ ] Verify return values are identical for valid designs (before/after comparison)
- [ ] Grep for `expected_stats` in `ship_design_stats.py` — should be removed or only in comments
