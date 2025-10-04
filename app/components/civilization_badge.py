"""
Civilization Badge component for ArchaeoVault.

This module provides a reusable component for displaying civilization information
in a badge format with key details and visual indicators.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import plotly.express as px
import plotly.graph_objects as go


class CivilizationBadge:
    """A reusable component for displaying civilization information."""
    
    def __init__(self, civilization: Dict[str, Any]):
        """Initialize the civilization badge with civilization data.
        
        Args:
            civilization: Dictionary containing civilization information
        """
        self.civilization = civilization
    
    def render(self, show_details: bool = True) -> None:
        """Render the civilization badge.
        
        Args:
            show_details: Whether to show detailed information
        """
        with st.container():
            # Badge header
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"🏛️ {self.civilization.get('name', 'Unknown Civilization')}")
            
            with col2:
                # Status indicator
                self._render_status_indicator()
            
            # Basic information
            self._render_basic_info()
            
            # Detailed information
            if show_details:
                self._render_detailed_info()
            
            # Action buttons
            self._render_actions()
    
    def _render_status_indicator(self) -> None:
        """Render the status indicator."""
        status = self.civilization.get('status', 'Unknown')
        status_colors = {
            'Active': '🟢',
            'Inactive': '🔴',
            'Researching': '🟡',
            'Unknown': '⚪'
        }
        
        status_color = status_colors.get(status, '⚪')
        st.write(f"{status_color} {status}")
    
    def _render_basic_info(self) -> None:
        """Render basic civilization information."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Period:** {self.civilization.get('period', 'Unknown')}")
            st.write(f"**Region:** {self.civilization.get('region', 'Unknown')}")
        
        with col2:
            st.write(f"**Time Span:** {self.civilization.get('start_date', 'Unknown')} - {self.civilization.get('end_date', 'Unknown')}")
            st.write(f"**Capital:** {self.civilization.get('capital', 'Unknown')}")
        
        with col3:
            st.write(f"**Language:** {self.civilization.get('language', 'Unknown')}")
            st.write(f"**Status:** {self.civilization.get('status', 'Unknown')}")
    
    def _render_detailed_info(self) -> None:
        """Render detailed civilization information."""
        # Description
        if self.civilization.get('description'):
            st.write("**Description:**")
            st.write(self.civilization['description'])
        
        # Key achievements
        if self.civilization.get('achievements'):
            st.write("**Key Achievements:**")
            for achievement in self.civilization['achievements']:
                st.write(f"• {achievement}")
        
        # Cultural characteristics
        if self.civilization.get('cultural_characteristics'):
            st.write("**Cultural Characteristics:**")
            for characteristic in self.civilization['cultural_characteristics']:
                st.write(f"• {characteristic}")
        
        # AI research results
        if self.civilization.get('ai_research'):
            self._render_ai_research()
    
    def _render_ai_research(self) -> None:
        """Render AI research results."""
        research = self.civilization['ai_research']
        
        st.subheader("🤖 AI Research")
        
        # Deep Research
        if 'deep_research' in research:
            research_data = research['deep_research']
            st.write("**Deep Research:**")
            st.write(f"• Research Focus: {research_data.get('research_focus', 'Unknown')}")
            st.write(f"• Key Findings: {research_data.get('key_findings', 'Unknown')}")
            st.write(f"• Confidence Level: {research_data.get('confidence_level', 'Unknown')}")
        
        # Geographic Analysis
        if 'geographic_analysis' in research:
            geo_data = research['geographic_analysis']
            st.write("**Geographic Analysis:**")
            st.write(f"• Territory Size: {geo_data.get('territory_size', 'Unknown')}")
            st.write(f"• Climate: {geo_data.get('climate', 'Unknown')}")
            st.write(f"• Natural Resources: {', '.join(geo_data.get('natural_resources', []))}")
        
        # Timeline Analysis
        if 'timeline_analysis' in research:
            timeline_data = research['timeline_analysis']
            st.write("**Timeline Analysis:**")
            st.write(f"• Founding Date: {timeline_data.get('founding_date', 'Unknown')}")
            st.write(f"• Peak Period: {timeline_data.get('peak_period', 'Unknown')}")
            st.write(f"• Decline Date: {timeline_data.get('decline_date', 'Unknown')}")
    
    def _render_actions(self) -> None:
        """Render action buttons."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Research", key=f"research_{self.civilization.get('id', 'unknown')}"):
                st.session_state.selected_civilization = self.civilization.get('id')
                st.session_state.selected_page = "civilizations"
                st.rerun()
        
        with col2:
            if st.button("🗺️ Map", key=f"map_{self.civilization.get('id', 'unknown')}"):
                st.session_state.selected_civilization = self.civilization.get('id')
                st.session_state.selected_page = "civilizations"
                st.rerun()
        
        with col3:
            if st.button("⏰ Timeline", key=f"timeline_{self.civilization.get('id', 'unknown')}"):
                st.session_state.selected_civilization = self.civilization.get('id')
                st.session_state.selected_page = "civilizations"
                st.rerun()


def render_civilization_badge(civilization: Dict[str, Any], show_details: bool = True) -> None:
    """Render a civilization badge component.
    
    Args:
        civilization: Dictionary containing civilization information
        show_details: Whether to show detailed information
    """
    badge = CivilizationBadge(civilization)
    badge.render(show_details)


def render_civilization_grid(civilizations: List[Dict[str, Any]], columns: int = 3) -> None:
    """Render a grid of civilization badges.
    
    Args:
        civilizations: List of civilization dictionaries
        columns: Number of columns in the grid
    """
    for i in range(0, len(civilizations), columns):
        cols = st.columns(columns)
        
        for j, col in enumerate(cols):
            if i + j < len(civilizations):
                with col:
                    render_civilization_badge(civilizations[i + j], show_details=True)
                    st.divider()


def render_civilization_list(civilizations: List[Dict[str, Any]]) -> None:
    """Render a list of civilization badges.
    
    Args:
        civilizations: List of civilization dictionaries
    """
    for civilization in civilizations:
        render_civilization_badge(civilization, show_details=True)
        st.divider()


def render_civilization_timeline(civilizations: List[Dict[str, Any]]) -> None:
    """Render a timeline of civilizations.
    
    Args:
        civilizations: List of civilization dictionaries
    """
    st.subheader("⏰ Civilization Timeline")
    
    # Prepare timeline data
    timeline_data = []
    for civ in civilizations:
        timeline_data.append({
            "Civilization": civ["name"],
            "Start": civ["start_date"],
            "End": civ["end_date"],
            "Period": civ["period"],
            "Region": civ["region"]
        })
    
    # Create timeline visualization
    import pandas as pd
    df = pd.DataFrame(timeline_data)
    
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Civilization",
        color="Period",
        title="Civilization Timeline"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_civilization_map(civilizations: List[Dict[str, Any]]) -> None:
    """Render a map of civilizations.
    
    Args:
        civilizations: List of civilization dictionaries
    """
    st.subheader("🗺️ Civilization Map")
    
    # Mock geographic data
    geo_data = []
    for civ in civilizations:
        # Mock coordinates based on region
        region_coords = {
            "Mediterranean": (35.0, 20.0),
            "Near East": (35.0, 40.0),
            "Asia": (35.0, 100.0),
            "Americas": (20.0, -100.0),
            "Africa": (0.0, 20.0),
            "Europe": (50.0, 10.0)
        }
        
        coords = region_coords.get(civ["region"], (0.0, 0.0))
        geo_data.append({
            "Civilization": civ["name"],
            "Latitude": coords[0],
            "Longitude": coords[1],
            "Period": civ["period"],
            "Region": civ["region"]
        })
    
    # Create map visualization
    import pandas as pd
    df = pd.DataFrame(geo_data)
    
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Civilization",
        color="Period",
        mapbox_style="open-street-map",
        title="Civilization Locations"
    )
    
    st.plotly_chart(fig, use_container_width=True)


