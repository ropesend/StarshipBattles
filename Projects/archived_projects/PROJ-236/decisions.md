# PROJ-236: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Project initialized | Starting point for Extract Magic Numbers from stars.py and planet_gen.py |
| 2026-03-28 | Partial table-driven refactor (Stefan-Boltzmann group only), NOT full table-driven | Risk assessment showed 8 star type branches are structurally diverse. MAIN_SEQUENCE (52.5%) should remain explicit. Only RED_GIANT, BROWN_DWARF, WHITE_DWARF share identical Stefan-Boltzmann formula — extract those 3 into a helper with a parameter table. Reduces LOC by ~15-20 without sacrificing readability. Full table-driven was rated HIGH risk. |
| 2026-03-28 | Physics constants (Kelvin-to-RGB, Wien's law, wavelengths) stay as named module-level constants, NOT in JSON | These are published physics/math constants, not gameplay tuning parameters. JSON externalization would suggest they're configurable when they shouldn't be. |
| 2026-03-28 | Tunable generation parameters go in JSON-backed config classes | Follows established `ClassificationConfig` / `ResourceGenerationConfig` pattern. Star type weights, mass bounds, orbital parameters, moon thresholds are all game balance values. |
| 2026-03-28 | New configs placed in `game/strategy/data/` (not a subpackage) | Existing configs are flat in this directory. No `configs/` subpackage exists. Pattern consistency. |
| 2026-03-28 | Chthonian stripping values added to existing ClassificationConfig (not a new file) | They are classification thresholds in the same domain. Avoids proliferating config files. |
| 2026-03-28 | `_RAMP_C` moved to ResourceGenerationConfig | It's a calibration constant for resource scaling, already loaded from astrophysics.json. Belongs with other resource generation parameters. |
| 2026-03-28 | Unbounded while-True in `_generate_mass` gets iteration cap with log-space fallback | Matches existing pattern in `_generate_mass_constrained` (line 698-704). Cap at 1000 iterations, fallback to uniform distribution in log space. |
| 2026-03-28 | AstrophysicsLoader gets new required sections | Per project migration policy, no backward-compat shims for old JSON files. |
