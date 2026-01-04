import json
import os
import sys
from typing import Dict, List

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

def pack_swarm(manifest_path: str):
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest not found at {manifest_path}")
        return

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Adjust context root relative to manifest location or CWD
    context_root = manifest.get("context_root", "./")
    
    # OUTPUT: Refactoring/swarm_prompts/
    # We assume manifest is in Refactoring/swarm_manifests/
    base_path = os.path.dirname(os.path.dirname(manifest_path))
    output_dir = os.path.join(base_path, "swarm_prompts")
    report_dir = os.path.join(base_path, "swarm_reports")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    print(f"Packing swarm from {manifest_path}...")
    
    for agent in manifest["agents"]:
        # Handle 'roles' vs 'role' typo flexibility
        role = agent["roles"] if "roles" in agent else agent["role"]
        focus = agent["focus"]
        files = agent.get("primary_files", [])
        
        file_content = load_file_context(context_root, files)
        
        full_prompt = f"""# INSTRUCTIONS FOR AGENT ({role})

**ROLE:** {role}
**FOCUS:** {focus}

## YOUR GOAL
Analyze the provided code context below.
Isolate issues specifically related to your FOCUS ({focus}).
Ignore unrelated issues unless they are critical system failures.

## OUTPUT INSTRUCTIONS
You are an autonomous agent.
1. Perform your analysis.
2. **CRITICAL:** You MUST use the `write_to_file` tool to save your report.
   - **Target File:** `{os.path.abspath(os.path.join(report_dir, f"{role}_Report.md"))}`
   - **Do NOT** just print the markdown to the chat. Save it to the file.

## CONTEXT
{file_content}
"""
        output_path = os.path.join(output_dir, f"{role}_Prompt.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_prompt)
            
        print(f"-> Generated: {output_path}")

    print(f"\n[Done] Generated {len(manifest['agents'])} prompts in '{output_dir}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pack_swarm.py <path_to_manifest>")
    else:
        pack_swarm(sys.argv[1])
