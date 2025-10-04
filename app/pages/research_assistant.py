"""
Research Assistant page for ArchaeoVault.

This module provides the interface for general archaeological research using AI agents.
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
from ..services.ai_agents.research_agent import ResearchAssistantAgent
from ..services.ai_orchestrator import AIOrchestrator
from ..utils.exceptions import ResearchAssistantError


def show_research_assistant_page() -> None:
    """Display the research assistant page."""
    st.title("🔍 Research Assistant")
    st.markdown("**AI-Powered Archaeological Research and Knowledge Assistance**")
    
    # Initialize session state
    if "research_results" not in st.session_state:
        st.session_state.research_results = {}
    
    if "selected_research" not in st.session_state:
        st.session_state.selected_research = None
    
    # Sidebar for research selection
    with st.sidebar:
        st.header("🔍 Research Library")
        
        # Search and filter
        search_term = st.text_input("🔍 Search research", placeholder="Enter research topic or ID")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            type_filter = st.selectbox("Type", ["All", "Literature", "Hypothesis", "Analysis", "Synthesis"])
        with col2:
            status_filter = st.selectbox("Status", ["All", "Active", "Completed", "Archived"])
        
        # Mock research list
        research_items = get_mock_research_items()
        
        # Filter research items
        filtered_research = filter_research_items(research_items, search_term, type_filter, status_filter)
        
        # Display research list
        for research in filtered_research:
            if st.button(f"🔍 {research['title']}", key=f"select_{research['id']}", use_container_width=True):
                st.session_state.selected_research = research['id']
                st.rerun()
    
    # Main content area
    if st.session_state.selected_research:
        show_research_details(st.session_state.selected_research)
    else:
        show_research_overview()


def show_research_overview() -> None:
    """Display research overview and statistics."""
    st.header("📊 Research Overview")
    
    # Get mock research items
    research_items = get_mock_research_items()
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Research", len(research_items))
    
    with col2:
        active_count = len([r for r in research_items if r["status"] == "Active"])
        st.metric("Active", active_count)
    
    with col3:
        completed_count = len([r for r in research_items if r["status"] == "Completed"])
        st.metric("Completed", completed_count)
    
    with col4:
        literature_count = len([r for r in research_items if r["type"] == "Literature"])
        st.metric("Literature", literature_count)
    
    # Type distribution
    st.subheader("📈 Research Type Distribution")
    type_counts = {}
    for research in research_items:
        research_type = research["type"]
        type_counts[research_type] = type_counts.get(research_type, 0) + 1
    
    fig = px.pie(
        values=list(type_counts.values()),
        names=list(type_counts.keys()),
        title="Research by Type"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Status distribution
    st.subheader("📊 Status Distribution")
    status_counts = {}
    for research in research_items:
        status = research["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    fig = px.bar(
        x=list(status_counts.keys()),
        y=list(status_counts.values()),
        title="Research by Status"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Timeline visualization
    st.subheader("⏰ Research Timeline")
    timeline_data = []
    for research in research_items:
        timeline_data.append({
            "Research": research["title"],
            "Created": research["created_date"],
            "Updated": research["updated_date"],
            "Type": research["type"],
            "Status": research["status"]
        })
    
    df = pd.DataFrame(timeline_data)
    
    fig = px.timeline(
        df,
        x_start="Created",
        x_end="Updated",
        y="Research",
        color="Type",
        title="Research Timeline"
    )
    st.plotly_chart(fig, use_container_width=True)


def show_research_details(research_id: str) -> None:
    """Display detailed research information and assistance."""
    # Get research data
    research = get_research_by_id(research_id)
    if not research:
        st.error("Research not found.")
        return
    
    # Display research information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🔍 Basic Info")
        
        # Display basic info
        info_data = {
            "Title": research["title"],
            "Type": research["type"],
            "Status": research["status"],
            "Created": research["created_date"],
            "Updated": research["updated_date"],
            "Author": research.get("author", "Unknown"),
            "Institution": research.get("institution", "Unknown")
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
        
        # Progress
        if research.get("progress"):
            st.write(f"**Progress:** {research['progress']}%")
        
        # Priority
        if research.get("priority"):
            st.write(f"**Priority:** {research['priority']}")
    
    with col2:
        st.subheader("📋 Description")
        
        # Description
        if research.get("description"):
            st.write(research["description"])
        
        # Objectives
        if research.get("objectives"):
            st.subheader("🎯 Objectives")
            for objective in research["objectives"]:
                st.write(f"• {objective}")
        
        # Methodology
        if research.get("methodology"):
            st.subheader("🔬 Methodology")
            for method in research["methodology"]:
                st.write(f"• {method}")
    
    # AI Assistance section
    st.header("🤖 AI Research Assistance")
    
    # Assistance controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Literature Search", use_container_width=True):
            run_literature_search(research_id)
    
    with col2:
        if st.button("💡 Hypothesis Generation", use_container_width=True):
            run_hypothesis_generation(research_id)
    
    with col3:
        if st.button("📊 Statistical Analysis", use_container_width=True):
            run_statistical_analysis(research_id)
    
    # Display assistance results
    if research_id in st.session_state.research_results:
        display_assistance_results(research_id)
    
    # Research visualization
    if research_id in st.session_state.research_results:
        show_research_visualization(research_id)


def run_literature_search(research_id: str) -> None:
    """Run literature search for the research."""
    try:
        with st.spinner("Searching literature..."):
            # Get AI orchestrator from session state
            if "services" in st.session_state:
                ai_orchestrator = st.session_state.services.get("ai_orchestrator")
                if ai_orchestrator:
                    # Run search
                    result = asyncio.run(ai_orchestrator.search_literature(research_id))
                    
                    # Store results
                    st.session_state.research_results[research_id] = result
                    
                    st.success("Literature search completed successfully!")
                else:
                    st.error("AI orchestrator not available.")
            else:
                st.error("Services not initialized.")
                
    except Exception as e:
        st.error(f"Error running literature search: {str(e)}")


def run_hypothesis_generation(research_id: str) -> None:
    """Run hypothesis generation for the research."""
    try:
        with st.spinner("Generating hypotheses..."):
            # Mock hypothesis generation
            result = {
                "hypothesis_generation": {
                    "hypotheses_generated": 5,
                    "hypotheses": [
                        "The settlement was abandoned due to environmental changes",
                        "Trade connections influenced cultural development",
                        "Social stratification increased over time",
                        "Technological innovations spread through migration",
                        "Religious practices evolved with political changes"
                    ],
                    "confidence_levels": [0.8, 0.7, 0.9, 0.6, 0.8],
                    "hypothesis_notes": "Hypotheses generated based on available data and literature"
                }
            }
            
            # Store results
            if research_id not in st.session_state.research_results:
                st.session_state.research_results[research_id] = {}
            st.session_state.research_results[research_id].update(result)
            
            st.success("Hypotheses generated successfully!")
            
    except Exception as e:
        st.error(f"Error running hypothesis generation: {str(e)}")


def run_statistical_analysis(research_id: str) -> None:
    """Run statistical analysis for the research."""
    try:
        with st.spinner("Running statistical analysis..."):
            # Mock statistical analysis
            result = {
                "statistical_analysis": {
                    "analyses_performed": 3,
                    "analysis_types": ["Descriptive", "Correlation", "Regression"],
                    "key_findings": [
                        "Strong positive correlation between artifact density and settlement size",
                        "Significant difference in pottery types across time periods",
                        "Linear relationship between burial depth and age"
                    ],
                    "statistical_notes": "Statistical analysis completed using standard archaeological methods"
                }
            }
            
            # Store results
            if research_id not in st.session_state.research_results:
                st.session_state.research_results[research_id] = {}
            st.session_state.research_results[research_id].update(result)
            
            st.success("Statistical analysis completed successfully!")
            
    except Exception as e:
        st.error(f"Error running statistical analysis: {str(e)}")


def display_assistance_results(research_id: str) -> None:
    """Display AI assistance results."""
    results = st.session_state.research_results[research_id]
    
    # Literature Search
    if "literature_search" in results:
        st.subheader("📚 Literature Search")
        literature_data = results["literature_search"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Sources Found:** {literature_data['sources_found']}")
            st.write(f"**Search Terms:** {', '.join(literature_data['search_terms'])}")
            st.write(f"**Date Range:** {literature_data['date_range']}")
        
        with col2:
            st.write(f"**Relevance Score:** {literature_data['relevance_score']}")
            st.write(f"**Language:** {literature_data['language']}")
            st.write(f"**Search Notes:** {literature_data['search_notes']}")
    
    # Hypothesis Generation
    if "hypothesis_generation" in results:
        st.subheader("💡 Hypothesis Generation")
        hypothesis_data = results["hypothesis_generation"]
        
        st.write(f"**Hypotheses Generated:** {hypothesis_data['hypotheses_generated']}")
        
        for i, (hypothesis, confidence) in enumerate(zip(hypothesis_data["hypotheses"], hypothesis_data["confidence_levels"])):
            st.write(f"**Hypothesis {i+1}:** {hypothesis} (Confidence: {confidence:.1%})")
        
        st.write(f"**Hypothesis Notes:** {hypothesis_data['hypothesis_notes']}")
    
    # Statistical Analysis
    if "statistical_analysis" in results:
        st.subheader("📊 Statistical Analysis")
        stats_data = results["statistical_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Analyses Performed:** {stats_data['analyses_performed']}")
            st.write(f"**Analysis Types:** {', '.join(stats_data['analysis_types'])}")
        
        with col2:
            st.write("**Key Findings:**")
            for finding in stats_data["key_findings"]:
                st.write(f"• {finding}")
        
        st.write(f"**Statistical Notes:** {stats_data['statistical_notes']}")


def show_research_visualization(research_id: str) -> None:
    """Display research visualization."""
    if research_id not in st.session_state.research_results:
        return
    
    results = st.session_state.research_results[research_id]
    
    if "statistical_analysis" not in results:
        return
    
    st.subheader("📊 Research Visualization")
    
    # Mock research data
    research_data = {
        "Period": ["Early Bronze", "Middle Bronze", "Late Bronze"],
        "Artifact_Count": [45, 78, 92],
        "Settlement_Size": [120, 180, 220],
        "Trade_Connections": [3, 7, 12]
    }
    
    df = pd.DataFrame(research_data)
    
    # Create correlation plot
    fig = px.scatter(
        df,
        x="Artifact_Count",
        y="Settlement_Size",
        size="Trade_Connections",
        color="Period",
        title="Artifact Count vs Settlement Size by Period"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def get_mock_research_items() -> List[Dict[str, Any]]:
    """Get mock research data for testing."""
    return [
        {
            "id": "res_001",
            "title": "Bronze Age Settlement Patterns",
            "type": "Literature",
            "status": "Active",
            "created_date": "2024-01-15",
            "updated_date": "2024-07-15",
            "author": "Dr. Sarah Johnson",
            "institution": "University of Archaeology",
            "progress": 75,
            "priority": "High",
            "description": "Comprehensive study of Bronze Age settlement patterns in the Mediterranean region.",
            "objectives": [
                "Analyze settlement distribution",
                "Identify cultural patterns",
                "Study environmental factors",
                "Compare regional variations"
            ],
            "methodology": [
                "Literature review",
                "GIS analysis",
                "Statistical analysis",
                "Comparative study"
            ]
        },
        {
            "id": "res_002",
            "title": "Pottery Typology Analysis",
            "type": "Analysis",
            "status": "Completed",
            "created_date": "2024-02-01",
            "updated_date": "2024-06-01",
            "author": "Dr. Michael Chen",
            "institution": "Institute of Classical Studies",
            "progress": 100,
            "priority": "Medium",
            "description": "Detailed analysis of pottery typology from the temple complex excavation.",
            "objectives": [
                "Classify pottery types",
                "Analyze manufacturing techniques",
                "Determine cultural affiliations",
                "Assess chronological development"
            ],
            "methodology": [
                "Typological analysis",
                "Petrographic analysis",
                "Chemical analysis",
                "Comparative study"
            ]
        },
        {
            "id": "res_003",
            "title": "Burial Practice Study",
            "type": "Synthesis",
            "status": "Active",
            "created_date": "2024-01-01",
            "updated_date": "2024-03-01",
            "author": "Dr. Emily Rodriguez",
            "institution": "Museum of Anthropology",
            "progress": 60,
            "priority": "High",
            "description": "Synthesis of burial practices across different time periods and cultures.",
            "objectives": [
                "Document burial practices",
                "Analyze cultural variations",
                "Study social implications",
                "Compare regional patterns"
            ],
            "methodology": [
                "Comparative analysis",
                "Statistical analysis",
                "Literature review",
                "Data synthesis"
            ]
        }
    ]


def filter_research_items(research_items: List[Dict[str, Any]], search_term: str, type_filter: str, status_filter: str) -> List[Dict[str, Any]]:
    """Filter research items based on search criteria."""
    filtered = research_items
    
    if search_term:
        filtered = [r for r in filtered if search_term.lower() in r["title"].lower()]
    
    if type_filter != "All":
        filtered = [r for r in filtered if r["type"] == type_filter]
    
    if status_filter != "All":
        filtered = [r for r in filtered if r["status"] == status_filter]
    
    return filtered


def get_research_by_id(research_id: str) -> Optional[Dict[str, Any]]:
    """Get research by ID."""
    # Check session state first
    if "research" in st.session_state and research_id in st.session_state.research:
        return st.session_state.research[research_id]
    
    # Check mock data
    mock_research = get_mock_research_items()
    for research in mock_research:
        if research["id"] == research_id:
            return research
    
    return None


