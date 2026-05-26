# V2 Import Checklist

> **Drafted:** 2026-05-25 against V1 HEAD `bc755f012`. Status: **draft, pending user review.**
>
> Action-ordered companion to [`MIGRATION_CLASSIFICATION.md`](MIGRATION_CLASSIFICATION.md). When the user runs Phases 11–13 of `STAGE_0_PLAN.md` (source import → asset import → planning/agent-config import), this is the source of truth for what to copy from V1, what to curate, and what to omit. Classification still answers "what bucket?"; this answers "what's the actual import command for this phase?"
>
> The V1 `.git` pack history (15.95 GiB, including all the pre-cleanup blobs) is **deliberately not preserved**. V2 starts with a fresh `git init` and a clean cutover — that's the entire point of Stage 0.

## Settled Task D decisions (2026-05-25)

The following inputs to this checklist are now settled. See [`STAGE_0_DECISIONS.md`](STAGE_0_DECISIONS.md) for full rationale.

1. **V2 root directory name:** `StellarHegemony/`. Settled.
2. **`Projects/active_projects/` content:** **drop all V1 content** (PROJ-481..499 + `Batch_*_Prompt.txt` + `_doc_consolidation/`). Vault under `<vault>/old_repo_exports/v1_active_projects/`. V2 ships with an empty `Projects/active_projects/` directory.
3. **`Projects/` infrastructure (README, index, protocols, gp_protocols):** keep as scaffolding.
4. **`AgentCoordination/protocols/` curation set:** all six files imported as-is.
5. **`Reviews/` import scope:** import top-level only; `Reviews/results/` to vault.
6. **`AgentCoordination/templates/`:** path does not exist in V1; references dropped from `STAGE_0_NEW_AGENT_PROMPT.md`, `STAGE_0_PLAN.md`, and `DETAILED_MIGRATION_PLAN.md`. V2 does NOT create this directory.

## Phase 11 — Source import (run after `.gitignore` + `.gitattributes` first-hygiene commit)

Working assumption: V2 working tree is at `<v2-checkout>/`; V1 working tree is at `<v1-checkout>/` (the current `c:/Dev2/StarshipBattles/`).

### Copy verbatim

```bash
# Source, tests, data, docs, top-level configs. Everything tracked under
# these paths goes to V2 plain Git as-is.

cp -r <v1-checkout>/game            <v2-checkout>/game
cp -r <v1-checkout>/tests           <v2-checkout>/tests
cp -r <v1-checkout>/data            <v2-checkout>/data
cp -r <v1-checkout>/docs            <v2-checkout>/docs

cp <v1-checkout>/AGENTS.md          <v2-checkout>/
cp <v1-checkout>/CLAUDE.md          <v2-checkout>/
cp <v1-checkout>/pyproject.toml     <v2-checkout>/   # update `name = "stellar-hegemony"` post-copy
cp <v1-checkout>/requirements.txt   <v2-checkout>/
cp <v1-checkout>/requirements-dev.txt <v2-checkout>/
cp <v1-checkout>/pytest.ini         <v2-checkout>/
cp <v1-checkout>/mypy.ini           <v2-checkout>/
cp <v1-checkout>/opencode.json      <v2-checkout>/
cp <v1-checkout>/.python-version    <v2-checkout>/
cp <v1-checkout>/conftest.py        <v2-checkout>/
cp <v1-checkout>/launcher.py        <v2-checkout>/
cp <v1-checkout>/qa_launcher.py     <v2-checkout>/

cp -r <v1-checkout>/combat_lab      <v2-checkout>/combat_lab
# After copy, in V2:
rm -f <v2-checkout>/combat_lab/battle.log
rm -rf <v2-checkout>/combat_lab/battle_states
rm -rf <v2-checkout>/combat_lab/test_history
# These are gitignored regardless, but removing them from the copy keeps
# `git status` clean and avoids them being read by mistake during smoke tests.

cp -r <v1-checkout>/Tools           <v2-checkout>/Tools
# After copy, in V2:
rm -rf <v2-checkout>/Tools/qa_observer/session_data
rm -f  <v2-checkout>/Tools/regenerate_ship_portraits/last_run.json
# Same reason as above.
```

### Verify before commit

```bash
cd <v2-checkout>
git status --short                                        # everything new should be tracked
git diff --stat --cached | tail -20                       # spot-check sizes
# Confirm no docs/_ignore content slipped in:
git ls-files docs/_ignore/ 2>&1 | head -5 | grep -q '^$' && echo OK || echo FAIL
# Confirm no test-output / pyc / cache in tests:
find <v2-checkout>/tests -name __pycache__ -o -name '*.pyc' | head
```

### Commit

```bash
git add game tests data docs combat_lab Tools \
        AGENTS.md CLAUDE.md pyproject.toml requirements*.txt \
        pytest.ini mypy.ini opencode.json .python-version \
        conftest.py launcher.py qa_launcher.py
git commit -m "Import V1 source, tests, data, docs, combat_lab, Tools (from <v1-sha>)"
```

## Phase 12 — Asset import (LFS-routed)

Working assumption: `.gitattributes` from `V2_GITATTRIBUTES_DRAFT.md` is already in the first hygiene commit; `git lfs install` already run.

### Copy verbatim (LFS-routed at add time)

```bash
cp -r <v1-checkout>/assets <v2-checkout>/assets
```

That's it for the copy. The 4.4 GiB of `assets/` content is mostly:
- Master-size PNGs in `components/1024/`, `flags/flag_*/1024/`, `stars/1024/`, `planets/2048/` (LFS-routed by `.gitattributes`).
- Single-resolution PNG/JPG runtime images in `cursor/`, `modifier_icons/`, `nebulae/`, `race_portraits/`, `resource_icons/`, `resource_portraits/`, `sphere_world/`, `system_backgrounds/`, `warp_points/`, `asteroids/`, `default_ship_portrait.png` (LFS-routed).
- Per-theme `ship_themes/<Theme>/{skins,portraits}/` (LFS-routed).
- JSON metadata (`asset_manifest.json`, `theme.json`, `theme.caption.json`, flag captions, race portrait metadata) — plain Git.

No derivative size folders should be present in V1 (the V1 cleanup pass dropped them); spot-check:

```bash
# Should all be empty:
find <v2-checkout>/assets/images/components/{64,128,256,512,2048} -type f 2>/dev/null | head
find <v2-checkout>/assets/images/flags/flag_*/{32,64,128,256,512} -type f 2>/dev/null | head
find <v2-checkout>/assets/images/stars/{128,256,512} -type f 2>/dev/null | head
find <v2-checkout>/assets/images/planets/{128,256,512,1024} -type f 2>/dev/null | head
# Should also be empty:
find <v2-checkout>/assets/images -name '.*_derivatives_manifest.json' | head
```

If any of these print content, halt and investigate before commit — derivative content sneaked into V1's tracked tree at some point and the gitignore patterns failed to catch it.

### Verify before commit

```bash
cd <v2-checkout>
git lfs status                                            # confirms LFS-tracked masters
git lfs ls-files | wc -l                                  # spot-check count vs inventory_post_cleanup.md
git lfs ls-files | head -5                                # spot-check format
# Confirm theme JSON went through plain Git (NOT LFS):
git check-attr filter assets/images/ship_themes/Federation/theme.json
# Should print: assets/images/ship_themes/Federation/theme.json: filter: unspecified
```

### Commit

```bash
git add assets
git commit -m "Import V1 runtime assets via LFS (from <v1-sha>)"
```

Verify `git push --dry-run` reports the expected LFS object count. (Hold off actual push until full validation; this commit just sits locally until Phase 14.)

## Phase 13 — Planning, projects, agent-config import (curated)

### Copy with curation: Planning/

```bash
cp -r <v1-checkout>/Planning <v2-checkout>/Planning

# Drop empty CURRENT_STATE.md scaffolds:
for f in <v2-checkout>/Planning/0[1-8]_*/CURRENT_STATE.md; do
  if [ -f "$f" ] && [ $(wc -c < "$f") -lt 200 ]; then
    rm -f "$f"
  fi
done
# Drop the V1-only onboarding artifact (no longer applicable post-V2):
rm -f <v2-checkout>/Planning/gitrepoV2/STAGE_0_NEW_AGENT_PROMPT.md
```

### Copy with curation: Projects/

Per settled Task D decisions: keep the project-system infrastructure (`README.md`, `index.md`, `protocols/`, `gp_protocols/`); ship `active_projects/` empty. The V1 PROJ-XXX content + Batch + _doc_consolidation moves to the vault, not V2.

```bash
# Scaffolding only — no V1 active-project content.
mkdir -p <v2-checkout>/Projects/active_projects   # empty placeholder
cp <v1-checkout>/Projects/README.md   <v2-checkout>/Projects/
cp <v1-checkout>/Projects/index.md    <v2-checkout>/Projects/
if [ -d <v1-checkout>/Projects/protocols ]; then
  cp -r <v1-checkout>/Projects/protocols     <v2-checkout>/Projects/
fi
if [ -d <v1-checkout>/Projects/gp_protocols ]; then
  cp -r <v1-checkout>/Projects/gp_protocols  <v2-checkout>/Projects/
fi

# Drop a brief README into Projects/active_projects/ so V2 doesn't ship
# with a bare empty directory (Git won't track empty dirs anyway):
cat > <v2-checkout>/Projects/active_projects/README.md <<'EOF'
# Active Projects

V2 starts with no carried-forward active projects. V1's PROJ-481..499,
Batch_*_Prompt.txt, and _doc_consolidation/ folders are preserved in
the external artifact vault at
`<vault>/old_repo_exports/v1_active_projects/` for forensic access.

New V2 projects land here as `PROJ-NNN/` folders following the
protocols in `../protocols/` and `../gp_protocols/`.
EOF

# Explicitly NOT copied:
# - <v1-checkout>/Projects/deep_archive               (VAULT)
# - <v1-checkout>/Projects/archived_projects           (VAULT, if exists)
# - <v1-checkout>/Projects/active_projects/PROJ-*      (VAULT: v1_active_projects/)
# - <v1-checkout>/Projects/active_projects/Batch_*     (VAULT: v1_active_projects/)
# - <v1-checkout>/Projects/active_projects/_doc_*      (VAULT: v1_active_projects/)
```

**Vault step (before this Phase-13 commit):** copy the dropped V1 active-project content to the vault:

```bash
# Run once, before the V2 active_projects/ Phase-13 commit lands.
VAULT="<absolute-path-to-vault-root>"
mkdir -p "$VAULT/old_repo_exports/v1_active_projects"
cp -r <v1-checkout>/Projects/active_projects/PROJ-*              "$VAULT/old_repo_exports/v1_active_projects/"
cp    <v1-checkout>/Projects/active_projects/Batch_*_Prompt.txt  "$VAULT/old_repo_exports/v1_active_projects/" 2>/dev/null || true
cp -r <v1-checkout>/Projects/active_projects/_doc_consolidation  "$VAULT/old_repo_exports/v1_active_projects/" 2>/dev/null || true
```

### Copy with curation: AgentCoordination/

```bash
mkdir -p <v2-checkout>/AgentCoordination
cp <v1-checkout>/AgentCoordination/README.md       <v2-checkout>/AgentCoordination/
cp <v1-checkout>/AgentCoordination/SCRATCHPAD.md   <v2-checkout>/AgentCoordination/
cp -r <v1-checkout>/AgentCoordination/protocols    <v2-checkout>/AgentCoordination/
cp -r <v1-checkout>/AgentCoordination/discovered_issues <v2-checkout>/AgentCoordination/

# Explicitly NOT copied:
# - <v1-checkout>/AgentCoordination/legacy_tickets   (VAULT)
# - <v1-checkout>/AgentCoordination/Scratchpad       (SKIP, gitignored)
# - <v1-checkout>/AgentCoordination/local            (SKIP, gitignored)
# - <v1-checkout>/AgentCoordination/generated        (SKIP; V2 starts clean,
#                                                     by_install/*.json files are
#                                                     per-installation and the
#                                                     summary.json is gitignored)
# - <v1-checkout>/AgentCoordination/opencodereview   (SKIP, gitignored)
# - <v1-checkout>/AgentCoordination/templates        (does not exist in V1;
#                                                     references dropped from
#                                                     prompts/plans per Task D)
```

### Copy with curation: Reviews/

Default (per the decision-sensitive assumption above): import top-level only.

```bash
cp <v1-checkout>/Reviews/README.md                  <v2-checkout>/Reviews/
cp <v1-checkout>/Reviews/Review_Report_2026_01_27.md <v2-checkout>/Reviews/
cp <v1-checkout>/Reviews/reviews_index.md           <v2-checkout>/Reviews/
cp -r <v1-checkout>/Reviews/prompts                 <v2-checkout>/Reviews/
cp -r <v1-checkout>/Reviews/protocols               <v2-checkout>/Reviews/
cp -r <v1-checkout>/Reviews/scripts                 <v2-checkout>/Reviews/

# Explicitly NOT copied:
# - <v1-checkout>/Reviews/results (VAULT)
```

If Task D resolves "drop the entire folder," skip this block and instead copy `Reviews/` whole to `<vault>/old_repo_exports/v1_reviews/`.

### Copy with curation: tracking-assets/

```bash
cp <v1-checkout>/tracking-assets/README.md          <v2-checkout>/tracking-assets/
cp -r <v1-checkout>/tracking-assets/projects        <v2-checkout>/tracking-assets/
cp -r <v1-checkout>/tracking-assets/screenshots     <v2-checkout>/tracking-assets/

# Explicitly NOT copied:
# - <v1-checkout>/tracking-assets/logs (VAULT)
```

After copy, audit `tracking-assets/screenshots/` for files >1 MiB — those should be LFS-tracked (the `.gitattributes` rule should handle this automatically; verify with `git lfs status` after `git add`).

### Copy with curation: dotfile dirs

```bash
# .github/ — copy if present in V1
if [ -d <v1-checkout>/.github ]; then
  cp -r <v1-checkout>/.github <v2-checkout>/.github
fi

# .codex/ — only the tracked config.toml
mkdir -p <v2-checkout>/.codex
cp <v1-checkout>/.codex/config.toml <v2-checkout>/.codex/

# .claude/ — skills + example settings only
mkdir -p <v2-checkout>/.claude
cp -r <v1-checkout>/.claude/skills <v2-checkout>/.claude/
cp <v1-checkout>/.claude/settings.example.json <v2-checkout>/.claude/

# .agent/ — Antigravity skills (lower priority but tracked)
cp -r <v1-checkout>/.agent <v2-checkout>/.agent

# .agents/ — Codex top-level + skills
cp -r <v1-checkout>/.agents <v2-checkout>/.agents

# .opencode/ — commands + skills + npm deps (NOT node_modules)
mkdir -p <v2-checkout>/.opencode
cp -r <v1-checkout>/.opencode/commands   <v2-checkout>/.opencode/
cp -r <v1-checkout>/.opencode/skills     <v2-checkout>/.opencode/
cp    <v1-checkout>/.opencode/package.json <v2-checkout>/.opencode/
cp    <v1-checkout>/.opencode/package-lock.json <v2-checkout>/.opencode/

# Explicitly NOT copied:
# - .claude/settings.json (per-machine)
# - .claude/settings.local.json (per-machine secrets/env)
# - .claude/settings.*.backup.* (gitignored)
# - .claude/scheduled_tasks.lock (runtime)
# - .claude/worktrees/ (gitignored)
# - .codex/sessions/ (gitignored per .codex/*)
# - .opencode/node_modules/ (gitignored)
```

### Commit

```bash
cd <v2-checkout>
git add Planning Projects AgentCoordination Reviews tracking-assets \
        .github .codex .claude .agent .agents .opencode
git commit -m "Import V1 planning, projects, agent config (curated; from <v1-sha>)"
```

## Phase 13.5 — Author V2-specific tracked files

These do not exist in V1 and are written fresh for V2.

```bash
# Top-level README.md (introductory; this is a Phase 17 follow-up to author
# in detail, but at minimum a placeholder so V2 doesn't ship with no README):
cat > <v2-checkout>/README.md <<'README_EOF'
# Stellar Hegemony

[describe game, build, run, link to docs/]
README_EOF

# External-artifact example config:
cat > <v2-checkout>/external_artifacts.example.json <<'EXAMPLE_EOF'
{
  "provider": "google_drive",
  "external_artifact_root": "<path-to-vault-root-on-this-machine>",
  ...
}
EXAMPLE_EOF
# (See EXTERNAL_ARTIFACT_POLICY.md for the full schema.)

git add README.md external_artifacts.example.json
git commit -m "Add V2 top-level README placeholder + external-artifact example config"
```

## What must NOT enter V2 — sweep list

Run before each commit; any FAIL halts the import:

```bash
test -d <v2-checkout>/Projects/deep_archive       && echo "FAIL: Projects/deep_archive"
test -d <v2-checkout>/Projects/archived_projects  && echo "FAIL: Projects/archived_projects"
test -d <v2-checkout>/AgentCoordination/legacy_tickets && echo "FAIL: legacy_tickets"
test -d <v2-checkout>/AgentCoordination/Scratchpad     && echo "FAIL: Scratchpad"
test -d <v2-checkout>/AgentCoordination/local          && echo "FAIL: AgentCoordination/local"
test -d <v2-checkout>/AgentCoordination/opencodereview/local && echo "FAIL: opencodereview/local"
test -d <v2-checkout>/Reviews/results             && echo "FAIL: Reviews/results"
test -d <v2-checkout>/tracking-assets/logs        && echo "FAIL: tracking-assets/logs"
test -d <v2-checkout>/output                      && echo "FAIL: output"
test -d <v2-checkout>/.agent_reports              && echo "FAIL: .agent_reports"
test -d <v2-checkout>/.pytest_cache               && echo "FAIL: .pytest_cache"
test -d <v2-checkout>/.opencode/node_modules      && echo "FAIL: opencode node_modules"
test -d <v2-checkout>/combat_lab/test_history     && echo "FAIL: combat_lab/test_history"
test -d <v2-checkout>/combat_lab/battle_states    && echo "FAIL: combat_lab/battle_states"
test -d <v2-checkout>/Tools/qa_observer/session_data && echo "FAIL: qa_observer/session_data"

# V1 accidentally-tracked artifacts:
test -d "<v2-checkout>/--help"                    && echo "FAIL: --help dir"
test -d "<v2-checkout>/--output-dir"              && echo "FAIL: --output-dir dir"
test -f <v2-checkout>/.coverage                   && echo "FAIL: .coverage"
test -f <v2-checkout>/panel_profile.prof          && echo "FAIL: panel_profile.prof"
ls <v2-checkout>/test_profiling_*.json* 2>/dev/null | head -1 | grep -q . && echo "FAIL: test_profiling_*.json*"

# Pre-deletion staging buckets:
ls -d <v2-checkout>/_marked_for_deletion_* 2>/dev/null | head -1 | grep -q . && echo "FAIL: _marked_for_deletion_*"

# V1 derivative manifests (should NOT enter V2 even by accident):
find <v2-checkout>/assets/images -name '.*_derivatives_manifest.json' 2>/dev/null | head -1 | grep -q . \
  && echo "FAIL: derivative manifests present"
```

If any FAIL fires, fix and re-sweep before committing.

## Open questions

1. **Top-level README.md content** — V1 has none. Phase 17 follow-up. Placeholder shipped at import.
2. **`Projects/protocols/` and `Projects/gp_protocols/` content** — verify at import.
3. **`.github/` content audit** — outdated workflows may need refresh in Phase 17.
4. **`tracking-assets/screenshots/` content sweep** — verify LFS routing matches expected file sizes.
5. **`profiling/` directory content** — verify whether to import or drop.

## Done when

- All Phase 11/12/13 commits land in the V2 working tree.
- Every FAIL line in the sweep above returns empty.
- `git lfs status` reports expected LFS object count (~1,400 per `MIGRATION_CLASSIFICATION.md`).
- `git status --short` shows clean tree after the last commit.
- Ready for Phase 14 (fresh-clone validation).
