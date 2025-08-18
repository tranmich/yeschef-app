"""
🎮 Interactive Pantry Toggle Demo
=================================

Quick interactive commands to test the toggle system
"""

# Import the configuration system
from core_systems.config import *

print("🎮 INTERACTIVE PANTRY TOGGLE DEMO")
print("=" * 50)
print()
print("Available commands:")
print("• print_config_status()     - Show current configuration")
print("• toggle_pantry()           - Toggle pantry on/off")
print("• enable_pantry()           - Turn pantry on")
print("• disable_pantry()          - Turn pantry off")
print("• is_pantry_enabled()       - Check if pantry is enabled")
print()
print("Try running these commands!")
print()

# Show initial status
print("📊 CURRENT STATUS:")
print_config_status()
