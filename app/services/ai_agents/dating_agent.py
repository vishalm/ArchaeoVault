"""
Carbon Dating Agent for ArchaeoVault.

This specialized agent performs carbon dating calculations and analysis
using scientific methods and calibration curves.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentConfig, AgentRequest, AgentResponse, AgentTool
from ...models.carbon_dating import (
    CarbonSample, DatingResult, DatingEstimate, CalibrationData,
    SampleType, CalibrationCurve, DatingMethod
)


class C14CalculationTool(AgentTool):
    """Tool for C-14 dating calculations."""
    
    def __init__(self):
        super().__init__(
            name="c14_calculation",
            description="Calculate carbon-14 dating with calibration"
        )
    
    async def execute(self, sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate C-14 dating."""
        # Mock calculation - in real implementation, this would use actual C-14 libraries
        radiocarbon_age = sample_data.get("radiocarbon_age", 2000)
        error = sample_data.get("radiocarbon_error", 50)
        
        # Simple calibration (mock)
        calibrated_age = radiocarbon_age + 200  # Mock calibration offset
        
        return {
            "radiocarbon_age": radiocarbon_age,
            "radiocarbon_error": error,
            "calibrated_age": calibrated_age,
            "confidence_interval": {
                "min_age": calibrated_age - error,
                "max_age": calibrated_age + error
            },
            "confidence_level": 0.95,
            "calibration_curve": "intcal20",
            "probability_distribution": [
                (calibrated_age - error, 0.1),
                (calibrated_age, 0.8),
                (calibrated_age + error, 0.1)
            ]
        }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "sample_data": {
                    "type": "object",
                    "description": "Sample data for C-14 calculation"
                }
            },
            "required": ["sample_data"]
        }


class CalibrationTool(AgentTool):
    """Tool for calibration curve operations."""
    
    def __init__(self):
        super().__init__(
            name="calibration",
            description="Apply calibration curves to radiocarbon dates"
        )
    
    async def execute(self, radiocarbon_age: int, curve: str = "intcal20") -> Dict[str, Any]:
        """Apply calibration curve."""
        # Mock calibration - in real implementation, this would use actual calibration libraries
        calibrated_age = radiocarbon_age + 200  # Mock offset
        
        return {
            "curve_used": curve,
            "calibrated_age": calibrated_age,
            "calibration_quality": 0.95,
            "age_range_1sigma": (calibrated_age - 50, calibrated_age + 50),
            "age_range_2sigma": (calibrated_age - 100, calibrated_age + 100)
        }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "radiocarbon_age": {
                    "type": "integer",
                    "description": "Radiocarbon age in BP"
                },
                "curve": {
                    "type": "string",
                    "description": "Calibration curve to use"
                }
            },
            "required": ["radiocarbon_age"]
        }


class CarbonDatingAgent(BaseAgent):
    """
    Specialized agent for carbon dating calculations.
    
    This agent provides scientific carbon dating calculations,
    calibration, and error analysis.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.agent_name = "CarbonDatingAgent"
        self.logger = logging.getLogger(self.agent_name)
    
    def _initialize_tools(self) -> List[AgentTool]:
        """Initialize carbon dating tools."""
        return [
            C14CalculationTool(),
            CalibrationTool()
        ]
    
    async def _process_request_impl(self, request: AgentRequest) -> AgentResponse:
        """Process carbon dating request."""
        try:
            # Extract sample data from request
            sample_data = CarbonSample(**request.data.get("sample_data", {}))
            
            # Perform carbon dating calculation
            dating_result = await self._perform_carbon_dating(sample_data)
            
            # Create response
            response_data = {
                "sample_id": str(sample_data.id),
                "dating_result": dating_result.dict(),
                "interpretation": self._interpret_results(dating_result),
                "recommendations": self._generate_recommendations(dating_result)
            }
            
            return AgentResponse(
                request_id=request.request_id,
                agent_type=self.agent_name,
                agent_version=self.config.agent_version,
                data=response_data,
                confidence=dating_result.confidence_level,
                processing_time=0.0,
                model_used=self.config.model,
                quality_score=dating_result.calibration_quality,
                completeness_score=1.0,
                tools_used=[tool.name for tool in self.tools],
                tool_calls=len(self.tools)
            )
            
        except Exception as e:
            self.logger.error(f"Error in carbon dating: {e}")
            raise e
    
    async def _perform_carbon_dating(self, sample: CarbonSample) -> DatingResult:
        """Perform carbon dating calculation."""
        # Use C-14 calculation tool
        calculation_result = await self.call_tool(
            "c14_calculation",
            sample_data=sample.dict()
        )
        
        # Apply calibration
        calibration_result = await self.call_tool(
            "calibration",
            radiocarbon_age=calculation_result["radiocarbon_age"],
            curve=sample.calibration_curve.value
        )
        
        # Create dating result
        result = DatingResult(
            sample_id=sample.id,
            calculation_method="c14_calculation",
            calibration_curve=sample.calibration_curve,
            radiocarbon_age=calculation_result["radiocarbon_age"],
            radiocarbon_error=calculation_result["radiocarbon_error"],
            calibrated_ages=calculation_result["probability_distribution"],
            best_estimate=calibration_result["calibrated_age"],
            confidence_intervals={
                "1σ": calibration_result["age_range_1sigma"],
                "2σ": calibration_result["age_range_2sigma"]
            },
            probability_distribution=calculation_result["probability_distribution"],
            peak_probability=max(calculation_result["probability_distribution"], key=lambda x: x[1])[1],
            age_range_1sigma=calibration_result["age_range_1sigma"],
            age_range_2sigma=calibration_result["age_range_2sigma"],
            calibration_quality=calibration_result["calibration_quality"],
            confidence_level=calculation_result["confidence_level"],
            notes=f"Calculated using {sample.calibration_curve.value} calibration curve"
        )
        
        return result
    
    def _interpret_results(self, result: DatingResult) -> str:
        """Interpret dating results."""
        return f"Sample dates to {result.best_estimate} cal BP with {result.confidence_level:.1%} confidence"
    
    def _generate_recommendations(self, result: DatingResult) -> List[str]:
        """Generate recommendations based on results."""
        recommendations = []
        
        if result.calibration_quality < 0.8:
            recommendations.append("Consider using a different calibration curve")
        
        if result.confidence_level < 0.9:
            recommendations.append("Consider additional dating samples for confirmation")
        
        if result.peak_probability < 0.5:
            recommendations.append("Multiple age ranges possible - consider additional analysis")
        
        return recommendations
