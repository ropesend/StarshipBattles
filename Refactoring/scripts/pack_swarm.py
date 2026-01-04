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

def validate_manifest(manifest: Dict[str, Any]) -> bool:
    if "agents" not in manifest:
        print("Error: Manifest missing 'agents' list.")
        return False
    # Add more validation as needed
    return True

def pack_swarm(manifest_path: str):
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest not found at {manifest_path}")
        return

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse manifest JSON: {e}")
        return

    if not validate_manifest(manifest):
        return

    # Adjust context root relative to manifest location or CWD
    context_root = manifest.get("context_root", "./")
    
    # Paths setup
    # Manifest assumed to be in Refactoring/swarm_manifests/
    base_path = os.path.dirname(os.path.dirname(manifest_path))
    output_dir = os.path.join(base_path, "swarm_prompts")
    report_dir = os.path.join(base_path, "swarm_reports")
    
    # Active Refactor Context Injection
    active_refactor_path = os.path.join(base_path, "active_refactor.md")
    global_context = ""
    if os.path.exists(active_refactor_path):
        print(f"Found active refactor context: {active_refactor_path}")
        with open(active_refactor_path, 'r', encoding='utf-8') as f:
            global_context += "\n--- ACTIVE REFACTOR CONTEXT ---\n"
            global_context += f.read()
            global_context += "\n--- END ACTIVE REFACTOR CONTEXT ---\n"
    else:
        print("No active_refactor.md found. Starting fresh context.")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    print(f"Packing swarm from {manifest_path}...")
    
    for agent in manifest["agents"]:
        # Handle 'roles' vs 'role' typo flexibility
        role = agent.get("roles", agent.get("role", "Unknown_Role"))
        focus = agent.get("focus", "General Analysis")
        files = agent.get("primary_files", [])
        
        file_content = load_file_context(context_root, files)
        
        full_prompt = f"""# INSTRUCTIONS FOR AGENT ({role})

**ROLE:** {role}
**FOCUS:** {focus}

## YOUR GOAL
Analyze the provided code context below.
Isolate issues specifically related to your FOCUS ({focus}).
Ignore unrelated issues unless they are critical system failures.

## PHASE STATUS
{global_context}

## OUTPUT INSTRUCTIONS
You are an autonomous agent.
1. Perform your analysis.
2. **CRITICAL:** You MUST use the `write_to_file` tool to save your report.
   - **Target File:** `{os.path.abspath(os.path.join(report_dir, f"{role}_Report.md"))}`
   - **Do NOT** just print the markdown to the chat. Save it to the file.

## CONTEXT
{file_content}
"""
        # Sanitize role for filename
        safe_role = "".join([c for c in role if c.isalnum() or c in (' ', '_', '-')]).strip()
        output_path = os.path.join(output_dir, f"{safe_role}_Prompt.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_prompt)
            
        print(f"-> Generated: {output_path}")

    print(f"\n[Done] Generated {len(manifest['agents'])} prompts in '{output_dir}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pack_swarm.py <path_to_manifest>")
    else:
        pack_swarm(sys.argv[1])
