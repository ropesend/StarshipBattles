# Phase 1: Migrate 3 readers + delete 5 forwarders

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-387 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate the 3 grandfathered external readers off the underscore-prefixed forwarders on `Galaxy` (`_global_hex_*`, `_planet_to_system`, `_zone_to_system`) onto public `GalaxyState` accessors, then delete the 5 forwarders. Audit's docstring acknowledged these were marked for "Phase 3 cleanup."

---

## Tasks

### Task 1.1: Migrate `movement.py` reader
**File:** `game/strategy/engine/handlers/movement.py` (corrected from plan: `data/movement.py` did not exist)
**Tests:** `pytest tests/ -k movement`

- [x] Replace `galaxy._global_hex_*` / `galaxy._planet_to_system` / `galaxy._zone_to_system` reads with the canonical `galaxy._state.<public_name>` accessors (LEG-03-022)
- [x] Verify: file no longer references underscore-prefixed forwarders

### Task 1.2: Migrate `fleet_navigation_service.py` reader
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/ -k fleet_navigation`

- [x] Replace forwarder reads with public `GalaxyState` accessors (LEG-03-022)
- [x] Verify: file no longer references underscore-prefixed forwarders

### Task 1.3: Migrate `hex_outlines.py` reader
**File:** `game/ui/screens/strategy_render/hex_outlines.py`
**Tests:** `pytest tests/ -k hex_outlines`

- [x] Replace forwarder reads with public `GalaxyState` accessors (LEG-03-022)
- [x] Verify: file no longer references underscore-prefixed forwarders

### Task 1.4: Delete the 5 forwarders on `Galaxy`
**File:** `game/strategy/data/galaxy.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Delete the 5 property forwarders at lines 97-131 (`_global_hex_<five>`, `_planet_to_system`, `_zone_to_system`) plus the "backwards-compat under-prefixed forwarders" docstring (LEG-03-022)
- [x] Verify: `grep -rn -E "galaxy\._(global_hex|planet_to_system|zone_to_system)" .` returns zero hits in live code (only audit/tracking docs remain)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
