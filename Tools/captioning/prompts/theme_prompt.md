# Gemini Capture Prompt — Ship Theme

Paste the text below this line into Gemini after uploading a representative
ship image from the theme (e.g., the theme's Battlecruiser or Battleship
portrait). Save the JSON output to
`assets/images/ship_themes/<theme_name>/theme.caption.json`.

If the theme has multiple representative ships, use whichever shows the
most defining visual features. The caption is meant to capture the theme's
overall aesthetic, not any single ship.

---

You are an art critic for a 4X space strategy game. You have been shown a representative ship of one of the game's playable factions. Produce a structured JSON description of the visual aesthetic that another LLM (with no vision) will use later to write narrative lore about the species' shipwrights and engineers.

Be specific about geometry, materials, and what the design choices imply. Avoid generic adjectives ("powerful", "imposing"). Keep each field to ~15 words.

Output a JSON object with these fields, exactly:

```json
{
  "schema_version": 1,
  "hull_geometry": "<overall silhouette, symmetry, sectional shapes (sleek/blocky/organic/jagged)>",
  "materials_and_finish": "<apparent materials, surface treatment, weathering, panel detail>",
  "design_philosophy": "<what the engineering choices imply (speed, durability, elegance, intimidation, mass production)>",
  "color_scheme": "<palette and accent placement across the hull>",
  "technology_level_hint": "<one of: primitive | medieval | industrial | advanced | post-human | unknown>",
  "distinctive_traits": "<anything unusual or memorable — recognizable silhouettes, signature features>"
}
```

Example output for a fictional sleek charcoal-grey ship with thin red accent stripes:

```json
{
  "schema_version": 1,
  "hull_geometry": "Long arrowhead silhouette; bilateral symmetry; smooth curved sectional shapes blended into a single flowing form",
  "materials_and_finish": "Matte charcoal composite plating with brushed metal seams; minimal panel lines; very clean finish",
  "design_philosophy": "Speed and stealth optimisation — every surface is angled to reduce sensor return; no obvious turrets",
  "color_scheme": "Charcoal-grey field with thin scarlet accent stripes along leading edges and at the engine bell",
  "technology_level_hint": "advanced",
  "distinctive_traits": "Twin parallel knife-thin nacelles flank the main hull; the bow forks into two prongs, suggesting a fixed forward weapon"
}
```

OUTPUT ONLY THE JSON. No prose, no preamble, no markdown fences.
