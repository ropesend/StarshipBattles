# tracking-assets/projects/

Static reference docs for GitHub-backed projects in the `claude-gp-*` skill
family. One subdirectory per project, keyed by GitHub issue number with the
`GP-` prefix.

```
tracking-assets/projects/
├── GP-<n>/                       # active project assets
│   ├── design.md                 # architecture analysis, rationale (never mutated post-planning)
│   ├── manifest.md               # initial planned-files manifest (never mutated post-planning)
│   ├── findings/                 # swarm reports, source triage, baseline measurements
│   │   └── *.md
│   └── consults/
│       └── round-N/              # archived codex consult artifacts
│           ├── request.md
│           └── response.md
└── archived/
    └── GP-<n>/                   # closed projects (moved here by /claude-gp-close)
```

## What lives here

- **Static** reference docs that don't change after the project is planned:
  design rationale, swarm-finding reports, initial planned-files manifest.
- Archived codex consult artifacts (`request.md` + `response.md` per round).
  These are copies — originals stay in `AgentCoordination/Scratchpad/Consult/`
  during the consult itself.

## What does NOT live here

- **Live project state.** Status, phase progress, current state handoff, and
  the live touched-files conflict surface all live on the GitHub issue
  (parent body, sub-issue bodies, comments, labels, board fields). Putting
  mutable state under `tracking-assets/` reintroduces the merge-conflict
  problem the GP system is designed to eliminate.
- **Decision log.** Project-wide decisions are parent-issue comments
  (`### Decision N — <title>`). Phase-implementation decisions are
  sub-issue comments. There is no project-local `decisions.md`.
- **`log.txt` from consult artifacts.** Logs may contain local paths; archive
  them manually only when investigating a failure.

## Size budget

- **Warn above 500 KB** per project asset directory.
- **Require explicit user approval above 2 MB** or for binary/non-Markdown
  additions.

Measured baselines: largest historical project assets (PROJ-410 swarm-findings
inclusive) ran ~95 KB. The 500 KB cap gives 5× headroom while preventing
findings inflation.

## Naming

- Active project: `GP-<n>/` where `<n>` is the GitHub issue number, no padding.
- Archived: `archived/GP-<n>/` — moved by `/claude-gp-close`, not by hand.
- Never reuse the legacy `PROJ-NNN` prefix here; that namespace is owned by
  the parallel `Projects/active_projects/` system.

## Linking from issues

Reference assets from issue bodies and comments using `?raw=1` for inline
rendering:

```markdown
[design.md](https://github.com/ropesend/StarshipBattles/blob/main/tracking-assets/projects/GP-512/design.md)
```

## Commit hygiene

- Stage assets in the same commit as project creation, with message
  `chore(gp): add assets for GP-<n>`.
- After commit, flip the parent issue's `asset-state:pending` label to
  `asset-state:committed`.
- Don't delete assets when a project closes; the closed-project history
  should remain readable. `/claude-gp-close` moves the directory into
  `archived/`, it does not delete.

## Storage policy

Inherits the repo-wide policy from `tracking-assets/README.md`: plain git,
no Git LFS, ~200 MB repository-level review threshold.
