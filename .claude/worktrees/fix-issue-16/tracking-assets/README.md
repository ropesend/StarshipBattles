# tracking-assets

Binary assets attached to GitHub Issues — screenshots and logs.

This directory exists so agents can fully manage issue attachments via plain
git commits, instead of relying on GitHub's drag-and-drop attachment uploader
(which agents can't easily script).

## Layout

```
tracking-assets/
├── screenshots/
│   └── YYYY-MM/
│       └── issue-NNN-<slug>.png
└── logs/
    └── issue-NNN/
        └── <filename>
```

- **screenshots/** — bucketed by `YYYY-MM` (the month the screenshot was first
  attached, not the month the bug was filed). Filename convention:
  `issue-NNN-<short-slug>.<ext>`. Slug is derived from the issue title,
  lowercased, hyphenated, ≤30 chars.
- **logs/** — bucketed by issue number. One subdirectory per issue.

## Linking from issues

Use the `?raw=1` query string so the image renders inline on github.com:

```markdown
![hud overlap](https://github.com/ropesend/StarshipBattles/blob/main/tracking-assets/screenshots/2026-05/issue-127-hud-overlap.png?raw=1)
```

For logs, just link normally — github.com renders text files in-page:

```markdown
[combat log](https://github.com/ropesend/StarshipBattles/blob/main/tracking-assets/logs/issue-127/combat_2026-05-02.log)
```

## Commit hygiene

- Stage screenshots/logs in the same commit as the issue work, with message
  `chore(tracking): add assets for #NNN`.
- Don't commit raw QA-observer dumps here — copy only the relevant files.
- Don't delete assets when an issue closes; the closed-issue history should
  remain readable.

## Storage policy

No Git LFS in use. Plain git tracking. Revisit this decision if
`tracking-assets/` exceeds ~200 MB; at that point options are LFS migration
(`git lfs migrate`), retention policy (delete assets older than N years), or
external hosting.
