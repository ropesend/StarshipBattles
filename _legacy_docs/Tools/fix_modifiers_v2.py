import os

file_path = r'c:\Dev\Starship Battles\builder_components.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Exact string from debug output (reconstructed)
# Indentation seems to be 25 spaces for the inner block
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
    print("Successfully patched via exact match (v2).")
else:
    print("Exact match failed again.")
    # Fallback: Normalized replace
    # We remove the indentation from target and regex match? 
    # Or just replace the inner part which is unique enough.
    
    unique_inner = """if self.editing_component.get_modifier(mod_id):
                             self.editing_component.remove_modifier(mod_id)
                             is_active = False"""
    
    # Try to find this ignoring leading whitespace?
    # No, let's keep it simple. If this fails, I'll manually modify the file content in full overwrite (risky but sure).
    pass
