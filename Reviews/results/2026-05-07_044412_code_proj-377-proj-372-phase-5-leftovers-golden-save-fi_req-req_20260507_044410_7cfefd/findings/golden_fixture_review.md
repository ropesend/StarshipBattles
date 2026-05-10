# Findings: Golden Fixture + Capture Script

## FND-FIX-001 [INFO]: _normalize_image_fields placeholders survive round-trip

The `_normalize_image_fields` function replaces `image_id` with `f"_fixture_planet_{planet.id}.png"` and `image_rotation` with `0.0`. Both are plain str/float fields in `planet_to_dict()` — `from_dict` restores them verbatim, and `to_dict` serializes them back unchanged. Round-trip identity is preserved.

## FND-FIX-002 [INFO]: Storms are stripped for known pre-existing drift

`_strip_storms()` mirrors the `test_save_round_trip.py` synthetic tests. `Storm.to_dict()/from_dict()` drift is documented and out of PROJ-372 scope. The capture script's approach is consistent with the existing test design.

## FND-FIX-003 [INFO]: Decorated planet exercises key serialization fields but not all 42 serialized fields

The `capture_populated()` function manually sets on one planet:
- `owner_id`, `atmosphere`, `atmosphere_target` (dict)
- `deposits` (nested dict), `stockpile`, `max_stockpile` (dict)
- `populations` (list of SpeciesPopulation)
- `intrinsic_abilities` (dict)

Not exercised (remain at defaults for synthetic planets):
- `construction_queue`, `staging_yard`, `max_staging_mass`, `facilities`
- `energy`, `energy_capacity`, `energy_generation`
- `gravity_target`, `water_target`, `radiation_shielding`, `radiation_shielding_target`
- `orders`, `species_configs`

This is acceptable — the fixture's purpose is structural drift detection, and the other 5 synthetic round-trip tests exercise the default-value paths. The decorated planet adds coverage for the fields that synthetic generation most often leaves at default.

## FND-FIX-004 [INFO]: Capture idempotence trade-off correctly documented

The `_capture_baseline.py` docstring (lines 9-23) accurately explains:
- What is seeded: system placement, names, planet body shapes, intrinsic abilities
- What is normalized: planet image_id / image_rotation
- What remains unseeded: star-image selection, warp-point type rolls, warp-point intrinsic abilities
- The CI contract: round-trip identity assertion, NOT byte-equality between captures

The decisions.md row 2026-05-07 provides additional rationale: threading rngs through every call site touches PROJ-301/302/304 production code (out of scope).

Potential improvement (not blocking): the `random.seed(2)` before `Galaxy()` construction and `random.seed(2)` after it ("indeterminate amount consumed") is a brittle pattern. If `Galaxy.__init__` gains a random call that doesn't consume an integer number of random states, the double-seed trick could produce different results.

## FND-FIX-005 [MIN]: Double-seed Galaxy init pattern is fragile

In `capture_baseline()`:
```python
random.seed(2)
galaxy = Galaxy(radius=30)
random.seed(2)  # Galaxy.__init__ may have consumed an indeterminate amount
galaxy.generate_systems(5, min_dist=5, rng=random.Random(2))
```

The re-seed at line 67 is a workaround for `Galaxy.__init__` consuming an unknown number of global `random` calls. If `Galaxy.__init__` ever adds an internal `Random` instance (using an independent `random.Random()`), the global `random.seed(2)` re-seed would not affect it. This is a latent fragility that could silently produce different galaxies. Consider pinning the systems to a known-valid checked-in fixture and switching to load-only mode as the primary CI path, with the capture script as a developer convenience only.
