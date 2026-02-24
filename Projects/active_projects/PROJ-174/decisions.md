# PROJ-174: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized from review `2026-02-23_185804_focused_registry-consolidation-migration` | Complete DI migration completing PROJ-27/38/50/58 work |
| 2026-02-23 | Keep RegistryManager as internal-only (not in __all__) | Lifecycle management (freeze/clear/hydrate) is valuable. Composition roots need it. But consumers should use IRegistryProvider. |
| 2026-02-23 | Keep GameRegistries (deprecate gradually, out of scope for removal) | Some code passes it as parameter. Full removal would cascade too far. Phase out in future project. |
| 2026-02-23 | Eliminate get_default_registries() from production code | Service locator replaced by get_default_registry_provider(). Mark deprecated with warning. |
| 2026-02-23 | Keep DefaultRegistryProvider and RegistryManager separate | Clean separation of concerns: lifecycle (RM) vs. access (DRP). |
| 2026-02-23 | Add get_resources() to IRegistryProvider | Complete the protocol. All 4 registries (components, modifiers, vehicle_classes, resources) accessible via DI. |
| 2026-02-23 | Defer RegistryManager singleton removal (AR-005) to future project | 180+ call sites. Not blocking. Wait for DI migration to stabilize. |
| 2026-02-23 | Defer GameRegistries frozen=True fix (MOD-CORE-002) to separate PR | Independent issue, 1-line fix, not related to DI migration. |
| 2026-02-23 | Defer frozen state enforcement fix (MOD-CORE-004) to separate PR | Independent issue, orthogonal to access pattern migration. |
| 2026-02-23 | Baseline: 12,023 passed, 1 skipped | Established before planning. |
| 2026-02-23 | Phase order: Protocol -> Internalize -> TIER 2 -> TIER 3 -> Tests | Lowest risk first. Each phase leaves codebase working. Tests last because they depend on production signatures. |
