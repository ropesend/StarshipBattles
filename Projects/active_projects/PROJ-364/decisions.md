# PROJ-364: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Strategy Layer Tech Debt Review finding #5 (P2 — copy-paste superweapon prologue) |
| 2026-05-04 | Renumbered from PROJ-354 to PROJ-364 | Merge-conflict collision on PROJ-351..360 |
| 2026-05-04 | SELF_DESTRUCT stays out of the spec table | No ability check, no stabilizer block, no galaxy mutation. Structural outlier; current code at `order_processor.py:722-724` already separates it. Forcing it into a spec would add a special-case flag for one entry. |
| 2026-05-04 | STELLERATE_STAR `ability_name=None` | The method delegates to `system_destroyer.collect_system_contents()` + `destroy_system()`. Indirection is preserved inside the per-weapon effect closure; the spec documents the absence of a direct ability lookup. |
| 2026-05-04 | Mirror `stabilizer_registry.py` pattern exactly | Frozen dataclass + immutable tuple + `find_*` lookup. Already proven in the codebase. |
| 2026-05-04 | Phase 1 = order-pop matrix + event-payload characterization | Findings/03 identified these as coverage gaps. Refactoring without these tests risks silent payload drift consumed by replay capture. |
| 2026-05-04 | Effect closures live in the same module as the dispatcher | One file, one responsibility (superweapon execution). Avoids creating a six-module micro-architecture. |
| 2026-05-04 | Depend on PROJ-363 landing first | PROJ-363's CommandSpec uses `category='superweapon'`, which PROJ-364 will use to filter the COMMAND_SPECS for spec entries. Not a hard dep — could be reordered if needed — but cleaner with PROJ-363 first. |
