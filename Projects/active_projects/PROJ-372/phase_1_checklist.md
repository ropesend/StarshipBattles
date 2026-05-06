# Phase 1: Star decomposition (770 LOC stars.py → ~280 facade + extracted services)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-372 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Depends on:** Phase 0 (verified)
**Review Mode:** cumulative (covers Phase 0 + Phase 1)
**Files (planned):** see manifest.md Phase 1 row group

**Status:** Complete

**Notes (Phase 1 outcomes):**
- stars.py: 770 -> 181 LOC (target 280; well under).
- spectrum.py: 74 LOC (target 80).
- star_generator.py: 471 LOC (target 500). `_map_solar_radius_to_hex_radius` retained per D6.
- spectrum_math.py: 155 LOC (target 200). `kelvin_to_rgb`, `stefan_boltzmann_luminosity`, `wien_peak_wavelength` + all solar/Kelvin/Wien/_HEX_RADIUS_/_SPECTRUM_ constants.
- stars.py re-exports preserve all 15+ existing import sites (Spectrum, SOLAR_TEMP_K, etc.); StarGenerator forwarded via module-level `__getattr__` to avoid circular import.
- 4827 strategy/integration tests pass. Save round-trip test (Phase 1 boundary) green.
**Objective:** Split `stars.py` (770 LOC, mixed dataclass + dataclass + generator + math) into 4 focused files: `Star` data class stays in `stars.py` (≤ 280 LOC), `Spectrum` moves to `game/strategy/data/spectrum.py` (≤ 80 LOC), `StarGenerator` moves to `game/strategy/generation/star_generator.py` (≤ 500 LOC), spectral math (`kelvin_to_rgb`, Wien's law, Stefan-Boltzmann helpers, all `_KELVIN_*` / `WIEN_*` / `_WAVELENGTHS` constants) moves to `game/core/spectrum_math.py` (≤ 200 LOC). Save format unchanged. All 13 `Star` dataclass fields and all 9 `Spectrum` dataclass fields verbatim. External readers in 15 files unchanged.

---

## Reading (Phase 1 prerequisites)

- [ ] `Projects/active_projects/PROJ-372/findings/facade_template.md` (from Phase 0 Task 0.6) — extraction rules
- [ ] `game/strategy/data/stars.py` lines 1-770 — full file
- [ ] `game/strategy/data/galaxy_system_generator.py` (354) — sole production reader of `StarGenerator`
- [ ] All 15 external readers of `Star`/`Spectrum` (per design.md) — confirm none reach into private generator helpers (verified during planning, but re-verify on the implementer's branch)

---

## Pre-flight (TDD baseline)

- [ ] Run `pytest tests/unit/strategy/data/test_stars.py -v` — capture pre-extraction pass count for the existing star tests; pin in `Notes:`.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count; pin in `Notes:`.
- [ ] `grep -rn 'from game.strategy.data.stars import' game/ tests/` — capture every importer of `stars`. Pin the list in `Notes:` so Task 1.7 can find them.
- [ ] `grep -rn '_kelvin_to_rgb\|WIEN_\|_KELVIN_\|_WAVELENGTHS' game/ tests/` — confirm every consumer of the math constants is inside `stars.py` (planning verified zero external readers).

---

## Tasks

### Task 1.1: AST regression test (TDD-first) [Simple]
**File:** `tests/unit/core/test_spectrum_math.py` (new)
**Tests:** `pytest tests/unit/core/test_spectrum_math.py -v`

- [ ] Write tests asserting these symbols exist and behave per their stars.py implementations:
  - `kelvin_to_rgb(temp_k: float) -> tuple[int, int, int]` returns `(255, 255, ...)` for solar temp `5778`
  - `kelvin_to_rgb(2000)` returns a warm-tinted tuple; `kelvin_to_rgb(20000)` returns a blue-tinted tuple
  - `stefan_boltzmann_luminosity(radius_solar=1.0, temp_k=5778) ≈ 1.0` (approximately solar)
  - `wien_peak_wavelength(temp_k=5778) ≈ 5e-7` (visible range)
  - Constants `SOLAR_MASS_KG`, `SOLAR_RADIUS_M`, `SOLAR_LUMINOSITY_W`, `SOLAR_TEMP_K`, `WIEN_DISPLACEMENT_CONSTANT`, `_WAVELENGTHS` are present at module level
- [ ] Run the test; **confirm it FAILS** (the module doesn't exist yet).
- [ ] **Verify:** test fails with `ModuleNotFoundError` for `game.core.spectrum_math`.

**Notes:**

### Task 1.2: Create `game/core/spectrum_math.py` [Medium]
**File:** `game/core/spectrum_math.py` (new)
**Tests:** `pytest tests/unit/core/test_spectrum_math.py -v`

- [ ] Copy `stars.py:1-49` constants block (Solar refs + Kelvin/Wien constants + `_WAVELENGTHS` + hex radius coeffs) into `spectrum_math.py`
- [ ] Copy `_kelvin_to_rgb` body (`stars.py:425-462`) as a module-level function `kelvin_to_rgb(temp_k: float) -> tuple[int, int, int]`. Keep the algorithm bit-identical.
- [ ] Add `stefan_boltzmann_luminosity(radius_solar: float, temp_k: float) -> float` extracted from the inline formula at `stars.py:406` (`luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)`).
- [ ] Add `wien_peak_wavelength(temp_k: float) -> float` extracted from `stars.py:496`.
- [ ] **Do NOT move `_map_solar_radius_to_hex_radius`** — it stays in `star_generator.py` (Decision D6 in decisions.md).
- [ ] Module docstring: "Pure-math spectral helpers. PROJ-372 extracted from `game/strategy/data/stars.py`. Used by `game/strategy/generation/star_generator.py` and any future spectral consumer. Zero domain knowledge."
- [ ] Run Task 1.1's test — **confirm it now PASSES**.
- [ ] **Verify:** module ≤ 200 LOC; tests green; `grep -rn '_kelvin_to_rgb\|kelvin_to_rgb' game/` shows the new symbol but the old one still in `stars.py` (cleanup in Task 1.5).

**Notes:**

### Task 1.3: Create `game/strategy/data/spectrum.py` [Simple]
**File:** `game/strategy/data/spectrum.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_spectrum.py -v`

- [ ] Move `class Spectrum` (`stars.py:62-130`) verbatim into `spectrum.py`. Preserve all 9 fields (`gamma_ray`, `xray`, `ultraviolet`, `blue`, `green`, `red`, `infrared`, `microwave`, `radio`), `get_total_output`, `to_dict`, `from_dict`.
- [ ] `from game.core.validation_helpers import require_keys, validate_non_negative` (already in stars.py imports).
- [ ] **Do NOT touch the data shape** — old saves load identically.
- [ ] Create `tests/unit/strategy/data/test_spectrum.py` (new) with: `to_dict`/`from_dict` round-trip, `get_total_output` correctness, `from_dict` raises `PersistenceException` on missing key.
- [ ] **Verify:** new module ≤ 80 LOC; new tests pass; **do NOT yet remove `Spectrum` from `stars.py`** — cleanup at Task 1.5 to allow phased import migration.

**Notes:**

### Task 1.4: Create `game/strategy/generation/star_generator.py` [Complex]
**File:** `game/strategy/generation/star_generator.py` (new)
**Tests:** `pytest tests/unit/strategy/generation/test_star_generator.py -v`

- [ ] Move `class StarGenerator` (`stars.py:253-770`) verbatim into the new file. All 14 methods.
- [ ] Imports: `from game.core.spectrum_math import kelvin_to_rgb, stefan_boltzmann_luminosity, wien_peak_wavelength, SOLAR_TEMP_K, _WAVELENGTHS, _SPECTRUM_SIGMA, _SPECTRUM_JITTER_RANGE, _HEX_RADIUS_*` (move whatever the generator reads).
- [ ] Replace internal `self._kelvin_to_rgb(...)` calls with module-level `kelvin_to_rgb(...)` import.
- [ ] Inline computation `luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)` at `_compute_stefan_boltzmann_type` becomes `luminosity = stefan_boltzmann_luminosity(radius, temperature)`.
- [ ] `_map_solar_radius_to_hex_radius` STAYS as a private method on `StarGenerator` (Decision D6).
- [ ] Imports of `Star` / `Spectrum`: `from game.strategy.data.stars import Star, StarType` and `from game.strategy.data.spectrum import Spectrum`.
- [ ] Create `tests/unit/strategy/generation/test_star_generator.py` (new) with at minimum: smoke test calling `generate_system_stars("Test")` returns a `[Star]` list of length 1-4; primary star has `name="Test A"`; companion stars have `name="Test B"` etc.
- [ ] Move existing tests from `tests/unit/strategy/data/test_stars.py` that test `StarGenerator` behavior (anything constructing a `StarGenerator()` and calling generate methods).
- [ ] **Verify:** new module ≤ 500 LOC; new tests + moved tests pass; existing `test_stars.py` (Star/Spectrum tests) still passes.

**Notes:**

### Task 1.5: Shrink `stars.py` to data-only + facade [Medium]
**File:** `game/strategy/data/stars.py` (modify)
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -v`

- [ ] Remove constants block (`stars.py:14-49`) — now lives in `core/spectrum_math.py`. Keep only `SOLAR_TEMP_K` re-export `from game.core.spectrum_math import SOLAR_TEMP_K` IF any external code imports it from `stars` (verified during Phase 1 pre-flight grep).
- [ ] Remove `class Spectrum` (`stars.py:62-130`) — now lives in `data/spectrum.py`. Keep `from game.strategy.data.spectrum import Spectrum` re-export so external readers of `stars.Spectrum` keep working (verified during pre-flight grep — this avoids touching the 15 reader files in Phase 1).
- [ ] Remove `class StarGenerator` (`stars.py:253-770`) — now lives in `generation/star_generator.py`. Keep `from game.strategy.generation.star_generator import StarGenerator` re-export for back-compat (Galaxy and `galaxy_system_generator.py` are the only readers, both updated in Task 1.7).
- [ ] Keep `class StarType(Enum)`, `class Star` dataclass, `Star.occupied_hexes` property, `Star.to_dict`, `Star.from_dict`.
- [ ] Module docstring: "`Star` data class. PROJ-372 split: `Spectrum` → `data/spectrum.py`; `StarGenerator` → `generation/star_generator.py`; spectral math → `core/spectrum_math.py`."
- [ ] **Verify:** `stars.py` ≤ 280 LOC; `tests/unit/strategy/data/test_stars.py` (Star tests only after Task 1.4 split) green.

**Notes:**

### Task 1.6: Save round-trip equality test [Simple]
**File:** `tests/integration/strategy/test_save_round_trip_phase1.py` (new — temporary, deleted at Phase 5 in favor of full save round-trip)
**Tests:** `pytest tests/integration/strategy/test_save_round_trip_phase1.py -v`

- [ ] Build a `Star` via `StarGenerator().generate_system_stars("Test")` then `to_dict()` → `from_dict()` → `to_dict()` and assert dict equality.
- [ ] Same for a `Spectrum` (build directly, round-trip).
- [ ] Confirm `Star.intrinsic_abilities` round-trips when populated.
- [ ] **Verify:** test passes (Phase 1 didn't break save format).

**Notes:**

### Task 1.7: Update Galaxy + galaxy_system_generator imports [Simple]
**File:** `game/strategy/data/galaxy.py`, `game/strategy/data/galaxy_system_generator.py` (both modify)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v` + sharded suite

- [ ] In `galaxy.py:14`, change `from game.strategy.data.stars import StarGenerator, Star` to `from game.strategy.data.stars import Star` and `from game.strategy.generation.star_generator import StarGenerator`.
- [ ] In `galaxy_system_generator.py` `if TYPE_CHECKING` block, update `from game.strategy.data.stars import StarGenerator` to the new path.
- [ ] If the `stars.py` re-export shim from Task 1.5 is in place, this task is **belt-and-suspenders** — but cut the shim's eventual lifetime by updating the canonical importers now.
- [ ] **Verify:** `galaxy.py` smoke test still works; full sharded suite green.

**Notes:**

### Task 1.8: Tighten LOC ceiling for `stars.py` [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` (modify)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py -v`

- [ ] Change the `STARS_LOC_CEILING` constant from 770 → 280.
- [ ] Run the test; **confirm it now passes** at the new ceiling.
- [ ] **Verify:** test green; pin actual `stars.py` LOC count in `Notes:`.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/data/ -v` — all star/spectrum/related tests pass
- [ ] `pytest tests/unit/core/test_spectrum_math.py -v` — pure-math tests pass
- [ ] `pytest tests/unit/strategy/generation/test_star_generator.py -v` — generator tests pass
- [ ] `pytest tests/integration/strategy/test_save_round_trip_phase1.py -v` — round-trip green
- [ ] `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count ≥ baseline
- [ ] `stars.py` ≤ 280 LOC (AST guard)
- [ ] `spectrum.py` ≤ 80 LOC, `star_generator.py` ≤ 500 LOC, `spectrum_math.py` ≤ 200 LOC (manual `wc -l` confirmation)
- [ ] All 13 Star fields + 9 Spectrum fields preserved verbatim (per `Star.from_dict` signature unchanged)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
