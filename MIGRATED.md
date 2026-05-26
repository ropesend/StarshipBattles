# This repository has migrated

`ropesend/StarshipBattles` is the V1 development repository for the
Starship Battles → Stellar Hegemony project. Active development
moved to **`ropesend/StellarHegemony`** on 2026-05-25/26, and this
V1 repository is now archived (read-only).

## New repository

- **GitHub:** https://github.com/ropesend/StellarHegemony
- **Local clone:**
  ```bash
  git clone https://github.com/ropesend/StellarHegemony.git
  cd StellarHegemony
  git lfs pull
  ```
- See the V2 `README.md` for quick-start and the
  `Planning/gitrepoV2/` directory for the full migration trail
  (source snapshot, classification, decisions, import checklist,
  validation receipts).

## Why the cutover?

V1 had accumulated ~16 GiB of historical pack weight (asset bloat
from earlier image regeneration passes, retired tooling, archival
project material). A clean cutover at V1 SHA `05c5b248c` with Git
LFS for runtime image assets, an off-Git vault for archival
material, and a fresh history was simpler than rewriting V1's
history in place.

## What about the issues / wiki / releases?

- GitHub Issues — see the V2 issues tab going forward. Active V1
  issues were resolved or recreated in V2 before archive (per the
  Phase 9 issue migration policy in
  `Planning/gitrepoV2/STAGE_0_DECISIONS.md`).
- Releases / tags — none beyond planning artifacts; V1's last
  pre-archive HEAD is tagged `v1-archive-final` for stable
  reference. (If the tag isn't present, the user opted out of
  tagging; the HEAD SHA at archive is recorded in V2's
  `PHASE_16_V1_ARCHIVE_RECEIPT.md`.)
