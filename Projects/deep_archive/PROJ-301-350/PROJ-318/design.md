# PROJ-318: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

This project's basis is a post-merge independent audit of PROJ-314
(Unify Ship Theme Loader Schema). The audit raised 8 claims (1 P1 +
7 P2). Four parallel verification agents independently checked each
claim; their findings are reproduced below as the design rationale
for each remediation phase.

The methodology was deliberately adversarial: each agent read code,
ran scripts, fetched external docs (OpenAI image-API metadata),
and reported a verify / refute / partial verdict with concrete
file:line citations and command output. No agent saw another's
findings.

## Verification Findings (from 4 parallel agents)

### Claim A — Project audit gate fails (P1) → VERIFIED → Phase 1 (R1)

**Cited:** `Projects/active_projects/PROJ-314/phase_1_checklist.md:8`

**Findings:**
- Plan.md Quick Status table (PROJ-314 plan.md lines 17-22): all 6
  phases marked `Complete`.
- `phase_1_checklist.md` line 8 reads literally `**Status:** Not Started`.
- Checkbox count in phase_1_checklist.md: **34 unchecked, 0 checked.**
- Files `phase_2_checklist.md` … `phase_6_checklist.md` do not
  exist; the plan-table just references them as "(TBD)".
- `python Projects/scripts/validate_audit_ready.py PROJ-314` exits
  **1** with **8 errors + 1 warning**. Sample errors:
  ```
  [FAIL] Phase 1: Not Started - not started
  [FAIL] 5 tasks have incomplete subtasks: (34 unchecked boxes total across tasks 1.1–1.5)
  [WARN] Index status: Planning / Blockers reported: None
  ```

The plan declared completion but neither the checklists nor the
project-audit script support that.

### Claim B — Audit script exits 0 despite reporting problems (P2) → VERIFIED → Phase 5 (R2)

**Cited:** `Tools/regenerate_ship_portraits/audit.py:129-142`

**Findings:**
- audit.py line 129-131 gates portrait checks on the presence of a
  portrait key in the assets dict:
  ```python
  portrait_rel = entry.get("portrait")
  if portrait_rel:
      ship_finding.portrait = _audit_file(...)
  ```
- Aetherwake (zero portrait keys declared) is reported **CLEAN**
  even though no portraits exist.
- Running `python -m Tools.regenerate_ship_portraits.audit` from
  repo root: exit code **0**, with **144 size-mismatch warnings**
  printed to stdout (declared `(2048, 2048)`, actual `(1024, 1024)`
  for Voidforged or `(640, 640)` for Thoraliens).

Unsuitable as a CI / release gate at present.

### Claim C — UI smoke test allows fallback as a pass condition (P1) → PARTIAL → Phase 5 (R2)

**Cited:** `tests/integration/ui/test_race_setup_ships_smoke.py:63-73`

**Findings:**
- The literal claim text ("20 missing or undeclared portrait
  entries, 151 declared portrait size mismatches") is wrong on
  count: 0 portrait entries are *missing* (Aetherwake's lack of
  portrait keys is schema-allowed), and 144 (not 151) size
  mismatches exist.
- BUT the substantive concern is valid:
  - Lines 63-73 assert only `isinstance(surf, pygame.Surface)`,
    accepting the synthetic-fallback Surface as a pass.
  - No dimension assertion (`(2048, 2048)`) anywhere in the file.
  - No `surf is_not the synthetic fallback` discrimination.
- Combined with Claim B, no quality gate exists today: the audit
  script silently passes, the smoke test silently passes, yet 144
  size mismatches and 20 missing-portrait gaps are real.

### Claim D — Legacy `<Class>_Portrait.jpg` helper still pinned (P2) → VERIFIED → Phase 3 (R3)

**Cited:** `game/ui/utils/portraits.py:83-97`

**Findings:**
- `portraits.py` lines 83-97 define `get_portrait_filename(ship_class)`:
  ```python
  def get_portrait_filename(ship_class: str) -> str:
      """Build the legacy portrait filename for a ship class.
      PROJ-314: this helper is kept for backward compatibility..."""
      class_clean = parse_ship_class_name(ship_class)
      return f"{class_clean}_Portrait.jpg"
  ```
- `tests/unit/ui/utils/test_portraits.py` `TestGetPortraitFilename`
  pins specific outputs (`"Escort_Portrait.jpg"`, etc.) — 3 tests
  asserting the legacy convention.
- `get_portrait_search_paths()` in the same file still references
  the legacy fallback path.
- PROJ-314's manifest at `Projects/active_projects/PROJ-314/manifest.md`
  explicitly listed lines 98-114 of this file as a deletion target
  ("Phase 5 — delete `get_portrait_search_paths()`…").

The function is dead-but-tested code. The `# kept for backward
compatibility` comment is exactly the kind of shim CLAUDE.md Rule 3
forbids after a migration.

### Claim E — Theme-creator skill writes legacy schema (P2) → PARTIAL → Phase 6 (R4)

**Cited:** `.agents/skills/codex-ship-theme-creator/scripts/create_manifest.py:28-32`

**Findings:**
- `theme_common.py` was correctly updated in PROJ-314 commit
  `0bbf9c36d`: docstring says "Updated for the unified theme.json
  `assets:` schema", and `load_manifest()` reads the new schema.
- BUT sibling files in the same skill directory were NOT updated:
  - `create_manifest.py:28-32` still writes
    `"images": {class_name: f"Skins/{skin}" ...}` (old schema, no
    portrait keys).
  - `validate_theme.py:19` still expects `"images"` (not
    `"assets"`), `Skins/{skin_name}` paths, and 1024×1024 JPG
    portraits.
- PROJ-314 manifest line 16 listed `theme_common.py` for update
  but did not list its sibling scripts. They were missed.

Future themes scaffolded by this skill will recreate the exact
schema drift the project was meant to remove.

### Claim F — New tool misses tool conventions (P2) → VERIFIED (3 of 3) → Phase 4 (R5)

**Cited:** `Tools/README.md:102-110`

**Findings:**
- `Tools/regenerate_ship_portraits/` directory listing: no
  `README.md` file present.
- `Tools/README.md` lines 40-82 (the catalog section): no entry
  for `regenerate_ship_portraits`. Per the project's own
  conventions section (line 102-103), "every tool must have one"
  README and be listed in the catalog.
- `Tools/regenerate_ship_portraits/cli.py` lines 45-53 contain
  module-top-level imports of `game.core.exceptions`,
  `game.core.paths`, `game.core.ship_classes`, and
  `game.ui.services.image`. These run at import time, before the
  `if __name__ == "__main__"` guard at line 431.
- Comparable tool (`Tools/process_components/check_orphans.py:8-19`)
  uses a project-root finder + `sys.path` insertion before any
  `from game.X` import. That pattern allows
  `python Tools/process_components/check_orphans.py` to work
  outside `python -m`. The new tool does not.

### Claim G — Architecture docs are stale (P2) → VERIFIED → Phase 2 (R6)

**Cited:** `docs/02_PATTERNS.md:60-83`

**Findings:**
- `game/context.py` `__init__` lines 44-58 wires 10 services:
  registry_manager, profiler, component_cache, policy_manager,
  asset_manager, sprite_manager, ship_theme_manager, game_settings,
  llm_provider, **image_provider** (line 58, the new addition).
- `docs/02_PATTERNS.md` lines 83-95 list only 9 services in the
  Singleton-Free DI section. `image_provider` is absent. Line 70
  of the code example says `# ... all 9 services`.
- `docs/README.md` line 4 says `ApplicationContext manages 9 services`.
- `AGENTS.md` line 51 says the same.
- `docs/01_ARCHITECTURE.md` was correctly updated by PROJ-314 (line 3:
  `Last verified: 2026-04-28 — PROJ-314 added game/ui/services/image/...`).
  The other 3 docs were missed.

### Claim H — Edit API default likely fails (P2) → REFUTED → No phase

**Cited:** `game/ui/services/image/openai_provider.py:85-125`

**Findings:**
- `openai_provider.py` line 85-96 signature defaults `model="gpt-image-2"`
  for both `/v1/images/generations` (line 130) and `/v1/images/edits`
  (line 124).
- OpenAI's current developer documentation
  (https://developers.openai.com/api/docs/models/gpt-image-2)
  confirms `gpt-image-2` is supported for both endpoints. Quote
  from the docs: "gpt-image-2 runs through v1/images/generations,
  v1/images/edits, v1/responses, and v1/chat/completions."
- No remediation needed. The single-default pattern is correct.

This claim is documented here so future agents don't relitigate
it.

## Architecture Implications

PROJ-318 doesn't change the architecture; it brings the docs and
scaffolding into alignment with the code that PROJ-314 shipped.
Specifically:

- The 10-service `ApplicationContext` (added by PROJ-314 Phase 2)
  is the new ground truth. Phase 2 of PROJ-318 updates the 3
  stale docs to match.
- The `assets:` schema in `theme.json` (PROJ-314 Phase 5) is the
  new ground truth. Phase 6 of PROJ-318 brings the
  codex-ship-theme-creator skill into alignment.
- The "deleted hardcoded portrait convention" (PROJ-314 Phase 3
  manifest goal) is now genuinely deleted (PROJ-318 Phase 3),
  with no `# kept for backward compatibility` shim.
- Quality gates (audit + smoke test) become real gates (PROJ-318
  Phase 5), so future regressions are caught at CI rather than at
  QA.

## Decisions

See [decisions.md](decisions.md) for the full log.
