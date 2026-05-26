# V1 → V2 Migration Classification

> **Drafted:** 2026-05-25 against V1 HEAD `bc755f012`. Status: **draft, pending user review.**
>
> Per-top-level-entry classification of every tracked V1 path into one of:
>
> | Bucket | Meaning | V2 destination |
> |---|---|---|
> | `IMPORT_GIT` | Migrate as normal Git (plain text/code/data) | V2 tree, plain Git |
> | `IMPORT_LFS` | Migrate through Git LFS (large runtime binaries) | V2 tree, LFS-tracked per `V2_GITATTRIBUTES_DRAFT.md` |
> | `RELEASE_ARTIFACT` | Move to GitHub Releases or Issue attachments | Not in V2 Git; uploaded as release/issue assets |
> | `VAULT` | Move to external artifact vault (Google Drive, per current proposal) | Not in V2 Git; per-machine vault path |
> | `SKIP` | Do not migrate at all | Discarded; pattern added to `V2_GITIGNORE_DRAFT.md` for defense |
>
> Listing scope: every tracked path's depth-1 component from `git ls-files | awk -F/ '{print $1}' | sort -u`. Where a depth-1 entry needs sub-classification (most directories), the row's `Notes` column points at the subdivision rows.

## Decision-sensitive assumptions (settle in Task D)

These rows are best-guess defaults. If the user changes a decision, flagged rows shift.

1. **Vault provider = Google Drive** (Task D decision). If different, every `VAULT` destination path changes provider-name; the bucket assignment is unaffected.
2. **Issue migration policy = "resolve/archive most old issues first; minimal migration into V2"** (Task D decision). If the user chooses to migrate more issues, `tracking-assets/logs/` may become partially `RELEASE_ARTIFACT` (Issue attachments) instead of fully `VAULT`. Today's row: full `VAULT`.
3. **`Reviews/` import scope.** Today the row assumes `Reviews/{README, Review_Report_2026_01_27.md, prompts, protocols, scripts, reviews_index.md}` = `IMPORT_GIT` and `Reviews/results/` = `VAULT`. Could also drop the entire folder to `VAULT` if the user prefers. Flagged.
4. **`Projects/active_projects/` curation.** Today the row assumes every PROJ-481..499 plus the `Batch_*_Prompt.txt` and `_doc_consolidation/` are in scope (`IMPORT_GIT`). Task D should confirm which are still active.
5. **`AgentCoordination/protocols/` curation.** Today the row assumes all six files are load-bearing. Task D should confirm.
6. **Old-repo handling = "leave unarchived until V2 validated"** (Task D decision). Affects only the V1-side post-migration step, not classification.

## Classification table

### Root-level individual files

| Path | Bucket | Reason | V2 destination | Decision status |
|---|---|---|---|---|
| `AGENTS.md` | `IMPORT_GIT` | Top-level agent reference. Load-bearing. | `StellarHegemony/AGENTS.md` | Settled |
| `CLAUDE.md` | `IMPORT_GIT` | Claude-Code adapter on top of AGENTS.md. | `StellarHegemony/CLAUDE.md` | Settled (re-verify content for V2 adapter accuracy at import) |
| `conftest.py` | `IMPORT_GIT` | Repo-root pytest config (SDL_VIDEODRIVER=dummy, fixture hierarchy). | `StellarHegemony/conftest.py` | Settled |
| `launcher.py` | `IMPORT_GIT` | Game launcher entry. | `StellarHegemony/launcher.py` | Settled |
| `qa_launcher.py` | `IMPORT_GIT` | QA launcher entry. | `StellarHegemony/qa_launcher.py` | Settled |
| `mypy.ini` | `IMPORT_GIT` | Per-module strict overrides (PROJ-483). | `StellarHegemony/mypy.ini` | Settled |
| `pyproject.toml` | `IMPORT_GIT` | Python project metadata (3.13+). | `StellarHegemony/pyproject.toml` | Settled (update `name = "stellar-hegemony"` at import) |
| `pytest.ini` | `IMPORT_GIT` | Pytest config. | `StellarHegemony/pytest.ini` | Settled |
| `requirements.txt` | `IMPORT_GIT` | Runtime deps. | `StellarHegemony/requirements.txt` | Settled |
| `requirements-dev.txt` | `IMPORT_GIT` | Dev deps. | `StellarHegemony/requirements-dev.txt` | Settled |
| `opencode.json` | `IMPORT_GIT` | OpenCode CLI config. | `StellarHegemony/opencode.json` | Settled |
| `.python-version` | `IMPORT_GIT` | Pyenv pin. | `StellarHegemony/.python-version` | Settled |
| `.gitignore` | `IMPORT_GIT` (rewritten) | V2 version from `V2_GITIGNORE_DRAFT.md`, not V1 verbatim. | `StellarHegemony/.gitignore` | Settled |
| `.coverage` | `SKIP` | Accidentally-tracked coverage.py SQLite output. Listed in `V2_GITIGNORE_DRAFT.md` defense block. **DI-log candidate.** | — | Settled |
| `panel_profile.prof` | `SKIP` | Accidentally-tracked profiling output. Listed in `V2_GITIGNORE_DRAFT.md` defense block. **DI-log candidate.** | — | Settled |
| `test_profiling_*.json` (1 file) | `SKIP` | Same family. **DI-log candidate.** | — | Settled |
| `test_profiling_*.json.tmp` (~10 files) | `SKIP` | Accidentally-tracked temp files; should never have been committed. **DI-log candidate.** | — | Settled |

### Root-level directories — verbatim imports

| Path | Bucket | Reason | V2 destination |
|---|---|---|---|
| `game/` | `IMPORT_GIT` | Canonical runtime source. | `StellarHegemony/game/` |
| `tests/` | `IMPORT_GIT` | Canonical test suite. | `StellarHegemony/tests/` |
| `data/` | `IMPORT_GIT` | Runtime JSON data (components, modifiers, designs, races). | `StellarHegemony/data/` |
| `docs/` | `IMPORT_GIT` | Project documentation. Excludes `docs/_ignore/` (gitignored). | `StellarHegemony/docs/` |
| `combat_lab/` | `IMPORT_GIT` | Combat Lab harness + test-only data. Excludes `battle_states/`, `test_history/`, `battle.log` (gitignored). | `StellarHegemony/combat_lab/` |
| `Tools/` | `IMPORT_GIT` | Development tooling. Excludes `qa_observer/session_data/`, `regenerate_ship_portraits/last_run.json` (gitignored). | `StellarHegemony/Tools/` |
| `profiling/` | `IMPORT_GIT` (re-verify) | Listed top-level but I haven't audited content. **Verify at import:** likely scaffolds for `Tools/profiling/`-driven runs; if empty/stale, drop. | `StellarHegemony/profiling/` |

### Assets (LFS via `.gitattributes`)

| Path | Bucket | Reason | V2 destination |
|---|---|---|---|
| `assets/asset_manifest.json` | `IMPORT_GIT` | Asset catalog metadata. Plain Git. | `StellarHegemony/assets/asset_manifest.json` |
| `assets/images/<size-tiered-family>/<master>/*.png` (`components/1024/`, `flags/flag_*/1024/`, `stars/1024/`, `planets/2048/`) | `IMPORT_LFS` | Master-size runtime assets. | `StellarHegemony/assets/images/<family>/<master>/` |
| `assets/images/<size-tiered-family>/<derivative-size>/` | `SKIP` (regenerable) | Generated by `game.assets.image_derivatives` at startup. Gitignored. None tracked in V1 anyway. | — |
| `assets/images/<single-resolution-family>/` (cursor, modifier_icons, nebulae, race_portraits, resource_icons, resource_portraits, sphere_world, system_backgrounds, warp_points, asteroids) | `IMPORT_LFS` | Single-resolution runtime assets. | `StellarHegemony/assets/images/<family>/` |
| `assets/images/ship_themes/<Theme>/{skins,portraits}/*.png` | `IMPORT_LFS` | Per-theme ship art. | `StellarHegemony/assets/images/ship_themes/<Theme>/` |
| `assets/images/ship_themes/<Theme>/{theme.json,theme.caption.json}` | `IMPORT_GIT` | Theme metadata. | `StellarHegemony/assets/images/ship_themes/<Theme>/` |
| `assets/images/flags/flag_*/flag_*.caption.json` | `IMPORT_GIT` | Flag metadata. | `StellarHegemony/assets/images/flags/flag_*/` |
| `assets/images/race_portraits/*.json` | `IMPORT_GIT` | Race-portrait metadata. | `StellarHegemony/assets/images/race_portraits/` |
| `assets/images/default_ship_portrait.png` | `IMPORT_LFS` | Default fallback portrait. | `StellarHegemony/assets/images/default_ship_portrait.png` |

### Root-level directories — curated imports

| Path | Bucket | Reason | V2 destination |
|---|---|---|---|
| `Planning/README.md` | `IMPORT_GIT` | Staged-planning overview. | `StellarHegemony/Planning/README.md` |
| `Planning/gitrepoV2/` | `IMPORT_GIT` | Migration history (this very pass). Excludes `STAGE_0_NEW_AGENT_PROMPT.md` (V1 onboarding artifact, not applicable post-V2). | `StellarHegemony/Planning/gitrepoV2/` |
| `Planning/0[1-8]_*/` (Stages 1–8) | `IMPORT_GIT` | Long-range stage planning. Drop empty `CURRENT_STATE.md` scaffolds at import (per `STAGE_0_NEW_AGENT_PROMPT.md:87`). | `StellarHegemony/Planning/0[1-8]_*/` |
| `Projects/active_projects/PROJ-481..499/` | `IMPORT_GIT` | **Decision-sensitive** — assumed all 19 active projects in scope; user confirms in Task D. | `StellarHegemony/Projects/active_projects/` |
| `Projects/active_projects/Batch_*_Prompt.txt` | `IMPORT_GIT` | Batch-execution prompts. **Decision-sensitive** — confirm still active. | `StellarHegemony/Projects/active_projects/` |
| `Projects/active_projects/_doc_consolidation/` | `IMPORT_GIT` | **Decision-sensitive** — confirm still active. | `StellarHegemony/Projects/active_projects/` |
| `Projects/{README.md, index.md}` | `IMPORT_GIT` | Project-system entry docs. | `StellarHegemony/Projects/` |
| `Projects/deep_archive/` | `VAULT` | 335.8 MiB / 3,997 files of historical project material. Includes the 317 MiB of accidentally-committed PROJ-295 dryrun wheels. Vault location: `StellarHegemonyVault/old_repo_exports/v1_projects_deep_archive/`. | external |
| `Projects/archived_projects/` (if exists) | `VAULT` | Same disposition as deep_archive. **Verify at import** — not seen in `git ls-files | awk` output but the prompt's SKIP list mentions it. | external |
| `Projects/protocols/`, `Projects/gp_protocols/` | `IMPORT_GIT` (verify) | Protocol templates per CLAUDE.md. **Verify at import.** | `StellarHegemony/Projects/` |
| `AgentCoordination/README.md`, `SCRATCHPAD.md` | `IMPORT_GIT` | Top-level coordination docs. | `StellarHegemony/AgentCoordination/` |
| `AgentCoordination/protocols/` (6 files) | `IMPORT_GIT` | Workflow protocols (canonical TDD / consult / discuss / partner-CLI / ticket-workflow). **Decision-sensitive** — user confirms full curation set. | `StellarHegemony/AgentCoordination/protocols/` |
| `AgentCoordination/discovered_issues/` | `IMPORT_GIT` | Shared discovered-issues inbox (tracked log + README). | `StellarHegemony/AgentCoordination/discovered_issues/` |
| `AgentCoordination/templates/` | **N/A — does not exist in V1** | Referenced by Stage 0 prompt + plan but no such directory. **Task D errata fix.** | — |
| `AgentCoordination/legacy_tickets/` | `VAULT` | 72.5 MiB / 195 files of frozen historical tickets including 71.7 MiB of bug logs. Vault: `StellarHegemonyVault/old_repo_exports/v1_legacy_tickets/`. | external |
| `AgentCoordination/Scratchpad/` | `SKIP` | Gitignored transient working area. | — |
| `AgentCoordination/local/` | `SKIP` | Gitignored per-checkout state. | — |
| `AgentCoordination/generated/` | `SKIP` (mostly) | Per-install counters; summary.json gitignored. The per-install JSON files under `by_install/` are tracked but each agent's installation generates its own; for V2, start clean — don't carry V1 install IDs. | — (regenerated on first skill use) |
| `AgentCoordination/opencodereview/local/` | `SKIP` | Gitignored. | — |
| `Reviews/{README.md, Review_Report_2026_01_27.md, prompts, protocols, scripts, reviews_index.md}` | `IMPORT_GIT` | Review infrastructure. **Decision-sensitive** — could drop entire `Reviews/` to VAULT. | `StellarHegemony/Reviews/` |
| `Reviews/results/` | `VAULT` | 40.1 MiB / 2,479 files of historical audit reports. Vault: `StellarHegemonyVault/old_repo_exports/v1_reviews_results/`. | external |
| `tracking-assets/{README.md, projects/, screenshots/}` | `IMPORT_GIT` (screenshots LFS-tracked via `.gitattributes`) | GH-issue support material; current `GP-<n>/` projects + current screenshots. **Audit screenshot directory at import** to verify LFS is correct disposition vs vault. | `StellarHegemony/tracking-assets/` |
| `tracking-assets/logs/` | `VAULT` | 64.1 MiB / 14 files; battle logs from closed issues (#17, #19, #8, #31). Vault: `StellarHegemonyVault/repro_bundles/v1_tracking_logs/`. Could alternatively be `RELEASE_ARTIFACT` if these are still relevant to open issues; current assumption "resolve/archive most issues first" + the related issues being closed makes VAULT correct. | external |

### Dotfile dirs

| Path | Bucket | Reason | V2 destination |
|---|---|---|---|
| `.github/` (if present in V1; verify) | `IMPORT_GIT` | Issue templates + workflows. **Verify content** at import; if outdated, draft new in Phase 17. | `StellarHegemony/.github/` |
| `.codex/config.toml` | `IMPORT_GIT` | Tracked Codex config. | `StellarHegemony/.codex/config.toml` |
| `.codex/sessions/` (et al.) | `SKIP` | Gitignored per `.codex/*` block. | — |
| `.claude/skills/` (all tracked claude-* skills) | `IMPORT_GIT` | Reusable Claude skills. | `StellarHegemony/.claude/skills/` |
| `.claude/settings.example.json` | `IMPORT_GIT` | Tracked example. | `StellarHegemony/.claude/settings.example.json` |
| `.claude/settings.json`, `.local.json`, backups, worktrees, `scheduled_tasks.lock` | `SKIP` | Gitignored / per-machine. | — |
| `.agent/skills/anti-*/` | `IMPORT_GIT` | Tracked Antigravity skills. (Antigravity is lower-priority per AGENTS.md; carry forward but agent itself is deprioritized.) | `StellarHegemony/.agent/skills/` |
| `.agents/CODEX.md` | `IMPORT_GIT` | Codex top-level adapter doc. | `StellarHegemony/.agents/CODEX.md` |
| `.agents/skills/codex-*/` | `IMPORT_GIT` | Tracked Codex skills. | `StellarHegemony/.agents/skills/` |
| `.opencode/commands/`, `.opencode/skills/` | `IMPORT_GIT` | Tracked OpenCode commands + ocode-* skills. | `StellarHegemony/.opencode/` |
| `.opencode/package.json`, `package-lock.json` | `IMPORT_GIT` | OpenCode npm deps. | `StellarHegemony/.opencode/` |
| `.opencode/node_modules/` | `SKIP` | Gitignored in V2; `npm install` regenerates. | — |

### Discovered-issue accidentals + workflow stragglers

| Path | Bucket | Reason | V2 destination |
|---|---|---|---|
| `--help/raw/{clones.json, dead_deps.txt, loc_baseline.txt, orphans.txt, radon.json, vulture_100.txt, vulture_80.txt}` | `SKIP` | 7 files accidentally tracked from `Tools/audit_shrink/audit_shrink.py` invoked with `--help` mis-parsed as a positional output dir. **DI-log candidate.** Gitignored in V2 defense block. | — |
| `--output-dir/raw/{same 7 files}` | `SKIP` | Same accidental-tracking pattern with `--output-dir` as flag-name-as-folder. **DI-log candidate.** | — |
| `_marked_for_deletion_2026-05-29/` | `SKIP` | Pre-deletion staging bucket; ~1.9 MiB / 140 files. The directory itself was a user-flagged "to delete" marker; don't carry to V2. | — |

## Aggregated bucket summary

| Bucket | Approximate size | Approximate file count |
|---|---:|---:|
| `IMPORT_GIT` (plain text/code/data) | ~150 MiB | ~11,500 |
| `IMPORT_LFS` (master + single-res image families) | ~4,100 MiB | ~1,400 |
| `RELEASE_ARTIFACT` | 0 | 0 |
| `VAULT` (Google Drive, per current proposal) | ~512 MiB | ~6,700 |
| `SKIP` | ~5 MiB (mostly accidentals + `_marked_for_deletion_`) | ~165 |
| **Total tracked in V1** | **~4,767 MiB (4.76 GiB)** | **12,590** |

The math reconciles within rounding to the inventory's `4.76 GiB / 12,590 files`. Numbers are approximate because some directories are sub-classified (e.g. `Projects/` splits into `IMPORT_GIT` + `VAULT`).

## Verification commands at V2 import

Before each Phase 11/12/13 commit, run:

```bash
# Sanity: every staged file is either non-asset OR LFS-tracked.
git status --short                                # staged files for the impending commit
git lfs status                                    # confirm LFS-tracked masters
git diff --stat --staged | head -50               # confirm no accidental size spike

# Per-bucket spot-checks (run against V2 working tree):
test -d Projects/deep_archive && echo "FAIL: deep_archive present"
test -d AgentCoordination/legacy_tickets && echo "FAIL: legacy_tickets present"
test -d tracking-assets/logs && echo "FAIL: tracking-assets/logs present"
ls -- "--help" "--output-dir" 2>/dev/null && echo "FAIL: V1 accidentals present"
test -d _marked_for_deletion_* && echo "FAIL: deletion marker present"
```

If any FAIL line prints, halt import and re-curate.

## Open questions

1. **`profiling/`** — top-level directory was visible in `git ls-files | awk` output but not audited; verify its content at import. Likely scaffolds for `Tools/profiling/` runs.
2. **`Projects/protocols/` and `Projects/gp_protocols/`** — referenced by CLAUDE.md but not enumerated in my inventory dump. Verify their tracked content at import.
3. **`Projects/archived_projects/`** — referenced by Stage 0 prompt's SKIP list, but `git ls-files | awk '{print $1}' | sort -u` doesn't show it as a top-level entry. Either (a) doesn't exist in V1 anymore (was deleted in the cleanup pass), or (b) it does exist but has no tracked content (just untracked files). Verify before V2 import.
4. **`.github/`** — listed top-level in my survey but I haven't dumped its tracked content. Audit before import; if outdated workflows / templates, do a Phase 17 follow-up to refresh.
5. **`tracking-assets/screenshots/`** content sweep — listed in `V2_GITATTRIBUTES_DRAFT.md` open questions.
