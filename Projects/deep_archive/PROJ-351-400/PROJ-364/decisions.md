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

## Audit Remediation (2026-05-05)

OpenCode review `req_20260505_070825_e838b1` raised 0 CRIT and 2 MAJ findings against the PROJ-364 refactor. Both were addressed in commit `fix(PROJ-364): audit remediation`.

| Finding | Severity | Verdict | Action |
|---------|----------|---------|--------|
| MAJ-001 — `DYSON_SPHERE_CREATED` event missing `planet_id` / `planet_name` | MAJ | Fix | Added `planet_id=dyson.id` and `planet_name=dyson.name` to the event kwargs returned by `process_create_dyson_sphere._effect` (`superweapon_order_processor.py:651-657`). The kwargs flow through `**event_kwargs` into `_finalize_superweapon.log_event(...)`. Updated `TestDysonSphereCreatedPayload.test_payload_keys` to assert both keys, mirroring the pattern already used by `TestPlanetImplodedPayload`. |
| MAJ-002 — `process_*` methods exceed the aspirational ≤30 LOC target | MAJ (acceptable) | Defer / accept | Reviewer flagged this as "acceptable — justified": the bulk is per-weapon `_effect` and `_precheck` closures whose extraction would require 7+ argument signatures and contradict decision row 11 (single-file responsibility). No code change. If the 500-line module ceiling becomes pressing, the three longest closures (`open_warp_point`, `close_warp_point`, `create_dyson_sphere`) are the natural candidates for extraction to private `_effect_for_*` methods. Tracked here so the deferral is explicit. |

MIN/INFO findings (precheck_fn doc, `empires=None` default cosmetic, stale docstring project number, logger import placement) are out of scope for this remediation.
