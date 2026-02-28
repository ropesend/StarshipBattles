# PROJ-178: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized from PROJ-171 audit | Remediate all audit findings for validation consistency |
| 2026-02-24 | RaceConfig.from_dict out of scope | Has separate extensive `validate()` method with 17+ tests; adding require_keys to from_dict is a separate concern |
| 2026-02-24 | DesignMetadata `category` usage is a BUG, not just brittleness | Component class has no `category` attribute; uses `type_str` and `major_classification`. The Ship-based calculation path always returns 0.0 |
| 2026-02-24 | Remove "Old layer format" warnings per System Migration Policy | CLAUDE.md mandates eradicating old systems; old layer formats should not be handled gracefully |
| 2026-02-24 | Use `major_classification` for weapon/armor classification | Components.json uses `"major_classification": "Weapons"` and `"major_classification": "Armor"` — more stable than checking individual type_str values |
| 2026-02-24 | Validate ShipInstance numeric fields only when present in data | Fields use `.get()` with defaults; only validate when explicitly provided (not None) to avoid false positives on missing optional data |
| 2026-02-24 | PlanetaryFacility/SpeciesPopulation get `from_dict` classmethods | Matches pattern used by all other child objects (Fleet, StarSystem, WarpPoint, Star, Spectrum) |
