import os

base_dir = "Refactoring"
structure = {
    "protocols": [],
    "swarm_manifests": [],
    "swarm_prompts": [],
    "swarm_reports": [],
    "scripts": [],
    "archives": []
}

# --- 1. THE USER'S PYTHON SCRIPTS ---

script_pack_swarm = r"""import json
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
"""

script_spin_swarm = r"""import json
import os
import sys

# Placeholder simulation script
def spin_swarm(manifest_path):
    print("This script is a placeholder for automated execution.")
    print("Please manually execute the prompts generated in Refactoring/swarm_prompts/")

if __name__ == "__main__":
    spin_swarm("placeholder")
"""

# --- 2. PROTOCOL CONTENT ---

p10 = """# PROTOCOL 10: Swarm Planning
**Role:** The Architect (Coordinator)
**Objective:** Decompose the user's goal into a Phased Engineering Plan.

**Phase 1: The Architect**
1. **Analyze Goal:** Read user input.
2. **Generate Manifest:** Create `Refactoring/swarm_manifests/plan_manifest.json`.
3. **Execute:** `python Refactoring/scripts/pack_swarm.py Refactoring/swarm_manifests/plan_manifest.json`
4. **STOP:** Wait for user to run swarm.

**Phase 2: The Synthesizer**
1. **Trigger:** Reports present in `Refactoring/swarm_reports/`.
2. **Synthesize:** Create `Refactoring/active_refactor.md`.
   * **Migration Map** (The Constitution)
   * **Test Triage Table** (Empty)
   * **Phased Schedule** (Phase 1 detailed, Phase 2+ placeholders)
"""

p11 = """# PROTOCOL 11: Execute Phase
**Role:** Senior Software Engineer
**Objective:** Execute *only* the current phase.

**Procedure:**
1. **Load Context:** Read `Refactoring/active_refactor.md`.
2. **Implementation Loop:**
   * Execute Checklist.
   * Write new tests.
   * Update `Refactoring/active_phase_log.md`.
3. **Test Gauntlet:**
   * Run ALL tests.
   * **Triage:** Update `active_refactor.md` table: [FIX / REMOVE / DEFER].
4. **Completion:**
   * Checklist Done? Triage Done?
   * **STOP.** Request Protocol 12.
"""

p12 = """# PROTOCOL 12: Swarm Review
**Role:** The Auditor
**Objective:** Verify phase completion.

**Phase 1: The Auditor**
1. **Analyze:** Read `active_refactor.md` (Checklist & Triage).
2. **Generate Manifest:** Create `Refactoring/swarm_manifests/review_manifest.json`.
   * Roles: `Code_Reviewer`, `Plan_Adjuster`.
3. **Execute:** `python Refactoring/scripts/pack_swarm.py Refactoring/swarm_manifests/review_manifest.json`
4. **STOP.**

**Phase 2: The Synthesizer**
1. **Synthesize:** Read `Refactoring/swarm_reports/`.
2. **Update Master Plan:**
   * Mark Phase [Complete].
   * Detail Next Phase.
   * Confirm Deferrals.
"""

# --- 3. BUILD SYSTEM ---

if not os.path.exists(base_dir):
    os.makedirs(base_dir)

for folder in structure:
    path = os.path.join(base_dir, folder)
    if not os.path.exists(path):
        os.makedirs(path)

# Write Scripts
with open(os.path.join(base_dir, "scripts", "pack_swarm.py"), "w", encoding="utf-8") as f:
    f.write(script_pack_swarm)
with open(os.path.join(base_dir, "scripts", "spin_swarm.py"), "w", encoding="utf-8") as f:
    f.write(script_spin_swarm)

# Write Protocols
with open(os.path.join(base_dir, "protocols", "10_swarm_plan.md"), "w") as f: f.write(p10)
with open(os.path.join(base_dir, "protocols", "11_execute_phase.md"), "w") as f: f.write(p11)
with open(os.path.join(base_dir, "protocols", "12_swarm_review.md"), "w") as f: f.write(p12)

print(f"✅ Refactoring Swarm System initialized in '{os.path.abspath(base_dir)}'")
print("   - Python tools are in /scripts/")
print("   - Protocols are in /protocols/")