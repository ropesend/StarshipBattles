# PROJ-487: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit
- **Audit directory:** `Reviews/results/2026-05-20_210635_legacy-audit/`
- **Bundle counts:** Audit verified: 17 (across all sibling projects) | This bundle: 1 verified, 0 uncertain, 0 INFO, 0 deferred
- **Sibling projects:** PROJ-484, PROJ-485, PROJ-486, PROJ-488, PROJ-489, PROJ-490
- **Cluster identity:** planet_fuel_wrappers — four `# Deprecated fuel-specific wrappers (F-A-012)` on `PlanetaryFacility`
- **Severity breakdown:** 0 CRITICAL, 1 MAJOR (covers 4 closely-coupled wrapper methods), 0 MINOR

## Initial Analysis
`PlanetaryFacility` (`game/strategy/data/planetary_facility.py`) carries four fuel-specific wrappers `get_fuel_storage`, `get_max_fuel_storage`, `add_fuel`, `withdraw_fuel` at lines 209-221. They are explicitly marked `# Deprecated fuel-specific wrappers (F-A-012)` (header at line 196). Each wrapper is a one-line delegate to a generic `*_consumable` API method on the same class.

Verifier-confirmed callers:
- **3 production sites** in `game/strategy/engine/resupply_engine.py:135, 208, 293`
- **~56 test sites** across `tests/unit/strategy/data/test_facility_resource_tracking.py` and related test files

### Architecture
The generic consumable API on `PlanetaryFacility` accepts a resource-name key (e.g. `"fuel"`) plus an amount, replacing the four single-resource wrappers. The wrappers internally call the generic methods with the literal `"fuel"` key, so migrating callers is mechanical: replace `add_fuel(amount)` with `add_consumable("fuel", amount)`, etc.

### Key Patterns to Reuse
- **Generic consumable API**: the canonical surface — confirm exact method names during Phase 1 Task 1.1.
- **Resource-name keying**: any future single-resource convenience layer should likewise use the generic API as the primary surface.

### Dependencies & Risks
1. **Production behavior preservation** — Because the wrappers internally call the generic API with `"fuel"`, migrating callers should produce zero behavioral diff. Verify by re-running the existing tests after Phase 1.
2. **Test churn volume** — ~56 test sites are a lot of mechanical edits. Consider a single sed-style migration over a manual edit if signatures are uniform.
3. **F-A-012 reference** — The marker references ticket F-A-012. Likely an older internal tracker. Once the wrappers are deleted, the F-A-012 reference disappears with them; no follow-up doc change needed.

### Opportunities Discovered
- The wrapper pattern is anti-Pattern-#36 (re-export shim with active migration plan) — there is no project tracking F-A-012, so this is a "deprecated but unowned" item. Removing it eliminates the deprecation drift.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
