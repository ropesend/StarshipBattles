# PROJ-335 — Decisions

Decisions are append-only. Each entry: ID, date, decision, rationale.

---

## D-001 — Characterization mode (record actual, not desired)

**Date:** 2026-05-04

Tests pin the behavior the code exhibits today, not the behavior we wish it
had. Where `Order.to_dict` produces an asymmetric shape (e.g. the `HexCoord`
branch emits `{q, r}` with no `type` discriminator while every other branch
includes `type`), the test asserts the asymmetry. Quirks are documented in
`design.md` and called out in test docstrings; they are **not** filed as bugs
in this project.

---

## D-002 — Verify prior coverage before writing

**Date:** 2026-05-04

`tests/unit/strategy/data/` already contains several feature-focused test
files (`test_facility_activation.py`, `test_facility_construction_queue.py`,
`test_facility_resource_tracking.py`, `test_population_model.py`,
`test_fleet_hierarchy.py`, `test_superweapon_orders.py`,
`test_fleet_order_resolution.py`). Phase 1 begins by reading each existing
test file end-to-end and listing which behaviors it already pins. New tests
characterize only the **gap**.

If `test_population_model.py::TestSpeciesPopulation` already covers
construction defaults, `from_dict` happy path, and `from_dict` missing-key
rejection, **skip writing a new test file for `species_population.py`** and
record the no-op here as an observation.

---

## D-003 — File naming: `_characterization` suffix

**Date:** 2026-05-04

New test files use `tests/unit/strategy/data/test_<file>_characterization.py`
to disambiguate from existing per-feature test files. This avoids:

- Growing existing files past the 500-LOC ceiling.
- Mixing characterization-style tests with the existing TDD-era tests in the
  same file.
- Reader confusion about which file owns which behavior.

---

## D-004 — Stub Planet/Fleet for `Order.to_dict` matrix

**Date:** 2026-05-04

The 10-branch `Order.to_dict` matrix dispatches on `type(self.target)`, with
branches for `Planet`, `Fleet`, `HexCoord`, `dict`, `list`. To exercise these
without importing real domain objects (and dragging in their dependencies),
the tests use `types.SimpleNamespace(id="p1")`-style stubs. This keeps the
data-layer tests data-layer-only.

---

## D-005 — Real I/O for `GroupPolicyRegistry.load`

**Date:** 2026-05-04

The `load` path uses `load_json` and reads a default file path
(`Paths.GROUP_POLICIES_FILE`). Tests write a temporary JSON file via the
`tmp_path` fixture and pass it as the `file_path` arg, exercising the real
I/O branch. The missing-file fallback (default `{}`) is exercised by passing
a non-existent path within `tmp_path`.

This is preferred over mocking `load_json` because the file format itself
(top-level `targeting` / `movement` / `retreat` keys) is part of what
characterization is pinning.

---

## D-006 — Per-file commit discipline

**Date:** 2026-05-04

Each production-file/test-file pair gets its own commit. Master plan
("Cross-cutting discipline") requires this for the test-coverage arc; it also
keeps reverts surgical if one file's tests later prove brittle.

---

## D-007 — Observed quirks logged, not fixed

**Date:** 2026-05-04

Any apparent bug discovered while writing characterization tests is recorded
here as an observation. A non-exhaustive list of suspects to look for:

- `Order.to_dict` HexCoord branch: missing `type` key in the emitted dict
  (every other branch includes one).
- `Order.from_dict` is the "simple" path only — HexCoord/Planet/Fleet branches
  do **not** round-trip via `from_dict` alone (they need `OrderSerializer`).
  Test asserts the simple-path round-trip, and asserts a non-round-trip for
  HexCoord with a docstring explaining why.
- `species_population.SpeciesPopulation` accepts `happiness` outside `[0, 1]`
  with no validation. Test pins the no-validation behavior.
- `PlanetaryFacility.is_shipyard` short-circuits to False when `is_operational`
  is False, regardless of components present. Test pins the short-circuit.

Add new entries below as discovered during Phase 1.
