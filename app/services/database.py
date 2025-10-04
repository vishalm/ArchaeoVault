"""
Database management service for ArchaeoVault.

This module provides database connection management, query execution,
and data persistence following 12-Factor App principles.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from ..config import DatabaseSettings
from ..models.base import SQLAlchemyBase


class DatabaseManager:
    """
    Database connection and management service.
    
    This class handles database connections, query execution,
    and connection pooling following 12-Factor App principles.
    """
    
    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Connection pool
        self.pool: Optional[asyncpg.Pool] = None
        self.engine = None
        self.async_session = None
        
        # Connection state
        self.is_connected = False
        self.connection_count = 0
        self.max_connections = settings.pool_size + settings.pool_overflow
        
        self.logger.info("Database manager initialized for %s", settings.host)
    
    async def initialize(self) -> None:
        """Initialize database connections and pool."""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.settings.url,
                poolclass=QueuePool,
                pool_size=self.settings.pool_size,
                max_overflow=self.settings.pool_overflow,
                pool_timeout=self.settings.pool_timeout,
                pool_recycle=self.settings.pool_recycle,
                echo=False  # Set to True for SQL debugging
            )
            
            # Create async session factory
            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self.is_connected = True
            self.logger.info("Database connection established successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize database: %s", e)
            raise e
    
    async def close(self) -> None:
        """Close database connections and pool."""
        try:
            if self.engine:
                await self.engine.dispose()
            
            if self.pool:
                await self.pool.close()
            
            self.is_connected = False
            self.logger.info("Database connections closed")
            
        except Exception as e:
            self.logger.error("Error closing database connections: %s", e)
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session context manager."""
        if not self.is_connected:
            raise Exception("Database not connected")
        
        session = self.async_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a raw SQL query."""
        if not self.is_connected:
            raise Exception("Database not connected")
        
        try:
            async with self.get_session() as session:
                result = await session.execute(text(query), params or {})
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                return [dict(row._mapping) for row in rows]
                
        except Exception as e:
            self.logger.error("Query execution failed: %s", e)
            raise e
    
    async def execute_scalar(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query that returns a single scalar value."""
        if not self.is_connected:
            raise Exception("Database not connected")
        
        try:
            async with self.get_session() as session:
                result = await session.execute(text(query), params or {})
                return result.scalar()
                
        except Exception as e:
            self.logger.error("Scalar query execution failed: %s", e)
            raise e
    
    async def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute an update/insert/delete query."""
        if not self.is_connected:
            raise Exception("Database not connected")
        
        try:
            async with self.get_session() as session:
                result = await session.execute(text(query), params or {})
                await session.commit()
                return result.rowcount
                
        except Exception as e:
            self.logger.error("Update query execution failed: %s", e)
            raise e
    
    async def create_tables(self) -> None:
        """Create database tables."""
        if not self.is_connected:
            raise Exception("Database not connected")
        
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLAlchemyBase.metadata.create_all)
            
            self.logger.info("Database tables created successfully")
            
        except Exception as e:
            self.logger.error("Failed to create tables: %s", e)
            raise e
    
    async def drop_tables(self) -> None:
        """Drop all database tables."""
        if not self.is_connected:
            raise Exception("Database not connected")
        
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLAlchemyBase.metadata.drop_all)
            
            self.logger.info("Database tables dropped successfully")
            
        except Exception as e:
            self.logger.error("Failed to drop tables: %s", e)
            raise e
    
    async def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get information about a table."""
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = :table_name
        ORDER BY ordinal_position
        """
        
        return await self.execute_query(query, {"table_name": table_name})
    
    async def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get statistics about a table."""
        query = """
        SELECT 
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats 
        WHERE tablename = :table_name
        """
        
        stats = await self.execute_query(query, {"table_name": table_name})
        
        # Get row count
        count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
        row_count = await self.execute_scalar(count_query)
        
        return {
            "table_name": table_name,
            "row_count": row_count,
            "column_stats": stats
        }
    
    async def backup_table(self, table_name: str, backup_name: Optional[str] = None) -> str:
        """Create a backup of a table."""
        if not backup_name:
            backup_name = f"{table_name}_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        query = f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}"
        await self.execute_update(query)
        
        self.logger.info("Table backup created: %s", backup_name)
        return backup_name
    
    async def restore_table(self, table_name: str, backup_name: str) -> None:
        """Restore a table from backup."""
        # Drop existing table
        await self.execute_update(f"DROP TABLE IF EXISTS {table_name}")
        
        # Restore from backup
        query = f"CREATE TABLE {table_name} AS SELECT * FROM {backup_name}"
        await self.execute_update(query)
        
        self.logger.info("Table restored from backup: %s", backup_name)
    
    async def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance."""
        optimization_results = {}
        
        try:
            # Analyze tables
            analyze_query = "ANALYZE"
            await self.execute_update(analyze_query)
            optimization_results["analyze"] = "completed"
            
            # Vacuum tables
            vacuum_query = "VACUUM"
            await self.execute_update(vacuum_query)
            optimization_results["vacuum"] = "completed"
            
            # Get database size
            size_query = """
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as database_size
            """
            size_result = await self.execute_scalar(size_query)
            optimization_results["database_size"] = size_result
            
            self.logger.info("Database optimization completed")
            
        except Exception as e:
            self.logger.error("Database optimization failed: %s", e)
            optimization_results["error"] = str(e)
        
        return optimization_results
    
    async def get_connection_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status."""
        if not self.engine:
            return {"status": "not_initialized"}
        
        pool = self.engine.pool
        return {
            "status": "active" if self.is_connected else "inactive",
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            self.logger.error("Connection test failed: %s", e)
            return False
    
    def get_database_url(self) -> str:
        """Get database URL."""
        return self.settings.url
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.is_connected
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information."""
        try:
            # Database version
            version_query = "SELECT version() as version"
            version = await self.execute_scalar(version_query)
            
            # Database size
            size_query = "SELECT pg_size_pretty(pg_database_size(current_database())) as size"
            size = await self.execute_scalar(size_query)
            
            # Connection count
            connections_query = """
            SELECT count(*) as connection_count 
            FROM pg_stat_activity 
            WHERE datname = current_database()
            """
            connections = await self.execute_scalar(connections_query)
            
            # Table count
            tables_query = """
            SELECT count(*) as table_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
            tables = await self.execute_scalar(tables_query)
            
            return {
                "version": version,
                "size": size,
                "connections": connections,
                "tables": tables,
                "connected": self.is_connected,
                "pool_status": await self.get_connection_pool_status()
            }
            
        except Exception as e:
            self.logger.error("Failed to get database info: %s", e)
            return {"error": str(e)}
