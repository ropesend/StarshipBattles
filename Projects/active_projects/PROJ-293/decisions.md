# PROJ-293: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for Habitability Factor Display Refactor (UI Label Overflow) |
| 2026-04-26 | Add `display_unit` + `display_precision` to `HabitabilityFactor`, NOT a separate Formatter class | Preserves the FACTOR_REGISTRY single-source-of-truth pattern (PROJ-283). A separate formatter would re-introduce indirection between data and display. Two simple fields are the minimum viable extension. |
| 2026-04-26 | Keep storage `unit` field as-is, do NOT rename | `unit` is the canonical storage label and may be referenced by code beyond display formatting (extractors, scorers, future scientific calculations). Mixing storage and display semantics would confuse callers. New fields are purely additive. |
| 2026-04-26 | Default `display_unit=""`, `display_precision=2` | Sensible defaults: empty unit means "bare number" (matches the current generic fallback's intent minus the verbose unit string); 2 decimals matches the existing `:.2f` fallback. Existing callers continue to work without per-factor edits if they didn't care. |
| 2026-04-26 | Tectonic and radiation get `display_unit=""` (no unit suffix) | These factors are abstract scales (0-1 fraction; signed shielding score) where "fraction"/"shielding" suffix added no information. Bare numbers are clearer. |
| 2026-04-26 | Water keeps `display_unit="%"` glued to the number (no space), all others use space | Convention: percent is glued by typographic norm ("50%" not "50 %"). Other units take a space ("101.3 kPa", "1.0 g"). Single special-case in `format_value()` is acceptable for this conventional formatting. |
| 2026-04-26 | Bump `_SETPOINT_LABEL_WIDTH` and `_TOLERANCE_LABEL_WIDTH` from 60 → 90px | 60px overflowed even `"101.3 kPa"` by 3px. 90px gives margin for the worst plausible future case (a 5-char display_unit at 2 decimals: `"±50.00 abcde"`). 75px would be tight; 90px is generous without rearranging the row. |
| 2026-04-26 | Test the refactor against the *exact same* output strings for the 5 currently-handled units | `TestDisplayScaling` already pins outputs like `"1.0 g"`, `"101.3 kPa"`, `"50%"`, `"288 K"`. The new fields are calibrated to produce identical strings → existing tests should pass without modification, proving zero behavior change for working factors. |
| 2026-04-26 | No changes to scoring, costs, or extractors | Out of scope. This project is purely about UI display contract. Scoring/extractor logic is independently tested and stable. |
| 2026-04-26 | Three phases (data → format → layout) over one big phase | Each phase has crisp test gates: Phase 1 changes data only (registry tests catch field gaps), Phase 2 changes format function (preference_row tests catch output regressions), Phase 3 changes layout (manual smoke catches the warnings). Decoupling lets a partial revert if any phase reveals a problem. |
