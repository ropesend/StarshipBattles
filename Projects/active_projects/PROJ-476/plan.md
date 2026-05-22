# PROJ-476: Facade read-path — tooling/editor/sandbox screens (battle_setup, galaxy_test, race_setup, builder, design-editor) exemption codification (follow-on tail of PROJ-472)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-476` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-476 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Re-inventory tooling imports against post-474/475/477 live code + reconcile the plan's triple set | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Add the machine-checkable `_TOOLING_EXEMPTIONS` category to the import guard (TDD) + move tooling residue out of `TAIL` into it | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Document the tooling-exemption policy in Pattern #5 + final guard/doc reconcile + full-suite verification | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Planned (execution-ready), pre-flesh + post-flesh Codex consults complete (live-code verified 2026-05-22).
**Last Action:** Fleshed to execution-ready + revised per post-flesh review
(`AgentCoordination/Scratchpad/Consult/proj476_postflesh/advice.md` — verdict:
ready, 1 in-plan fix, no user-decision blocker). Fixes: (Finding 1) the live
build-queue `compute_planet_production` triples — out of 476, previously unowned
— now have an explicit owning row in PROJ-475 plan.md; (Finding 6) Phase 3
doc/guard tag-parity is now a concrete TDD task, not optional. Pre-flesh consult
(`.../proj476_preflesh/advice.md`) confirmed the
key finding: **there are ZERO `.session` / `._session` / `.facade_state.session`
reads in any of the four tooling dirs** (`battle_setup/`, `galaxy_test/`,
`race_setup/`, `builder/`) — so PROJ-476 is **import-guard-only**, NO
session-read-guard work. The remaining `game.strategy.*` imports in these screens
are NOT live-session reads; they are detached pre-session editors / sandbox
harnesses / pre-session authoring services. Once PROJ-474 promotes the pure
value/enum/static-metadata symbols to `UISAFE`, the residue is a small set of
genuine **tooling exemptions** that should become a first-class, machine-checkable
`_TOOLING_EXEMPTIONS` category (exact `(file, module, member)` triples + a
category tag + reason), replacing the comment-only `TAIL` parking.
**Next Action:** **DO NOT START until PROJ-474, PROJ-475, and PROJ-477 land.**
Then Phase 1 = a fresh re-inventory of the tooling `game.strategy.*` imports
against post-474/475/477 live code (the `TAIL` block will have shrunk; the exact
residue set in this plan is the 2026-05-22 snapshot and MUST be re-verified).
**Blockers:** **GATED on PROJ-474 (UISAFE consolidation) + PROJ-475 + PROJ-477
(live boundary).** Executes LAST so the legitimate tooling exemptions are fully
knowable only after the live boundary is closed. The two read-path guards from
PROJ-472 have landed (verified green 2026-05-22), so the PROJ-472 gate itself is
cleared; the 474/475/477 gate is what remains.

## Overview
Last follow-on of **PROJ-472**, which closed the StrategySessionFacade read-path
gap with two static guards (`test_facade_read_path_imports_guard.py`,
`test_facade_read_path_session_guard.py`) and a documented UI-safe read surface
(Pattern #5, option (b)). PROJ-472 parked the tooling-screen imports in a
comment-labelled `TAIL` block of the import-guard allowlist as a transitional
holding pen for three follow-ons:

- **PROJ-474** — promote the *pure* value/config/enum/static-metadata symbols to
  a machine-checkable `UISAFE` surface.
- **PROJ-475 / PROJ-477** — close the *live* strategy-screen + render read path.
- **PROJ-476 (this project)** — the *tooling/editor/sandbox* screens.

After 474/475/477 land, the only `TAIL` entries left for the tooling screens are
**detached, legitimate, intentionally-outside-the-facade-DTO-boundary** imports:
pre-session editors that construct/mutate config or detached domain objects
(`battle_setup`, `race_setup`), standalone sandbox harnesses that build their own
world (`galaxy_test`), and design-editor metadata/catalog loaders
(`builder/right_panel`, `design_selector_window`, `workshop_event_router`). None
of these reads a live `GameSession`; facade migration is the wrong tool. PROJ-476
**codifies them as a principled, machine-checkable tooling-exemption category**
(not a comment, not a folder waiver) and clears the transitional `TAIL` parking
for those files.

**Honest scope note (do not overclaim).** PROJ-476 does NOT migrate any tooling
screen to the facade and does NOT add a facade DTO surface. There are no
live-session reads here to migrate (verified live 2026-05-22). The deliverable is
turning the comment-only `TAIL` holding pen into an enforced
`_TOOLING_EXEMPTIONS` invariant + a Pattern #5 policy paragraph, so the
exemptions are documented and a net-new tooling import still has to be
classified rather than silently parked.

## Goals
- Make the tooling exemptions a first-class, machine-checkable
  `_TOOLING_EXEMPTIONS` data structure in
  `tests/static_guards/test_facade_read_path_imports_guard.py`: exact
  `(file, module, member) -> (category_tag, reason)` entries, mirroring how
  PROJ-474 makes `UISAFE` machine-checkable. Category tags:
  `prebattle-editor`, `sandbox-harness`, `race-authoring`, `design-editor`.
- Move the genuine tooling residue out of the comment-only `TAIL` block into
  `_TOOLING_EXEMPTIONS`. Keep exact triples — **no blanket subpackage/folder
  waivers** (the tooling dirs mix promotable pure symbols with live imports).
- Add a **no-misfile invariant**: no `(module, member)` in PROJ-474's
  `_UISAFE_SYMBOLS` may also appear in `_TOOLING_EXEMPTIONS`, and no
  `_TOOLING_EXEMPTIONS` triple may also sit in the residual `TAIL`/`CLUSTER`/
  `FLEETCAP` blocks (each import is classified exactly once).
- Document the tooling-exemption policy in Pattern #5 (`docs/02_PATTERNS.md`):
  what qualifies (detached pre-session editor / sandbox harness / authoring
  service / design-editor metadata, NO live `GameSession` read), and that it is
  exact-triple scoped, not a folder waiver.
- Re-verify the exact residue set at execution time against post-474/475/477
  live code (the snapshot below is 2026-05-22 and the `TAIL` block will have
  shrunk).

## Scope
**In:**
- The `_TOOLING_EXEMPTIONS` machine-checkable category + the no-misfile invariant
  test + a positive-control test, all in
  `tests/static_guards/test_facade_read_path_imports_guard.py`.
- Moving the verified tooling residue triples (see "Residue set" below) out of
  `TAIL` into `_TOOLING_EXEMPTIONS`.
- The Pattern #5 tooling-exemption policy paragraph in `docs/02_PATTERNS.md`.
- Pruning any tooling triple whose live import no longer exists post-474/475/477.

**Out:**
- Pure value/config/enum/static-metadata symbol promotion → **PROJ-474** (already
  owns `RaceConfig`, `RacePointBudget`, `FieldStatus`, `PlanetType`, `BattleRole`,
  `CombatPolicy`, `VALID_GALAXY_TYPES`, `StrategicKind`, `abilities_with_kind_tag`,
  `SUPERWEAPONS`). PROJ-476 must NOT re-promote or duplicate these.
- Live strategy-screen / render / `.session` readers + pass-through deprecation →
  **PROJ-475 / PROJ-477**.
- `build_queue_panel_factory.py` (`compute_planet_production`) — live build-queue
  screen, NOT tooling; PROJ-475 owns it (consult §3, verified live 2026-05-22).
- Any session-read-guard work (`test_facade_read_path_session_guard.py`) — the
  tooling dirs have ZERO session reads, so this guard is untouched by PROJ-476.
- Any facade DTO surface expansion or `game/ui/` code motion beyond import-line /
  guard / doc edits.

## Residue set — the tooling-exemption triples (2026-05-22 snapshot; RE-VERIFY at execution)
After PROJ-474 promotes the pure symbols, these are the residual tooling imports
PROJ-476 moves from `TAIL` into `_TOOLING_EXEMPTIONS`. Each is verified to import
a live/generation/authoring symbol (NOT a pure value/enum) and to NOT read a live
session.

**`prebattle-editor`** (battle_setup detached pre-battle fleet editor; holds real
`Fleet`/`ShipInstance`/`TaskForce`/`Squadron` objects, mutates the hierarchy
directly — `battle_setup_state.py:2-4`, `fleet_hierarchy_editor.py:8,26,158`):
```
("game/ui/screens/battle_setup/fleet_hierarchy_editor.py", "game.strategy.data.ship_instance", "ShipInstance")   # :165 runtime local
("game/ui/screens/battle_setup/fleet_hierarchy_editor.py", "game.strategy.data.squadron", "Squadron")            # :18
("game/ui/screens/battle_setup/fleet_hierarchy_editor.py", "game.strategy.data.task_force", "TaskForce")         # :19
("game/ui/screens/battle_setup_state.py", "game.strategy.data.fleet", "Fleet")                                   # :16
("game/ui/screens/battle_setup_state.py", "game.strategy.data.ship_instance", "ShipInstance")                    # :17
```
> `battle_setup_state.py` lives at `screens/` root but IS in PROJ-476 scope: it is
> the model behind the `battle_setup` package, imported by
> `battle_setup/screen.py:32`, `controller.py:33`, `spec_compiler.py:77`.
> `CombatPolicy` (`fleet_hierarchy_editor.py:17`) + `BattleRole`
> (`constants.py:10`, `controller.py:31`) are PROJ-474 UISAFE — NOT here.

**`sandbox-harness`** (galaxy_test standalone galaxy/system inspector; constructs
its OWN `Galaxy`/`StarSystem`, not a scene pass-through — `galaxy_mode.py:1,25`,
`system_mode.py:1,25`):
```
("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.data.galaxy", "Galaxy")                                              # :18
("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.generation.density.density_map", "DensityMap")                       # :260 runtime local
("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.generation.loaders.galaxy_layouts_loader", "GalaxyLayoutsLoader")    # :259 runtime local
("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.generation.placement_strategies", "DensityBasedPlacementStrategy")   # :255 runtime local
("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.generation.placement_strategies", "RandomPlacementStrategy")         # :255 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet", "Planet")                                              # :373 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet_gen", "PlanetGenerator")                                 # :210 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet_physics", "MASS_EARTH")                                  # :408 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet_physics", "calculate_escape_velocity")                   # :408 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet_physics", "calculate_surface_gravity")                   # :408 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.star_system", "StarSystem")                                     # :208 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.stars", "Star")                                                 # :372 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.stars", "StarGenerator")                                        # :209 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.generation.loaders.system_blueprints_loader", "SystemBlueprintsLoader") # :196/:212 runtime local
("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.generation.planet_image_registry", "PlanetImageRegistry")            # :211 runtime local
```
> `PlanetType` (`constants.py:6`, `system_mode.py:21`) + `VALID_GALAXY_TYPES`
> (`galaxy_mode.py:20`) are PROJ-474 UISAFE — NOT here.

**`race-authoring`** (race_setup pre-session authoring tool; `RaceLibrary` =
filesystem race-file orchestration, `RaceRandomizer` = randomizes detached
`RaceConfig`, `RaceCaptionLoader` = caption sidecars,
`RaceDescriptionLLMController` = UI-polled LLM state machine — none traverse a
live `GameSession`):
```
("game/ui/screens/race_setup/controller.py", "game.strategy.systems.race_library", "RaceLibrary")                                  # :20
("game/ui/screens/race_setup/controller.py", "game.strategy.systems.race_randomizer", "RaceRandomizer")                            # :21
("game/ui/screens/race_setup/panel_factory.py", "game.strategy.data.race_caption_loader", "RaceCaptionLoader")                     # :162 runtime local
("game/ui/screens/race_setup/panel_factory.py", "game.strategy.services.race_description_llm_controller", "RaceDescriptionLLMController") # :163 runtime local
("game/ui/screens/race_setup/screen.py", "game.strategy.systems.race_library", "RaceLibrary")                                      # :25
("game/ui/screens/race_setup/screen.py", "game.strategy.systems.race_randomizer", "RaceRandomizer")                               # :28 (test re-export seam — prune if removed)
```
> `RaceConfig`, `RacePointBudget`, `FieldStatus` are PROJ-474 UISAFE — NOT here.

**`design-editor`** (ship-design editor metadata/catalog loaders;
`get_default_design_role_registry` = mutable lazy-loaded base/mod/user overlay,
`DesignCatalog` = design-library browse — both editor-time, neither a UI-safe
immutable symbol nor a live-session read):
```
("game/ui/screens/builder/right_panel.py", "game.strategy.data.design_role_registry", "get_default_design_role_registry")          # :387 runtime local
("game/ui/screens/design_selector_window.py", "game.strategy.data.design_role_registry", "get_default_design_role_registry")        # confirm live
("game/ui/screens/design_selector_window.py", "game.strategy.systems.design_catalog", "DesignCatalog")                              # :21
("game/ui/screens/workshop_event_router.py", "game.strategy.data.design_role_registry", "get_default_design_role_registry")         # :568 runtime local
```
> `StrategicKind`, `abilities_with_kind_tag` (`stat_rows_dynamic.py`),
> `SUPERWEAPONS` (`stat_getters.py`) are PROJ-474 UISAFE — NOT here.
> `design_selector_window.py` / `workshop_event_router.py` are screens-root but
> ARE design-editor tooling per PROJ-474 design.md §"Stay deferred — PROJ-476"
> (`design.md:132-141`). RE-VERIFY their exact triples at execution.

## Key Files
| Component | File Path | Verified refs (2026-05-22) |
|-----------|-----------|----------------------------|
| Import guard + allowlist (TAIL → `_TOOLING_EXEMPTIONS`) | `tests/static_guards/test_facade_read_path_imports_guard.py` | flat set `:66-222`; TAIL block `:118-221`; matcher `:262-314` |
| Session-read guard (UNTOUCHED; zero tooling reads) | `tests/static_guards/test_facade_read_path_session_guard.py` | allowlist `:67-96` (no tooling-dir entries) |
| Read-path + tooling-exemption policy doc | `docs/02_PATTERNS.md` (Pattern #5) | UI-safe prose `:188-199`; add tooling-exemption paragraph |
| PROJ-474 UISAFE structure (no-misfile must cross-check) | `tests/static_guards/test_facade_read_path_imports_guard.py` (`_UISAFE_SYMBOLS`, post-474) | added by PROJ-474 |
| battle_setup editor + state | `game/ui/screens/battle_setup/fleet_hierarchy_editor.py`, `game/ui/screens/battle_setup_state.py` | editor `:17-19,165`; state `:16-17`; "real Fleet objects" `:2-4` |
| galaxy_test sandbox harness | `game/ui/screens/galaxy_test/galaxy_mode.py`, `game/ui/screens/galaxy_test/system_mode.py` | harness docstrings `:1,25` both |
| race_setup authoring | `game/ui/screens/race_setup/controller.py`, `screen.py`, `panel_factory.py` | imports `controller:20-21`, `screen:25-28`, `panel_factory:162-164` |
| design-editor | `game/ui/screens/builder/right_panel.py`, `game/ui/screens/design_selector_window.py`, `game/ui/screens/workshop_event_router.py` | `right_panel:387`, `design_selector:21`, `workshop_event_router:568` |

## Related Documents
- [design.md](design.md) - Classification rationale, structure choice, residue table
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File / conflict map
- Pre-flesh consult: `AgentCoordination/Scratchpad/Consult/proj476_preflesh/advice.md`
- Post-flesh consult: `AgentCoordination/Scratchpad/Consult/proj476_postflesh/advice.md`

## Verification
- [ ] All phase checklists complete
- [ ] `python Tools/test_sharded/test_sharded.py` green (or targeted static-guard
      + affected-tooling-screen runs)
- [ ] `_TOOLING_EXEMPTIONS` is machine-checkable data; positive-control +
      no-misfile invariant tests pass
- [ ] No tooling residue left in the comment-only `TAIL` block; each tooling
      import is classified exactly once (UISAFE | tooling-exemption | live-defer)
- [ ] Pattern #5 documents the tooling-exemption category
- [ ] Both read-path guards green; session-read guard unchanged
- [ ] User verified
