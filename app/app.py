"""
Main application entry point for ArchaeoVault.

This module creates and configures the Streamlit application with all
necessary components, following 12-Factor App principles.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import streamlit as st
from streamlit import config as st_config

try:
    from .config import get_settings
    from .services.ai_orchestrator import AIOrchestrator
    from .services.database import DatabaseManager
    from .services.cache import CacheManager
    from .services.storage import StorageManager
    from .utils.logging import setup_logging
    from .utils.exceptions import ArchaeoVaultError
except ImportError:
    from config import get_settings
    from services.ai_orchestrator import AIOrchestrator
    from services.database import DatabaseManager
    from services.cache import CacheManager
    from services.storage import StorageManager
    from utils.logging import setup_logging
    from utils.exceptions import ArchaeoVaultError


class ArchaeoVaultApp:
    """Main application class for ArchaeoVault."""
    
    def __init__(self):
        """Initialize the application."""
        self.settings = get_settings()
        self._setup_logging()
        self._setup_streamlit_config()
        self._initialize_services()
    
    def _setup_logging(self) -> None:
        """Setup application logging."""
        setup_logging(self.settings.logging)
        self.logger = logging.getLogger(__name__)
        self.logger.info("ArchaeoVault application initialized")
    
    def _setup_streamlit_config(self) -> None:
        """Configure Streamlit settings."""
        # Set Streamlit configuration
        st_config.set_option("server.port", self.settings.streamlit.port)
        st_config.set_option("server.address", self.settings.streamlit.host)
        st_config.set_option("server.headless", self.settings.streamlit.headless)
        st_config.set_option("server.runOnSave", self.settings.streamlit.server_run_on_save)
        st_config.set_option("server.fileWatcherType", self.settings.streamlit.server_file_watcher_type)
        st_config.set_option("browser.gatherUsageStats", self.settings.streamlit.browser_gather_usage_stats)
        
        # Set page configuration
        st.set_page_config(
            page_title=self.settings.app_name,
            page_icon="🏺",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                "Get Help": "https://github.com/vishalm/ArchaeoVault",
                "Report a bug": "https://github.com/vishalm/ArchaeoVault/issues",
                "About": f"{self.settings.app_name} v{self.settings.app_version}"
            }
        )
    
    def _initialize_services(self) -> None:
        """Initialize application services."""
        try:
            # Initialize database manager
            self.db_manager = DatabaseManager(self.settings.database)
            
            # Initialize cache manager
            self.cache_manager = CacheManager(self.settings.redis)
            
            # Initialize storage manager
            self.storage_manager = StorageManager(self.settings.storage)
            
            # Initialize AI orchestrator
            self.ai_orchestrator = AIOrchestrator(
                settings=self.settings.ai,
                cache_manager=self.cache_manager
            )
            
            # Store services in session state
            if "services" not in st.session_state:
                st.session_state.services = {
                    "db_manager": self.db_manager,
                    "cache_manager": self.cache_manager,
                    "storage_manager": self.storage_manager,
                    "ai_orchestrator": self.ai_orchestrator,
                }
            
            self.logger.info("All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            raise ArchaeoVaultError(f"Service initialization failed: {e}")
    
    def run(self) -> None:
        """Run the Streamlit application."""
        try:
            # Set up navigation
            self._setup_navigation()
            
            # Run the main application
            self._run_main_app()
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            st.error(f"Application error: {e}")
            st.stop()
    
    def _setup_navigation(self) -> None:
        """Setup application navigation."""
        # Sidebar navigation
        with st.sidebar:
            st.title("🏺 ArchaeoVault")
            st.caption(f"Version {self.settings.app_version}")
            
            # Navigation menu
            st.markdown("## Navigation")
            
            # Main pages
            pages = {
                "🏠 Home": "home",
                "🏺 Artifact Analyzer": "artifact_analyzer",
                "⏳ Carbon Dating": "carbon_dating",
                "🌍 Civilizations": "civilizations",
                "⛏️ Excavation Planner": "excavation_planner",
                "📄 Report Generator": "report_generator",
                "🔍 Research Assistant": "research_assistant",
            }
            
            selected_page = st.selectbox(
                "Select a page",
                list(pages.keys()),
                key="page_selector"
            )
            
            # Store selected page in session state
            st.session_state.selected_page = pages[selected_page]
            
            # Feature status indicators
            st.markdown("## Feature Status")
            self._display_feature_status()
            
            # System status
            st.markdown("## System Status")
            self._display_system_status()
    
    def _display_feature_status(self) -> None:
        """Display feature status indicators."""
        features = [
            ("AI Analysis", self.settings.features.enable_ai_analysis),
            ("3D Viewer", self.settings.features.enable_3d_viewer),
            ("API Access", self.settings.features.enable_api_access),
            ("Real-time Collaboration", self.settings.features.enable_real_time_collaboration),
        ]
        
        for feature_name, is_enabled in features:
            status = "✅" if is_enabled else "❌"
            st.text(f"{status} {feature_name}")
    
    def _display_system_status(self) -> None:
        """Display system status indicators."""
        try:
            # Check database connection
            db_status = "✅" if self.db_manager.is_connected() else "❌"
            st.text(f"{db_status} Database")
            
            # Check Redis connection
            cache_status = "✅" if self.cache_manager.is_connected() else "❌"
            st.text(f"{cache_status} Cache")
            
            # Check AI services
            ai_status = "✅" if self.ai_orchestrator.is_available() else "❌"
            st.text(f"{ai_status} AI Services")
            
        except Exception as e:
            st.text(f"❌ System Status Error: {e}")
    
    def _run_main_app(self) -> None:
        """Run the main application logic."""
        # Get selected page
        selected_page = st.session_state.get("selected_page", "home")
        
        # Route to appropriate page
        try:
            if selected_page == "home":
                from .pages.home import show_home_page
                show_home_page()
            elif selected_page == "artifact_analyzer":
                from .pages.artifact_analyzer import show_artifact_analyzer_page
                show_artifact_analyzer_page()
            elif selected_page == "carbon_dating":
                from .pages.carbon_dating import show_carbon_dating_page
                show_carbon_dating_page()
            elif selected_page == "civilizations":
                from .pages.civilizations import show_civilizations_page
                show_civilizations_page()
            elif selected_page == "excavation_planner":
                from .pages.excavation_planner import show_excavation_planner_page
                show_excavation_planner_page()
            elif selected_page == "report_generator":
                from .pages.report_generator import show_report_generator_page
                show_report_generator_page()
            elif selected_page == "research_assistant":
                from .pages.research_assistant import show_research_assistant_page
                show_research_assistant_page()
            else:
                st.error(f"Unknown page: {selected_page}")
        except ImportError:
            if selected_page == "home":
                from pages.home import show_home_page
                show_home_page()
            elif selected_page == "artifact_analyzer":
                from pages.artifact_analyzer import show_artifact_analyzer_page
                show_artifact_analyzer_page()
            elif selected_page == "carbon_dating":
                from pages.carbon_dating import show_carbon_dating_page
                show_carbon_dating_page()
            elif selected_page == "civilizations":
                from pages.civilizations import show_civilizations_page
                show_civilizations_page()
            elif selected_page == "excavation_planner":
                from pages.excavation_planner import show_excavation_planner_page
                show_excavation_planner_page()
            elif selected_page == "report_generator":
                from pages.report_generator import show_report_generator_page
                show_report_generator_page()
            elif selected_page == "research_assistant":
                from pages.research_assistant import show_research_assistant_page
                show_research_assistant_page()
            else:
                st.error(f"Unknown page: {selected_page}")


def create_app() -> ArchaeoVaultApp:
    """
    Create and return the ArchaeoVault application instance.
    
    This function follows the application factory pattern and is used
    to create the application instance with proper configuration.
    
    Returns:
        ArchaeoVaultApp: Configured application instance
    """
    return ArchaeoVaultApp()


def main() -> None:
    """
    Main entry point for the application.
    
    This function is called when the application is run directly
    and handles the complete application lifecycle.
    """
    try:
        # Create application instance
        app = create_app()
        
        # Run the application
        app.run()
        
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
