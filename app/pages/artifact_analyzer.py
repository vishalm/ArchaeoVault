"""
Artifact Analyzer page for ArchaeoVault.

This module provides the interface for analyzing artifacts using AI agents.
"""

import streamlit as st
import asyncio
from typing import Dict, Any, Optional, List
from PIL import Image
import io

from ..components.artifact_card import ArtifactCard
from ..components.civilization_badge import CivilizationBadge
from ..components.timeline_widget import TimelineWidget
from ..services.ai_agents.artifact_agent import ArtifactAnalysisAgent
from ..services.ai_orchestrator import AIOrchestrator
from ..models.artifact import Artifact
from ..utils.exceptions import ArtifactAnalysisError


def show_artifact_analyzer_page() -> None:
    """Display the artifact analyzer page."""
    st.title("🏺 Artifact Analyzer")
    st.markdown("**AI-Powered Artifact Analysis and Research**")
    
    # Initialize session state
    if "artifact_analysis_results" not in st.session_state:
        st.session_state.artifact_analysis_results = {}
    
    if "selected_artifact" not in st.session_state:
        st.session_state.selected_artifact = None
    
    # Sidebar for artifact selection
    with st.sidebar:
        st.header("📁 Artifact Library")
        
        # Search and filter
        search_term = st.text_input("🔍 Search artifacts", placeholder="Enter artifact name or ID")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            period_filter = st.selectbox("Period", ["All", "Paleolithic", "Neolithic", "Bronze Age", "Iron Age", "Classical", "Medieval"])
        with col2:
            culture_filter = st.selectbox("Culture", ["All", "Greek", "Roman", "Egyptian", "Minoan", "Mycenaean"])
        
        # Mock artifact list
        artifacts = get_mock_artifacts()
        
        # Filter artifacts
        filtered_artifacts = filter_artifacts(artifacts, search_term, period_filter, culture_filter)
        
        # Display artifact list
        for artifact in filtered_artifacts:
            if st.button(f"📄 {artifact['name']}", key=f"select_{artifact['id']}", use_container_width=True):
                st.session_state.selected_artifact = artifact['id']
                st.rerun()
    
    # Main content area
    if st.session_state.selected_artifact:
        show_artifact_details(st.session_state.selected_artifact)
    else:
        show_artifact_upload_form()


def show_artifact_upload_form() -> None:
    """Display the artifact upload form."""
    st.header("📤 Upload New Artifact")
    
    with st.form("artifact_upload_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            artifact_name = st.text_input("Artifact Name", placeholder="Enter artifact name")
            period = st.selectbox("Period", ["Paleolithic", "Neolithic", "Bronze Age", "Iron Age", "Classical", "Medieval"])
            culture = st.text_input("Culture", placeholder="Enter culture name")
            material = st.text_input("Material", placeholder="Enter material type")
        
        with col2:
            discovery_date = st.date_input("Discovery Date")
            discovery_location = st.text_input("Discovery Location", placeholder="Enter discovery location")
            current_location = st.text_input("Current Location", placeholder="Enter current location")
            dimensions = st.text_input("Dimensions", placeholder="e.g., 15cm x 10cm x 5cm")
        
        # Image upload
        st.subheader("📷 Artifact Images")
        uploaded_files = st.file_uploader(
            "Upload artifact images",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Upload multiple images from different angles"
        )
        
        # Additional information
        st.subheader("📝 Additional Information")
        description = st.text_area("Description", placeholder="Enter detailed description of the artifact")
        notes = st.text_area("Notes", placeholder="Enter any additional notes or observations")
        
        # Submit button
        if st.form_submit_button("🔍 Analyze Artifact", use_container_width=True):
            if artifact_name and uploaded_files:
                # Create artifact object
                artifact_data = {
                    "name": artifact_name,
                    "period": period,
                    "culture": culture,
                    "material": material,
                    "discovery_date": discovery_date,
                    "discovery_location": discovery_location,
                    "current_location": current_location,
                    "dimensions": dimensions,
                    "description": description,
                    "notes": notes,
                    "images": uploaded_files
                }
                
                # Process artifact
                process_artifact_upload(artifact_data)
            else:
                st.error("Please provide artifact name and upload at least one image.")


def show_artifact_details(artifact_id: str) -> None:
    """Display detailed artifact information and analysis."""
    # Get artifact data
    artifact = get_artifact_by_id(artifact_id)
    if not artifact:
        st.error("Artifact not found.")
        return
    
    # Display artifact information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📷 Images")
        if artifact.get("images"):
            for i, image in enumerate(artifact["images"]):
                st.image(image, caption=f"Image {i+1}", use_column_width=True)
        else:
            st.image("https://via.placeholder.com/300x300?text=No+Image", caption="No image available")
    
    with col2:
        st.subheader("📋 Basic Information")
        
        # Display basic info
        info_data = {
            "Name": artifact["name"],
            "Period": artifact["period"],
            "Culture": artifact["culture"],
            "Material": artifact["material"],
            "Discovery Date": artifact.get("discovery_date", "Unknown"),
            "Discovery Location": artifact.get("discovery_location", "Unknown"),
            "Current Location": artifact.get("current_location", "Unknown"),
            "Dimensions": artifact.get("dimensions", "Unknown")
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
        
        # Description
        if artifact.get("description"):
            st.subheader("📝 Description")
            st.write(artifact["description"])
        
        # Notes
        if artifact.get("notes"):
            st.subheader("📌 Notes")
            st.write(artifact["notes"])
    
    # AI Analysis section
    st.header("🤖 AI Analysis")
    
    # Analysis controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Run Full Analysis", use_container_width=True):
            run_full_analysis(artifact_id)
    
    with col2:
        if st.button("📊 Material Analysis", use_container_width=True):
            run_material_analysis(artifact_id)
    
    with col3:
        if st.button("🌍 Cultural Context", use_container_width=True):
            run_cultural_analysis(artifact_id)
    
    # Display analysis results
    if artifact_id in st.session_state.artifact_analysis_results:
        display_analysis_results(artifact_id)


def process_artifact_upload(artifact_data: Dict[str, Any]) -> None:
    """Process uploaded artifact data."""
    try:
        # Create artifact ID
        artifact_id = f"art_{len(st.session_state.get('artifacts', [])) + 1:03d}"
        
        # Store artifact data
        if "artifacts" not in st.session_state:
            st.session_state.artifacts = {}
        
        st.session_state.artifacts[artifact_id] = artifact_data
        
        # Set as selected artifact
        st.session_state.selected_artifact = artifact_id
        
        st.success(f"Artifact '{artifact_data['name']}' uploaded successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error uploading artifact: {str(e)}")


def run_full_analysis(artifact_id: str) -> None:
    """Run full AI analysis on the artifact."""
    try:
        with st.spinner("Running AI analysis..."):
            # Get AI orchestrator from session state
            if "services" in st.session_state:
                ai_orchestrator = st.session_state.services.get("ai_orchestrator")
                if ai_orchestrator:
                    # Run analysis
                    result = asyncio.run(ai_orchestrator.analyze_artifact(artifact_id))
                    
                    # Store results
                    st.session_state.artifact_analysis_results[artifact_id] = result
                    
                    st.success("Analysis completed successfully!")
                else:
                    st.error("AI orchestrator not available.")
            else:
                st.error("Services not initialized.")
                
    except Exception as e:
        st.error(f"Error running analysis: {str(e)}")


def run_material_analysis(artifact_id: str) -> None:
    """Run material analysis on the artifact."""
    try:
        with st.spinner("Analyzing material..."):
            # Mock material analysis
            result = {
                "material_analysis": {
                    "primary_material": "Ceramic",
                    "secondary_materials": ["Clay", "Pigment"],
                    "manufacturing_technique": "Hand-formed",
                    "firing_temperature": "800-900°C",
                    "decorative_technique": "Painted",
                    "preservation_state": "Good",
                    "conservation_notes": "Minor surface wear, stable condition"
                }
            }
            
            # Store results
            if artifact_id not in st.session_state.artifact_analysis_results:
                st.session_state.artifact_analysis_results[artifact_id] = {}
            st.session_state.artifact_analysis_results[artifact_id].update(result)
            
            st.success("Material analysis completed!")
            
    except Exception as e:
        st.error(f"Error running material analysis: {str(e)}")


def run_cultural_analysis(artifact_id: str) -> None:
    """Run cultural context analysis on the artifact."""
    try:
        with st.spinner("Analyzing cultural context..."):
            # Mock cultural analysis
            result = {
                "cultural_analysis": {
                    "cultural_period": "Bronze Age",
                    "cultural_group": "Minoan",
                    "functional_purpose": "Religious/Ceremonial",
                    "social_significance": "High",
                    "artistic_style": "Naturalistic",
                    "cultural_influences": ["Egyptian", "Mesopotamian"],
                    "historical_context": "Peak of Minoan civilization"
                }
            }
            
            # Store results
            if artifact_id not in st.session_state.artifact_analysis_results:
                st.session_state.artifact_analysis_results[artifact_id] = {}
            st.session_state.artifact_analysis_results[artifact_id].update(result)
            
            st.success("Cultural analysis completed!")
            
    except Exception as e:
        st.error(f"Error running cultural analysis: {str(e)}")


def display_analysis_results(artifact_id: str) -> None:
    """Display AI analysis results."""
    results = st.session_state.artifact_analysis_results[artifact_id]
    
    # Material Analysis
    if "material_analysis" in results:
        st.subheader("🔬 Material Analysis")
        material_data = results["material_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Primary Material:** {material_data['primary_material']}")
            st.write(f"**Manufacturing Technique:** {material_data['manufacturing_technique']}")
            st.write(f"**Firing Temperature:** {material_data['firing_temperature']}")
        
        with col2:
            st.write(f"**Decorative Technique:** {material_data['decorative_technique']}")
            st.write(f"**Preservation State:** {material_data['preservation_state']}")
            st.write(f"**Conservation Notes:** {material_data['conservation_notes']}")
    
    # Cultural Analysis
    if "cultural_analysis" in results:
        st.subheader("🌍 Cultural Analysis")
        cultural_data = results["cultural_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Cultural Period:** {cultural_data['cultural_period']}")
            st.write(f"**Cultural Group:** {cultural_data['cultural_group']}")
            st.write(f"**Functional Purpose:** {cultural_data['functional_purpose']}")
        
        with col2:
            st.write(f"**Social Significance:** {cultural_data['social_significance']}")
            st.write(f"**Artistic Style:** {cultural_data['artistic_style']}")
            st.write(f"**Historical Context:** {cultural_data['historical_context']}")
    
    # Dating Analysis
    if "dating_analysis" in results:
        st.subheader("⏳ Dating Analysis")
        dating_data = results["dating_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Estimated Age:** {dating_data['estimated_age']}")
            st.write(f"**Dating Method:** {dating_data['dating_method']}")
            st.write(f"**Confidence Level:** {dating_data['confidence_level']}")
        
        with col2:
            st.write(f"**Date Range:** {dating_data['date_range']}")
            st.write(f"**Cultural Period:** {dating_data['cultural_period']}")
            st.write(f"**Historical Context:** {dating_data['historical_context']}")


def get_mock_artifacts() -> List[Dict[str, Any]]:
    """Get mock artifact data for testing."""
    return [
        {
            "id": "art_001",
            "name": "Minoan Snake Goddess",
            "period": "Bronze Age",
            "culture": "Minoan",
            "material": "Ceramic",
            "discovery_date": "2024-01-15",
            "discovery_location": "Knossos, Crete",
            "current_location": "Heraklion Archaeological Museum",
            "dimensions": "25cm x 15cm x 8cm",
            "description": "A ceramic figurine depicting a female figure holding snakes, typical of Minoan religious art.",
            "notes": "Excellent preservation, minor surface wear"
        },
        {
            "id": "art_002",
            "name": "Roman Legionary Helmet",
            "period": "Classical",
            "culture": "Roman",
            "material": "Bronze",
            "discovery_date": "2024-02-03",
            "discovery_location": "Pompeii, Italy",
            "current_location": "Naples National Archaeological Museum",
            "dimensions": "30cm x 25cm x 20cm",
            "description": "A bronze helmet from a Roman legionary, featuring decorative elements and battle damage.",
            "notes": "Significant battle damage, well-preserved decorative elements"
        },
        {
            "id": "art_003",
            "name": "Egyptian Scarab",
            "period": "Classical",
            "culture": "Egyptian",
            "material": "Stone",
            "discovery_date": "2024-01-28",
            "discovery_location": "Valley of the Kings, Egypt",
            "current_location": "Cairo Museum",
            "dimensions": "3cm x 2cm x 1cm",
            "description": "A carved stone scarab beetle, used as an amulet in ancient Egypt.",
            "notes": "Intact, clear hieroglyphic inscriptions"
        }
    ]


def filter_artifacts(artifacts: List[Dict[str, Any]], search_term: str, period_filter: str, culture_filter: str) -> List[Dict[str, Any]]:
    """Filter artifacts based on search criteria."""
    filtered = artifacts
    
    if search_term:
        filtered = [a for a in filtered if search_term.lower() in a["name"].lower()]
    
    if period_filter != "All":
        filtered = [a for a in filtered if a["period"] == period_filter]
    
    if culture_filter != "All":
        filtered = [a for a in filtered if a["culture"] == culture_filter]
    
    return filtered


def get_artifact_by_id(artifact_id: str) -> Optional[Dict[str, Any]]:
    """Get artifact by ID."""
    # Check session state first
    if "artifacts" in st.session_state and artifact_id in st.session_state.artifacts:
        return st.session_state.artifacts[artifact_id]
    
    # Check mock data
    mock_artifacts = get_mock_artifacts()
    for artifact in mock_artifacts:
        if artifact["id"] == artifact_id:
            return artifact
    
    return None
