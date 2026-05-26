# V2 Folder Structure — StellarHegemony Target Tree

> **Drafted:** 2026-05-25 against V1 HEAD `bc755f012`. Status: **draft, post-Task-D updates applied.**
>
> The target tree is **a verbatim copy of the current cleaned V1 shape**, minus the SKIP/VAULT buckets enumerated in [`MIGRATION_CLASSIFICATION.md`](MIGRATION_CLASSIFICATION.md). Stage 0 is repo hygiene; it does not redesign the source tree. If anything below diverges from the live V1 layout, the live V1 layout wins and this file is the bug.
>
> **Settled (Task D 2026-05-25):**
>
> - V2 repository name: `StellarHegemony`.
> - `Projects/active_projects/` content: **drop all V1 PROJ-XXX content + Batch + _doc_consolidation** to vault. `Projects/active_projects/` ships empty in V2 (scaffolding only).
> - `Projects/` infrastructure (README, index, protocols, gp_protocols): **keep as scaffolding**.
> - `AgentCoordination/protocols/`: **all six files** imported as-is.
> - `AgentCoordination/templates/`: **does not exist in V1; references removed from prompts/plans**. V2 does NOT create this directory.

## Target tree

```text
StellarHegemony/
  AGENTS.md
  CLAUDE.md
  README.md                           # written fresh for V2 (V1 has no top-level README.md)
  pyproject.toml
  requirements.txt
  requirements-dev.txt
  pytest.ini
  mypy.ini
  opencode.json
  .python-version
  conftest.py
  launcher.py
  qa_launcher.py
  .gitignore                          # from V2_GITIGNORE_DRAFT.md
  .gitattributes                      # from V2_GITATTRIBUTES_DRAFT.md
  external_artifacts.example.json     # tracked example
  external_artifacts.local.json       # gitignored, per-machine

  game/                               # full verbatim copy
  tests/                              # full verbatim copy
  data/                               # full verbatim copy
  docs/                               # full verbatim copy (excludes docs/_ignore/, which is gitignored)
  combat_lab/                         # full verbatim copy of tracked content
    ABILITY_TEST_COVERAGE_PLAN.md
    COMBAT_LAB_DOCUMENTATION.md
    README.md
    __init__.py
    battle_state_capture.py
    data/                             # combat-lab test fixtures
    design_loader.py
    logging_config.py
    registry.py
    run_tests.py
    runner.py
    scenario_role_registry.py
    scenarios/
    services/
    spec_compiler.py
    suites/
    telemetry.py
    test_constants.py
    test_history.py
    utils/
    validation/
    # NOT imported (gitignored locally, regenerable):
    # battle.log, battle_states/, test_history/

  Tools/
    # full verbatim copy of tracked content; per CLAUDE.md "live parts of Tools"
    # specifically EXCLUDES test_sharded timing artifacts (gitignored)
    agent_coordination/
    audit_shrink/
    captioning/
    image_comparator/
    process_components/
    process_cursors/
    process_flags/
    process_planet_spheres/
    profiling/
    qa_observer/                      # excludes Tools/qa_observer/session_data/ (gitignored)
    regenerate_ship_portraits/        # excludes Tools/regenerate_ship_portraits/last_run.json (gitignored)
    setup/                            # TBD post-V2 follow-up scripts
    test_sharded/
    validate_designs/
    # add post-V2: migration/, qa/, etc. per STAGE_0_PLAN.md Phase 17

  assets/
    asset_manifest.json
    images/                           # flat, snake_case; cleaned-up V1 shape
      asteroids/
      components/                     # master is 1024/; sibling sizes regenerated
        1024/                         # tracked (LFS)
        # gitignored locally: 64/, 128/, 256/, 512/, 2048/, .component_derivatives_manifest.json
      cursor/
      default_ship_portrait.png
      flags/
        flag_*/                       # per-flag dirs; master is 1024/
          1024/                       # tracked (LFS)
          # gitignored locally: 32/, 64/, 128/, 256/, 512/
        # gitignored: .flag_derivatives_manifest.json
      modifier_icons/                 # single-resolution
      nebulae/                        # single-resolution
      planets/
        2048/                         # master, tracked (LFS)
        # gitignored locally: 128/, 256/, 512/, 1024/, .planet_derivatives_manifest.json
      race_portraits/                 # single-resolution
      resource_icons/                 # single-resolution
      resource_portraits/             # single-resolution
      ship_themes/
        <ThemeName>/                  # per-theme; e.g. Federation, Klingons, Voidforged
          skins/                      # single-resolution PNGs, LFS
          portraits/                  # single-resolution PNGs, LFS
          theme.json
          # gitignored: <Theme>/Production/* if any Production dirs survive
      sphere_world/                   # single-resolution
      stars/
        1024/                         # master, tracked (LFS)
        # gitignored locally: 128/, 256/, 512/, .star_derivatives_manifest.json
      system_backgrounds/             # single-resolution
      warp_points/                    # single-resolution
    audio/                            # placeholder; populate when audio added
    fonts/                            # placeholder; license-gated tracking

  Planning/
    README.md
    gitrepoV2/                        # this folder ships with V2 as migration history
      STAGE_0_PLAN.md
      STAGE_0_DECISIONS.md
      DETAILED_MIGRATION_PLAN.md
      MIGRATION_SOURCE_SNAPSHOT.md
      inventory_post_cleanup.md
      V2_FOLDER_STRUCTURE.md          # this file
      V2_GITIGNORE_DRAFT.md
      V2_GITATTRIBUTES_DRAFT.md
      MIGRATION_CLASSIFICATION.md
      EXTERNAL_ARTIFACT_POLICY.md
      V2_IMPORT_CHECKLIST.md
      # STAGE_0_NEW_AGENT_PROMPT.md intentionally NOT carried into V2 — it
      # was the V1 onboarding artifact and is no longer applicable.
    01_information_boundary_and_fog_of_war/
    02_server_style_turn_packages_and_commands/
    02_5_developer_cheat_test_control_plane/
    03_migration_readiness_standards/
    04_research_integration/
    05_computer_player_ai/
    06_tactical_combat_persistence_and_formations/
    07_network_multiplayer_architecture/
    08_language_migration_plan/
    # current_design/ subfolder mentioned by STAGE_0_PLAN.md Phase 3 does NOT
    # exist in V1; do not create it speculatively.

  Projects/
    README.md
    index.md
    protocols/                        # Settled Task D: keep as scaffolding
    gp_protocols/                     # Settled Task D: keep as scaffolding
    active_projects/                  # Settled Task D: empty at V2 import.
                                      #   V1 PROJ-481..499 + Batch_* + _doc_consolidation
                                      #   went to <vault>/old_repo_exports/v1_active_projects/.
                                      #   New V2 projects land here when started.

    # NOT imported (frozen archives / V1 content):
    # deep_archive/, archived_projects/
    # active_projects/PROJ-* (vaulted)

  AgentCoordination/
    README.md
    SCRATCHPAD.md
    discovered_issues/                # log + README; tracked, shared across agents
    protocols/                        # canonical workflow protocols
      consult_prompt_block.md
      group_execution_protocol.md
      interagent_discussion.md
      partner_cli.md
      ticket_deep_dive.md
      ticket_workflow.md
    # NOT imported (frozen / local / generated):
    # legacy_tickets/, Scratchpad/, generated/, local/, opencodereview/local/

  Reviews/                            # curate or skip entire? — see decision note below
    README.md
    Review_Report_2026_01_27.md       # single named review; keep
    prompts/                          # review prompts; keep
    protocols/                        # review protocols; keep
    scripts/                          # review scripts; keep
    reviews_index.md
    # NOT imported: results/ (39.7 MiB across 2,435 files; archival)
    # Decision-sensitive: if `Reviews/` is mostly retrospective and not used
    # by current workflow, it can drop to VAULT instead of being imported.

  tracking-assets/                    # GitHub-issue support material
    README.md
    projects/                         # GH-backed project system (GP-<n>/)
    screenshots/                      # issue screenshots (current)
    # NOT imported: logs/ (64 MiB; battle logs from old issues; rehome to vault)

  .github/                            # if present in V1 (verify at import)
    ISSUE_TEMPLATE/
    workflows/

  .codex/
    config.toml                       # tracked
    # NOT imported: sessions/ (gitignored)
  .claude/
    settings.example.json             # tracked, reusable
    skills/                           # tracked, reusable Claude skills
    # NOT imported: settings.json (per-machine), settings.local.json
    # (machine-local secrets/env), scheduled_tasks.lock (runtime),
    # *.json.backup.* (gitignored), worktrees/ (gitignored)
  .agent/
    skills/                           # tracked anti-* analysis skills
  .agents/
    CODEX.md
    skills/                           # tracked codex-* skills
  .opencode/
    commands/                         # tracked slash commands
    skills/                           # tracked ocode-* skills
    package.json
    package-lock.json
    # NOT imported: node_modules/ (untracked; npm regenerates locally)
```

## Per-folder policy

### `game/`

- **Purpose:** Canonical runtime source. The application code.
- **Allowed:** Python modules organized per `docs/01_ARCHITECTURE.md` layer model (Core → Services → Assets/Engine → Simulation/Research → Strategy/AI → UI).
- **Forbidden:** Generated artifacts, agent transcripts, runtime caches.
- **Storage:** Plain Git. No LFS.

### `tests/`

- **Purpose:** Canonical test suite.
- **Allowed:** Pytest modules mirroring `game/`'s structure; shared fixtures in `conftest.py` hierarchy per `docs/03_CONVENTIONS.md`.
- **Forbidden:** Test output, coverage data, `.testmondata*`, `.test_durations.json`, `__pycache__`.
- **Storage:** Plain Git.

### `data/`

- **Purpose:** Runtime JSON data that ships with the game (components, modifiers, vehicle classes, resources, designs, races).
- **Allowed:** JSON files only.
- **Forbidden:** Generated data, scratch JSON, agent output.
- **Storage:** Plain Git.

### `docs/`

- **Purpose:** Project documentation (`README.md`, `01_ARCHITECTURE.md`, `02_PATTERNS.md`, `03_CONVENTIONS.md`, system/guide docs).
- **Allowed:** Markdown documenting current behavior. Every doc carries a `Last verified:` timestamp per `docs/03_CONVENTIONS.md` "Documentation Freshness".
- **Forbidden:** `docs/_ignore/` (personal notes; gitignored).
- **Storage:** Plain Git.

### `combat_lab/`

- **Purpose:** Combat Lab scenario harness + test-only data.
- **Allowed:** Source + `data/` fixtures + scenario scripts.
- **Forbidden:** `battle.log`, `battle_states/`, `test_history/` (gitignored locally).
- **Storage:** Plain Git.

### `Tools/`

- **Purpose:** Development tooling (audit, sharded test runner, image processors, validation, agent coordination scripts).
- **Allowed:** Python tools + their per-tool data.
- **Forbidden:** `Tools/qa_observer/session_data/`, `Tools/regenerate_ship_portraits/last_run.json`, ad-hoc test output.
- **Storage:** Plain Git.

### `assets/`

- **Purpose:** Canonical runtime art assets.
- **Allowed:** `asset_manifest.json` + master-size PNGs for each size-tiered family (`components/1024/`, `flags/flag_*/1024/`, `stars/1024/`, `planets/2048/`); single-resolution PNGs for non-tiered families (`asteroids/`, `cursor/`, `modifier_icons/`, `nebulae/`, `race_portraits/`, `resource_icons/`, `resource_portraits/`, `sphere_world/`, `system_backgrounds/`, `warp_points/`); per-theme `ship_themes/<Theme>/{skins,portraits,theme.json}`.
- **Forbidden:** Generated derivative sizes (regenerated at startup by `game/assets/image_derivatives.py`); preview folders; raw AI iterations; PSD/KRA/XCF source masters.
- **Storage:** Plain Git for `asset_manifest.json` and `theme.json`; **LFS** for all PNG/JPG masters (path-scoped, per `V2_GITATTRIBUTES_DRAFT.md`).

### `Planning/`

- **Purpose:** Long-range staged-planning docs (Stage 0 migration history; Stages 1–8 design docs).
- **Allowed:** Stage planning docs; the `gitrepoV2/` migration-history subfolder.
- **Forbidden:** Empty `CURRENT_STATE.md` scaffolds (drop on import unless they have real content per `STAGE_0_NEW_AGENT_PROMPT.md:87`); stale auxiliary expansion notes the prompt's Ignore list calls out.
- **Storage:** Plain Git.

### `Projects/`

- **Purpose:** Active project trackers (PROJ-XXX folders).
- **Allowed:** Active PROJ-XXX directories + batch-execution prompts + project README/index.
- **Forbidden:** `deep_archive/`, `archived_projects/` (frozen; rehome to vault).
- **Storage:** Plain Git.

### `AgentCoordination/`

- **Purpose:** Cross-agent workflow infrastructure (protocols, discovered-issues inbox, shared READMEs).
- **Allowed:** `protocols/`, `discovered_issues/`, top-level READMEs.
- **Forbidden:** `Scratchpad/` (transient working area; gitignored), `legacy_tickets/` (frozen historical archive; vault), `generated/` (derived artifacts; mostly gitignored), `local/` and `opencodereview/local/` (per-checkout state).
- **Storage:** Plain Git.

### `Reviews/`

- **Purpose:** Review prompts, protocols, and report scaffolding.
- **Allowed:** `prompts/`, `protocols/`, `scripts/`, top-level review reports + index.
- **Forbidden:** `results/` (archival; vault).
- **Storage:** Plain Git. **Decision-sensitive:** if `Reviews/` is not used by current workflow, can drop entirely.

### `tracking-assets/`

- **Purpose:** GitHub-issue support material (screenshots, project tracker for the GH-backed `GP-<n>` project system).
- **Allowed:** `README.md`, `projects/`, `screenshots/`.
- **Forbidden:** `logs/` (64 MiB of historical battle logs from closed issues; rehome to vault).
- **Storage:** Plain Git. Large images in `screenshots/` should go through LFS per the LFS draft.

### Dotfile dirs (`.github/`, `.codex/`, `.claude/`, `.agent/`, `.agents/`, `.opencode/`)

- **Purpose:** Per-agent tooling configuration + reusable skills/commands.
- **Allowed:** Skills (`skills/<skill-name>/SKILL.md` + supporting files), commands, config templates, agent-specific reference docs.
- **Forbidden:** Per-machine settings (`settings.json`, `settings.local.json`), session state (`sessions/`, `scheduled_tasks.lock`, `worktrees/`), `node_modules/`, runtime backups.
- **Storage:** Plain Git.

### `assets/audio/`, `assets/fonts/` (placeholders)

- **Purpose:** Forward-looking placeholders. Empty in V2 at import time.
- **Allowed (when populated):** `audio/` — `.wav`, `.ogg`, `.mp3`, `.flac` masters via LFS; `fonts/` — `.ttf`, `.otf` only if license permits redistribution (license-gated).
- **Forbidden:** Generated audio variants; sound effect compilations from raw stems; commercial fonts without license review.
- **Storage:** **LFS** when populated.

## Open structure questions

1. ~~**`AgentCoordination/templates/`**~~ **Settled Task D 2026-05-25:** drop the reference from prompts/plans; V2 does not create this directory.
2. ~~**`Reviews/` import scope.**~~ **Settled Task D 2026-05-25:** import top-level only; `Reviews/results/` to vault.
3. **`combat_lab/test_history.json.migrated`** — sentinel file from a per-test-id history shard migration, currently in `.gitignore` line 78. Drop from V2 (V2 starts post-migration so the marker is irrelevant).
4. **Top-level `README.md`** — V1 has no top-level `README.md`. V2 should ship with one explaining what Stellar Hegemony is, how to run it, and where to find docs. Defer authoring to post-import; flag as a Phase 17 follow-up.

## Forbidden content (cross-cutting)

These never enter V2 regardless of which folder they sit in:

- `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`
- `.pytest_cache/`, `.testmondata*`, `.test_durations.json`, `.test_file_duration_history.json`
- `output/`, `combat_lab/output/`, `combat_lab/battle_states/`, `combat_lab/test_history/`, `combat_lab/battle.log`
- `coverage.json`, `.coverage`, `htmlcov/`
- `AgentCoordination/Scratchpad/`, `AgentCoordination/local/`, `AgentCoordination/generated/skill_usage/summary.json`, `AgentCoordination/generated/test_baseline/summary.json`, `AgentCoordination/opencodereview/local/`
- `.agent_reports/`
- `.claude/settings.json`, `.claude/settings.local.json`, `.claude/settings.*.backup.*`, `.claude/worktrees/`
- `.worktrees/`
- `.codex/sessions/`
- Generated previews (`assets/images/components/_ai_recreate_*preview*/`, `_processed_preview*/`)
- Per-family derivative manifests (`.component_derivatives_manifest.json`, `.flag_derivatives_manifest.json`, etc.)
- Per-family generated derivative size folders (everything under `assets/images/components/{64,128,256,512,2048}/`, `assets/images/flags/flag_*/{32,64,128,256,512}/`, `assets/images/stars/{128,256,512}/`, `assets/images/planets/{128,256,512,1024}/`)
- Build/dist output (`build/`, `dist/`, `*.egg-info/`)
- Editor state (`.vscode/`, `.idea/`, `.VSCodeCounter/`)
- Local env (`.env`, `.venv/`, `venv/`, `env/`, `*.local`, `*.local.json` except `external_artifacts.example.json`)
- Discovered-issue candidate accidentals from V1 (do NOT carry into V2): `--help/`, `--output-dir/`, `panel_profile.prof`, `test_profiling_*.json.tmp`, `nul`, `MagicMock/`
- `_marked_for_deletion_2026-05-29/`

## Exit criteria for this file

- Each folder has documented purpose, allowed content, forbidden content, and storage policy. ✓
- Open structure questions are listed (4 items, above).
- The tree below is a verbatim reflection of the cleaned V1 shape — verifiable by `git ls-files | awk -F/ '{print $1}' | sort -u` against the live tree minus the SKIP buckets.
