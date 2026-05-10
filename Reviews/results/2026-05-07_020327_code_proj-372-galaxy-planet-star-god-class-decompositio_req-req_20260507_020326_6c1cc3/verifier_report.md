# PROJ-372 Verifier Report

**Reviewer:** independent verifier
**Source review:** `report.md` in this directory
**Verified at:** 2026-05-07
**Method:** read every cited file/range; cross-check claims against project decisions, plan, and AST guard.

---

## Verdicts

| Finding | Severity | Verdict |
|---|---|---|
| MAJ-001 | MAJOR | CONFIRM |
| MAJ-002 | MAJOR | CONFIRM |
| MAJ-003 | MAJOR | REJECT |
| MIN-001 | MINOR | CONFIRM |
| MIN-002 | MINOR | CONFIRM_REMEDIATION_REVISE |
| MIN-003 | MINOR | CONFIRM_REMEDIATION_REVISE |
| MIN-004 | MINOR | CONFIRM_REMEDIATION_REVISE |
| INFO-001 | INFO | CONFIRM (with minor caveat — see below) |
| INFO-002 | INFO | CONFIRM |
| INFO-003 | INFO | CONFIRM (spot-checked) |
| INFO-004 | INFO | CONFIRM |
| INFO-005 | INFO | CONFIRM |
| INFO-006 | INFO | CONFIRM (spot-checked) |
| INFO-007 | INFO | CONFIRM (spot-checked) |

**Counts:** 0 CRIT, 2 MAJ confirmed, 1 MAJ rejected, 1 MIN confirmed, 3 MIN confirmed-with-revised-remediation, 7 INFO confirmed.

---

## MAJOR

### MAJ-001 — Save round-trip is synthetic-only — **CONFIRM**

Read `tests/integration/strategy/test_save_round_trip.py:1-99`. All five round-trip tests (`test_round_trip_empty_galaxy`, `_single_system_with_planet`, `_5_system_synthetic_with_warp`, `_10_systems_with_planets`, `_20_systems_planets_warp`) build galaxies in-memory via `Galaxy(radius=N)` + `generate_systems(...)` + a manually-built planet. None loads a checked-in fixture.

Per-phase tests (`test_save_round_trip_phase{1..4}.py`) exist but are all synthetic too (verified phase4: lines 13-28 generate via `Galaxy(...)`+`generate_systems`+`generate_warp_lanes`). They are explicitly described as boundary checks in their docstrings.

Searched `tests/integration/save_load/**/*.json` and `tests/**/fixtures/**/*.json` — no checked-in save fixture exists.

OpenCode's golden-file remediation is appropriate. A stronger guard would be checking in a single binary save produced from a pre-PROJ-372 commit (or capturing an `.json` snapshot now and re-checking on every refactor). Either approach catches cumulative format drift across PROJ-368 → PROJ-372.

### MAJ-002 — `Galaxy.from_dict` duplicates `add_system` — **CONFIRM**

Read `galaxy.py:316-350` and compared to `galaxy_entity_registry.py:40-45`.

`from_dict` lines 340-345:
```
galaxy._state.systems[coord] = system
galaxy._state.name_map[system.name] = system
galaxy._registry._register_zones_from_system(system)
galaxy._registry._rebuild_warp_point_index_for(system)
```

`GalaxyEntityRegistry.add_system(system)` lines 40-45:
```
self._state.systems[system.global_location] = system
self._state.name_map[system.name] = system
self._register_zones_from_system(system)
self._rebuild_warp_point_index_for(system)
```

These are byte-for-byte equivalent (the `coord` from serde is restored into `system.global_location` by `StarSystem.from_dict` at `star_system.py:134`). The duplication is real; `from_dict` reaches into private members `_register_zones_from_system` / `_rebuild_warp_point_index_for`.

The proposed remediation (`galaxy._registry.add_system(system)`) is safe — `add_system` performs no side effects beyond the four lines (no event emission, no logging, no validation). Adding it preserves behavior.

Caveat the parent should know: `from_dict` does NOT call `register_planet`/`restore_planet` from inside `add_system` — those are called separately on lines 347-348 (with explicit `restore_planet` for ID-preserving deserialization). So replacing with `add_system` is correctly the system-level call only; planets continue via `restore_planet`.

### MAJ-003 — `tectonic_activity` spelling mismatch — **REJECT**

OpenCode claims the field name is "missing the 'c'" and is a "misspelling of 'tectonic'". This is wrong.

`game/strategy/data/planet.py:68`: `tectonic_activity: float`
`game/strategy/data/planet_serde.py:44`: `"tectonic_activity": planet.tectonic_activity`

The word "tectonic" is spelled t-e-c-t-o-n-i-c. The field name `tectonic_activity` is **correctly spelled**. There is no missing 'c', no misspelling. The 115 files that reference `tectonic` all use the same correct spelling.

This finding appears to be a model hallucination. Reject and ignore. No action required.

---

## MINOR

### MIN-001 — `galaxy._intercept` is dead code — **CONFIRM**

Read `galaxy.py:66`: `self._intercept = InterceptCalculator(self._pathfinder)`.

Searched `_intercept\b` across `game/`. Only two references: the construction itself, and a docstring comment in `pathfinding.py:6`. No production reader.

`pathfinding.py:60-67` `_intercept_for(galaxy)` always wraps `_pathfinder_for(galaxy)` in a fresh `InterceptCalculator` — by design, per its own docstring ("Always constructs a fresh calculator so test patches of the shim free functions ... flow through to the calculator's pathfinding calls"). So even if `galaxy._intercept` were used, test-patch transparency would break.

**Recommended fix:** delete `self._intercept = InterceptCalculator(self._pathfinder)` and update the `pathfinding.py:6` docstring to drop the `_intercept` mention. Do NOT route the shim to use `galaxy._intercept` — that would defeat test-patch transparency.

### MIN-002 — Pathfinding shim migration not complete — **CONFIRM_REMEDIATION_REVISE**

Confirmed shim still present in `game/strategy/data/pathfinding.py`. Searched `from game\.strategy\.data\.pathfinding import|from game\.strategy\.data import pathfinding` — found exactly 14 production import sites matching OpenCode's list. Spot-checked three (`game_session.py:321`, `fleet_navigation_service.py:36`, `intercept_calculator.py:121`) — all real, all import the shim.

`decisions.md` row "Pathfinding shims ... **Deleted at Phase 5 close**" sets the contract. The plan said Phase 5 close was the sweep. Phase 5 closed without it. This is a Phase 5 leftover, not deferred work.

**Remediation revision:** OpenCode suggests "complete the migration as Phase 5 closeout work, OR file a follow-up project". Given the shim is "functional and correct in the interim", the lower-cost option is to either (a) extend the project's "Recent Work" log with an honest note "Phase 5 left shim cleanup unfinished; tracked as follow-up", and either complete now or file PROJ-376. Don't claim Phase 5 fully landed.

### MIN-003 — `IStockpileHolder`/`IStagingYardHolder` naming — **CONFIRM_REMEDIATION_REVISE**

Read `galaxy_protocols.py:1-23, 124-176`.

Module docstring line 1: "Read protocols". But the class docstrings explicitly self-correct: "Read+write surface for planet-side resource stockpiles" (line 126) / "Read+write surface for planet-side staging-yard storage" (line 153). The module docstring is internally inconsistent — its first line claims pure read, but `IStockpileHolder` and `IStagingYardHolder` declare themselves as Read+write.

**Remediation revision:** the smaller, lower-churn fix is to update the **module docstring** to acknowledge that two of the five protocols are Read+write surfaces. The classes themselves already state this. Renaming to `IStockpileAccessor`/`IStagingYardAccessor` is more invasive and adds churn for marginal benefit. Defer the rename to PROJ-370 if PROJ-370 wants to consolidate writes there.

### MIN-004 — `remove_warp_link` directly mutates state — **CONFIRM_REMEDIATION_REVISE**

Read `galaxy.py:210-233`. Confirmed direct mutation of `self._state.global_hex_warp_points` and `system.warp_points`.

OpenCode's claim that "preserved as-is per Decision" is documented — partially correct. The rationale is in the **AST guard test allow-list** (`tests/unit/strategy/data/test_no_method_body_over_5_loc.py:22` — comment: `"remove_warp_link",  # Two-system warp removal — preserved as-is per Decision; not algorithmic enough to extract for marginal gain.`), but **NOT** in `Projects/active_projects/PROJ-372/decisions.md`.

Worse, `decisions.md`, `plan.md:118`, `manifest.md:56`, `design.md:48,219,298`, and `findings/initial_review.md:17` ALL explicitly call for `remove_warp_link` to be moved to `GalaxyWarpGenerator` / `WarpLinkService`. The plan said move; the implementation kept it; the rationale to keep it appears only in the test allow-list comment with no mention in decisions.md. This is a documentation drift, not a code bug.

**Remediation revision:** OpenCode says "Acceptable as-is". Stronger ask: either (a) actually do the move (Phase 5 leftover, ~10 LOC), or (b) add a row to `decisions.md` explaining the deviation from plan — so future agents don't re-read plan.md and try to "fix" it.

---

## INFO findings (spot-checked)

- **INFO-001 (round-trip field coverage):** counted serialized keys in `planet_to_dict` (lines 32-79): 42 top-level keys. Report claim "47 fields" is approximate and likely counts populations sub-fields (race_id, count, happiness) and intrinsic_abilities/species_configs nested entries separately. Substantive claim "all dataclass fields are serialized" verified — no silently-dropped field. **CONFIRM** with the caveat that the exact "47" number is loose; nothing missing.
- **INFO-002 (facade thinness):** spot-checked `Galaxy.register_planet:158-160` (1-line delegation), `Galaxy.get_system_at_location:235-237` (1-line delegation), `Galaxy.get_all_fleets_in_system:239-241` (1-line delegation). **CONFIRM**.
- **INFO-005 (PROJ-370 protocol integration):** read `PlanetQueryService` (`game/strategy/services/planet_query_service.py`) — all four methods are static, take Planet, return derived value, never mutate. Read `IPlanetMutator` (`game/core/protocols/strategy_mutators.py:77-106`) — has `set_max_stockpile`/`add_staging_item`/`pop_staging_item`. Surface differs from `IStockpileHolder`/`IStagingYardHolder` (per-item add/consume/remove vs batch set/pop). No method-name collision. **CONFIRM**.
- INFO-003, INFO-004, INFO-006, INFO-007 — sampled via the cited line-ranges; consistent with their claims; no red flags.

---

## Recommended actions for Claude

| Action | Severity | Effort | Recommendation |
|---|---|---|---|
| Add a checked-in golden-save round-trip test (or pre-PROJ-372 fixture replay) | MAJ-001 | 30-60 min | **Do now** — protects every future serialization touch |
| Replace `from_dict` system-registration block with `galaxy._registry.add_system(system)` | MAJ-002 | 5 min | **Do now** — pure cleanup, eliminates duplicated logic |
| Ignore MAJ-003 entirely | (rejected) | n/a | OpenCode hallucinated a misspelling that doesn't exist |
| Delete `self._intercept` line in `Galaxy.__init__` and clean the `pathfinding.py` docstring mention | MIN-001 | 2 min | **Do now** — pure dead-code removal |
| Decide pathfinding shim cleanup: complete sweep now (~30 min, mechanical) or file PROJ-376 | MIN-002 | 30 min OR 5 min to file ticket | **File PROJ-376** if you'd rather not interleave; otherwise sweep now |
| Update `galaxy_protocols.py` module docstring to acknowledge two Read+write protocols | MIN-003 | 2 min | **Do now** — defer renames to PROJ-370 |
| Either move `remove_warp_link` to `GalaxyWarpGenerator` (per plan) OR add a `decisions.md` row explaining the deviation | MIN-004 | 5 min (either way) | **Add decisions.md row now**; leave the move for a future ticket if desired |

The decomposition is sound. None of the issues block PROJ-372 closeout, but MAJ-001 is a real future-regression risk and MAJ-002 is a maintainability cliff that's worth closing in the same touch.
