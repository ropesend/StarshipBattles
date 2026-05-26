# Stage 0 — Post-Cleanup Inventory Delta

> **Captured:** 2026-05-25 at HEAD `bc755f012`.
>
> This is a **delta report** against the prior inventory at
> [`.agent_reports/stage0_inventory/inventory_report.md`](../../.agent_reports/stage0_inventory/inventory_report.md)
> (2026-05-24, pre-cleanup). That earlier report is preserved for
> historical reference; do **not** treat it as current. The cleanup
> commits between `327d6824b` and `9aab233d7` on `main` (see the
> "Current status" block of `DETAILED_MIGRATION_PLAN.md`) shipped after
> it was written.

## Headline shift

| Metric | Pre-cleanup (2026-05-24) | Post-cleanup (2026-05-25) | Δ |
|---|---:|---:|---:|
| Tracked files | 18,743 | **12,590** | −6,153 (−33%) |
| Tracked bytes (working tree) | 18.00 GB | **4.76 GiB** | **−13.24 GiB (−74%)** |
| PNG count | 7,632 | 1,590 | −6,042 (−79%) |
| PNG bytes | 17.29 GB | 4.34 GiB | −12.95 GiB (−75%) |
| JPG count | 162 | 36 | −126 |
| `.gitattributes` | absent | absent | — |
| `.git` pack size | (not captured) | **15.95 GiB** | (still carries pre-cleanup blobs) |

The earlier Stage 0 prompt described the cleanup as "~1 GB of
regenerable / non-runtime content was removed from the V1 working tree."
**That was an understatement.** The actual tracked-content shrinkage is
~13 GiB. The cleanup removed not only regenerable derivatives but also
non-runtime workflow material: `Inspiration_Batch_*`,
`Earth/Mars/Moon/...` byte-mirror buckets, ShipTheme `Production/`
and `Original Art/` source folders, `Flags To Process/`,
`altcomponents/`, and the entire pre-existing resolution ladders for
planets and stars.

`size-pack: 15.95 GiB` still carries every blob ever committed; that's
why the **V2 clean cutover remains worthwhile** even with the V1
working tree already light. A `git clone` of V1 today is still ~16
GiB; V2 (LFS for masters only, no pre-cleanup history) lands well
under that.

## Tracked-content composition (post-cleanup)

### By extension (top 10)

```text
.png     1,590 files   4,337.7 MiB
.whl        80 files     302.3 MiB
.log        29 files     135.1 MiB
.jpg        36 files      72.6 MiB
.md      6,333 files      45.3 MiB
.json    1,496 files      24.9 MiB
.py      2,804 files      24.4 MiB
.txt       140 files       7.7 MiB
.prof        1 files       1.1 MiB
.csv         3 files       1.0 MiB
```

Code + docs + config combined are ~100 MiB — about 2.0% of working-tree
bytes. The migration is still asset-dominated, but no longer
catastrophically so.

### By directory (top, depth ≤ 3)

```text
4,398.4 MiB   1,624f   assets/
4,398.4 MiB   1,623f   assets/images/
2,613.3 MiB     530f   assets/images/planets/        # master is 2048/; derivatives gitignored
  871.3 MiB     340f   assets/images/ship_themes/
  640.6 MiB     540f   assets/images/components/     # master is 1024/; derivatives gitignored
  339.0 MiB   4,565f   Projects/
  335.8 MiB   3,997f   Projects/deep_archive/        # V2 SKIP
  305.3 MiB     584f   Projects/deep_archive/PROJ-251-300/  # V2 SKIP
   91.4 MiB      22f   assets/images/system_backgrounds/
   73.2 MiB     313f   AgentCoordination/
   72.5 MiB     195f   AgentCoordination/legacy_tickets/    # V2 SKIP
   71.7 MiB      21f   AgentCoordination/legacy_tickets/bug_logs/  # V2 SKIP
   71.4 MiB      48f   tracking-assets/
   64.1 MiB      14f   tracking-assets/logs/         # V2 SKIP (5 battle.log files >5 MiB)
   55.8 MiB      42f   assets/images/stars/          # master is 1024/
   43.5 MiB      60f   assets/images/flags/          # master is flag_*/1024/
   42.7 MiB      28f   assets/images/race_portraits/
   40.1 MiB   2,479f   Reviews/results/              # V2 SKIP
```

`assets/images/` is uniformly snake_case and flat (16 entries; no
`Images/`, `ShipThemes/`, `Stellar Objects/`, `Sphere world`,
`Warp Points/`, or `Flags/Processed/`):

```text
asteroids/  components/  cursor/  default_ship_portrait.png  flags/
modifier_icons/  nebulae/  planets/  race_portraits/  resource_icons/
resource_portraits/  ship_themes/  sphere_world/  stars/
system_backgrounds/  warp_points/
```

### Top 10 largest tracked files

```text
49.49 MiB   AgentCoordination/legacy_tickets/bug_logs/BUG-122_logs/battle.log
38.35 MiB   Projects/deep_archive/.../dryrun_full/opencv_python-4.13.0.92-...whl
38.35 MiB   Projects/deep_archive/.../dryrun/opencv_python-4.13.0.92-...whl
34.82 MiB   Projects/deep_archive/.../dryrun_full/scipy-1.17.1-...whl
34.82 MiB   Projects/deep_archive/.../dryrun/scipy-1.17.1-...whl
29.47 MiB   Projects/deep_archive/.../dryrun_full/pygame_gui-0.6.14-...whl
29.47 MiB   Projects/deep_archive/.../dryrun/pygame_gui-0.6.14-...whl
24.54 MiB   tracking-assets/logs/issue-19/battle.log
24.54 MiB   tracking-assets/logs/issue-17/battle.log
20.40 MiB   AgentCoordination/legacy_tickets/bug_logs/BUG-126_logs/battle.log
```

**Every file in the top 10 is in a V2 SKIP path.** The pattern from the
old report holds: a few battle-log files and the duplicated PROJ-295
wheels dominate the long tail. Past slot 14 the list goes to single
8–9 MiB PNGs in `assets/images/system_backgrounds/` (the Gemini-generated
single-resolution backdrops) and `assets/images/planets/2048/` masters
— both legitimate runtime content destined for LFS.

## V2 import-scope projection

Subtracting the SKIP paths from the 4.76 GiB working-tree total:

| Path | Size (MiB) | V2 bucket |
|---|---:|---|
| `Projects/deep_archive/` | 335.8 | SKIP |
| `AgentCoordination/legacy_tickets/` | 72.5 | SKIP |
| `tracking-assets/logs/` | 64.1 | SKIP (logs; rehome to vault or Issue attachments) |
| `Reviews/results/_archive_*` | ~17 | SKIP |
| `_marked_for_deletion_2026-*` | ~1.9 | SKIP |
| **V2-imported (before LFS)** | **~4,388 MiB (~4.28 GiB)** | IMPORT_GIT + IMPORT_LFS |

After applying path-scoped LFS to the master-size folders under
`assets/images/`, the **non-LFS Git working tree of V2 sits at roughly
100–200 MiB** (code + docs + data + single-resolution image families
that don't fit the size-tiered LFS rules — e.g.
`system_backgrounds/`, `race_portraits/`, `modifier_icons/`). The bulk
(~4.1 GiB) lives in LFS objects.

A fresh `git clone` of V2 (no LFS pull) pulls ~150 MiB instead of
~16 GiB. With `git lfs pull`, the user's machine ends up at roughly the
same size as today's working tree, but the history is clean and
multi-machine clones don't redundantly pay the 15.95 GiB pack tax for
content that was deleted before V2 ever existed.

## Fonts and audio: still nothing tracked

Same as the pre-cleanup report: zero `.ttf`/`.otf`/`.woff*` and zero
`.wav`/`.ogg`/`.mp3`/`.flac` in `git ls-files`. The earlier finding —
no font-licensing red flag, no audio LFS rule needed in Stage 0 — still
holds. The Stage 0 plan's audio placeholder (`assets/audio/`) is
correctly forward-looking, not retroactive.

## Verification grep result

Stage 0 prompt task A.3 (zero stale PascalCase asset path references in
live tracked sources): **clean.** Search across `game/`, `tests/`,
`Tools/`, repo-root config, and `Planning/gitrepoV2/` for
`assets/Images/`, `ShipThemes/`, `Stellar Objects/`, `StellarObjects/`,
`SphereWorld`, `Sphere world`, `Warp Points/`, `WarpPoints/`,
`Flags/Processed`, `Planets_V3`, `Stars_{128,256,512,1024}`,
`Inspiration_Batch` returned:

- `Tools/`: no matches.
- `game/`: one match — `game/ui/screens/fleet_data_source.py:50` on
  `"CreateSphereWorld"`. **False positive.** It's the registry key for a
  superweapon ability (siblings: `DestroyPlanet`, `OpenWarpPoint`,
  `CloseWarpPoint`, `DestroyStar` — none of which are asset paths).
- `tests/`: one match — the corresponding test on the same ability
  string. False positive.
- `.gitignore`: 11 lines under the deliberate "Legacy pre-rename
  size-folder names" block (lines 131–150). Intentional: those entries
  mute pre-rename leftover derivative directories so machines that ran
  the derivative engine before pulling the rename commits don't see
  them in `git status`. The block's own comment says it's safe to
  remove the old folders from disk; for V2 it's unnecessary and
  **gets dropped from `V2_GITIGNORE_DRAFT.md`**.
- `Planning/gitrepoV2/STAGE_0_PLAN.md` and `STAGE_0_NEW_AGENT_PROMPT.md`:
  matches inside narrative paragraphs explicitly calling out the old
  names as things the cleanup removed and Stage 0 must not reintroduce.
  Intended.

Nothing in production paths, tests, tools, or non-Stage-0 docs
references a stale asset folder. No standalone-fix commit needed.

## What this means for the rest of Task B / C

- **`V2_GITIGNORE_DRAFT.md`** (Phase 4 deliverable): start from the live
  V1 `.gitignore`, drop the "Legacy pre-rename size-folder names" block
  (lines 131–150) and the frozen-archive entries that won't exist in V2
  (`AgentCoordination/legacy_tickets/`-adjacent local state, etc.).
- **`V2_GITATTRIBUTES_DRAFT.md`** (Phase 5 deliverable): the path-scoped
  LFS skeleton in `STAGE_0_PLAN.md` Phase 5 covers the four size-tiered
  families exactly. Single-resolution families
  (`system_backgrounds/`, `race_portraits/`, `resource_icons/`,
  `resource_portraits/`, `modifier_icons/`, `sphere_world/`,
  `warp_points/`, `asteroids/`, `nebulae/`, `cursor/`,
  `default_ship_portrait.png`) need their own LFS lines too — the
  skeleton in `STAGE_0_PLAN.md` already lists them; cross-check
  against the actual file extensions when drafting (e.g.
  `asteroids/` is currently `.jpg/.jpeg`, not `.png`).
- **`MIGRATION_CLASSIFICATION.md`** (Phase 2 deliverable): top-level
  directories to classify (per `git ls-files | awk -F/ '{print $1}' |
  sort -u`) — exact list to confirm when drafting that file.
- **No standalone-fix commit needed.** The post-reorg state is
  consistent; the verification grep produced no leftover bugs.
