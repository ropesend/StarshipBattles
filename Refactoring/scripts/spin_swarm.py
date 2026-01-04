import json
import os
import sys
import time

def spin_swarm():
    # Assume script is run from project root or checks relative path
    base_path = "Refactoring"
    prompts_dir = os.path.join(base_path, "swarm_prompts")
    reports_dir = os.path.join(base_path, "swarm_reports")

    if not os.path.exists(prompts_dir):
        print(f"Error: Prompts directory not found at {prompts_dir}")
        print("Did you run pack_swarm.py first?")
        return

    print(f"Scanning for prompts in {prompts_dir}...")
    
    prompts = [f for f in os.listdir(prompts_dir) if f.endswith("_Prompt.txt")]
    
    if not prompts:
        print("No prompts found.")
        return

    print(f"Found {len(prompts)} agents to spin up.")
    print("--- SWARM ORCHESTRATION ---")
    
    pending_agents = []
    
    for prompt_file in prompts:
        agent_name = prompt_file.replace("_Prompt.txt", "")
        report_file = os.path.join(reports_dir, f"{agent_name}_Report.md")
        
        if os.path.exists(report_file):
            print(f"[OK] {agent_name} has already reported.")
        else:
            pending_agents.append(agent_name)
            print(f"[PENDING] {agent_name} needs to run.")
            
    if not pending_agents:
        print("\nAll agents have reported! Swarm execution complete.")
        return

    print(f"\nWaiting for {len(pending_agents)} agents to complete...")
    print("Please execute the pending agents using the generated prompt files.")
    
    # Simple monitoring loop
    try:
        while pending_agents:
            still_pending = []
            for agent in pending_agents:
                report_file = os.path.join(reports_dir, f"{agent}_Report.md")
                if os.path.exists(report_file):
                    print(f"\n[RECEIVED] Report from {agent}!")
                else:
                    still_pending.append(agent)
            
            pending_agents = still_pending
            if pending_agents:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(2)
                
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

    print("\nSwarm cycle finished.")

if __name__ == "__main__":
    spin_swarm()
