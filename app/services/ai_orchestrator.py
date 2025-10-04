"""
AI Orchestrator for ArchaeoVault.

This module provides the central orchestration system that coordinates
multiple specialized AI agents to handle complex archaeological tasks.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass

from .ai_agents import (
    ArtifactAnalysisAgent, CarbonDatingAgent, CivilizationResearchAgent,
    ExcavationPlanningAgent, ReportGenerationAgent, ResearchAssistantAgent,
    AgentConfig, AgentRequest, AgentResponse
)
from ..config import AISettings
from ..models.base import BaseModel


@dataclass
class WorkflowStep:
    """Represents a step in a multi-agent workflow."""
    
    agent_type: str
    action: str
    input_data: Dict[str, Any]
    dependencies: List[str] = None
    timeout: int = 30
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    
    step_id: str
    agent_type: str
    success: bool
    result: Optional[AgentResponse] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class AIOrchestrator:
    """
    Central orchestrator for AI agents.
    
    This class coordinates multiple specialized AI agents to handle
    complex archaeological tasks that require multiple agents working together.
    """
    
    def __init__(self, settings: AISettings, cache_manager=None):
        self.settings = settings
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize agent configuration
        self.agent_config = AgentConfig(
            api_key=settings.anthropic_api_key,
            model=settings.default_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            timeout=settings.timeout,
            max_retries=settings.agent_max_retries,
            retry_delay=settings.agent_retry_delay,
            cache_ttl=settings.agent_cache_ttl
        )
        
        # Initialize agents
        self.agents = {
            "artifact_analysis": ArtifactAnalysisAgent(self.agent_config),
            "carbon_dating": CarbonDatingAgent(self.agent_config),
            "civilization_research": CivilizationResearchAgent(self.agent_config),
            "excavation_planning": ExcavationPlanningAgent(self.agent_config),
            "report_generation": ReportGenerationAgent(self.agent_config),
            "research_assistant": ResearchAssistantAgent(self.agent_config)
        }
        
        # Workflow state
        self.active_workflows: Dict[str, List[WorkflowStep]] = {}
        self.workflow_results: Dict[str, List[WorkflowResult]] = {}
        
        self.logger.info("AI Orchestrator initialized with %d agents", len(self.agents))
    
    async def process_simple_request(self, agent_type: str, request_data: Dict[str, Any]) -> AgentResponse:
        """
        Process a simple request using a single agent.
        
        Args:
            agent_type: Type of agent to use
            request_data: Request data
            
        Returns:
            Agent response
        """
        if agent_type not in self.agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent = self.agents[agent_type]
        request = AgentRequest(
            agent_type=agent_type,
            data=request_data
        )
        
        return await agent.process(request)
    
    async def process_complex_request(self, workflow_steps: List[WorkflowStep]) -> Dict[str, Any]:
        """
        Process a complex request using multiple agents in a workflow.
        
        Args:
            workflow_steps: List of workflow steps
            
        Returns:
            Combined results from all agents
        """
        workflow_id = f"workflow_{datetime.utcnow().timestamp()}"
        self.active_workflows[workflow_id] = workflow_steps
        self.workflow_results[workflow_id] = []
        
        try:
            # Execute workflow steps
            results = await self._execute_workflow(workflow_id, workflow_steps)
            
            # Combine results
            combined_results = self._combine_workflow_results(results)
            
            self.logger.info("Workflow %s completed with %d steps", workflow_id, len(results))
            return combined_results
            
        except Exception as e:
            self.logger.error("Workflow %s failed: %s", workflow_id, e)
            raise e
        
        finally:
            # Clean up
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            if workflow_id in self.workflow_results:
                del self.workflow_results[workflow_id]
    
    async def _execute_workflow(self, workflow_id: str, steps: List[WorkflowStep]) -> List[WorkflowResult]:
        """Execute workflow steps in order."""
        results = []
        
        for i, step in enumerate(steps):
            step_id = f"{workflow_id}_step_{i}"
            
            try:
                # Check dependencies
                if step.dependencies:
                    dependency_results = [r for r in results if r.step_id in step.dependencies]
                    if not all(r.success for r in dependency_results):
                        raise Exception(f"Dependencies not met for step {step_id}")
                
                # Execute step
                result = await self._execute_workflow_step(step_id, step)
                results.append(result)
                
                # Update workflow results
                self.workflow_results[workflow_id].append(result)
                
            except Exception as e:
                self.logger.error("Step %s failed: %s", step_id, e)
                results.append(WorkflowResult(
                    step_id=step_id,
                    agent_type=step.agent_type,
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    async def _execute_workflow_step(self, step_id: str, step: WorkflowStep) -> WorkflowResult:
        """Execute a single workflow step."""
        start_time = datetime.utcnow()
        
        try:
            if step.agent_type not in self.agents:
                raise ValueError(f"Unknown agent type: {step.agent_type}")
            
            agent = self.agents[step.agent_type]
            request = AgentRequest(
                agent_type=step.agent_type,
                data=step.input_data
            )
            
            # Execute with timeout
            response = await asyncio.wait_for(
                agent.process(request),
                timeout=step.timeout
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return WorkflowResult(
                step_id=step_id,
                agent_type=step.agent_type,
                success=True,
                result=response,
                execution_time=execution_time
            )
            
        except asyncio.TimeoutError:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return WorkflowResult(
                step_id=step_id,
                agent_type=step.agent_type,
                success=False,
                error="Timeout",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return WorkflowResult(
                step_id=step_id,
                agent_type=step.agent_type,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def _combine_workflow_results(self, results: List[WorkflowResult]) -> Dict[str, Any]:
        """Combine results from multiple workflow steps."""
        combined = {
            "workflow_summary": {
                "total_steps": len(results),
                "successful_steps": len([r for r in results if r.success]),
                "failed_steps": len([r for r in results if not r.success]),
                "total_execution_time": sum(r.execution_time for r in results)
            },
            "step_results": [],
            "combined_data": {},
            "errors": []
        }
        
        for result in results:
            step_info = {
                "step_id": result.step_id,
                "agent_type": result.agent_type,
                "success": result.success,
                "execution_time": result.execution_time
            }
            
            if result.success and result.result:
                step_info["data"] = result.result.data
                step_info["confidence"] = result.result.confidence
                
                # Combine data
                combined["combined_data"][result.agent_type] = result.result.data
            else:
                step_info["error"] = result.error
                combined["errors"].append({
                    "step_id": result.step_id,
                    "agent_type": result.agent_type,
                    "error": result.error
                })
            
            combined["step_results"].append(step_info)
        
        return combined
    
    def create_artifact_analysis_workflow(self, artifact_data: Dict[str, Any]) -> List[WorkflowStep]:
        """Create workflow for comprehensive artifact analysis."""
        return [
            WorkflowStep(
                agent_type="artifact_analysis",
                action="analyze_artifact",
                input_data={"artifact_data": artifact_data}
            ),
            WorkflowStep(
                agent_type="carbon_dating",
                action="calculate_dating",
                input_data={"sample_data": artifact_data.get("dating_sample", {})},
                dependencies=["artifact_analysis"]
            ),
            WorkflowStep(
                agent_type="civilization_research",
                action="research_context",
                input_data={"civilization_data": artifact_data.get("civilization_context", {})},
                dependencies=["artifact_analysis"]
            )
        ]
    
    def create_excavation_planning_workflow(self, excavation_data: Dict[str, Any]) -> List[WorkflowStep]:
        """Create workflow for excavation planning."""
        return [
            WorkflowStep(
                agent_type="excavation_planning",
                action="generate_plan",
                input_data={"excavation_data": excavation_data}
            ),
            WorkflowStep(
                agent_type="report_generation",
                action="generate_plan_report",
                input_data={"excavation_plan": excavation_data},
                dependencies=["excavation_planning"]
            )
        ]
    
    def create_research_workflow(self, research_query: str, context: Dict[str, Any]) -> List[WorkflowStep]:
        """Create workflow for comprehensive research."""
        return [
            WorkflowStep(
                agent_type="research_assistant",
                action="comprehensive_research",
                input_data={"research_query": research_query, "research_context": context}
            ),
            WorkflowStep(
                agent_type="report_generation",
                action="generate_research_report",
                input_data={"research_results": context},
                dependencies=["research_assistant"]
            )
        ]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        for agent_type, agent in self.agents.items():
            status[agent_type] = {
                "available": agent.is_available,
                "current_requests": agent.current_requests,
                "total_requests": agent.total_requests,
                "average_processing_time": (
                    agent.total_processing_time / agent.total_requests
                    if agent.total_requests > 0 else 0
                ),
                "tools_count": len(agent.tools),
                "memory_enabled": agent.memory is not None
            }
        return status
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of active workflows."""
        return {
            "active_workflows": len(self.active_workflows),
            "workflow_details": {
                workflow_id: {
                    "total_steps": len(steps),
                    "completed_steps": len(self.workflow_results.get(workflow_id, [])),
                    "successful_steps": len([
                        r for r in self.workflow_results.get(workflow_id, [])
                        if r.success
                    ])
                }
                for workflow_id, steps in self.active_workflows.items()
            }
        }
    
    def is_available(self) -> bool:
        """Check if orchestrator is available."""
        return any(agent.is_available for agent in self.agents.values())
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents."""
        return [agent_type for agent_type, agent in self.agents.items() if agent.is_available]
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all agents."""
        capabilities = {}
        for agent_type, agent in self.agents.items():
            capabilities[agent_type] = [tool.name for tool in agent.tools]
        return capabilities
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents."""
        health_status = {
            "orchestrator_available": self.is_available(),
            "agents": {},
            "overall_health": "healthy"
        }
        
        unhealthy_agents = 0
        for agent_type, agent in self.agents.items():
            try:
                # Simple health check - try to get agent metrics
                metrics = agent.get_performance_metrics()
                health_status["agents"][agent_type] = {
                    "status": "healthy",
                    "available": agent.is_available,
                    "metrics": metrics
                }
            except Exception as e:
                health_status["agents"][agent_type] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                unhealthy_agents += 1
        
        if unhealthy_agents > 0:
            health_status["overall_health"] = "degraded"
        if unhealthy_agents == len(self.agents):
            health_status["overall_health"] = "unhealthy"
        
        return health_status
