"""
Artifact Card component for ArchaeoVault.

This module provides a reusable component for displaying artifact information
in a card format with image, basic details, and action buttons.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from PIL import Image
import io


class ArtifactCard:
    """A reusable component for displaying artifact information."""
    
    def __init__(self, artifact: Dict[str, Any]):
        """Initialize the artifact card with artifact data.
        
        Args:
            artifact: Dictionary containing artifact information
        """
        self.artifact = artifact
    
    def render(self, show_actions: bool = True) -> None:
        """Render the artifact card.
        
        Args:
            show_actions: Whether to show action buttons
        """
        with st.container():
            # Card header
            st.subheader(f"🏺 {self.artifact.get('name', 'Unknown Artifact')}")
            
            # Main content
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Artifact image
                self._render_image()
            
            with col2:
                # Basic information
                self._render_basic_info()
                
                # AI analysis results
                if self.artifact.get('ai_analysis'):
                    self._render_ai_analysis()
            
            # Action buttons
            if show_actions:
                self._render_actions()
    
    def _render_image(self) -> None:
        """Render the artifact image."""
        if self.artifact.get('image_url'):
            st.image(
                self.artifact['image_url'],
                caption=f"Image of {self.artifact.get('name', 'artifact')}",
                use_column_width=True
            )
        else:
            st.image(
                "https://via.placeholder.com/200x200?text=No+Image",
                caption="No image available",
                use_column_width=True
            )
    
    def _render_basic_info(self) -> None:
        """Render basic artifact information."""
        info_data = {
            "Period": self.artifact.get('period', 'Unknown'),
            "Culture": self.artifact.get('culture', 'Unknown'),
            "Material": self.artifact.get('material', 'Unknown'),
            "Discovery Date": self.artifact.get('discovery_date', 'Unknown'),
            "Discovery Location": self.artifact.get('discovery_location', 'Unknown'),
            "Current Location": self.artifact.get('current_location', 'Unknown'),
            "Dimensions": self.artifact.get('dimensions', 'Unknown')
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
        
        # Description
        if self.artifact.get('description'):
            st.write("**Description:**")
            st.write(self.artifact['description'])
        
        # Notes
        if self.artifact.get('notes'):
            st.write("**Notes:**")
            st.write(self.artifact['notes'])
    
    def _render_ai_analysis(self) -> None:
        """Render AI analysis results."""
        analysis = self.artifact['ai_analysis']
        
        st.subheader("🤖 AI Analysis")
        
        # Material Analysis
        if 'material_analysis' in analysis:
            material_data = analysis['material_analysis']
            st.write("**Material Analysis:**")
            st.write(f"• Primary Material: {material_data.get('primary_material', 'Unknown')}")
            st.write(f"• Manufacturing Technique: {material_data.get('manufacturing_technique', 'Unknown')}")
            st.write(f"• Preservation State: {material_data.get('preservation_state', 'Unknown')}")
        
        # Cultural Analysis
        if 'cultural_analysis' in analysis:
            cultural_data = analysis['cultural_analysis']
            st.write("**Cultural Analysis:**")
            st.write(f"• Cultural Period: {cultural_data.get('cultural_period', 'Unknown')}")
            st.write(f"• Cultural Group: {cultural_data.get('cultural_group', 'Unknown')}")
            st.write(f"• Functional Purpose: {cultural_data.get('functional_purpose', 'Unknown')}")
        
        # Dating Analysis
        if 'dating_analysis' in analysis:
            dating_data = analysis['dating_analysis']
            st.write("**Dating Analysis:**")
            st.write(f"• Estimated Age: {dating_data.get('estimated_age', 'Unknown')}")
            st.write(f"• Dating Method: {dating_data.get('dating_method', 'Unknown')}")
            st.write(f"• Confidence Level: {dating_data.get('confidence_level', 'Unknown')}")
    
    def _render_actions(self) -> None:
        """Render action buttons."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Analyze", key=f"analyze_{self.artifact.get('id', 'unknown')}"):
                st.session_state.selected_artifact = self.artifact.get('id')
                st.session_state.selected_page = "artifact_analyzer"
                st.rerun()
        
        with col2:
            if st.button("📊 Details", key=f"details_{self.artifact.get('id', 'unknown')}"):
                st.session_state.selected_artifact = self.artifact.get('id')
                st.session_state.selected_page = "artifact_analyzer"
                st.rerun()
        
        with col3:
            if st.button("📄 Report", key=f"report_{self.artifact.get('id', 'unknown')}"):
                st.session_state.selected_artifact = self.artifact.get('id')
                st.session_state.selected_page = "report_generator"
                st.rerun()


def render_artifact_card(artifact: Dict[str, Any], show_actions: bool = True) -> None:
    """Render an artifact card component.
    
    Args:
        artifact: Dictionary containing artifact information
        show_actions: Whether to show action buttons
    """
    card = ArtifactCard(artifact)
    card.render(show_actions)


def render_artifact_grid(artifacts: List[Dict[str, Any]], columns: int = 3) -> None:
    """Render a grid of artifact cards.
    
    Args:
        artifacts: List of artifact dictionaries
        columns: Number of columns in the grid
    """
    for i in range(0, len(artifacts), columns):
        cols = st.columns(columns)
        
        for j, col in enumerate(cols):
            if i + j < len(artifacts):
                with col:
                    render_artifact_card(artifacts[i + j], show_actions=True)


def render_artifact_list(artifacts: List[Dict[str, Any]]) -> None:
    """Render a list of artifact cards.
    
    Args:
        artifacts: List of artifact dictionaries
    """
    for artifact in artifacts:
        render_artifact_card(artifact, show_actions=True)
        st.divider()


