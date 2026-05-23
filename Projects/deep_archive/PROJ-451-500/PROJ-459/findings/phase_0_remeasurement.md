# PROJ-459 Phase 0 — Re-measurement Findings

> Date: 2026-05-19
> Branch: `group-a` (post PROJ-449 + PROJ-451 merges to `main`)

## 1. Dependency status

- **PROJ-449** merged into `main` at SHA `ebb5c0e7f` ("Merge group-a through PROJ-449 (end of project)") — wrapper retirement + setter cluster deletion shipped. **Hard gate for Phase 3 — SATISFIED.**
- **PROJ-451** merged into `main` at SHA `893482c04` ("Merge group-a through PROJ-451 (end of project)") — production resource-consumption semantics shipped. **Hard gate for Phases 1+2+3 — SATISFIED.**
- **PROJ-454** (Group B) merged into `main` at SHA `ab2da0669` (component_inspector retirement + `Fleet`-side production trim). Read on `origin/main` to inform the Phase 3 verdict per the prompt's cross-group dependency note.
- **PROJ-456** (Group B) merged into `main` at SHA `244c1fa16` (UI build-queue shim retirements). Not a Phase-0 dependency; recorded for completeness.

Group A is unblocked on all PROJ-459 phases.

## 2. Re-measurement table

| File | Baseline (2026-05-19 pre-Group-A) | Current (post merges) | Delta | Notes |
|------|------------------------------------|------------------------|-------|-------|
| `game/strategy/data/fleet.py` | 686 | 693 | +7 | PROJ-451 Phase 2 Task 2.0 rounded the consume-side gate; added a comment block referencing DI-006 + codex r5 review. |
| `game/strategy/data/planet_gen.py` | 610 | 610 | 0 | Untouched by PROJ-449/451/454. |
| `game/strategy/data/ship_instance.py` | 839 | 789 | −50 | PROJ-449 deleted the wrapper + 2 setters; replaced the property pair docstrings with the read-only-view framing. PROJ-454 trimmed the `component_inspector` import (small further shrink). PROJ-449 internal measurement reported 783 LOC; the 6-LOC delta is the audit-driven docstring restoration. |

Both Phase 1's extraction target (fleet.py) and Phase 3's measurement target (ship_instance.py) are stable. planet_gen.py is unchanged.

## 3. Phase 1 extraction surface confirmation

`game/strategy/data/fleet.py`:

- `Fleet.to_dict` at line **527** (was at 520 in the 2026-05-19 baseline; shifted +7 because of the PROJ-451 Task 2.0 hunk).
- `Fleet.from_dict` at line **565** (was at 558).
- `Fleet.resolve_order_references` at line **664** (was at 657).

All three targets exist; the +7 shift is the Phase 2 Task 2.0 expansion of `consume_cargo_resource`, which sits above `to_dict` in the file. The relative spacing of the three methods is unchanged. Phase 1's plan target ("extract ~140 LOC") still holds — re-measuring the actual span: `:527` to `:660`+ is roughly **133-140 LOC** of `to_dict` + `from_dict` body. Goal: drop fleet.py to ~553 LOC (still slightly over 500 but tractable next-touch).

## 4. Phase 2 split candidates in planet_gen.py

13 methods in one class (`PlanetGenerator`):

| Line | Method | Bucket |
|------|--------|--------|
| 40 | `__init__` | infra |
| 48 | `generate_system_bodies` | top-level orchestration |
| 95 | `_generate_orbital_slots` | orbital arrangement |
| 186 | `_collect_star_exclusion_zones` | orbital arrangement |
| 205 | `_generate_mass_constrained` | body construction (mass) |
| 246 | `_generate_moons` | moon generation |
| 283 | `_calculate_moon_chance` | moon generation |
| 317 | `_generate_moon_mass` | moon generation |
| 336 | `_create_planet_objects` | body construction |
| 363 | `_create_single_planet` | body construction |
| 425 | `_generate_surface_flags` | surface-type-resource |
| 453 | `_determine_type` | surface-type-resource |
| 541 | `_generate_resources` | surface-type-resource |

Two clean axes emerge from inspection:

1. **Moon generation** — `_generate_moons` + `_calculate_moon_chance` + `_generate_moon_mass` (lines 246-335, ≈90 LOC) splits cleanly to `planet_gen_moons.py`. These methods share no `self.*` state beyond `self._image_registry` (which can be passed as a parameter).
2. **Surface-type-resource cluster** — `_generate_surface_flags` + `_determine_type` + `_generate_resources` (lines 425-end, ≈170 LOC) splits to `planet_gen_surface.py`. Same lightweight `self` coupling.

Phase 2 should attempt one of these (probably the surface cluster — bigger LOC payoff). Defer if the methods turn out to share state more deeply than the inspection suggests.

## 5. Phase 3 provisional verdict

`game/strategy/data/ship_instance.py` is at **789 LOC**. The threshold is 500 LOC. Margin: **+289 LOC over ceiling**.

PROJ-449 deleted the wrapper + setters but the file remains heavy with:

- The 5 TD-06 high-value shim entry points (`to_dict`/`from_dict`/`to_json`/`from_json`/`clone`/`to_ship`/`update_from_ship`/`consume_resource`/`get_resource_capacity` etc.) documented in the class docstring at `ship_instance.py:106-125`. Each is a 5-10 LOC method.
- Inline `design_data` D2(a) carry-along (heavy fields + lookup methods).
- Two surviving read-only @property views (`consumable_levels`, `cargo_contents`) that compose with the manager APIs.

**Verdict (per Codex r4 directive "F-A-007 should not be smuggled in as a side quest"): SPINOUT.** Phase 3 records the verdict and scaffolds **PROJ-461 ship_instance.py LOC reduction** as a fresh project. The 910-caller sweep required to retire the TD-06 shims is too large to fold into PROJ-459.

## 6. Gate decision

- Phase 1: PROCEED. Extraction surface stable at ~140 LOC.
- Phase 2: PROCEED. Moon-generation and surface-type-resource clusters are clean split candidates.
- Phase 3: PROCEED with verdict already known — SPINOUT (789 LOC > 500). Final SHA recorded after the merge.

No production code touched.
