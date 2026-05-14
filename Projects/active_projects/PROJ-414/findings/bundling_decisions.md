# Bundling Decisions — 2026-05-13 legacy audit run

This record is identical across all 9 sibling projects (PROJ-413 … PROJ-421)
so any one of them shows the full Phase D narrative.

## Default Proposal (computed in Phase D Step 1)

| # | Title                                                                              | Cluster                       | Verified  |
|---|------------------------------------------------------------------------------------|-------------------------------|-----------|
| 1 | Legacy removal — stars.py + galaxy.py re-export shims                              | stars_galaxy_reexports        | 2 (+1 dup)|
| 2 | Legacy removal — pathfinding.py shim (PROJ-376)                                    | pathfinding_shim              | 1         |
| 3 | Legacy removal — planet.py re-exports (PROJ-210/284 vestige)                       | planet_reexports              | 1         |
| 4 | Legacy removal — race_setup_screen.py shim + Game.running (PROJ-309 vestige)       | proj309_vestige               | 2         |
| 5 | Legacy removal — test_run_details.py shim                                          | test_run_details_shim         | 1         |
| 6 | Legacy removal — to_roman wrapper                                                  | to_roman_wrapper              | 1         |
| 7 | Legacy removal — light cleanup of stale comments and dead imports                  | light_cleanup                 | 5         |
| 8 | Legacy removal — lazy-init registry cache consolidation                            | lazy_cache_consolidation      | 1         |

UNCERTAIN bucket (1): LEG-02-001 (Pattern #30 slot cleanup) — audit's "8 non-modal" claim fabricated.
INFO bucket (7): MIN-03-007, LEG-01-002, LEG-01-004, LEG-01-005, LEG-01-006, MIN-03-003, MIN-004.


## User Adjustments (Phase D)

- **Bundling shape:** User selected "8 projects (strict per-cluster)" — keep each
  removal cluster as its own project rather than merging shim cleanups.
- **LEG-02-001 (UNCERTAIN):** User chose **Include — frame as 'remove redundant
  slot-nulls'**. Verifier had found the audit's "8 non-modal slots" claim was
  fabricated (all 9 slots are StrategyModalWindow subclasses) but the underlying
  observation that slot-nulls are redundant with Pattern #31 deregistration is
  valid. Project PROJ-421 frames the work as the latter, not as the audit's
  original framing. This added a 9th project to the strict-per-cluster default.
- **INFO items (7):** User chose **Exclude all 7** — they are scanner false
  positives explicitly confirmed not legacy by the original audit reviewers.
  Excluded items are recorded in `verification_report.md` and fed back via the
  refinement-feedback channel as a signal of over-eager INFO classification.


## Final Bundle Definitions (9 projects)

| # | Project ID | Title                                                                                       | Cluster                       | Items                                                            |
|---|------------|---------------------------------------------------------------------------------------------|-------------------------------|------------------------------------------------------------------|
| 1 | PROJ-413   | Legacy removal — stars.py + galaxy.py re-export shims (2026-05-13)                          | stars_galaxy_reexports        | LEG-02-002, MIN-03-006 (MIN-03-005 merged as dup)                |
| 2 | PROJ-414   | Legacy removal — pathfinding.py shim (PROJ-376) (2026-05-13)                                | pathfinding_shim              | MAJ-001                                                          |
| 3 | PROJ-415   | Legacy removal — planet.py re-exports (PROJ-210/284 vestige) (2026-05-13)                   | planet_reexports              | LEG-02-003                                                       |
| 4 | PROJ-416   | Legacy removal — race_setup_screen.py shim + Game.running (PROJ-309 vestige) (2026-05-13)   | proj309_vestige               | MIN-002, MIN-001                                                 |
| 5 | PROJ-417   | Legacy removal — test_run_details.py shim (2026-05-13)                                      | test_run_details_shim         | MIN-003                                                          |
| 6 | PROJ-418   | Legacy removal — to_roman wrapper (2026-05-13)                                              | to_roman_wrapper              | LEG-01-003                                                       |
| 7 | PROJ-419   | Legacy removal — light cleanup of stale comments and dead imports (2026-05-13)              | light_cleanup                 | LEG-01-001, MIN-03-001, MIN-03-002, LEG-02-005, MIN-03-004       |
| 8 | PROJ-420   | Legacy removal — lazy-init registry cache consolidation (2026-05-13)                        | lazy_cache_consolidation      | LEG-02-004                                                       |
| 9 | PROJ-421   | Legacy removal — Pattern #30 slot cleanup in strategy_event_router (2026-05-13)             | pattern30_slot_cleanup        | LEG-02-001 (user-included from UNCERTAIN)                        |


## UNCERTAIN Item Resolution (Phase D Step 3)

| ID         | Bundle    | Question                                                                                                                                          | Decision           |
|------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| LEG-02-001 | PROJ-421  | Audit claimed 8 non-modal slots; verifier confirmed all 9 ARE StrategyModalWindow subclasses. Remove slot-nulls as redundant with Pattern #31?    | Include in PROJ-421 |


## INFO Item Resolution (Phase D Step 4)

| ID         | Verifier Note                                                                                              | Decision    |
|------------|------------------------------------------------------------------------------------------------------------|-------------|
| MIN-03-007 | image/__init__.py:37 — provider-registration side-effect import; intentional Pattern #4 (Registry).        | Exclude     |
| LEG-01-002 | dialogs.py:256 — `# Old value (strikethrough)` is a UI rendering label, not a deprecation marker.          | Exclude     |
| LEG-01-004 | superweapon_order_processor.py:343 — `_get_system_at_hex` is documented test-patch surface (Pattern #5).   | Exclude     |
| LEG-01-005 | effect_ability_metadata.py:150 — `find_metadata()` is the canonical public accessor over private index.    | Exclude     |
| LEG-01-006 | ModifierManager vs ModifierService — zero behavioural overlap; coincidental naming similarity.             | Exclude     |
| MIN-03-003 | component_constants.py:45 — `create_modifier` is an idiomatic factory method on the definition class.      | Exclude     |
| MIN-004    | Shard 04 wrapper-delegate detections — documented Pattern #5 Facade/Delegate intentional delegation.       | Exclude     |


## Final Confirmation

User accepted the 9-project bundle on 2026-05-13. Project creation proceeded
immediately afterward via `Projects/scripts/create_project.py` invoked once
per cluster.
