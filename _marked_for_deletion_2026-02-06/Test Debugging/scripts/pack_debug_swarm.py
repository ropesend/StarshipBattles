import json
import os
import sys
from typing import Dict, List, Any

def load_file_context(base_path: str, files: List[str]) -> str:
    context = ""
    for file_path in files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                context += f"\n--- START FILE: {file_path} ---\n"
                context += f.read()
                context += f"\n--- END FILE: {file_path} ---\n"
        else:
            context += f"\n[WARNING: File not found: {file_path}]\n"
    return context

def pack_debug_swarm(manifest_path: str):
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest not found at {manifest_path}")
        return

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse manifest JSON: {e}")
        return

    # Paths setup
    # Manifest assumed to be in Test Debugging/swarm_manifests/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    debug_root = os.path.dirname(script_dir)
    workspace_root = os.path.dirname(debug_root)
    
    output_dir = os.path.join(debug_root, "swarm_prompts")
    report_dir = os.path.join(debug_root, "swarm_reports")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    # Clean previous prompts
    for file in os.listdir(output_dir):
        if file.endswith(".txt"):
            os.remove(os.path.join(output_dir, file))

    print(f"Packing debug swarm from {manifest_path}...")
    
    for agent in manifest.get("agents", []):
        role = agent.get("role", "Scout")
        zone = agent.get("zone", "General")
        files = agent.get("primary_files", [])
        
        file_content = load_file_context(workspace_root, files)
        
        full_prompt = f"""# INSTRUCTIONS FOR DEBUG SCOUT ({role})

**ZONE:** {zone}
**OBJECTIVE:** Find clues related to the failing test in this specific area.

## CONTEXT
{file_content}

## FAILURE OUTPUT
{manifest.get('failure_summary', 'No summary provided.')}

## OUTPUT
1. Analyze your zone. 
2. Use `write_to_file` to save your report to:
   `{os.path.abspath(os.path.join(report_dir, f"{role}_Report.md"))}`
"""
        safe_role = "".join([c for c in role if c.isalnum() or c in (' ', '_', '-')]).strip()
        output_path = os.path.join(output_dir, f"Debug_{safe_role}_Prompt.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_prompt)
            
        print(f"-> Generated: {output_path}")

    print(f"\n[Done] Generated {len(manifest.get('agents', []))} prompts.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pack_debug_swarm.py <path_to_manifest>")
    else:
        pack_debug_swarm(sys.argv[1])
