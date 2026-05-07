# PROJ-340 — Decisions

Decisions made while planning PROJ-340. Each entry records the choice, the
alternatives considered, and the rationale.

---

## D-001 — Characterization style, not TDD

**Decision:** Tests are written **after** observing current behavior; they
pin what the code does today, not what it "should" do. No failing-test-first
discipline applies.

**Alternatives:** Strict TDD (write red test → fix code). Rejected because
the master-plan rule for this arc is explicitly "characterization only — do
not change production behavior."

**Rationale:** PROJ-340 sits in a coverage-only arc whose value comes from
freezing current behavior so PROJ-337..339-adjacent refactors have a safety
net. TDD would invite scope creep into production fixes.

---

## D-002 — Pin behavior; observed bugs become observations, not fixes

**Decision:** If a test surfaces incorrect behavior (e.g. wrong default
color, swallowed exception), the test pins the **current** behavior and the
finding is recorded in this file as an observation. No production edit.

**Alternatives:** Inline-fix obvious bugs while the file is open. Rejected
per arc-wide scope rule.

**Rationale:** Mixing fixes into characterization tests defeats the safety-
net purpose (the diff stops being byte-stable across refactor candidates).

---

## D-003 — `ship_theme_manager`: monkeypatch the path constant

**Decision:** Tests for `ship_theme_manager.py` will:
- monkeypatch `game.ui.assets.ship_theme_manager.Paths.SHIP_THEMES_DIR` to
  point at a `tmp_path`-built fake themes tree;
- never read or write the real `assets/ship_themes/` tree.

**Alternatives:**
1. Add an injectable `themes_dir` constructor parameter to
   `ShipThemeManager`. Rejected — production refactors are out of scope.
2. Symlink the real tree into a tmp fixture. Rejected — fragile on Windows
   and couples tests to live asset content.

**Rationale:** Monkeypatching is the lowest-touch path that keeps production
unchanged. The injectable-path improvement is recorded as an observation
below for a future refactor project to pick up.

---

## D-004 — pygame surfaces over real display

**Decision:**
- Construct surfaces with `pygame.Surface((W, H), SRCALPHA)` — no display
  required.
- For `ship_theme_manager`, patch `pygame.image.load(...).convert_alpha()`
  to return a synthetic surface so tests do not rely on PNGs on disk.
- For `hit_effects` / `scrollable_json_panel` `draw` calls, pass a real
  `pygame.Surface` as the destination — no display needed.

**Alternatives:** Spin up a hidden pygame display in conftest. Rejected as
overkill; SRCALPHA surfaces work without a display.

---

## D-005 — `pygame_gui` widgets in panel tests: patch, do not instantiate

**Decision:** For `base_gallery.py` and `builder_widgets.py`, patch
`pygame_gui.elements.*` (UIPanel, UIButton, UIImage, UILabel,
UIScrollingContainer) with Mocks. Assertions inspect call shape (which
widget classes were constructed, with which rects), not pixel output.

**Alternatives:** Use real `pygame_gui` with a display fixture. Rejected —
master-plan's "minimum-viable" sizing for boilerplate-heavy panel files
explicitly caps these at ~3 tests; setting up real `pygame_gui` widgets
costs more setup than it adds in coverage value.

---

## D-006 — One test file per production file

**Decision:** Mirror the production tree: each in-scope file gets exactly
one matching `test_<name>.py` under the parallel `tests/unit/ui/...`
location.

**Rationale:** Master-plan default; matches existing repo convention.

---

## D-007 — `hit_effects._draw_*` covered indirectly via `draw_effects`

**Decision:** The four private `_draw_<type>` helpers
(`_draw_shield`, `_draw_armor`, `_draw_component`, `_draw_ship_destroyed`)
are exercised via `draw_effects(...)` rather than each tested directly.

**Rationale:** They are dispatch branches of one tick loop; testing them
directly would bind tests to an internal dispatch detail rather than the
observable contract of `draw_effects`.

---

## D-008 — Per-file commit discipline

**Decision:** One commit per production file's test module (6 commits
total), each with the production file path in the subject line.

**Rationale:** Master-plan discipline; keeps blast radius of any revert to
a single test module.

---

## Observations (filed during planning, not in scope to fix)

- **Obs-A — ShipThemeManager has no injectable themes dir.** `initialize`
  reads `Paths.SHIP_THEMES_DIR` (module-level constant). A future refactor
  project should add a `themes_dir: Path | None = None` parameter so tests
  do not need monkeypatch. Tracked here for follow-up.
- **Obs-B — BaseGallery and ModifierEditorPanel build pygame_gui widgets in
  `__init__`.** This forces test patching at construction time. A
  build-after-construct split (`build_widgets()` separate call) would let
  tests construct without patching.
