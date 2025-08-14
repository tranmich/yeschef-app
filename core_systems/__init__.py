"""
Core Systems Module - Essential Production Components

This module contains core production systems that should NEVER be archived:
- Enhanced Recipe Suggestions System
- Enhanced Search Engine  
- Production Flavor System

These are critical components for the Hungie application functionality.
"""

# Core systems version
__version__ = "1.0.0"

# Mark this as a production module
PRODUCTION_MODULE = True
ARCHIVE_PROTECTION = True

# Import core components for easy access
try:
    from .enhanced_recipe_suggestions import get_smart_suggestions, get_database_info
    ENHANCED_SUGGESTIONS_AVAILABLE = True
except ImportError:
    ENHANCED_SUGGESTIONS_AVAILABLE = False

try:
    from .enhanced_search import EnhancedSearchEngine
    ENHANCED_SEARCH_AVAILABLE = True
except ImportError:
    ENHANCED_SEARCH_AVAILABLE = False

try:
    from .production_flavor_system import FlavorProfileSystem, enhance_recipe_with_flavor_intelligence
    FLAVOR_SYSTEM_AVAILABLE = True
except ImportError:
    FLAVOR_SYSTEM_AVAILABLE = False

# System status
def get_core_systems_status():
    """Return status of all core systems"""
    return {
        "enhanced_suggestions": ENHANCED_SUGGESTIONS_AVAILABLE,
        "enhanced_search": ENHANCED_SEARCH_AVAILABLE,
        "flavor_system": FLAVOR_SYSTEM_AVAILABLE,
        "version": __version__
    }

print("Core Systems Module Loaded - Archive Protected")

