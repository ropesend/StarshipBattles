import os
import json
import re

# Configuration
DESCRIPTIONS_FILE = r"C:\Developer\StarshipBattles\assets\Images\altcomponents\descriptions.txt"
PROMPT_SUFFIX = (
    "Isolated mechanical component floating in a pure black space void. "
    "Cinematic lighting, high detail, 8k, photorealistic sci-fi style. "
    "Centered composition, the object is contained within the frame with significant black space margins. "
    "Pure black background, no stars, no horizon."
)

def parse_descriptions():
    with open(DESCRIPTIONS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by "Image X:"
    images = re.split(r"Image \d+:", content)
    image_map = {}
    
    for section in images:
        if not section.strip():
            continue
            
        # Extract component ID (e.g., "004" from "2048Portrait_Comp_004.jpg")
        match_file = re.search(r"\d+Portrait_Comp_(\d+)\.\w+", section)
        if not match_file:
            continue
        comp_id = match_file.group(1)

        # Extract description
        desc_match = re.search(r"Description: (.*)", section, re.DOTALL)
        if not desc_match:
            continue
        description = desc_match.group(1).strip()

        # Clean up description (remove subsequent "Image X" header if split failed)
        description = re.split(r"Image \d+:", description)[0].strip()

        image_map[comp_id] = description

    return image_map

def get_engineered_prompt(filename, description):
    # Transformation logic for interior scenes
    if "pilot's chair" in description.lower() or "command center" in description.lower():
        description = description.replace("interior view of a futuristic starship command center focusing on a", "futuristic starship pilot's chair and its semi-circular control console, appearing as a single")
        description = description.replace("The floor is a textured metallic surface with a circular pattern.", "The console sits on a small, circular textured metallic base.")
    
    if "hangar" in description.lower() or "assembly bay" in description.lower():
        description = "A modular starship maintenance-hub docking cradle, skeletal archway supports equipped with small robotic arms. A single sleek minimalist spacecraft is suspended by service tethers. Industrial grating, yellow safety lines."

    if "crew quarters" in description.lower():
        description = "A compact, modular two-story starship crew quarters pod. The pod's side is cut away to reveal a cross-section of the interior: green-cushioned bunk beds on the top level and a small dining area with a round table and swivel chairs on the bottom."

    if "cargo corridor" in description.lower() or "boarding umbilical" in description.lower():
        description = "A modular starship corridor umbilical segment, appearing as an isolated octagonal tunnel section. Heavy, weathered grey metal plates with prominent yellow safety stripes. Ribbed support beams."

    return f"{description} {PROMPT_SUFFIX}"

def main():
    print(f"Loading descriptions from {DESCRIPTIONS_FILE}...")
    image_map = parse_descriptions()
    
    # Target range 5-15 (Comp_004 to Comp_014)
    target_ids = [f"{i:03d}" for i in range(4, 15)]

    print("\n--- Engineered Prompts for Floating Aesthetics ---\n")
    for comp_id in target_ids:
        if comp_id in image_map:
            prompt = get_engineered_prompt(comp_id, image_map[comp_id])
            print(f"ID: Comp_{comp_id}")
            print(f"Prompt: {prompt}\n")

if __name__ == "__main__":
    main()
