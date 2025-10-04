"""
ArchaeoVault - Agentic AI Archaeological Research Platform

A comprehensive archaeological research platform featuring multiple specialized AI agents
that collaborate to analyze artifacts, research civilizations, reconstruct timelines,
and generate excavation reports. Built with 12-Factor App principles and microservices architecture.

Author: Vishal Mishra
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Vishal Mishra"
__email__ = "vishal@archaeovault.com"
__description__ = "Agentic AI-powered archaeological research platform"

# Core application imports
from .config import get_settings
from .app import create_app

# Export main application components
__all__ = [
    "create_app",
    "get_settings",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
