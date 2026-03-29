# PROJ-236: Extract Magic Numbers from stars.py and planet_gen.py

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-236` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-236 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Star Generation Config + Constants | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Orbital Generation Config | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Classification + Resource Config Additions | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final Verification | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-03-28 23:00
**Active Phase:** Complete — all 4 phases done
**Last Action:** All phases implemented. Full test suite: 13926 passed (22 new tests), 17 pre-existing failures (unchanged). Zero new failures.
**Next Action:** User verification / audit
**Blockers:** None
**Context for Next Agent:** Project implementation complete. stars.py is 759 lines (above 500 target due to 22 named constants + SB helper; could be split in a future project). planet_gen.py is 602 lines (essentially unchanged LOC — magic numbers replaced by config refs). Pre-existing DYSON_SPHERE test failure in test_planet_classification_logic.py is not related to this project.

## Overview

`stars.py` (705 lines) and `planet_gen.py` (600 lines) contain the densest concentration of magic numbers in the strategy layer — 117+ in stars.py and 50+ in planet_gen.py. This project extracts all magic numbers into named constants or JSON-backed config classes, following the established `ClassificationConfig` / `ResourceGenerationConfig` pattern.

## Goals
- Replace all bare numeric literals with named constants or config references
- Extract star type properties into a data table for the 3 Stefan-Boltzmann types
- Name physics constants (Kelvin-to-RGB, spectrum wavelengths) with citations
- Fix unbounded `while True` loop in `_generate_mass` (add iteration cap)
- Add missing chthonian stripping thresholds to ClassificationConfig
- Move `_RAMP_C` to ResourceGenerationConfig

## Scope
**In:** `stars.py`, `planet_gen.py`, new config files, updates to existing configs, `astrophysics.json`, `AstrophysicsLoader`, new tests
**Out:** Public API changes to `Star`/`Spectrum`/`StarType`/`Planet`/`PlanetType`, other strategy layer files, UI code

## Key Files
| Component | File Path |
|-----------|-----------|
| Star generator | `game/strategy/data/stars.py` |
| Planet generator | `game/strategy/data/planet_gen.py` |
| Classification config (reference) | `game/strategy/data/classification_config.py` |
| Resource gen config (reference) | `game/strategy/data/resource_generation_config.py` |
| Astrophysics JSON | `data/astrophysics.json` |
| Astrophysics loader | `game/strategy/generation/loaders/astrophysics_loader.py` |
| Star tests | `tests/unit/strategy/data/test_stars.py` |
| Planet gen tests | `tests/unit/strategy/data/test_planet_gen.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis, swarm findings, risk assessment
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline: 13904 passed)
- [ ] No remaining bare magic numbers in target files
- [ ] File sizes within convention (~500 lines)
- [ ] Audit passed
- [ ] User verified
