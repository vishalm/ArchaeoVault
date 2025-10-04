"""
Cache management service for ArchaeoVault.

This module provides Redis-based caching functionality following
12-Factor App principles for performance optimization.
"""

import asyncio
import json
import logging
import pickle
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from ..config import RedisSettings


class CacheManager:
    """
    Redis-based cache management service.
    
    This class provides high-level caching functionality using Redis
    with connection pooling and automatic serialization.
    """
    
    def __init__(self, settings: RedisSettings):
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Redis connection
        self.redis: Optional[redis.Redis] = None
        self.pool: Optional[ConnectionPool] = None
        
        # Cache configuration
        self.default_ttl = 3600  # 1 hour
        self.serializer = "json"  # json or pickle
        
        # Connection state
        self.is_connected = False
        
        self.logger.info("Cache manager initialized for %s:%d", settings.host, settings.port)
    
    async def initialize(self) -> None:
        """Initialize Redis connection and pool."""
        try:
            # Create connection pool
            self.pool = ConnectionPool(
                host=self.settings.host,
                port=self.settings.port,
                db=self.settings.db,
                password=self.settings.password,
                max_connections=self.settings.pool_size,
                socket_timeout=self.settings.pool_timeout,
                decode_responses=False  # We'll handle encoding/decoding ourselves
            )
            
            # Create Redis client
            self.redis = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.redis.ping()
            
            self.is_connected = True
            self.logger.info("Redis connection established successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize Redis: %s", e)
            raise e
    
    async def close(self) -> None:
        """Close Redis connection and pool."""
        try:
            if self.redis:
                await self.redis.close()
            
            if self.pool:
                await self.pool.disconnect()
            
            self.is_connected = False
            self.logger.info("Redis connections closed")
            
        except Exception as e:
            self.logger.error("Error closing Redis connections: %s", e)
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data for storage."""
        if self.serializer == "json":
            return json.dumps(data, default=str).encode('utf-8')
        elif self.serializer == "pickle":
            return pickle.dumps(data)
        else:
            raise ValueError(f"Unknown serializer: {self.serializer}")
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data from storage."""
        if self.serializer == "json":
            return json.loads(data.decode('utf-8'))
        elif self.serializer == "pickle":
            return pickle.loads(data)
        else:
            raise ValueError(f"Unknown serializer: {self.serializer}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_connected:
            return None
        
        try:
            data = await self.redis.get(key)
            if data is None:
                return None
            
            return self._deserialize(data)
            
        except Exception as e:
            self.logger.error("Cache get failed for key %s: %s", key, e)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.is_connected:
            return False
        
        try:
            serialized_value = self._serialize(value)
            ttl = ttl or self.default_ttl
            
            await self.redis.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            self.logger.error("Cache set failed for key %s: %s", key, e)
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis.delete(key)
            return result > 0
            
        except Exception as e:
            self.logger.error("Cache delete failed for key %s: %s", key, e)
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis.exists(key)
            return result > 0
            
        except Exception as e:
            self.logger.error("Cache exists check failed for key %s: %s", key, e)
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key."""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis.expire(key, ttl)
            return result
            
        except Exception as e:
            self.logger.error("Cache expire failed for key %s: %s", key, e)
            return False
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        if not self.is_connected:
            return -1
        
        try:
            return await self.redis.ttl(key)
            
        except Exception as e:
            self.logger.error("Cache TTL check failed for key %s: %s", key, e)
            return -1
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        if not self.is_connected:
            return []
        
        try:
            keys = await self.redis.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
            
        except Exception as e:
            self.logger.error("Cache keys search failed for pattern %s: %s", pattern, e)
            return []
    
    async def flush(self) -> bool:
        """Flush all keys from cache."""
        if not self.is_connected:
            return False
        
        try:
            await self.redis.flushdb()
            return True
            
        except Exception as e:
            self.logger.error("Cache flush failed: %s", e)
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        if not self.is_connected:
            return {}
        
        try:
            values = await self.redis.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)
            
            return result
            
        except Exception as e:
            self.logger.error("Cache get_many failed for keys %s: %s", keys, e)
            return {}
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        if not self.is_connected:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized_mapping = {k: self._serialize(v) for k, v in mapping.items()}
            
            # Use pipeline for better performance
            pipe = self.redis.pipeline()
            for key, value in serialized_mapping.items():
                pipe.setex(key, ttl, value)
            
            await pipe.execute()
            return True
            
        except Exception as e:
            self.logger.error("Cache set_many failed: %s", e)
            return False
    
    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from cache."""
        if not self.is_connected:
            return 0
        
        try:
            result = await self.redis.delete(*keys)
            return result
            
        except Exception as e:
            self.logger.error("Cache delete_many failed for keys %s: %s", keys, e)
            return 0
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache."""
        if not self.is_connected:
            return None
        
        try:
            result = await self.redis.incrby(key, amount)
            return result
            
        except Exception as e:
            self.logger.error("Cache increment failed for key %s: %s", key, e)
            return None
    
    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement numeric value in cache."""
        if not self.is_connected:
            return None
        
        try:
            result = await self.redis.decrby(key, amount)
            return result
            
        except Exception as e:
            self.logger.error("Cache decrement failed for key %s: %s", key, e)
            return None
    
    async def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Value not in cache, generate it
        if asyncio.iscoroutinefunction(factory_func):
            value = await factory_func()
        else:
            value = factory_func()
        
        # Store in cache
        await self.set(key, value, ttl)
        return value
    
    async def cache_artifact_analysis(self, artifact_id: str, analysis: Dict[str, Any], ttl: int = 7200) -> bool:
        """Cache artifact analysis results."""
        key = f"artifact_analysis:{artifact_id}"
        return await self.set(key, analysis, ttl)
    
    async def get_artifact_analysis(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Get cached artifact analysis results."""
        key = f"artifact_analysis:{artifact_id}"
        return await self.get(key)
    
    async def cache_civilization_research(self, civilization_id: str, research: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache civilization research results."""
        key = f"civilization_research:{civilization_id}"
        return await self.set(key, research, ttl)
    
    async def get_civilization_research(self, civilization_id: str) -> Optional[Dict[str, Any]]:
        """Get cached civilization research results."""
        key = f"civilization_research:{civilization_id}"
        return await self.get(key)
    
    async def cache_excavation_plan(self, excavation_id: str, plan: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache excavation plan."""
        key = f"excavation_plan:{excavation_id}"
        return await self.set(key, plan, ttl)
    
    async def get_excavation_plan(self, excavation_id: str) -> Optional[Dict[str, Any]]:
        """Get cached excavation plan."""
        key = f"excavation_plan:{excavation_id}"
        return await self.get(key)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.is_connected:
            return {"status": "not_connected"}
        
        try:
            info = await self.redis.info()
            
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
                    if (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)) > 0 else 0
                )
            }
            
        except Exception as e:
            self.logger.error("Failed to get cache stats: %s", e)
            return {"status": "error", "error": str(e)}
    
    def is_connected(self) -> bool:
        """Check if cache is connected."""
        return self.is_connected
    
    async def test_connection(self) -> bool:
        """Test cache connection."""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            self.logger.error("Cache connection test failed: %s", e)
            return False
