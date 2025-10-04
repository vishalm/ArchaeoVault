"""
AI Agents module for ArchaeoVault.

This module contains all specialized AI agents that work together
to provide comprehensive archaeological analysis and research capabilities.
"""

from .base_agent import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from .artifact_agent import ArtifactAnalysisAgent
from .dating_agent import CarbonDatingAgent
from .civilization_agent import CivilizationResearchAgent
from .excavation_agent import ExcavationPlanningAgent
from .report_agent import ReportGenerationAgent
from .research_agent import ResearchAssistantAgent

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentConfig",
    "AgentRequest",
    "AgentResponse",
    
    # Specialized agents
    "ArtifactAnalysisAgent",
    "CarbonDatingAgent",
    "CivilizationResearchAgent",
    "ExcavationPlanningAgent",
    "ReportGenerationAgent",
    "ResearchAssistantAgent",
]
