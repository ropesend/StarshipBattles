# V2 `.gitattributes` Draft (Path-Scoped LFS)

> **Drafted:** 2026-05-25 against V1 HEAD `bc755f012`. Status: **draft, pending user review.**
>
> Policy: **path-scoped LFS** per the settled section of `STAGE_0_DECISIONS.md` and `STAGE_0_PLAN.md` Phase 5. **Not** extension-scoped (`*.png filter=lfs`) — extension-scoping would LFS-track generated derivative PNGs alongside masters, which the per-family `game.assets.image_derivatives` engine produces on every startup.
>
> The rules below are the Phase 5 skeleton, **corrected** against the live V1 tree's actual file extensions (verified 2026-05-25):
>
> - `cursor/` is **`.png`, not `.jpg`** as the Phase 5 skeleton claimed.
> - `race_portraits/` is **`.jpg` only**, no `.png` tracked.
> - `asteroids/` is `.jpg` only (confirmed).
> - `system_backgrounds/` is mixed `.jpg` + `.png` (confirmed).
> - `ship_themes/<Theme>/portraits/` is optional per the theme schema; the rule applies to all themes regardless (no-op for themes that lack portraits, like Aetherwake currently).
>
> **Decision-sensitive assumptions** (settle in Task D):
>
> - Whether the V2 GitHub plan tier provides enough LFS storage + bandwidth. Free/Pro give 10 GiB; Team/Enterprise give 250 GiB. The projected V2 LFS footprint is ~4.1 GiB (see `inventory_post_cleanup.md`), well under 10 GiB headroom-wise; but bandwidth (downloads per month) is also 10 GiB on Free/Pro and 250 GiB on higher tiers, and *every fresh clone of every machine* draws from that pool. If we expect >2 fresh clones per month, Free/Pro will throttle.

## Proposed `.gitattributes`

```gitattributes
# ============================================================================
# Stellar Hegemony .gitattributes — path-scoped Git LFS rules
#
# Policy: each multi-size image-asset family tracks ONE master size
# in source control (in LFS); sibling sizes are regenerated locally at
# startup by `game.assets.image_derivatives` and gitignored.
#
# Master sizes per family (canonical, see docs/03_CONVENTIONS.md
# "Image Asset Derivatives"):
#   components/1024/         master = 1024px PNG
#   flags/flag_*/1024/       master = 1024px PNG, per flag
#   stars/1024/              master = 1024px PNG
#   planets/2048/            master = 2048px PNG (larger than other families)
#
# Single-resolution families are LFS-tracked at their canonical path.
# Format mix (PNG vs JPG) follows whatever is currently tracked in V1;
# new image assets must be PNG per docs/03_CONVENTIONS.md.
# ============================================================================

# Size-tiered master directories
assets/images/components/1024/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/flags/flag_*/1024/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/stars/1024/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/planets/2048/*.png filter=lfs diff=lfs merge=lfs -text

# Ship-theme single-resolution per-class art (PNG only per the theme schema)
assets/images/ship_themes/*/skins/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/ship_themes/*/portraits/*.png filter=lfs diff=lfs merge=lfs -text

# Single-resolution PNG families
assets/images/cursor/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/modifier_icons/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/nebulae/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/resource_icons/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/resource_portraits/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/sphere_world/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/warp_points/*.png filter=lfs diff=lfs merge=lfs -text

# Single-resolution JPG families (legacy; migrate to PNG when touched
# per docs/03_CONVENTIONS.md "Image Assets")
assets/images/asteroids/*.jpg filter=lfs diff=lfs merge=lfs -text
assets/images/asteroids/*.jpeg filter=lfs diff=lfs merge=lfs -text
assets/images/race_portraits/*.jpg filter=lfs diff=lfs merge=lfs -text
assets/images/race_portraits/*.jpeg filter=lfs diff=lfs merge=lfs -text

# Mixed-format family
assets/images/system_backgrounds/*.png filter=lfs diff=lfs merge=lfs -text
assets/images/system_backgrounds/*.jpg filter=lfs diff=lfs merge=lfs -text
assets/images/system_backgrounds/*.jpeg filter=lfs diff=lfs merge=lfs -text

# Top-level single files
assets/images/default_ship_portrait.png filter=lfs diff=lfs merge=lfs -text

# tracking-assets/screenshots — likely large issue screenshots. LFS by path
# scope; the directory's actual content is mixed and will need a sweep at
# import. Conservative: LFS-track all images under it.
tracking-assets/screenshots/**/*.png filter=lfs diff=lfs merge=lfs -text
tracking-assets/screenshots/**/*.jpg filter=lfs diff=lfs merge=lfs -text
tracking-assets/screenshots/**/*.jpeg filter=lfs diff=lfs merge=lfs -text

# ============================================================================
# Audio + fonts: track via LFS when added. Currently zero files in V1;
# rules placed pre-emptively so the first `git add` of audio/font content
# routes through LFS automatically.
# Fonts are license-gated — do NOT add commercial fonts without license review.
# ============================================================================
assets/audio/**/*.wav filter=lfs diff=lfs merge=lfs -text
assets/audio/**/*.ogg filter=lfs diff=lfs merge=lfs -text
assets/audio/**/*.mp3 filter=lfs diff=lfs merge=lfs -text
assets/audio/**/*.flac filter=lfs diff=lfs merge=lfs -text
assets/fonts/**/*.ttf filter=lfs diff=lfs merge=lfs -text
assets/fonts/**/*.otf filter=lfs diff=lfs merge=lfs -text
```

## What every asset path falls into

Cross-check against the live tree (`git ls-files assets/images/` + extension audit, 2026-05-25):

| Path | Files (V1) | Format | V2 disposition |
|---|---:|---|---|
| `assets/images/components/1024/` | ~540 | PNG | **LFS** (master tier) |
| `assets/images/components/{64,128,256,512,2048}/` | 0 tracked | — | **gitignored** (regenerated) |
| `assets/images/components/.component_derivatives_manifest.json` | 0 tracked | — | **gitignored** |
| `assets/images/flags/flag_*/1024/*.png` | ~3 per flag × ~15 flags ≈ 45 | PNG | **LFS** (master tier) |
| `assets/images/flags/flag_*/<other-size>/` | 0 tracked | — | **gitignored** (regenerated) |
| `assets/images/flags/flag_*/flag_*.caption.json` | 1 per flag | JSON | plain Git (metadata) |
| `assets/images/stars/1024/` | ~42 | PNG | **LFS** (master tier) |
| `assets/images/stars/{128,256,512}/` | 0 tracked | — | **gitignored** |
| `assets/images/planets/2048/` | ~530 | PNG | **LFS** (master tier) |
| `assets/images/planets/{128,256,512,1024}/` | 0 tracked | — | **gitignored** |
| `assets/images/ship_themes/<Theme>/skins/` | 19 per theme × 9 themes = 171 | PNG | **LFS** |
| `assets/images/ship_themes/<Theme>/portraits/` | up to 19 per theme × 8 themes ≈ 152 | PNG | **LFS** (optional per schema; Aetherwake currently has none) |
| `assets/images/ship_themes/<Theme>/theme.json` | 9 | JSON | plain Git |
| `assets/images/ship_themes/<Theme>/theme.caption.json` | 9 | JSON | plain Git |
| `assets/images/asteroids/` | ~3 | JPG | **LFS** |
| `assets/images/cursor/` | ~3 | PNG | **LFS** |
| `assets/images/modifier_icons/` | ~14 | PNG | **LFS** |
| `assets/images/nebulae/` | ~5 | PNG | **LFS** |
| `assets/images/race_portraits/` | ~28 | JPG (+ JSON metadata) | **LFS** for JPG; plain Git for JSON |
| `assets/images/resource_icons/` | ~6 | PNG | **LFS** |
| `assets/images/resource_portraits/` | ~10 | PNG | **LFS** |
| `assets/images/sphere_world/` | ~1 | PNG | **LFS** |
| `assets/images/system_backgrounds/` | ~22 | JPG + PNG | **LFS** |
| `assets/images/warp_points/` | ~3 | PNG | **LFS** |
| `assets/images/default_ship_portrait.png` | 1 | PNG | **LFS** |
| `assets/asset_manifest.json` | 1 | JSON | plain Git |
| `assets/audio/` | 0 | — | placeholder; rule pre-armed |
| `assets/fonts/` | 0 | — | placeholder; rule pre-armed (license-gated) |

**Every asset path is either covered by an LFS rule or explicitly gitignored.** No asset content slips into plain Git as a large binary.

## What this draft deliberately does NOT do

- **Does not LFS the `.json` metadata files** in `ship_themes/<Theme>/`, `race_portraits/`, or `flags/flag_*/`. JSON is small, diff-friendly, and absolutely must NOT be filtered through LFS — diffs would become opaque.
- **Does not LFS `Reviews/` or `Projects/` content.** Those subtrees do not contain large binaries in V2 (the archival material is excluded from import).
- **Does not LFS `combat_lab/data/`.** Test fixtures are JSON + tiny PNGs (no large binaries there in the V1 inventory).
- **Does not introduce a fallback `*.png filter=lfs` umbrella rule.** That would catch generated derivatives the moment someone forgot to update `.gitignore`. The "safety net" is the gitignore patterns, not a broad LFS catch-all.

## Setup notes (for V2 Phase 10)

When the user creates V2 and first clones it locally, before any `git add` of assets:

```bash
git lfs install
# .gitattributes ships in the first hygiene commit (Phase 10 step 4).
# Verify rules are active:
git lfs track   # should list all the patterns above
```

After the first asset import (Phase 12), verify what actually went to LFS:

```bash
git lfs status
git lfs ls-files | head -20  # spot-check master-size files appear
git ls-files | xargs -I{} git check-attr filter -- {} | grep -v 'filter: lfs' | head -20
# the second command lists files NOT routed through LFS; verify only
# JSON / source / docs appear, no large PNG/JPG masters
```

## Exit criteria

- `.gitattributes` draft written. ✓
- LFS extensions reviewed against inventory: every `assets/images/` path is covered by either an LFS rule or a gitignore rule (cross-check above). ✓
- Font licensing question flagged: yes, in the rules section (license-gated). ✓
- Generated/scaled assets excluded from LFS via the gitignore-not-gitattributes split. ✓
- `tracking-assets/screenshots/` LFS-tracked conservatively pending an import-time sweep.

## Open questions

1. **GitHub plan tier (Task D).** Free/Pro = 10 GiB LFS storage + 10 GiB/mo bandwidth; Team = 250 GiB each. Projected V2 LFS payload is ~4.1 GiB. Storage fits Free/Pro. Bandwidth headroom on Free/Pro is ~2.5 fresh clones/month per machine before throttling. If you expect to set up V2 on multiple machines + CI + occasional clean re-clones, Team starts to look necessary.
2. **`tracking-assets/screenshots/` content sweep.** Today V1 has a `screenshots/` directory but I haven't audited its actual content. Need a small import-time sweep: if anything in there is over a few hundred KB, LFS is correct; if it's all small thumbnails, the rule is harmless overhead. (Listed in `V2_IMPORT_CHECKLIST.md`.)
