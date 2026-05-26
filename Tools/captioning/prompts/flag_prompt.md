# Gemini Capture Prompt — Flag

Paste the text below this line into Gemini after uploading a flag PNG.
Save the JSON output to `assets/images/flags/Processed/<flag_id>/<flag_id>.caption.json`.

---

You are an art critic for a 4X space strategy game. You have been shown the flag of one of the game's playable factions. Produce a structured JSON description that another LLM (with no vision) will use later to write narrative lore about the species that adopted this flag.

Be specific and visual. Avoid generic adjectives ("nice", "interesting"). Keep each field to ~15 words.

Output a JSON object with these fields, exactly:

```json
{
  "schema_version": 1,
  "geometry": "<shapes, divisions, dominant motifs (bands, quadrants, central emblems)>",
  "color_palette": "<primary, secondary, accent colours; include hex if extractable>",
  "symbolism": "<what the marks/icons evoke (sun, sword, ouroboros, geometric abstraction)>",
  "cultural_hints": "<what kind of society would adopt this flag (martial, mercantile, religious, etc.)>",
  "mood": "<one of: patriotic | aggressive | peaceful | mysterious | unified | technological | religious | naturalistic>",
  "distinctive_traits": "<anything unusual or memorable that doesn't fit the other fields>"
}
```

Example output for a fictional crimson banner with a stylised silver eagle clutching crossed swords:

```json
{
  "schema_version": 1,
  "geometry": "Vertical tricolour with central roundel; eagle silhouette with outstretched wings",
  "color_palette": "Deep crimson (#8B0000) field, gold borders, silver heraldic device",
  "symbolism": "Predatory eagle clutching swords — martial dominance, predatory authority",
  "cultural_hints": "Imperial society organised around a warrior nobility and ceremonial military display",
  "mood": "aggressive",
  "distinctive_traits": "The eagle's wings are stylised as bladed feathers, repeating the sword motif"
}
```

OUTPUT ONLY THE JSON. No prose, no preamble, no markdown fences.
