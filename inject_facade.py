with open('game/strategy/facade/strategy_session_facade.py', 'r') as f:
    content = f.read()
with open('facade_commands_output.txt', 'r') as f:
    helpers = f.read()

target = "    # =========================================================================\n    # QUERIES (Read Path) - Return DTOs only, never domain objects\n    # ========================================================================="

index = content.find(target)
if index != -1:
    new_content = content[:index] + "    # --- Command Dispatch Helpers ---\n" + helpers + "\n" + content[index:]
    with open('game/strategy/facade/strategy_session_facade.py', 'w') as f:
        f.write(new_content)
    print("Injected successfully")
else:
    print("Target not found")
