# PROJ-362 Follow-up: Verify Audit Remediation Resolved Findings

**Review mode:** code (follow-up, concise)
**Scope:** 3 files (2 production, 1 decisions doc)
**Parent request:** req_20260505_061729_30913a
**Remediation SHA:** `6d21765f6`
**Attribution marker:** `b23b88d46`
**Limitations:** No full re-review — targeted verification of MAJ-001 resolution and `__all__` back-compat only.

---

## Verification Matrix

| Parent Finding | Status | Evidence |
|---|---|---|
| **MAJ-001**: `system_effects_collector.py` 569 LOC > 500 LOC ceiling | **resolved** | Collector now 442 LOC. Display/grouping/format helpers (`make_group_key`, `make_display_name`, `format_intrinsic_ability_magnitude`, `_ability_kind`, `_format_status`, `_is_activatable`) extracted to new module `effect_ability_display.py` (168 LOC). Both files independently under the 500-LOC ceiling. |
| **MIN-001**: `_aggregate` accepts unused `registries`/`system` params | **unresolved** | Not in remediation scope — decisions.md states "Only the MAJ is addressed here per remediation policy." Still present at `system_effects_collector.py:385-412`. Expected, not a regression. |
| **MIN-002**: `all_owner_aware_scopes()` dead code | **unresolved** | Not in remediation scope. Still present in `effect_ability_metadata.py`. Expected. |
| **MIN-003**: `Optional[X]` → PEP 604 `X | None` | **partially-resolved** | `find_sector_effect` return type updated to `Dict[str, Any] | None` (line 131). `Optional` removed from typing import (line 29). `effect_ability_metadata.py:150` was not changed per decisions.md scope limitation. |

---

## `__all__` Re-export Verification

All UI consumers continue to import from `system_effects_collector` unchanged:

| Consumer | Import | Covered by `__all__`? |
|---|---|---|
| `planet_list_window.py:36-38` | `make_display_name`, `format_intrinsic_ability_magnitude` | Yes |
| `planet_list_window.py:77` | `make_group_key` | Yes |
| `planet_list_filters.py:29` | `make_group_key` | Yes |
| `planet_list_sidebar.py:159-160` | `make_display_name` | Yes |
| `system_tree_panel.py:452,484` | `collect_system_effects` | Yes |
| `system_tree_panel.py:499` | `collect_sector_effects` | Yes |
| `system_tree_panel.py:607-608` | `format_intrinsic_ability_magnitude` | Yes |

The `__all__` block (lines 63-72) covers all 8 consumer import sites. Two additional entries (`aggregate_value_or`, `is_known_effect_ability`) are included for documented API completeness; `is_known_effect_ability` has no UI consumers but is re-exported as a public-path convenience.

---

## Regressions

### REG-001: Dead import `_ability_kind` in collector — MINOR

**File:** `game/strategy/services/system_effects_collector.py:45`

`_ability_kind` is imported from `effect_ability_display` but never referenced in the collector body. In the pre-extraction code it was used to distinguish rate vs. multiplier abilities; after the metadata registry, `metadata.kind` replaced it. The extraction moved it to `effect_ability_display` correctly, but the re-import in the collector is dead code.

**Remediation:** Remove `_ability_kind` from the import block at line 45.

---

## Summary

| Status | Count |
|---|---|
| Resolved | 1 (MAJ-001) |
| Partially-resolved | 1 (MIN-003) |
| Unresolved (expected) | 2 (MIN-001, MIN-002) |
| New regression | 1 (REG-001, MINOR) |
