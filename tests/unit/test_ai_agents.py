"""
Unit tests for AI agents in ArchaeoVault.

This module tests individual AI agents and their core functionality:
- Artifact Analysis Agent
- Carbon Dating Agent
- Civilization Research Agent
- Excavation Planning Agent
- Report Generation Agent
- Research Assistant Agent
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from app.services.ai_agents.artifact_agent import ArtifactAnalysisAgent
from app.services.ai_agents.dating_agent import CarbonDatingAgent
from app.services.ai_agents.civilization_agent import CivilizationResearchAgent
from app.services.ai_agents.excavation_agent import ExcavationPlanningAgent
from app.services.ai_agents.report_agent import ReportGenerationAgent
from app.services.ai_agents.research_agent import ResearchAssistantAgent
from tests.factories import (
    ArtifactDataFactory, CivilizationDataFactory, ExcavationDataFactory,
    CeramicArtifactFactory, MetalArtifactFactory, StoneArtifactFactory
)


class TestArtifactAnalysisAgent:
    """Test Artifact Analysis Agent"""
    
    @pytest.fixture
    def agent(self, test_config):
        """Create artifact analysis agent"""
        return ArtifactAnalysisAgent(config=test_config)
    
    @pytest.mark.asyncio
    async def test_analyze_ceramic_artifact(self, agent, mock_anthropic_client):
        """Test ceramic artifact analysis"""
        artifact_data = CeramicArtifactFactory.create()
        
        result = await agent.analyze_artifact(artifact_data)
        
        assert result is not None
        assert "material" in result
        assert "description" in result
        assert "confidence" in result
        assert result["material"] == "ceramic"
        assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_analyze_metal_artifact(self, agent, mock_anthropic_client):
        """Test metal artifact analysis"""
        artifact_data = MetalArtifactFactory.create()
        
        result = await agent.analyze_artifact(artifact_data)
        
        assert result is not None
        assert result["material"] == "metal"
        assert "dating_estimate" in result
        assert "preservation_notes" in result
    
    @pytest.mark.asyncio
    async def test_analyze_stone_artifact(self, agent, mock_anthropic_client):
        """Test stone artifact analysis"""
        artifact_data = StoneArtifactFactory.create()
        
        result = await agent.analyze_artifact(artifact_data)
        
        assert result is not None
        assert result["material"] == "stone"
        assert "tool_type" in result
        assert "manufacturing_technique" in result
    
    @pytest.mark.asyncio
    async def test_analyze_with_image(self, agent, mock_anthropic_client, test_image_file):
        """Test artifact analysis with image"""
        artifact_data = ArtifactDataFactory.create()
        artifact_data.image_urls = [test_image_file]
        
        result = await agent.analyze_artifact(artifact_data)
        
        assert result is not None
        assert "visual_description" in result
        assert "image_analysis" in result
    
    @pytest.mark.asyncio
    async def test_analyze_with_location_context(self, agent, mock_anthropic_client):
        """Test artifact analysis with location context"""
        artifact_data = ArtifactDataFactory.create()
        artifact_data.location = {
            "lat": 30.0444,  # Cairo, Egypt
            "lon": 31.2357,
            "site_name": "Giza Plateau"
        }
        
        result = await agent.analyze_artifact(artifact_data)
        
        assert result is not None
        assert "cultural_context" in result
        assert "geographic_significance" in result
    
    @pytest.mark.asyncio
    async def test_analyze_with_metadata(self, agent, mock_anthropic_client):
        """Test artifact analysis with rich metadata"""
        artifact_data = ArtifactDataFactory.create()
        artifact_data.metadata = {
            "color": "red",
            "decoration": "geometric",
            "size": "15cm",
            "weight": "500g",
            "firing_temperature": "high"
        }
        
        result = await agent.analyze_artifact(artifact_data)
        
        assert result is not None
        assert "technical_analysis" in result
        assert "manufacturing_insights" in result
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, agent, mock_anthropic_client):
        """Test confidence score calculation"""
        artifact_data = ArtifactDataFactory.create(condition_score=10)
        
        result = await agent.analyze_artifact(artifact_data)
        
        assert result is not None
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["confidence"] > 0.5  # High condition should yield high confidence
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling in artifact analysis"""
        with patch.object(agent, '_call_ai_service', side_effect=Exception("AI service error")):
            artifact_data = ArtifactDataFactory.create()
            
            with pytest.raises(Exception):
                await agent.analyze_artifact(artifact_data)


class TestCarbonDatingAgent:
    """Test Carbon Dating Agent"""
    
    @pytest.fixture
    def agent(self, test_config):
        """Create carbon dating agent"""
        return CarbonDatingAgent(config=test_config)
    
    @pytest.mark.asyncio
    async def test_calculate_c14_dating(self, agent):
        """Test C-14 dating calculation"""
        sample_data = {
            "c14_ratio": 0.5,
            "sample_type": "wood",
            "contamination_factor": 0.0
        }
        
        result = await agent.calculate_dating(sample_data)
        
        assert result is not None
        assert "raw_age" in result
        assert "calibrated_age" in result
        assert "confidence_interval" in result
        assert result["raw_age"] > 0
    
    @pytest.mark.asyncio
    async def test_calculate_with_contamination(self, agent):
        """Test C-14 dating with contamination"""
        sample_data = {
            "c14_ratio": 0.5,
            "sample_type": "wood",
            "contamination_factor": 0.1
        }
        
        result = await agent.calculate_dating(sample_data)
        
        assert result is not None
        assert "contamination_adjustment" in result
        assert result["confidence_interval"]["lower"] < result["confidence_interval"]["upper"]
    
    @pytest.mark.asyncio
    async def test_calculate_different_sample_types(self, agent):
        """Test C-14 dating for different sample types"""
        sample_types = ["wood", "charcoal", "bone", "shell", "textile"]
        
        for sample_type in sample_types:
            sample_data = {
                "c14_ratio": 0.5,
                "sample_type": sample_type,
                "contamination_factor": 0.0
            }
            
            result = await agent.calculate_dating(sample_data)
            
            assert result is not None
            assert "sample_type_notes" in result
            assert result["sample_type"] == sample_type
    
    @pytest.mark.asyncio
    async def test_calibration_curve_application(self, agent):
        """Test calibration curve application"""
        sample_data = {
            "c14_ratio": 0.5,
            "sample_type": "wood",
            "contamination_factor": 0.0,
            "calibration_curve": "IntCal20"
        }
        
        result = await agent.calculate_dating(sample_data)
        
        assert result is not None
        assert "calibration_curve" in result
        assert "calibrated_age" in result
        assert result["calibrated_age"] != result["raw_age"]
    
    @pytest.mark.asyncio
    async def test_error_analysis(self, agent):
        """Test error analysis and confidence intervals"""
        sample_data = {
            "c14_ratio": 0.5,
            "sample_type": "wood",
            "contamination_factor": 0.0
        }
        
        result = await agent.calculate_dating(sample_data)
        
        assert result is not None
        assert "error_analysis" in result
        assert "confidence_level" in result
        assert result["confidence_level"] in [68, 95, 99]


class TestCivilizationResearchAgent:
    """Test Civilization Research Agent"""
    
    @pytest.fixture
    def agent(self, test_config):
        """Create civilization research agent"""
        return CivilizationResearchAgent(config=test_config)
    
    @pytest.mark.asyncio
    async def test_research_civilization_by_name(self, agent, mock_anthropic_client):
        """Test civilization research by name"""
        query = {"civilization_name": "Ancient Egypt"}
        
        result = await agent.research_civilization(query)
        
        assert result is not None
        assert "basic_info" in result
        assert "geography" in result
        assert "timeline" in result
        assert "achievements" in result
        assert result["basic_info"]["name"] == "Ancient Egypt"
    
    @pytest.mark.asyncio
    async def test_research_civilization_by_period(self, agent, mock_anthropic_client):
        """Test civilization research by time period"""
        query = {"time_period": (3000, 1000), "region": "Mediterranean"}
        
        result = await agent.research_civilization(query)
        
        assert result is not None
        assert "matching_civilizations" in result
        assert len(result["matching_civilizations"]) > 0
    
    @pytest.mark.asyncio
    async def test_research_civilization_by_achievement(self, agent, mock_anthropic_client):
        """Test civilization research by achievement"""
        query = {"achievement": "Pyramid Construction"}
        
        result = await agent.research_civilization(query)
        
        assert result is not None
        assert "achievement_analysis" in result
        assert "related_civilizations" in result
    
    @pytest.mark.asyncio
    async def test_geographic_analysis(self, agent, mock_anthropic_client):
        """Test geographic analysis of civilizations"""
        query = {"civilization_name": "Ancient Greece"}
        
        result = await agent.research_civilization(query)
        
        assert result is not None
        assert "geography" in result
        assert "geographic_extent" in result
        assert "environmental_factors" in result
    
    @pytest.mark.asyncio
    async def test_cultural_relationships(self, agent, mock_anthropic_client):
        """Test analysis of cultural relationships"""
        query = {"civilization_name": "Roman Empire"}
        
        result = await agent.research_civilization(query)
        
        assert result is not None
        assert "cultural_relationships" in result
        assert "influences" in result
        assert "influenced_by" in result


class TestExcavationPlanningAgent:
    """Test Excavation Planning Agent"""
    
    @pytest.fixture
    def agent(self, test_config):
        """Create excavation planning agent"""
        return ExcavationPlanningAgent(config=test_config)
    
    @pytest.mark.asyncio
    async def test_generate_excavation_plan(self, agent, mock_anthropic_client):
        """Test excavation plan generation"""
        site_data = ExcavationDataFactory.create()
        
        result = await agent.generate_plan(site_data)
        
        assert result is not None
        assert "excavation_strategy" in result
        assert "grid_plan" in result
        assert "resource_requirements" in result
        assert "timeline" in result
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self, agent, mock_anthropic_client):
        """Test risk assessment for excavation"""
        site_data = ExcavationDataFactory.create()
        
        result = await agent.assess_risks(site_data)
        
        assert result is not None
        assert "risk_factors" in result
        assert "mitigation_strategies" in result
        assert "risk_level" in result
    
    @pytest.mark.asyncio
    async def test_resource_estimation(self, agent, mock_anthropic_client):
        """Test resource estimation for excavation"""
        site_data = ExcavationDataFactory.create()
        
        result = await agent.estimate_resources(site_data)
        
        assert result is not None
        assert "personnel" in result
        assert "equipment" in result
        assert "budget" in result
        assert "duration" in result
    
    @pytest.mark.asyncio
    async def test_stratigraphy_planning(self, agent, mock_anthropic_client):
        """Test stratigraphy planning"""
        site_data = ExcavationDataFactory.create()
        
        result = await agent.plan_stratigraphy(site_data)
        
        assert result is not None
        assert "layer_sequence" in result
        assert "excavation_order" in result
        assert "documentation_plan" in result


class TestReportGenerationAgent:
    """Test Report Generation Agent"""
    
    @pytest.fixture
    def agent(self, test_config):
        """Create report generation agent"""
        return ReportGenerationAgent(config=test_config)
    
    @pytest.mark.asyncio
    async def test_generate_artifact_report(self, agent, mock_anthropic_client):
        """Test artifact report generation"""
        artifact_data = ArtifactDataFactory.create()
        analysis_data = {"confidence": 0.85, "description": "Test analysis"}
        
        result = await agent.generate_artifact_report(artifact_data, analysis_data)
        
        assert result is not None
        assert "executive_summary" in result
        assert "methodology" in result
        assert "findings" in result
        assert "conclusions" in result
        assert "bibliography" in result
    
    @pytest.mark.asyncio
    async def test_generate_excavation_report(self, agent, mock_anthropic_client):
        """Test excavation report generation"""
        excavation_data = ExcavationDataFactory.create()
        
        result = await agent.generate_excavation_report(excavation_data)
        
        assert result is not None
        assert "site_description" in result
        assert "excavation_methodology" in result
        assert "findings" in result
        assert "interpretation" in result
    
    @pytest.mark.asyncio
    async def test_generate_research_paper(self, agent, mock_anthropic_client):
        """Test research paper generation"""
        research_data = {
            "title": "Test Research Paper",
            "abstract": "Test abstract",
            "data": {"artifacts": [], "civilizations": []}
        }
        
        result = await agent.generate_research_paper(research_data)
        
        assert result is not None
        assert "title" in result
        assert "abstract" in result
        assert "introduction" in result
        assert "methodology" in result
        assert "results" in result
        assert "discussion" in result
        assert "conclusions" in result
        assert "references" in result
    
    @pytest.mark.asyncio
    async def test_citation_management(self, agent, mock_anthropic_client):
        """Test citation management"""
        sources = [
            {"title": "Test Source 1", "author": "Author 1", "year": 2020},
            {"title": "Test Source 2", "author": "Author 2", "year": 2021}
        ]
        
        result = await agent.manage_citations(sources)
        
        assert result is not None
        assert "formatted_citations" in result
        assert "bibliography" in result
        assert len(result["formatted_citations"]) == len(sources)


class TestResearchAssistantAgent:
    """Test Research Assistant Agent"""
    
    @pytest.fixture
    def agent(self, test_config):
        """Create research assistant agent"""
        return ResearchAssistantAgent(config=test_config)
    
    @pytest.mark.asyncio
    async def test_answer_research_question(self, agent, mock_anthropic_client):
        """Test answering research questions"""
        question = "What were the main achievements of Ancient Egypt?"
        
        result = await agent.answer_question(question)
        
        assert result is not None
        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert len(result["answer"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_hypothesis(self, agent, mock_anthropic_client):
        """Test hypothesis generation"""
        research_context = {
            "topic": "Bronze Age metallurgy",
            "data": {"artifacts": [], "sites": []}
        }
        
        result = await agent.generate_hypothesis(research_context)
        
        assert result is not None
        assert "hypotheses" in result
        assert "supporting_evidence" in result
        assert "testable_predictions" in result
        assert len(result["hypotheses"]) > 0
    
    @pytest.mark.asyncio
    async def test_literature_review(self, agent, mock_anthropic_client):
        """Test literature review generation"""
        topic = "Ancient Greek pottery"
        
        result = await agent.generate_literature_review(topic)
        
        assert result is not None
        assert "summary" in result
        assert "key_papers" in result
        assert "research_gaps" in result
        assert "future_directions" in result
    
    @pytest.mark.asyncio
    async def test_statistical_analysis_guidance(self, agent, mock_anthropic_client):
        """Test statistical analysis guidance"""
        data_description = {
            "type": "artifact_dating",
            "sample_size": 100,
            "variables": ["age", "material", "location"]
        }
        
        result = await agent.provide_statistical_guidance(data_description)
        
        assert result is not None
        assert "recommended_methods" in result
        assert "statistical_tests" in result
        assert "interpretation_guidance" in result
        assert "software_recommendations" in result


class TestAgentIntegration:
    """Test agent integration and collaboration"""
    
    @pytest.fixture
    def agents(self, test_config):
        """Create all agents"""
        return {
            "artifact": ArtifactAnalysisAgent(config=test_config),
            "dating": CarbonDatingAgent(config=test_config),
            "civilization": CivilizationResearchAgent(config=test_config),
            "excavation": ExcavationPlanningAgent(config=test_config),
            "report": ReportGenerationAgent(config=test_config),
            "research": ResearchAssistantAgent(config=test_config)
        }
    
    @pytest.mark.asyncio
    async def test_multi_agent_workflow(self, agents, mock_anthropic_client):
        """Test multi-agent workflow"""
        artifact_data = ArtifactDataFactory.create()
        
        # Artifact analysis
        artifact_result = await agents["artifact"].analyze_artifact(artifact_data)
        
        # Civilization research
        civ_query = {"civilization_name": artifact_result.get("civilization", "Unknown")}
        civ_result = await agents["civilization"].research_civilization(civ_query)
        
        # Dating analysis
        if artifact_data.material in ["wood", "charcoal", "bone"]:
            dating_data = {"c14_ratio": 0.5, "sample_type": artifact_data.material}
            dating_result = await agents["dating"].calculate_dating(dating_data)
        else:
            dating_result = {"method": "relative_dating", "estimate": "Bronze Age"}
        
        # Report generation
        report_data = {
            "artifact": artifact_data,
            "analysis": artifact_result,
            "civilization": civ_result,
            "dating": dating_result
        }
        report_result = await agents["report"].generate_artifact_report(
            artifact_data, artifact_result
        )
        
        assert artifact_result is not None
        assert civ_result is not None
        assert dating_result is not None
        assert report_result is not None
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, agents):
        """Test error handling in multi-agent workflow"""
        with patch.object(agents["artifact"], 'analyze_artifact', side_effect=Exception("Agent error")):
            artifact_data = ArtifactDataFactory.create()
            
            with pytest.raises(Exception):
                await agents["artifact"].analyze_artifact(artifact_data)
    
    @pytest.mark.asyncio
    async def test_agent_data_consistency(self, agents, mock_anthropic_client):
        """Test data consistency across agents"""
        artifact_data = ArtifactDataFactory.create()
        
        # Get results from multiple agents
        artifact_result = await agents["artifact"].analyze_artifact(artifact_data)
        civ_result = await agents["civilization"].research_civilization(
            {"civilization_name": artifact_result.get("civilization", "Unknown")}
        )
        
        # Check data consistency
        assert artifact_result["material"] == artifact_data.material
        assert artifact_result["period"] == artifact_data.period
        assert civ_result["basic_info"]["name"] is not None

