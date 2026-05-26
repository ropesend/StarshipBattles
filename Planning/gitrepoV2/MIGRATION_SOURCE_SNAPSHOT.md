# Stage 0 Migration Source Snapshot

> **Captured:** 2026-05-25
> **Last updated:** 2026-05-25 (cutover-SHA refresh; see history at bottom)
>
> This file records the exact V1-repo state at the moment Stage 0 V2-prep
> work began. It is the audit trail for "what we migrated from." Update
> it only if the Stage 0 prep work itself ships further commits before
> the V2 import; do not retroactively rewrite it after V2 exists.

## Source repository

- Repo: `ropesend/StarshipBattles`
- Default branch: `main`
- Local checkout path: `c:\Dev2\StarshipBattles`
- HEAD SHA: `bb3e86823f3ccf709d1482073852cb744ad0b326`
- HEAD subject: `docs(planning): add Stage 0 execution agent prompt (Phases 10-14)`

Verify with:

```bash
git rev-parse HEAD
# bb3e86823f3ccf709d1482073852cb744ad0b326
```

## Working-tree status

```text
$ git status --short
(clean — no output)
```

No uncommitted edits, no untracked tracked-eligible files. The HEAD
commit is the authoritative state at snapshot time.

## `.git` object / pack metrics

```text
$ git count-objects -vH
count: 4687
size: 997.60 MiB
in-pack: 97666
packs: 50
size-pack: 15.95 GiB
prune-packable: 102
garbage: 0
size-garbage: 0 bytes
```

Interpretation:

- **`size-pack: 15.95 GiB`** is the dominant number. It is the size of
  the pack history — every blob ever committed to `main`, including all
  the asset bloat removed in the 2026-05-27 working-tree cleanup. This
  is precisely the figure that motivates the Stage 0 clean cutover:
  the V1 working tree is already ~1 GB lighter post-cleanup, but a
  fresh `git clone` of V1 still pulls all 15.95 GiB of pack history.
- **`size: 997.60 MiB`** loose-object size and **`count: 4687`** loose
  objects reflect recent unpacked work (the asset reorganization
  commits + planning docs). A normal `git gc` would fold most of these
  into the pack; we deliberately do not run `gc` here so the snapshot
  reflects the actual on-disk state at handoff.
- **`packs: 50`** — many small packs, also a `git gc` candidate, but
  irrelevant to V2: V2 starts fresh.
- **`prune-packable: 102`** — duplicate loose copies of packed objects.
  Cosmetic.
- **`garbage: 0`** — clean.

## What is NOT in this snapshot

- No tracked-file inventory: that lives in
  [`inventory_post_cleanup.md`](inventory_post_cleanup.md) (paired
  artifact, generated in the same Stage 0 re-baseline pass).
- No verification grep results: those live in the re-baseline commit
  message and any follow-up standalone-fix commit.
- No remote-state record: we do not snapshot GitHub Issues / Releases
  / Actions state here. Issue migration is Phase 9 of the Stage 0 plan
  and gets its own deliverable (`ISSUE_MIGRATION_PLAN.md`) when the
  user decides on issue policy.

## Use

When V2 ships, the V2 `MIGRATION_LOG.md` should reference this file's
SHA as the "imported from" anchor. If the user ever wants to diff
"what V2 contains" vs "what V1 contained at cutover," `git diff
<this-SHA>..HEAD` on the V1 repo answers the V1-side question; the V2
import commit answers the V2-side question.

## Snapshot update history

The cutover SHA has been refreshed once between initial capture and V2
import kickoff, because additional planning-only commits landed on V1
`main` while Stage 0 planning artifacts were being authored. No code
or data changed; only docs under `Planning/gitrepoV2/` and one
agent-skill-usage counter file.

| Date       | SHA         | HEAD subject                                                       | Reason for update                                                              |
|------------|-------------|--------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 2026-05-25 | `bc755f012` | `docs(planning): add Stage 0 new-agent onboarding prompt`          | Initial snapshot capture.                                                       |
| 2026-05-25 | `bb3e86823` | `docs(planning): add Stage 0 execution agent prompt (Phases 10-14)` | Refresh at Phase 10 kickoff after 10 planning-only commits accumulated on main. |

Diff between the two anchors (V1 side): `git diff bc755f012..bb3e86823 --stat`
shows planning artifacts only — no `game/`, `tests/`, `assets/`, `data/`, or
`docs/` touched.
