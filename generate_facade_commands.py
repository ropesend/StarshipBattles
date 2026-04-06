import ast

def parse_commands(filename):
    with open(filename, 'r') as f:
        tree = ast.parse(f.read())
    
    commands = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it inherits from Command
            is_command = any(getattr(b, 'id', '') == 'Command' for b in node.bases)
            if is_command and node.name != 'Command':
                commands.append(node.name)
    return commands

commands = parse_commands("game/strategy/engine/commands.py")

output = []
for cmd in commands:
    method_name = ""
    # convert CamelCase to snake_case
    for i, c in enumerate(cmd):
        if c.isupper() and i > 0:
            method_name += "_"
        method_name += c.lower()
    
    # remove _command at the end
    if method_name.endswith("_command"):
        method_name = method_name[:-8]
    if method_name.endswith("_commands"): # edge case
        method_name = method_name[:-9]
        
    code = f"""    def dispatch_{method_name}(self, **kwargs) -> 'ValidationResult':
        \"\"\"Helper to dispatch {cmd}.\"\"\"
        from game.strategy.engine.commands import {cmd}
        return self.handle_command({cmd}(**kwargs))
"""
    output.append(code)

with open("facade_commands_output.txt", "w") as f:
    f.write("\n".join(output))
print("Generated to facade_commands_output.txt")
