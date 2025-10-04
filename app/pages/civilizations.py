"""
Civilizations page for ArchaeoVault.

This module provides the interface for researching civilizations using AI agents.
"""

import streamlit as st
import asyncio
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ..components.artifact_card import ArtifactCard
from ..components.civilization_badge import CivilizationBadge
from ..components.timeline_widget import TimelineWidget
from ..services.ai_agents.civilization_agent import CivilizationResearchAgent
from ..services.ai_orchestrator import AIOrchestrator
from ..models.civilization import Civilization
from ..utils.exceptions import CivilizationResearchError


def show_civilizations_page() -> None:
    """Display the civilizations page."""
    st.title("🌍 Civilization Research")
    st.markdown("**AI-Powered Cultural and Historical Analysis**")
    
    # Initialize session state
    if "civilization_research_results" not in st.session_state:
        st.session_state.civilization_research_results = {}
    
    if "selected_civilization" not in st.session_state:
        st.session_state.selected_civilization = None
    
    # Sidebar for civilization selection
    with st.sidebar:
        st.header("🏛️ Civilization Library")
        
        # Search and filter
        search_term = st.text_input("🔍 Search civilizations", placeholder="Enter civilization name")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            period_filter = st.selectbox("Period", ["All", "Paleolithic", "Neolithic", "Bronze Age", "Iron Age", "Classical", "Medieval"])
        with col2:
            region_filter = st.selectbox("Region", ["All", "Mediterranean", "Near East", "Asia", "Americas", "Africa", "Europe"])
        
        # Mock civilization list
        civilizations = get_mock_civilizations()
        
        # Filter civilizations
        filtered_civilizations = filter_civilizations(civilizations, search_term, period_filter, region_filter)
        
        # Display civilization list
        for civilization in filtered_civilizations:
            if st.button(f"🏛️ {civilization['name']}", key=f"select_{civilization['id']}", use_container_width=True):
                st.session_state.selected_civilization = civilization['id']
                st.rerun()
    
    # Main content area
    if st.session_state.selected_civilization:
        show_civilization_details(st.session_state.selected_civilization)
    else:
        show_civilization_overview()


def show_civilization_overview() -> None:
    """Display civilization overview and statistics."""
    st.header("📊 Civilization Overview")
    
    # Get mock civilizations
    civilizations = get_mock_civilizations()
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Civilizations", len(civilizations))
    
    with col2:
        bronze_age_count = len([c for c in civilizations if c["period"] == "Bronze Age"])
        st.metric("Bronze Age", bronze_age_count)
    
    with col3:
        classical_count = len([c for c in civilizations if c["period"] == "Classical"])
        st.metric("Classical", classical_count)
    
    with col4:
        mediterranean_count = len([c for c in civilizations if c["region"] == "Mediterranean"])
        st.metric("Mediterranean", mediterranean_count)
    
    # Period distribution
    st.subheader("📈 Period Distribution")
    period_counts = {}
    for civ in civilizations:
        period = civ["period"]
        period_counts[period] = period_counts.get(period, 0) + 1
    
    fig = px.pie(
        values=list(period_counts.values()),
        names=list(period_counts.keys()),
        title="Civilizations by Period"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional distribution
    st.subheader("🗺️ Regional Distribution")
    region_counts = {}
    for civ in civilizations:
        region = civ["region"]
        region_counts[region] = region_counts.get(region, 0) + 1
    
    fig = px.bar(
        x=list(region_counts.keys()),
        y=list(region_counts.values()),
        title="Civilizations by Region"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Timeline visualization
    st.subheader("⏰ Civilization Timeline")
    timeline_data = []
    for civ in civilizations:
        timeline_data.append({
            "Civilization": civ["name"],
            "Start": civ["start_date"],
            "End": civ["end_date"],
            "Period": civ["period"],
            "Region": civ["region"]
        })
    
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


def show_civilization_details(civilization_id: str) -> None:
    """Display detailed civilization information and research."""
    # Get civilization data
    civilization = get_civilization_by_id(civilization_id)
    if not civilization:
        st.error("Civilization not found.")
        return
    
    # Display civilization information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🏛️ Basic Info")
        
        # Display basic info
        info_data = {
            "Name": civilization["name"],
            "Period": civilization["period"],
            "Region": civilization["region"],
            "Time Span": f"{civilization['start_date']} - {civilization['end_date']}",
            "Capital": civilization.get("capital", "Unknown"),
            "Language": civilization.get("language", "Unknown")
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
        
        # Status
        status = civilization.get("status", "Active")
        status_color = {
            "Active": "🟢",
            "Inactive": "🔴",
            "Researching": "🟡"
        }.get(status, "⚪")
        
        st.write(f"**Status:** {status_color} {status}")
    
    with col2:
        st.subheader("📋 Description")
        
        # Description
        if civilization.get("description"):
            st.write(civilization["description"])
        
        # Key achievements
        if civilization.get("achievements"):
            st.subheader("🏆 Key Achievements")
            for achievement in civilization["achievements"]:
                st.write(f"• {achievement}")
        
        # Cultural characteristics
        if civilization.get("cultural_characteristics"):
            st.subheader("🎭 Cultural Characteristics")
            for characteristic in civilization["cultural_characteristics"]:
                st.write(f"• {characteristic}")
    
    # AI Research section
    st.header("🤖 AI Research")
    
    # Research controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Deep Research", use_container_width=True):
            run_deep_research(civilization_id)
    
    with col2:
        if st.button("🗺️ Geographic Analysis", use_container_width=True):
            run_geographic_analysis(civilization_id)
    
    with col3:
        if st.button("⏰ Timeline Analysis", use_container_width=True):
            run_timeline_analysis(civilization_id)
    
    # Display research results
    if civilization_id in st.session_state.civilization_research_results:
        display_research_results(civilization_id)
    
    # Geographic visualization
    if civilization_id in st.session_state.civilization_research_results:
        show_geographic_visualization(civilization_id)


def run_deep_research(civilization_id: str) -> None:
    """Run deep research on the civilization."""
    try:
        with st.spinner("Running deep research..."):
            # Get AI orchestrator from session state
            if "services" in st.session_state:
                ai_orchestrator = st.session_state.services.get("ai_orchestrator")
                if ai_orchestrator:
                    # Run research
                    result = asyncio.run(ai_orchestrator.research_civilization(civilization_id))
                    
                    # Store results
                    st.session_state.civilization_research_results[civilization_id] = result
                    
                    st.success("Deep research completed successfully!")
                else:
                    st.error("AI orchestrator not available.")
            else:
                st.error("Services not initialized.")
                
    except Exception as e:
        st.error(f"Error running deep research: {str(e)}")


def run_geographic_analysis(civilization_id: str) -> None:
    """Run geographic analysis on the civilization."""
    try:
        with st.spinner("Running geographic analysis..."):
            # Mock geographic analysis
            result = {
                "geographic_analysis": {
                    "territory_size": "500,000 km²",
                    "major_cities": ["Athens", "Sparta", "Corinth", "Thebes"],
                    "geographic_features": ["Mountains", "Coastline", "Islands"],
                    "climate": "Mediterranean",
                    "natural_resources": ["Marble", "Silver", "Olive Oil", "Wine"],
                    "trade_routes": ["Mediterranean Sea", "Black Sea", "Aegean Sea"],
                    "geographic_notes": "Mountainous terrain with extensive coastline"
                }
            }
            
            # Store results
            if civilization_id not in st.session_state.civilization_research_results:
                st.session_state.civilization_research_results[civilization_id] = {}
            st.session_state.civilization_research_results[civilization_id].update(result)
            
            st.success("Geographic analysis completed!")
            
    except Exception as e:
        st.error(f"Error running geographic analysis: {str(e)}")


def run_timeline_analysis(civilization_id: str) -> None:
    """Run timeline analysis on the civilization."""
    try:
        with st.spinner("Running timeline analysis..."):
            # Mock timeline analysis
            result = {
                "timeline_analysis": {
                    "founding_date": "800 BCE",
                    "peak_period": "500-400 BCE",
                    "decline_date": "146 BCE",
                    "major_events": [
                        "776 BCE - First Olympic Games",
                        "508 BCE - Democracy established in Athens",
                        "490 BCE - Battle of Marathon",
                        "480 BCE - Battle of Thermopylae",
                        "431 BCE - Peloponnesian War begins",
                        "146 BCE - Roman conquest"
                    ],
                    "cultural_periods": ["Archaic", "Classical", "Hellenistic"],
                    "timeline_notes": "Rapid cultural and political development"
                }
            }
            
            # Store results
            if civilization_id not in st.session_state.civilization_research_results:
                st.session_state.civilization_research_results[civilization_id] = {}
            st.session_state.civilization_research_results[civilization_id].update(result)
            
            st.success("Timeline analysis completed!")
            
    except Exception as e:
        st.error(f"Error running timeline analysis: {str(e)}")


def display_research_results(civilization_id: str) -> None:
    """Display AI research results."""
    results = st.session_state.civilization_research_results[civilization_id]
    
    # Deep Research
    if "deep_research" in results:
        st.subheader("🔍 Deep Research")
        research_data = results["deep_research"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Research Focus:** {research_data['research_focus']}")
            st.write(f"**Key Findings:** {research_data['key_findings']}")
            st.write(f"**Research Method:** {research_data['research_method']}")
        
        with col2:
            st.write(f"**Data Sources:** {research_data['data_sources']}")
            st.write(f"**Confidence Level:** {research_data['confidence_level']}")
            st.write(f"**Research Notes:** {research_data['research_notes']}")
    
    # Geographic Analysis
    if "geographic_analysis" in results:
        st.subheader("🗺️ Geographic Analysis")
        geo_data = results["geographic_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Territory Size:** {geo_data['territory_size']}")
            st.write(f"**Climate:** {geo_data['climate']}")
            st.write(f"**Geographic Features:** {', '.join(geo_data['geographic_features'])}")
        
        with col2:
            st.write(f"**Natural Resources:** {', '.join(geo_data['natural_resources'])}")
            st.write(f"**Trade Routes:** {', '.join(geo_data['trade_routes'])}")
            st.write(f"**Geographic Notes:** {geo_data['geographic_notes']}")
    
    # Timeline Analysis
    if "timeline_analysis" in results:
        st.subheader("⏰ Timeline Analysis")
        timeline_data = results["timeline_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Founding Date:** {timeline_data['founding_date']}")
            st.write(f"**Peak Period:** {timeline_data['peak_period']}")
            st.write(f"**Decline Date:** {timeline_data['decline_date']}")
        
        with col2:
            st.write(f"**Cultural Periods:** {', '.join(timeline_data['cultural_periods'])}")
            st.write(f"**Timeline Notes:** {timeline_data['timeline_notes']}")
        
        # Major events
        st.write("**Major Events:**")
        for event in timeline_data["major_events"]:
            st.write(f"• {event}")


def show_geographic_visualization(civilization_id: str) -> None:
    """Display geographic visualization."""
    if civilization_id not in st.session_state.civilization_research_results:
        return
    
    results = st.session_state.civilization_research_results[civilization_id]
    
    if "geographic_analysis" not in results:
        return
    
    st.subheader("🗺️ Geographic Visualization")
    
    # Mock geographic data
    cities = [
        {"name": "Athens", "lat": 37.9755, "lon": 23.7348, "size": 100},
        {"name": "Sparta", "lat": 37.0833, "lon": 22.4333, "size": 80},
        {"name": "Corinth", "lat": 37.9333, "lon": 22.9333, "size": 60},
        {"name": "Thebes", "lat": 38.3167, "lon": 23.3167, "size": 70}
    ]
    
    df = pd.DataFrame(cities)
    
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        size="size",
        hover_name="name",
        mapbox_style="open-street-map",
        title="Civilization Cities"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def get_mock_civilizations() -> List[Dict[str, Any]]:
    """Get mock civilization data for testing."""
    return [
        {
            "id": "civ_001",
            "name": "Ancient Greece",
            "period": "Classical",
            "region": "Mediterranean",
            "start_date": "800 BCE",
            "end_date": "146 BCE",
            "capital": "Athens",
            "language": "Greek",
            "status": "Active",
            "description": "A civilization known for its contributions to philosophy, democracy, art, and science.",
            "achievements": [
                "Democracy",
                "Philosophy",
                "Olympic Games",
                "Theater",
                "Mathematics",
                "Medicine"
            ],
            "cultural_characteristics": [
                "City-states",
                "Democratic government",
                "Philosophical tradition",
                "Artistic excellence",
                "Military prowess"
            ]
        },
        {
            "id": "civ_002",
            "name": "Ancient Rome",
            "period": "Classical",
            "region": "Mediterranean",
            "start_date": "753 BCE",
            "end_date": "476 CE",
            "capital": "Rome",
            "language": "Latin",
            "status": "Active",
            "description": "A powerful empire that dominated the Mediterranean world for centuries.",
            "achievements": [
                "Roman Law",
                "Engineering",
                "Architecture",
                "Roads",
                "Aqueducts",
                "Military organization"
            ],
            "cultural_characteristics": [
                "Imperial system",
                "Legal tradition",
                "Engineering excellence",
                "Military discipline",
                "Cultural assimilation"
            ]
        },
        {
            "id": "civ_003",
            "name": "Ancient Egypt",
            "period": "Bronze Age",
            "region": "Africa",
            "start_date": "3100 BCE",
            "end_date": "30 BCE",
            "capital": "Memphis",
            "language": "Egyptian",
            "status": "Active",
            "description": "A civilization known for its pyramids, pharaohs, and advanced culture.",
            "achievements": [
                "Pyramids",
                "Hieroglyphics",
                "Mummification",
                "Mathematics",
                "Medicine",
                "Architecture"
            ],
            "cultural_characteristics": [
                "Pharaonic system",
                "Religious tradition",
                "Artistic excellence",
                "Agricultural society",
                "Funerary practices"
            ]
        }
    ]


def filter_civilizations(civilizations: List[Dict[str, Any]], search_term: str, period_filter: str, region_filter: str) -> List[Dict[str, Any]]:
    """Filter civilizations based on search criteria."""
    filtered = civilizations
    
    if search_term:
        filtered = [c for c in filtered if search_term.lower() in c["name"].lower()]
    
    if period_filter != "All":
        filtered = [c for c in filtered if c["period"] == period_filter]
    
    if region_filter != "All":
        filtered = [c for c in filtered if c["region"] == region_filter]
    
    return filtered


def get_civilization_by_id(civilization_id: str) -> Optional[Dict[str, Any]]:
    """Get civilization by ID."""
    # Check session state first
    if "civilizations" in st.session_state and civilization_id in st.session_state.civilizations:
        return st.session_state.civilizations[civilization_id]
    
    # Check mock data
    mock_civilizations = get_mock_civilizations()
    for civilization in mock_civilizations:
        if civilization["id"] == civilization_id:
            return civilization
    
    return None


