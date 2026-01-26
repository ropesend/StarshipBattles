import os
import re

file_path = r'c:\Dev\Starship Battles\builder_components.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define target block using regex to be flexible with indentation if needed, 
# but try exact string first for safety.
target_block = """                    if self.editing_component:
                          # Update component directly
                          if self.editing_component.get_modifier(mod_id):
                              self.editing_component.remove_modifier(mod_id)
                              is_active = False
                          else:
                              self.editing_component.add_modifier(mod_id)
                              is_active = True"""

replacement_block = """                    if self.editing_component:
                          # Update component directly
                          if self.editing_component.get_modifier(mod_id):
                              # Check mandatory
                              if mod_id in ['simple_size', 'range_mount', 'facing']:
                                   is_active = True
                              else:
                                   self.editing_component.remove_modifier(mod_id)
                                   is_active = False
                          else:
                              self.editing_component.add_modifier(mod_id)
                              is_active = True"""

if target_block in content:
    new_content = content.replace(target_block, replacement_block)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully patched via exact match.")
else:
    # Try normalized spacing
    print("Exact match failed. Attempting to diagnose...")
    # I'll just print unique snippets to see what's wrong if I were debugging, 
    # but here I'll try to find the location by unique string 'Update component directly'
    start_marker = "# Update component directly"
    idx = content.find(start_marker)
    if idx != -1:
        # Check context
        print(f"Found marker at {idx}. Context:")
        print(repr(content[idx-40:idx+200]))
    else:
        print("Marker not found.")
