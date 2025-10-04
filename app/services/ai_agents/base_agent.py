"""
Base AI agent implementation for ArchaeoVault.

This module provides the base classes and interfaces for all AI agents,
following the agentic AI architecture pattern.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field

import anthropic
from pydantic import BaseModel, Field

from ...models.base import BaseModel as PydanticBaseModel


@dataclass
class AgentConfig:
    """Configuration for AI agents."""
    
    # API configuration
    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 30
    
    # Agent configuration
    agent_name: str = "BaseAgent"
    agent_version: str = "1.0.0"
    max_retries: int = 3
    retry_delay: float = 1.0
    cache_ttl: int = 3600
    
    # Memory configuration
    memory_enabled: bool = True
    memory_size: int = 1000
    memory_ttl: int = 86400
    
    # Tool configuration
    tools_enabled: bool = True
    max_tool_calls: int = 10
    tool_timeout: int = 15


class AgentRequest(PydanticBaseModel):
    """Request model for AI agents."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str = Field(..., description="Type of agent")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    
    # Request data
    data: Dict[str, Any] = Field(..., description="Request data")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    # Request metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(default=0, description="Request priority")
    timeout: Optional[int] = Field(None, description="Request timeout")
    
    # Processing options
    use_cache: bool = Field(default=True, description="Use cached results")
    use_memory: bool = Field(default=True, description="Use agent memory")
    use_tools: bool = Field(default=True, description="Use agent tools")


class AgentResponse(PydanticBaseModel):
    """Response model for AI agents."""
    
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="Original request ID")
    agent_type: str = Field(..., description="Type of agent")
    agent_version: str = Field(..., description="Agent version")
    
    # Response data
    data: Dict[str, Any] = Field(..., description="Response data")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence")
    
    # Processing information
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    tokens_used: int = Field(default=0, ge=0, description="Tokens used")
    model_used: str = Field(..., description="Model used")
    
    # Quality metrics
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score")
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="Completeness score")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = Field(default=False, description="Result was cached")
    error: Optional[str] = Field(None, description="Error message if any")
    
    # Tool usage
    tools_used: List[str] = Field(default_factory=list, description="Tools used")
    tool_calls: int = Field(default=0, ge=0, description="Number of tool calls")


class AgentMemory:
    """Agent memory system for context retention."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 86400):
        self.max_size = max_size
        self.ttl = ttl
        self.memory: Dict[str, Any] = {}
        self.timestamps: Dict[str, datetime] = {}
    
    def store(self, key: str, value: Any) -> None:
        """Store value in memory."""
        self.memory[key] = value
        self.timestamps[key] = datetime.utcnow()
        
        # Clean up old entries
        self._cleanup()
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from memory."""
        if key not in self.memory:
            return None
        
        # Check if expired
        if self._is_expired(key):
            del self.memory[key]
            del self.timestamps[key]
            return None
        
        return self.memory[key]
    
    def clear(self) -> None:
        """Clear all memory."""
        self.memory.clear()
        self.timestamps.clear()
    
    def _is_expired(self, key: str) -> bool:
        """Check if memory entry is expired."""
        if key not in self.timestamps:
            return True
        
        age = (datetime.utcnow() - self.timestamps[key]).total_seconds()
        return age > self.ttl
    
    def _cleanup(self) -> None:
        """Clean up expired entries and maintain size limit."""
        # Remove expired entries
        expired_keys = [k for k in self.memory.keys() if self._is_expired(k)]
        for key in expired_keys:
            del self.memory[key]
            del self.timestamps[key]
        
        # Maintain size limit
        if len(self.memory) > self.max_size:
            # Remove oldest entries
            sorted_keys = sorted(
                self.timestamps.keys(),
                key=lambda k: self.timestamps[k]
            )
            keys_to_remove = sorted_keys[:len(self.memory) - self.max_size]
            for key in keys_to_remove:
                del self.memory[key]
                del self.timestamps[key]


class AgentTool(ABC):
    """Base class for agent tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for AI model."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    @abstractmethod
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema for the tool."""
        pass


class BaseAgent(ABC):
    """
    Base class for all AI agents.
    
    This class provides common functionality for all specialized agents
    including memory management, tool integration, and error handling.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Initialize Claude client
        self.client = anthropic.Anthropic(api_key=config.api_key)
        
        # Initialize memory
        self.memory = AgentMemory(
            max_size=config.memory_size,
            ttl=config.memory_ttl
        ) if config.memory_enabled else None
        
        # Initialize tools
        self.tools = self._initialize_tools() if config.tools_enabled else []
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # Agent state
        self.is_available = True
        self.current_requests = 0
        self.total_requests = 0
        self.total_processing_time = 0.0
    
    @abstractmethod
    def _initialize_tools(self) -> List[AgentTool]:
        """Initialize agent-specific tools."""
        pass
    
    @abstractmethod
    async def _process_request(self, request: AgentRequest) -> AgentResponse:
        """Process a request using the agent's specialized logic."""
        pass
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request using the agent.
        
        This method handles common functionality like caching, memory,
        error handling, and tool integration.
        """
        start_time = time.time()
        self.current_requests += 1
        self.total_requests += 1
        
        try:
            # Check if agent is available
            if not self.is_available:
                raise Exception("Agent is not available")
            
            # Check cache if enabled
            if request.use_cache:
                cached_response = await self._get_cached_response(request)
                if cached_response:
                    self.logger.info(f"Returning cached response for request {request.request_id}")
                    return cached_response
            
            # Process request
            response = await self._process_request(request)
            
            # Update processing time
            processing_time = time.time() - start_time
            response.processing_time = processing_time
            self.total_processing_time += processing_time
            
            # Cache response if enabled
            if request.use_cache:
                await self._cache_response(request, response)
            
            # Store in memory if enabled
            if request.use_memory and self.memory:
                self._store_in_memory(request, response)
            
            self.logger.info(f"Processed request {request.request_id} in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing request {request.request_id}: {e}")
            processing_time = time.time() - start_time
            
            return AgentResponse(
                request_id=request.request_id,
                agent_type=self.config.agent_name,
                agent_version=self.config.agent_version,
                data={"error": str(e)},
                confidence=0.0,
                processing_time=processing_time,
                model_used=self.config.model,
                quality_score=0.0,
                completeness_score=0.0,
                error=str(e)
            )
        
        finally:
            self.current_requests -= 1
    
    async def _process_request(self, request: AgentRequest) -> AgentResponse:
        """Process request with retry logic."""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                return await self._process_request_impl(request)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                else:
                    self.logger.error(f"All attempts failed: {e}")
                    raise e
        
        raise last_error
    
    async def _process_request_impl(self, request: AgentRequest) -> AgentResponse:
        """Implementation of request processing."""
        # This will be overridden by specialized agents
        return await self._process_request(request)
    
    async def _get_cached_response(self, request: AgentRequest) -> Optional[AgentResponse]:
        """Get cached response if available."""
        # This would integrate with the cache manager
        # For now, return None (no caching)
        return None
    
    async def _cache_response(self, request: AgentRequest, response: AgentResponse) -> None:
        """Cache response for future use."""
        # This would integrate with the cache manager
        pass
    
    def _store_in_memory(self, request: AgentRequest, response: AgentResponse) -> None:
        """Store request/response in agent memory."""
        if not self.memory:
            return
        
        # Store key information
        memory_key = f"{request.agent_type}:{request.request_id}"
        self.memory.store(memory_key, {
            "request": request.dict(),
            "response": response.dict(),
            "timestamp": datetime.utcnow()
        })
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a specific tool."""
        if tool_name not in self.tool_map:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tool_map[tool_name]
        return await tool.execute(**kwargs)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools."""
        return [tool.get_schema() for tool in self.tools]
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory usage summary."""
        if not self.memory:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "size": len(self.memory.memory),
            "max_size": self.memory.max_size,
            "ttl": self.memory.ttl
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        avg_processing_time = (
            self.total_processing_time / self.total_requests
            if self.total_requests > 0 else 0
        )
        
        return {
            "total_requests": self.total_requests,
            "current_requests": self.current_requests,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": avg_processing_time,
            "is_available": self.is_available,
            "tools_count": len(self.tools),
            "memory_enabled": self.memory is not None
        }
    
    def set_availability(self, available: bool) -> None:
        """Set agent availability."""
        self.is_available = available
        self.logger.info(f"Agent availability set to {available}")
    
    def clear_memory(self) -> None:
        """Clear agent memory."""
        if self.memory:
            self.memory.clear()
            self.logger.info("Agent memory cleared")
    
    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self.total_requests = 0
        self.total_processing_time = 0.0
        self.logger.info("Agent metrics reset")
