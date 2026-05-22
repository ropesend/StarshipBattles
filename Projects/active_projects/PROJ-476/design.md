# PROJ-476: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source / gating
Last follow-on of **PROJ-472** (closed the StrategySessionFacade read-path gap
with two static guards + Pattern #5 option-(b) UI-safe surface). GATED on
**PROJ-474** (UISAFE symbol promotion), **PROJ-475**, and **PROJ-477** (live
read-path boundary). Executes LAST because the legitimate tooling exemptions are
only fully knowable once the live boundary is closed and PROJ-474 has subtracted
the pure value/enum/static-metadata symbols from the tooling files' import set.
See `Projects/active_projects/PROJ-472/plan.md`,
`Projects/active_projects/PROJ-474/design.md` §"Stay deferred — PROJ-476"
(`:132-141`), and the pre-flesh consult at
`AgentCoordination/Scratchpad/Consult/proj476_preflesh/advice.md`.

## The problem precisely
PROJ-472 documented the UI-safe read surface (Pattern #5) and parked every
non-write-path `game.strategy.*` UI import in a flat
`(file, module, member)` allowlist with **comment-only category labels**
(`UISAFE` / `CLUSTER` / `FLEETCAP` / `TAIL`). The tooling/editor/sandbox screens
landed in the `TAIL` comment block as a transitional holding pen.

`TAIL` is a comment, not a checkable invariant. Nothing distinguishes a genuine
detached tooling import (which should stay outside the facade DTO boundary) from
a not-yet-migrated live read (which PROJ-475/477 must close) from a pure symbol
that PROJ-474 should promote. PROJ-476 is the cleanup that gives the tooling
imports a **first-class, enforced category** so the holding pen is emptied
honestly: each tooling import becomes a documented exemption with a reason, not
an undifferentiated `TAIL` line.

## Key finding (verified live 2026-05-22, confirmed by pre-flesh consult)
**There are ZERO `.session` / `._session` / `.facade_state.session` reads in any
of `battle_setup/`, `galaxy_test/`, `race_setup/`, `builder/`** (and none in the
two in-scope screens-root files `battle_setup_state.py`,
`design_selector_window.py`, nor `workshop_event_router.py`). Evidence: grep over
all four dirs returned no matches; the session-read guard's allowlist
(`test_facade_read_path_session_guard.py:67-96`) contains NO tooling-dir entry.

Therefore **PROJ-476 is import-guard-only**. There is no live-session read to
migrate to the facade and no session-read-guard change. The deliverable is
purely: codify the tooling import exemptions + document the policy.

## Classification (the testable definition)
An imported `game.strategy.*` member in a tooling/editor/sandbox file is a
**legitimate tooling exemption** (stays in PROJ-476's `_TOOLING_EXEMPTIONS`,
NOT migrated, NOT promoted to UISAFE) iff ALL of:

1. It does NOT read or traverse a live `GameSession` (no `.session` chain, not
   handed a session-owned graph object at runtime in the UI).
2. It is NOT one of PROJ-474's pure UI-safe symbols (enum / constant /
   frozen-or-static metadata table / detached scalar config dataclass). Those go
   to `_UISAFE_SYMBOLS`, not here — even when imported by a tooling file
   (membership is a property of the symbol, not the file: PROJ-474 design.md
   `:143-149`).
3. It is one of:
   - a **detached pre-session editor** that constructs/mutates real domain
     objects before any session exists (`battle_setup` holds real
     `Fleet`/`ShipInstance`/`TaskForce`/`Squadron`);
   - a **standalone sandbox harness** that builds its OWN world for inspection
     (`galaxy_test` constructs its own `Galaxy`/`StarSystem` via generation —
     NOT a scene pass-through, explicitly out of PROJ-477's render boundary per
     PROJ-477 plan.md `:101`);
   - a **pre-session authoring service** (`race_setup`'s `RaceLibrary` /
     `RaceRandomizer` / `RaceCaptionLoader` / `RaceDescriptionLLMController`);
   - **design-editor metadata/catalog** loaders
     (`get_default_design_role_registry`, browse-time `DesignCatalog`).

**Sharp edge — why these are NOT UISAFE.** They are detached but not *immutable*
pure symbols: `RaceLibrary` orchestrates filesystem load/save;
`get_default_design_role_registry` lazy-loads a mutable base/mod/user overlay
with runtime invalidation; `RaceDescriptionLLMController` is a live state
machine; the battle-setup models are mutable real domain objects. Promoting any
of them to `_UISAFE_SYMBOLS` would silently widen the always-safe policy (consult
§6 over-exemption risk). They earn an exact tooling exemption instead.

**Sharp edge — why these are NOT live-defer (PROJ-475/477).** None reads a live
`GameSession`. `battle_setup` and `galaxy_test` own their objects/world;
`race_setup` runs before a session exists. `build_queue_panel_factory.py`
(`compute_planet_production`) IS a live read on the live build-queue screen — it
is explicitly NOT tooling and stays with PROJ-475 (consult §3).

## Structure decision: machine-checkable `_TOOLING_EXEMPTIONS`, exact triples
Chosen (consult §4):

- Add `_TOOLING_EXEMPTIONS: frozenset[tuple[str, str, str, str, str]]` (or a
  `dict[(file, module, member) -> (category_tag, reason)]`) to
  `test_facade_read_path_imports_guard.py`. **Exact `(file, module, member)`
  scoped**, with a `category_tag` in
  {`prebattle-editor`, `sandbox-harness`, `race-authoring`, `design-editor`} and
  a one-line reason.
- The matcher allows an import if: always-allowed facade/commands path **OR**
  `(module, member) ∈ _UISAFE_SYMBOLS` (PROJ-474) **OR** the exact
  `(file, module, member)` is in `_TOOLING_EXEMPTIONS` **OR** it is in the
  residual transitional `TAIL`/`CLUSTER`/`FLEETCAP` blocks.
- **No-misfile invariant test**: the `(module, member)` projection of
  `_TOOLING_EXEMPTIONS` must be disjoint from `_UISAFE_SYMBOLS`, and the
  `(file, module, member)` set must be disjoint from the residual
  `TAIL`/`CLUSTER`/`FLEETCAP` set. Each import is classified exactly once.
- **Positive-control test**: pin that a tooling triple is allowed via
  `_TOOLING_EXEMPTIONS` and that a synthetic live-domain import in a NON-exempt
  file (e.g. a fake `game.strategy.engine.game_session.GameSession`) is still
  flagged — so the category cannot be widened into a folder waiver.

**Why NOT a folder/subpackage waiver** (consult §4): `galaxy_test`, `race_setup`,
and `builder` each MIX promotable pure symbols (`PlanetType`,
`VALID_GALAXY_TYPES`, `RaceConfig`, `RacePointBudget`, `FieldStatus`,
`StrategicKind`, `SUPERWEAPONS`) with genuine tooling imports. A folder waiver
would let a net-new live import sneak in under the tooling banner. The guard stays
active everywhere; only exact triples are exempt.

**Why a SEPARATE category, not just leaving them in `TAIL`:** `TAIL` is by
definition the *not-yet-classified* transitional pen. After 474/475/477 it should
be empty (or only contain genuinely-still-deferred items). A durable, named
`_TOOLING_EXEMPTIONS` with reasons states "this is intended to stay outside the
facade" — which is the actual end state for these imports — instead of implying
"migration pending."

## Dependencies & Risks
1. **Over-exemption** — `RaceLibrary`, `get_default_design_role_registry`,
   `RaceDescriptionLLMController`, `DesignCatalog` are not live-session reads but
   are also not immutable pure symbols. Mitigation: keep `_UISAFE_SYMBOLS`
   symbol-level and narrow; put these ONLY in exact tooling exemptions; the
   no-misfile test enforces the split.
2. **Whole-file/folder waivers** — the tooling dirs mix safe + tooling imports.
   Mitigation: exact triples only; positive-control test pins that a non-exempt
   live import in a tooling file is still flagged.
3. **Post-474/475/477 drift** — the stub counts (battle_setup x4 / galaxy_test x3
   / race_setup x4 / builder x3) and even the 2026-05-22 residue triple set are
   planning snapshots, not durable truth. Mitigation: Phase 1 is a mandatory
   fresh re-inventory against post-gate live code before any guard edit.
4. **Test-seam churn** — `race_setup/screen.py:28` imports `RaceRandomizer` only
   as a test-patch re-export seam. Mitigation: treat as a real exemption now;
   prune the triple if execution removes the seam.
5. **Screens-root scope ambiguity** — `battle_setup_state.py` IS in scope (model
   behind the package); `design_selector_window.py` / `workshop_event_router.py`
   ARE design-editor tooling (PROJ-474 design.md `:132-141`);
   `build_queue_panel_factory.py` is NOT (live build-queue). Mitigation: classify
   by ownership/usage at execution time, not by directory name.

## Sequencing rationale
1. **Re-inventory first (Phase 1)** — non-optional. After 474 promotes pure
   symbols and 475/477 migrate live readers, the `TAIL` block is materially
   smaller; the exact residue must be re-derived from live code.
2. **Guard category + move (Phase 2)** — TDD: write the failing no-misfile +
   positive-control tests first, then add `_TOOLING_EXEMPTIONS` and move the
   residue out of `TAIL`.
3. **Doc + reconcile (Phase 3)** — Pattern #5 paragraph + final guard/doc parity
   + full-suite verification.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
