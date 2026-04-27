# PROJ-293: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The Habitability Factor Registry (PROJ-283) was designed so that adding a new habitability axis is a single data edit. Today there's a leak: the **display formatting** of factor values is hardcoded UI logic, not registry data. When a new factor lands with a unit string that isn't in the `format_value()` if-tree, it falls through to a verbose `f"{scaled:.2f} {unit}"` fallback. Two factors already hit this path:

| Factor | Stored unit | Default tolerance | Generic format output | UI label width | Overflow |
|--------|-------------|-------------------|------------------------|----------------|----------|
| `tectonic` | `fraction` (display_scale=1.0) | 0.20 | `"0.30 fraction"`, `"±0.20 fraction"` | 60px | -23, -31px |
| `radiation` | `shielding` | 50.00 | `"0.00 shielding"`, `"±50.00 shielding"` | 60px | -35, -51px |

Even `"101.3 kPa"` (which the if-tree formats correctly) overflows by 3px because the label width is too tight.

## Swarm Findings Summary

Single Explore agent's findings; full report in [findings/research.md](findings/research.md). Highlights:

### Architecture

- `HabitabilityFactor` is a frozen dataclass with 12 fields. Single instantiation site (`_SCALAR_FACTORS` tuple + `_build_gas_factors()` generator). Schema is centrally controlled.
- 17 factors total: 7 scalar (gravity, temperature, water, pressure, tectonic, magnetic, radiation) + 10 gases (O2, N2, CO2, H2O, CH4, H2, He, Ar, NH3, SO2).
- All gas factors share `unit="Pa"` and `display_scale=0.001` (kPa display).
- `PreferenceRow.format_value()` is the only display formatter — 6 call sites, all in `preference_row.py`.

### Key Patterns to Reuse

- **Registry-as-data (PROJ-283)**: per CLAUDE.md, "adding a new axis is a single data edit". Each factor declares its own behavior; UI code iterates the registry. The fix extends this to display formatting.
- **Frozen dataclass with default fields**: existing `display_scale`, `default_tolerance`, etc. all use defaults. Adding `display_unit: str = ""` and `display_precision: int = 2` follows the existing pattern. No subclasses, no out-of-registry instances — schema migration is centrally controlled.
- **Test-first per CLAUDE.md Rule 1**: extend [tests/unit/strategy/data/test_habitability_factors.py](../../../tests/unit/strategy/data/test_habitability_factors.py) `TestRegistryShape` to assert every factor has `display_unit` set; extend [tests/unit/ui/widgets/test_preference_row.py](../../../tests/unit/ui/widgets/test_preference_row.py) `TestDisplayScaling` to lock in the data-driven format.

### Dependencies & Risks

1. **Risk: HabitabilityFactor is frozen** — adding fields with defaults is backward-compatible (no callers break), but every existing instantiation must accept the change. Mitigation: defaults make the change additive; existing callers ignore the new fields.
2. **Risk: storage unit vs display unit confusion** — `unit` (storage label, e.g. `"Pa"`) is different from new `display_unit` (UI label, e.g. `"kPa"`). Mitigation: docstrings and decision-log entry. Don't rename `unit`.
3. **Risk: tests that pin existing format strings** — `TestDisplayScaling` calls `format_value()` directly (lines 194, 202, 211, 220 per research). Updates need to keep "0.5 g", "21 K", etc. matching after the refactor. Mitigation: pick `display_unit`/`display_precision` values that produce identical strings to today for the 5 already-handled units.

### Opportunities Discovered

- The verbose generic fallback `f"{scaled:.2f} {unit}"` was "good enough" until the registry expanded to factors with long unit names. The lesson: data-driven UI formatters are required from day one for any registry-grown widget. Consider documenting this in `docs/02_PATTERNS.md` under the Habitability Factor Registry pattern entry (out of scope for this project — flag as a follow-up).

## Display Format Mapping (Phase 1 contract)

This is the proposed mapping from `unit` (storage) to `(display_unit, display_precision)` for each factor. Designed to **preserve** the current format strings for all 5 currently-handled units (no behavior change there) and to **fix** the two broken ones.

| Factor id | Storage unit | display_scale | New display_unit | New display_precision | Output example | Was |
|-----------|--------------|---------------|-------------------|----------------------|-----------------|-----|
| gravity | m/s^2 | 1/9.81 | `g` | 1 | `1.0 g` | unchanged |
| temperature | K | 1.0 | `K` | 0 | `288 K` | unchanged |
| water | fraction | 100.0 | `%` | 0 | `50%` | was `"50%"` (collapse to "50%") |
| pressure | Pa | 0.001 | `kPa` | 1 | `101.3 kPa` | unchanged |
| tectonic | fraction | 1.0 | `""` (none) | 2 | `0.30` | **was `"0.30 fraction"` ← FIXED** |
| magnetic | earth_equiv | 1.0 | `EE` | 2 | `1.00 EE` | unchanged |
| radiation | shielding | 1.0 | `""` (none) | 0 | `0` | **was `"0.00 shielding"` ← FIXED** |
| All gases | Pa | 0.001 | `kPa` | 1 | `21.0 kPa` | unchanged |

**Format function** (one line replaces the current 26-line if-tree):
```python
@staticmethod
def format_value(factor: "HabitabilityFactor", raw_value: float) -> str:
    scaled = raw_value * factor.display_scale
    text = f"{scaled:.{factor.display_precision}f}"
    if factor.display_unit:
        text += f" {factor.display_unit}" if factor.display_unit not in ("%",) else factor.display_unit
    return text
```

(The `%` special case keeps `"50%"` glued to its number, matching today's water output. All other units take a separating space.)

## Label Width

Bumping from 60 → 90px gives:
- Worst case after refactor: `"±50.00 shld"` style isn't used (radiation has no display_unit), but a hypothetical future factor with `display_unit="shld"` and 2 decimals → `"±50.00 shld"` is 10 chars × ~7px ≈ 70px. 90px gives margin.
- Today's longest legitimate string `"101.3 kPa"` is 9 chars ≈ 63px. Trivially fits at 90px.

90 chosen over a tighter 75 to avoid future overflows when factors with longer display_units are added (e.g. "rad/s", "Sv/yr", etc.).

## Design Decisions

See [decisions.md](decisions.md) for full rationale.
