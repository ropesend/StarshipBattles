# PROJ-283..292 Consolidated Manual Smoke Checklist

> **Audience:** user. This document aggregates every deferred
> manual-smoke item accumulated across the PROJ-283..292 audit cycle.
> Run it in one sitting before signing off PROJ-283..292 → Archived.
>
> **When:** after PROJ-291 Phase 4 Task 4.5 and PROJ-292 Phase 6 Task 6.4
> have both landed. Neither project closes without this sweep.

---

## 1. Treasury / Economy (PROJ-290 + PROJ-291 C1)

**Goal:** verify the Treasury panel's Total row is arithmetically
consistent with its displayed category rows and that population upkeep
is correctly included.

- [ ] Start a new game with 2 empires (human player + AI).
- [ ] Play 3-5 turns so colonies accumulate population + construction queues.
- [ ] Open the Empire Panel → Treasury tab.
- [ ] Confirm: every visible expense category row shows a per-resource value.
- [ ] Confirm: **Population Upkeep** row appears (with negative-magnitude
  cells) when the empire has populations.
- [ ] Confirm: the **Total** row per-resource value equals the sum of
  Tributes + Ships + Complexes + **Upkeep** for every resource.
  Pre-PROJ-291 bug: Total was too low by the Upkeep magnitude.

---

## 2. Food Allocation Editor (PROJ-291 C2)

**Goal:** verify the editor opens without crashing and renders a
per-resource consumption preview that matches the displayed `economy.json`
`population_consumption` dict.

- [ ] On a colonized planet with at least one population, open the
  Planet Abilities window and click **Food Allocation**.
- [ ] Confirm: the editor opens — no `AttributeError` / `TypeError`.
- [ ] Confirm: each species row has a slider + typed-input + preview label.
- [ ] Drag the slider. Confirm: the preview label updates live with
  every declared resource in `economy.population_consumption` — e.g.,
  `Preview: 0.100 organics, 0.010 metals/turn` for a 2-resource economy.
- [ ] Drag the slider above 1.0 (over-allocation). Confirm: preview values
  scale linearly; no clamping in the display.

---

## 3. Multi-species Growth + Happiness (PROJ-291 C3)

**Goal:** verify `HappinessEngine` and `PopulationEngine` correctly
resolve each species' own `RaceConfig` on a multi-species colony.

- [ ] Create (or load into) a game state with a colony hosting TWO
  species with visibly different `base_happiness` / `base_reproduction_rate`
  race configs (humans + voidari is the canonical test pair).
- [ ] Open the Planet Report panel. Note each species' happiness + growth rate.
- [ ] End turn.
- [ ] Reopen the Planet Report panel. Confirm: the two species show
  DIFFERENT growth deltas and happiness values. Pre-PROJ-291 bug:
  both species silently used the empire's primary race_config, so
  their growth + happiness matched when they shouldn't have.

---

## 4. Planet Report Per-species Sub-block (PROJ-289 + PROJ-292 H1)

**Goal:** verify the per-species sub-block (habitability + happiness +
growth + food ratio + allocation) displays in EVERY colonized-planet
context, not just the strategy detail panel.

- [ ] Open the **Planet List** window (galactic registry).
  - [ ] Click a colonized planet. Confirm: right-side detail panel shows
    the PROJ-289 sub-block per species, not the legacy single-line
    `- {race_id}: {count}` fallback.
  - [ ] Click an uncolonized planet. Confirm: panel falls back to
    uncolonized rendering (no sub-block) without error.
- [ ] Open the **Build Queue** screen on a colonized planet.
  - [ ] Confirm: the upper planet-report panel in the build queue screen
    shows the PROJ-289 sub-block (same rendering as the strategy screen).
  - Pre-PROJ-292-H1 bug: build-queue context showed the legacy fallback
    because `view` was not threaded into `PlanetReportPanel`.
- [ ] Cross-check: open the strategy screen, click the SAME planet used
  above. The sub-block values (happiness, growth %) match what the list
  window + build queue screen show.

---

## 5. Uncolonized Planet Habitability (PROJ-290)

**Goal:** verify the habitability-for-my-species section renders
correctly on uncolonized worlds.

- [ ] Open the Planet List. Sort by uncolonized.
- [ ] Click an uncolonized world. Confirm: the detail panel shows one
  `{species}: {score}/100` row per species currently resident in the
  viewing empire (`empire.resident_species()`). Best-fit first.
- [ ] If the viewing empire has exactly one species, only one row renders.
- [ ] If the empire has multiple species, rows are ordered by habitability
  descending, with alphabetical tie-break on equal scores.

---

## 6. Exception Handling in Projection Grid (PROJ-292 H3)

**Goal:** no specific user-facing check. The automated test coverage in
`tests/unit/ui/panels/test_planet_report_panel.py::TestNetCellColorExceptionHandling`
verifies that real bugs now propagate instead of being silently
swallowed. If the planet report panel ever renders with missing net-cell
colours despite valid projection data, file a ticket.

---

## 7. Race Registry Staleness (PROJ-287 + PROJ-292 M2)

**Goal:** verify the race editor's save flow correctly invalidates the
session-scoped race cache so subsequent UI renders read the edited values.

- [ ] Start a game. Open the race editor on an empire's primary race.
- [ ] Change a visible field (e.g. `base_happiness` from 0.5 to 0.8).
- [ ] Click Save.
- [ ] Open the Planet Report panel on a colonized planet owned by that
  empire. Confirm: happiness calculations reflect the new value.
  - Pre-fix risk: if the cache was never invalidated, old `base_happiness`
    would persist across the editor save until game restart.

---

## After every box is ticked

- Update [`Projects/projects_index.md`](../../projects_index.md):
  - Move PROJ-283, PROJ-284, PROJ-285, PROJ-286, PROJ-287, PROJ-288,
    PROJ-289, PROJ-290, PROJ-291, PROJ-292 rows from **Awaiting Verification**
    to **Archived** (or bulk move as appropriate).
- Delete `Temp Review Docs/` (optional — the durable archive is at
  `Projects/active_projects/PROJ-291/findings/`).

---

**Cross-references:**
- PROJ-291 Phase 4 Task 4.5 (Treasury + food editor + 2-species growth smokes)
- PROJ-292 Phase 6 Task 6.4 (this document's umbrella sign-off step)
- [`Projects/active_projects/PROJ-291/findings/`](../PROJ-291/findings/) — dual audit source
