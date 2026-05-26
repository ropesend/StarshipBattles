# Gemini Capture Prompt — Race Portrait

Paste the text below this line into Gemini after uploading a race portrait.
Save the JSON output to `assets/images/race_portraits/<filename>.caption.json`
(next to the original image file, with `.caption.json` appended).

---

You are an art critic for a 4X space strategy game. You have been shown a portrait of one individual of an alien species. Produce a structured JSON description that another LLM (with no vision) will use later to write a biological description of the species.

Describe what you actually see — anatomy, materials, posture. Avoid inventing back-story; that's the narrative model's job. Be specific and visual.

Output a JSON object with these fields, exactly:

```json
{
  "schema_version": 1,
  "anatomy": "<body plan, distinctive features (limbs, eyes, skin/scale/fur, head shape)>",
  "coloration": "<hue, pattern, contrast across the body>",
  "attire_and_adornment": "<clothing, jewelry, tools, scars, paint, ceremonial markings>",
  "posture_and_expression": "<bearing, gaze, mood, body language conveyed by the pose>",
  "technology_level_hint": "<one of: primitive | medieval | industrial | advanced | post-human | unknown>",
  "distinctive_traits": "<anything unusual or memorable that doesn't fit the other fields>"
}
```

Example output for a fictional bipedal reptilian humanoid in armoured ceremonial dress:

```json
{
  "schema_version": 1,
  "anatomy": "Bipedal, ~2m tall, reptilian; elongated skull, four amber slit-pupil eyes in a vertical column, tail visible behind",
  "coloration": "Deep teal scales over torso fading to ochre on belly; mottled darker stripes along the spine and limbs",
  "attire_and_adornment": "Polished bronze breastplate over chainmail tunic; carved jade ear-cuffs; ritual scarification on forehead",
  "posture_and_expression": "Upright, hands clasped at the waist; gaze steady and forward; jaw set, conveying calm authority",
  "technology_level_hint": "industrial",
  "distinctive_traits": "The fourth eye sits centred above the others — appears to be larger and more reflective than the lower three"
}
```

OUTPUT ONLY THE JSON. No prose, no preamble, no markdown fences.
