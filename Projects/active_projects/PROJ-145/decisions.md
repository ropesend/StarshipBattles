# PROJ-145: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project created from review | Review identified 145 findings; 21 selected for remediation |
| 2026-02-13 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-14 | CON-FND-001: INTENTIONAL DESIGN | `get_default_registry_provider()` factory function is intentionally different from `SingletonMeta` - provides DI interface (PROJ-27), wraps existing singleton, offers testing flexibility |
| 2026-02-14 | DUP-FND-001: INTENTIONAL DESIGN | `Profiler.clear()` vs `SingletonMeta.reset()` serve different purposes: `clear()` preserves instance, clears data; `reset()` destroys instance entirely. Both needed for test isolation |
| 2026-02-14 | DUP-FND-003: INTENTIONAL DESIGN | `load_resources_data()` manual exception handling is domain-specific: requires path resolution, data transformation, domain-specific defaults (_get_default_resources), context-specific error messages. Not generic JSON loading |
| 2026-02-14 | CON-SIM-003: ALREADY COMPLIANT | No reST-style docstrings in simulation module. Google style is standard throughout with good `Raises:` coverage (23 sections) |
| 2026-02-14 | CON-SIM-005: INTENTIONAL DESIGN | Ability naming: Registry keys shorter for JSON clarity, class names semantic (weapons=*Ability suffix, passives=noun form) |
| 2026-02-14 | DUP-SIM-001/002/003: INTENTIONAL DESIGN | Ability boilerplate (__init__, sync_data, recalculate) is explicit by design. STAT_BINDINGS are for introspection, not auto-application. Maintains flexibility, debugging clarity |
| 2026-02-14 | DUP-SIM-004: INTENTIONAL DESIGN | Battle state serialization explicit for save/load safety: type conversion, nested objects, backward compatibility |
| 2026-02-14 | DUP-SIM-008: INTENTIONAL DESIGN | Weapon formula handling contained in single class, weapon-specific feature |
| 2026-02-14 | DUP-SIM-011/012: POSITIVE | Helper class pattern (PROJ-44/88) and combat subsystem decomposition commended as good architecture |
| 2026-02-14 | DUP-STR-001: INTENTIONAL DESIGN | Facility component iteration explicit in 6 locations. Each engine is self-contained with specific ability needs. iterate_design_components() exists for ships; facility-specific helpers would add coupling |
| 2026-02-14 | DUP-STR-003: INTENTIONAL DESIGN | Resource cost calculation in maintenance/production engines has different format handling. Explicit ~15 line iteration clearer than shared abstraction |
| 2026-02-14 | DUP-STR-004: INTENTIONAL DESIGN | SuperweaponValidator.find_ship_with_ability() wraps component_inspector for API stability and module encapsulation. Intentional interface wrapper |
| 2026-02-14 | DUP-STR-005: INTENTIONAL DESIGN | Superweapon ship removal pattern repeated 4 times (~5-7 lines each). Each superweapon has different primary logic. Explicit inline code preferred |
| 2026-02-14 | DUP-STR-006: INTENTIONAL DESIGN | to_dict/from_dict serialization explicit per domain object. Each class has unique fields, type conversion, nested object handling |
| 2026-02-14 | DUP-STR-007: INTENTIONAL DESIGN | "Fleet not found." error message repeated 22+ times is explicit and grep-friendly. No abstraction needed for string constant |
| 2026-02-14 | DUP-STR-010: COVERED BY 3.1 | Same finding as DUP-STR-001 (layer iteration pattern) |
| 2026-02-14 | DUP-STR-011: INTENTIONAL DESIGN | DTO from_X factory methods are unique conversion logic per domain object. Factory method pattern is correct |
| 2026-02-14 | DUP-STR-012: ALREADY CONSOLIDATED | NavigationState.from_fleet() IS the consolidated implementation. Replaced FleetState from fleet_movement.py |
