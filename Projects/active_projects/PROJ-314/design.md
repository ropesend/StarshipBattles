# PROJ-314: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis (Phase A)

### Foundation
- `docs/01_ARCHITECTURE.md` reviewed: layer structure (UI → Assets →
  Strategy → Simulation → Engine → Services → Core); `ApplicationContext`
  is the DI container (~9 services).
- `docs/02_PATTERNS.md` reviewed: 30 patterns, most relevant to PROJ-314 are
  Singleton-Free DI, Protocol + TypeGuard, Provider Factory, Background
  Service Call (#28).
- `docs/03_CONVENTIONS.md` lines 261, 285–288 reviewed: paths must use
  `Paths.*` constants; all image assets must be PNG; existing `.jpg`
  files transitioned to `.png` when touched.

### Code Audit Findings (Phase A.5 — three Explore agents)

**ShipThemeManager audit (`game/ui/assets/ship_theme_manager.py`):**
- 7 public methods. 11 importers, all UI-layer.
- Discovery is eager from `Paths.ASSET_DIR + "ShipThemes"` (line 67) —
  bypasses the existing `Paths.SHIP_THEMES_DIR` constant.
- Skin loading uses `data.get('images', {})` at line 93 — old schema
  only.
- Portrait loading uses `Portraits/<Class>_Portrait.jpg` hardcoded
  convention at line 269-289, with `_ship_class_to_portrait_name()`
  string-parsing display names.
- Default fallback theme is hardcoded `"Federation"` at line 45.
- Caches keyed by `theme_name → ship_class`; cleared only via `clear()`,
  which is called in tests but never at runtime.

**Theme.json audit (9 themes):**
- 8 themes use legacy `images:` schema; 1 (Thoraliens) uses new
  `assets:` schema.
- Federation, Atlantians, Klingons, Romulans have mixed-case
  skin filenames (`Destroyer.png`, `Frigate.png`, `Battlecruiser.png`)
  alongside lowercase ones — Linux CI breaks today.
- Atlantians: typo `heavey cruiser.png` referenced in theme.json (file
  exists with the typo but should be fixed).
- Thoraliens: declares `super_dread_naught.png` but file is
  `super_dreadnaught.png` — load fails silently.
- Aetherwake: no `Portraits/` directory at all (19 portraits to
  generate).
- Atlantians: 18 portraits exist, missing Light Cruiser (1 to generate).
- Federation/Klingons/Ossivine/Prismsteel/Romulans/Voidforged: full
  19-portrait coverage but in `.jpg` format (151 files to convert to
  `.png`).

**LLM service / image-gen capability check:**
- `game/services/llm/` is chat-only (`LLMProvider.complete()`); adding
  image methods would break the protocol contract.
- `Tools/process_components/recreate_ai_samples.py:37-59` already uses
  `OPENAI_API_KEY` env-var (Windows fallback via PowerShell). Reuse the
  convention.
- PIL/Pillow is in 16 `Tools/` files — standard for image I/O.
- `gpt-image-2` confirmed real via OpenAI developer docs. Endpoint
  `v1/images/generations` for text→image; `v1/images/edits` for
  image→image. Output sizes not documented on the landing page (verify
  on first call).
- The PROJ-314 plan was originally drafted assuming `game/services/image/`
  but the architecture analyst (below) flagged that placement; the
  service belongs at `game/ui/services/image/`.

## Swarm Findings Summary (Phase B — 7 agents)

Combined analysis from agent reports stored in this conversation's transcript.
Per-agent narratives are condensed below.

### Architecture
- **`ImageProvider` belongs at `game/ui/services/image/`, not
  `game/services/image/`.** All 11 importers of
  `get_default_ship_theme_manager()` are UI-layer (renderers, panels,
  screens). The "2+ layer" criterion in `docs/01_ARCHITECTURE.md` for
  top-level services is not met.
- `ShipThemeManager` itself arguably belongs in `game/assets/` rather
  than `game/ui/assets/` — flagged as out-of-scope architectural
  cleanup; file as a follow-up project.
- Add `Paths.SHIP_THEMES_TARGET_SIZE = 2048` constant.
- The new `ImageProvider` joins ~9 existing services in `ApplicationContext`
  — no max-services antipattern yet, but if it grows past ~15
  consider sub-context grouping.

### Dependency / Ripple
- 19 direct importers of `ship_theme_manager`.
- **Hardcoded portrait convention duplicated in 4 sites** (loader +
  `design_image_helper.py:72-74`, `builder/right_panel.py:262-263`,
  `utils/portraits.py:98-114`). Migration must touch all 4.
- 5 places construct paths via `SHIP_THEMES_DIR` directly bypassing the
  loader. Centralise in `ShipThemeManager` post-refactor.
- External skill at
  `.agents/skills/codex-ship-theme-creator/scripts/theme_common.py:31`
  reads `theme.json` directly — needs schema update too.
- 9 tests pin `_ship_class_to_portrait_name()` outputs (will break;
  delete with the function).
- Tests poke private `theme_data['Battleship']['path']` (will break;
  schema changes the keys).

### Test Impact
- ~9 breaking tests (4 deleted, ~5 rewrite for new schema mocks).
- ~12 new contract tests (3 loader contract, 3 schema sanity, 5
  ImageProvider, 1 CLI idempotency).
- 2 integration smoke tests (Race Setup all-9-themes render, fallback
  warning).
- **Net delta: +6 tests** (15893 → ~15899).
- Test isolation: existing autouse fixture resets `ShipThemeManager`
  singleton; extend pattern to the new `ImageProvider` singleton.

### Patterns to Reuse
- **Singleton-Free DI / `get_default_*` accessor pair** —
  `game/services/llm/defaults.py` is the gold standard.
- **Protocol + TypeGuard** — `game/services/llm/provider.py` shape.
- **Provider Factory** — `game/services/llm/factory.py:36-91` with
  registration-at-import-time + env-var dispatch.
- **Background Service Call (#28)** — `game/services/llm/background.py`
  for the threaded image-generation wrapper.
- **`OPENAI_API_KEY` env-var convention** — already established in
  `Tools/process_components/recreate_ai_samples.py:37-59`.
- **PIL/Pillow** — for size validation and `.jpg`→`.png` re-encoding.
- **`AssetManager` manifest pattern** — eliminates filename-parsing
  conventions; data is the source of truth.
- **`Tools/captioning/validate_captions.py` shape** — for the new
  regenerate CLI's enumerate→derive→call API→write→idempotent loop.

### Risks (top 3)
1. **Cross-platform filename case mismatch** — Linux CI will fail
   today on 4 themes that have mixed-case skin filenames. Phase 5
   normalises every filename to `lowercase_with_underscores.png`.
2. **Unmocked `ImageProvider` hits real OpenAI API** —
   `NullImageProvider` raises on `generate_image()` when no key is
   set; default in `create_test()`. Tests must explicitly opt-in to
   a mock.
3. **`gpt-image-2` 2048×2048 not natively supported** — verify on
   first call in Phase 4. The protocol's "actual size" policy makes
   the failure visible; regenerator decides whether to upscale via
   PIL or accept lower size.

### Data Flow
- **Skin path:** `theme.json` → `theme_data[name][cls]` →
  `pygame.image.load(path).convert_alpha()` → cached Surface →
  `load_image()` → renderer.
- **Portrait path (today):** divergent — computed by string parsing
  via `_ship_class_to_portrait_name()`.
- **Portrait path (post):** symmetric with skins; both come from
  `theme.json`'s `assets:` block.
- **Cache invalidation gap:** `clear()` is only called in tests. If
  the regenerator CLI runs while game is open, surfaces stay stale
  until restart. Mitigation: regenerator emits a stdout warning.

### API / Interface (final shapes)

**`ImageProvider` Protocol:**
```python
@runtime_checkable
class ImageProvider(Protocol):
    """Generates images via an external AI model.

    Implementations may not honor the requested `size` exactly. Callers
    must inspect `result.size` and re-request or upscale if a strict
    dimension is required. Errors raise ImageException; never return
    ImageResult with empty bytes.
    """
    def generate_image(
        self,
        prompt: str,
        *,
        size: str = "2048x2048",
        model: str = "gpt-image-2",
        edit_image: pathlib.Path | None = None,
        mask: pathlib.Path | None = None,
        timeout_seconds: float | None = None,
        cancel_token: threading.Event | None = None,
        **opts: Any,
    ) -> ImageResult: ...
```

**`ImageResult`:**
```python
@dataclass(frozen=True)
class ImageResult:
    image_bytes: bytes
    size: tuple[int, int]       # actual returned size, NOT the requested size
    model: str
    latency_ms: float
    provider: str
    request_id: str | None = None
    revised_prompt: str | None = None  # gpt-image-2's interpreted prompt
```

**`theme.json` final schema:**
```json
{
  "schema_version": 1,
  "name": "Federation",
  "description": "...",
  "image_sizes": {
    "skin": [2048, 2048],
    "portrait": [2048, 2048]
  },
  "assets": {
    "Battleship": {
      "skin": "Skins/battleship.png",
      "portrait": "Portraits/battleship.png",
      "scale": 1.0
    }
  }
}
```
- Keys must match `SHIP_CLASSES_WITH_VISUAL_THEMES` exactly.
- `portrait` is optional. If absent, the loader returns the synthetic
  portrait fallback.
- `scale` is per-ship optional, defaults `1.0`.
- Unknown `schema_version` logs warning; loader continues
  (forward-compat).

**Regenerator CLI:** `--theme`, `--ship-class`, `--dry-run`, `--force`,
`--cost-cap`, `--model`, `--size`, `--batch`, `--list-themes`,
`--list-classes`, `--verbose`. Default cost cap $5.00.

### Opportunities Discovered

1. **`AssetManager` manifest pattern** could be applied to component
   sprites + planet images post-PROJ-314 to remove similar hardcoded
   conventions in those domains. Out of scope here.
2. **Move `ShipThemeManager` from `game/ui/assets/` to `game/assets/`**
   per the layer rules. Out of scope; follow-up project recommended.
3. **Cache invalidation hook** (e.g. inotify/watchdog listener for
   live game development) was flagged but is out of scope.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
