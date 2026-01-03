import ui
print(f"ui package: {ui}")
print(f"dir(ui): {dir(ui)}")
try:
    from ui import Button
    print("Button imported successfully")
except ImportError as e:
    print(f"Failed to import Button: {e}")

try:
    from ui.builder import BuilderLeftPanel
    print("BuilderLeftPanel imported successfully")
except ImportError as e:
    print(f"Failed to import BuilderLeftPanel: {e}")
