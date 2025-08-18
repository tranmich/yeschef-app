"""
⚙️ Me Hungie Configuration System
===============================

This module manages application configuration, including the ability to toggle
major features like the pantry system for testing and development.

Author: GitHub Copilot
Date: August 18, 2025
"""

import os
from typing import Dict, Any

class MeHungieConfig:
    """
    ⚙️ Central configuration management for Me Hungie
    
    Manages feature toggles and application settings
    """
    
    def __init__(self):
        self._config = {
            # Pantry System Configuration
            'PANTRY_ENABLED': self._get_env_bool('PANTRY_ENABLED', True),
            'PANTRY_EXPIRY_TRACKING': self._get_env_bool('PANTRY_EXPIRY_TRACKING', False),
            
            # Search Enhancement Configuration  
            'PANTRY_ENHANCED_SEARCH': self._get_env_bool('PANTRY_ENHANCED_SEARCH', True),
            'PANTRY_RECIPE_MATCHING': self._get_env_bool('PANTRY_RECIPE_MATCHING', True),
            
            # Development Configuration
            'DEVELOPMENT_MODE': self._get_env_bool('DEVELOPMENT_MODE', True),
            'DEBUG_PANTRY': self._get_env_bool('DEBUG_PANTRY', False),
        }
    
    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable with default fallback"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
        print(f"🔧 Config updated: {key} = {value}")
    
    def is_pantry_enabled(self) -> bool:
        """Check if pantry system is enabled"""
        return self.get('PANTRY_ENABLED', True)
    
    def is_pantry_search_enabled(self) -> bool:
        """Check if pantry-enhanced search is enabled"""
        return self.get('PANTRY_ENABLED', True) and self.get('PANTRY_ENHANCED_SEARCH', True)
    
    def is_expiry_tracking_enabled(self) -> bool:
        """Check if expiry date tracking is enabled"""
        return self.get('PANTRY_ENABLED', True) and self.get('PANTRY_EXPIRY_TRACKING', False)
    
    def toggle_pantry(self) -> bool:
        """Toggle pantry system on/off and return new state"""
        current = self.is_pantry_enabled()
        new_state = not current
        self.set('PANTRY_ENABLED', new_state)
        
        status = "🟢 ENABLED" if new_state else "🔴 DISABLED"
        print(f"🥫 Pantry System: {status}")
        
        return new_state
    
    def enable_pantry(self) -> None:
        """Enable pantry system"""
        self.set('PANTRY_ENABLED', True)
        print("🟢 Pantry system ENABLED")
    
    def disable_pantry(self) -> None:
        """Disable pantry system"""
        self.set('PANTRY_ENABLED', False)
        print("🔴 Pantry system DISABLED")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current configuration status"""
        return {
            'pantry_enabled': self.is_pantry_enabled(),
            'pantry_search_enabled': self.is_pantry_search_enabled(),
            'expiry_tracking_enabled': self.is_expiry_tracking_enabled(),
            'development_mode': self.get('DEVELOPMENT_MODE', True),
            'debug_mode': self.get('DEBUG_PANTRY', False)
        }
    
    def print_status(self) -> None:
        """Print current configuration status"""
        status = self.get_status()
        
        print("\n⚙️ ME HUNGIE CONFIGURATION STATUS:")
        print("=" * 40)
        
        pantry_status = "🟢 ENABLED" if status['pantry_enabled'] else "🔴 DISABLED"
        print(f"🥫 Pantry System: {pantry_status}")
        
        if status['pantry_enabled']:
            search_status = "🟢 ENABLED" if status['pantry_search_enabled'] else "🔴 DISABLED"
            print(f"🔍 Pantry-Enhanced Search: {search_status}")
            
            expiry_status = "🟢 ENABLED" if status['expiry_tracking_enabled'] else "🔴 DISABLED"
            print(f"📅 Expiry Tracking: {expiry_status}")
        
        dev_status = "🟢 ENABLED" if status['development_mode'] else "🔴 DISABLED"
        print(f"🔧 Development Mode: {dev_status}")
        
        debug_status = "🟢 ENABLED" if status['debug_mode'] else "🔴 DISABLED"
        print(f"🐛 Debug Mode: {debug_status}")


# Global configuration instance
config = MeHungieConfig()

def get_config() -> MeHungieConfig:
    """Get the global configuration instance"""
    return config

# Convenience functions for common operations
def is_pantry_enabled() -> bool:
    """Check if pantry system is enabled"""
    return config.is_pantry_enabled()

def toggle_pantry() -> bool:
    """Toggle pantry system and return new state"""
    return config.toggle_pantry()

def enable_pantry() -> None:
    """Enable pantry system"""
    config.enable_pantry()

def disable_pantry() -> None:
    """Disable pantry system"""
    config.disable_pantry()

def print_config_status() -> None:
    """Print current configuration status"""
    config.print_status()

if __name__ == "__main__":
    # Demo the configuration system
    print("🔧 ME HUNGIE CONFIGURATION SYSTEM DEMO")
    print("=" * 50)
    
    # Show initial status
    config.print_status()
    
    # Demo toggling
    print(f"\n🔄 Toggling pantry system...")
    toggle_pantry()
    config.print_status()
    
    print(f"\n🔄 Toggling back...")
    toggle_pantry()
    config.print_status()
