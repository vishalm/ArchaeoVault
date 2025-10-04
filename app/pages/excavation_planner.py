"""
Excavation Planner page for ArchaeoVault.

This module provides the interface for planning excavations using AI agents.
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
from ..services.ai_agents.excavation_agent import ExcavationPlanningAgent
from ..services.ai_orchestrator import AIOrchestrator
from ..models.excavation import Excavation
from ..utils.exceptions import ExcavationPlanningError


def show_excavation_planner_page() -> None:
    """Display the excavation planner page."""
    st.title("⛏️ Excavation Planner")
    st.markdown("**AI-Powered Excavation Site Planning and Strategy**")
    
    # Initialize session state
    if "excavation_planning_results" not in st.session_state:
        st.session_state.excavation_planning_results = {}
    
    if "selected_excavation" not in st.session_state:
        st.session_state.selected_excavation = None
    
    # Sidebar for excavation selection
    with st.sidebar:
        st.header("⛏️ Excavation Projects")
        
        # Search and filter
        search_term = st.text_input("🔍 Search excavations", placeholder="Enter site name or ID")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Status", ["All", "Planning", "Active", "Completed", "Suspended"])
        with col2:
            priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
        
        # Mock excavation list
        excavations = get_mock_excavations()
        
        # Filter excavations
        filtered_excavations = filter_excavations(excavations, search_term, status_filter, priority_filter)
        
        # Display excavation list
        for excavation in filtered_excavations:
            if st.button(f"⛏️ {excavation['name']}", key=f"select_{excavation['id']}", use_container_width=True):
                st.session_state.selected_excavation = excavation['id']
                st.rerun()
    
    # Main content area
    if st.session_state.selected_excavation:
        show_excavation_details(st.session_state.selected_excavation)
    else:
        show_excavation_overview()


def show_excavation_overview() -> None:
    """Display excavation overview and statistics."""
    st.header("📊 Excavation Overview")
    
    # Get mock excavations
    excavations = get_mock_excavations()
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Excavations", len(excavations))
    
    with col2:
        active_count = len([e for e in excavations if e["status"] == "Active"])
        st.metric("Active", active_count)
    
    with col3:
        completed_count = len([e for e in excavations if e["status"] == "Completed"])
        st.metric("Completed", completed_count)
    
    with col4:
        high_priority_count = len([e for e in excavations if e["priority"] == "High"])
        st.metric("High Priority", high_priority_count)
    
    # Status distribution
    st.subheader("📈 Status Distribution")
    status_counts = {}
    for exc in excavations:
        status = exc["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    fig = px.pie(
        values=list(status_counts.values()),
        names=list(status_counts.keys()),
        title="Excavations by Status"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Priority distribution
    st.subheader("🎯 Priority Distribution")
    priority_counts = {}
    for exc in excavations:
        priority = exc["priority"]
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    fig = px.bar(
        x=list(priority_counts.keys()),
        y=list(priority_counts.values()),
        title="Excavations by Priority"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Timeline visualization
    st.subheader("⏰ Excavation Timeline")
    timeline_data = []
    for exc in excavations:
        timeline_data.append({
            "Excavation": exc["name"],
            "Start": exc["start_date"],
            "End": exc["end_date"],
            "Status": exc["status"],
            "Priority": exc["priority"]
        })
    
    df = pd.DataFrame(timeline_data)
    
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Excavation",
        color="Status",
        title="Excavation Timeline"
    )
    st.plotly_chart(fig, use_container_width=True)


def show_excavation_details(excavation_id: str) -> None:
    """Display detailed excavation information and planning."""
    # Get excavation data
    excavation = get_excavation_by_id(excavation_id)
    if not excavation:
        st.error("Excavation not found.")
        return
    
    # Display excavation information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⛏️ Basic Info")
        
        # Display basic info
        info_data = {
            "Name": excavation["name"],
            "Site": excavation["site"],
            "Status": excavation["status"],
            "Priority": excavation["priority"],
            "Start Date": excavation["start_date"],
            "End Date": excavation["end_date"],
            "Director": excavation.get("director", "Unknown"),
            "Institution": excavation.get("institution", "Unknown")
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
        
        # Grid size
        if excavation.get("grid_size"):
            st.write(f"**Grid Size:** {excavation['grid_size']}")
        
        # Layers
        if excavation.get("layers"):
            st.write(f"**Layers:** {excavation['layers']}")
    
    with col2:
        st.subheader("📋 Description")
        
        # Description
        if excavation.get("description"):
            st.write(excavation["description"])
        
        # Objectives
        if excavation.get("objectives"):
            st.subheader("🎯 Objectives")
            for objective in excavation["objectives"]:
                st.write(f"• {objective}")
        
        # Methodology
        if excavation.get("methodology"):
            st.subheader("🔬 Methodology")
            for method in excavation["methodology"]:
                st.write(f"• {method}")
    
    # AI Planning section
    st.header("🤖 AI Planning")
    
    # Planning controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Generate Plan", use_container_width=True):
            run_plan_generation(excavation_id)
    
    with col2:
        if st.button("📊 Resource Analysis", use_container_width=True):
            run_resource_analysis(excavation_id)
    
    with col3:
        if st.button("⚠️ Risk Assessment", use_container_width=True):
            run_risk_assessment(excavation_id)
    
    # Display planning results
    if excavation_id in st.session_state.excavation_planning_results:
        display_planning_results(excavation_id)
    
    # Grid visualization
    if excavation_id in st.session_state.excavation_planning_results:
        show_grid_visualization(excavation_id)


def run_plan_generation(excavation_id: str) -> None:
    """Run plan generation for the excavation."""
    try:
        with st.spinner("Generating excavation plan..."):
            # Get AI orchestrator from session state
            if "services" in st.session_state:
                ai_orchestrator = st.session_state.services.get("ai_orchestrator")
                if ai_orchestrator:
                    # Run planning
                    result = asyncio.run(ai_orchestrator.plan_excavation(excavation_id))
                    
                    # Store results
                    st.session_state.excavation_planning_results[excavation_id] = result
                    
                    st.success("Excavation plan generated successfully!")
                else:
                    st.error("AI orchestrator not available.")
            else:
                st.error("Services not initialized.")
                
    except Exception as e:
        st.error(f"Error generating plan: {str(e)}")


def run_resource_analysis(excavation_id: str) -> None:
    """Run resource analysis for the excavation."""
    try:
        with st.spinner("Analyzing resources..."):
            # Mock resource analysis
            result = {
                "resource_analysis": {
                    "estimated_duration": "6 months",
                    "required_personnel": 15,
                    "estimated_budget": "$150,000",
                    "equipment_needed": [
                        "Trowels",
                        "Brushes",
                        "Screens",
                        "Measuring tools",
                        "Photography equipment",
                        "GPS devices"
                    ],
                    "supplies_needed": [
                        "Bags for artifacts",
                        "Labels",
                        "Recording forms",
                        "Conservation materials"
                    ],
                    "resource_notes": "Standard excavation equipment and supplies required"
                }
            }
            
            # Store results
            if excavation_id not in st.session_state.excavation_planning_results:
                st.session_state.excavation_planning_results[excavation_id] = {}
            st.session_state.excavation_planning_results[excavation_id].update(result)
            
            st.success("Resource analysis completed!")
            
    except Exception as e:
        st.error(f"Error running resource analysis: {str(e)}")


def run_risk_assessment(excavation_id: str) -> None:
    """Run risk assessment for the excavation."""
    try:
        with st.spinner("Assessing risks..."):
            # Mock risk assessment
            result = {
                "risk_assessment": {
                    "weather_risk": "Medium",
                    "safety_risk": "Low",
                    "budget_risk": "Low",
                    "schedule_risk": "Medium",
                    "identified_risks": [
                        "Weather delays",
                        "Equipment failure",
                        "Personnel availability",
                        "Budget overruns"
                    ],
                    "mitigation_strategies": [
                        "Weather monitoring",
                        "Equipment backup",
                        "Flexible scheduling",
                        "Budget contingency"
                    ],
                    "risk_notes": "Overall risk level is manageable with proper planning"
                }
            }
            
            # Store results
            if excavation_id not in st.session_state.excavation_planning_results:
                st.session_state.excavation_planning_results[excavation_id] = {}
            st.session_state.excavation_planning_results[excavation_id].update(result)
            
            st.success("Risk assessment completed!")
            
    except Exception as e:
        st.error(f"Error running risk assessment: {str(e)}")


def display_planning_results(excavation_id: str) -> None:
    """Display AI planning results."""
    results = st.session_state.excavation_planning_results[excavation_id]
    
    # Plan Generation
    if "plan_generation" in results:
        st.subheader("📋 Excavation Plan")
        plan_data = results["plan_generation"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Plan Type:** {plan_data['plan_type']}")
            st.write(f"**Methodology:** {plan_data['methodology']}")
            st.write(f"**Grid System:** {plan_data['grid_system']}")
        
        with col2:
            st.write(f"**Excavation Phases:** {plan_data['excavation_phases']}")
            st.write(f"**Recording System:** {plan_data['recording_system']}")
            st.write(f"**Plan Notes:** {plan_data['plan_notes']}")
    
    # Resource Analysis
    if "resource_analysis" in results:
        st.subheader("📊 Resource Analysis")
        resource_data = results["resource_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Duration:** {resource_data['estimated_duration']}")
            st.write(f"**Personnel:** {resource_data['required_personnel']}")
            st.write(f"**Budget:** {resource_data['estimated_budget']}")
        
        with col2:
            st.write(f"**Equipment:** {', '.join(resource_data['equipment_needed'])}")
            st.write(f"**Supplies:** {', '.join(resource_data['supplies_needed'])}")
            st.write(f"**Resource Notes:** {resource_data['resource_notes']}")
    
    # Risk Assessment
    if "risk_assessment" in results:
        st.subheader("⚠️ Risk Assessment")
        risk_data = results["risk_assessment"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Weather Risk:** {risk_data['weather_risk']}")
            st.write(f"**Safety Risk:** {risk_data['safety_risk']}")
            st.write(f"**Budget Risk:** {risk_data['budget_risk']}")
            st.write(f"**Schedule Risk:** {risk_data['schedule_risk']}")
        
        with col2:
            st.write("**Identified Risks:**")
            for risk in risk_data["identified_risks"]:
                st.write(f"• {risk}")
            
            st.write("**Mitigation Strategies:**")
            for strategy in risk_data["mitigation_strategies"]:
                st.write(f"• {strategy}")
        
        st.write(f"**Risk Notes:** {risk_data['risk_notes']}")


def show_grid_visualization(excavation_id: str) -> None:
    """Display grid visualization."""
    if excavation_id not in st.session_state.excavation_planning_results:
        return
    
    results = st.session_state.excavation_planning_results[excavation_id]
    
    if "plan_generation" not in results:
        return
    
    st.subheader("📐 Grid Visualization")
    
    # Mock grid data
    grid_size = 10
    grid_data = []
    
    for i in range(grid_size):
        for j in range(grid_size):
            grid_data.append({
                "X": i,
                "Y": j,
                "Status": "Planned" if (i + j) % 2 == 0 else "Reserved",
                "Priority": "High" if i < 3 or j < 3 else "Medium"
            })
    
    df = pd.DataFrame(grid_data)
    
    fig = px.scatter(
        df,
        x="X",
        y="Y",
        color="Status",
        size="Priority",
        title="Excavation Grid Plan"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def get_mock_excavations() -> List[Dict[str, Any]]:
    """Get mock excavation data for testing."""
    return [
        {
            "id": "exc_001",
            "name": "Site A-47 Excavation",
            "site": "Site A-47",
            "status": "Active",
            "priority": "High",
            "start_date": "2024-01-15",
            "end_date": "2024-07-15",
            "director": "Dr. Sarah Johnson",
            "institution": "University of Archaeology",
            "grid_size": "10x10 meters",
            "layers": 5,
            "description": "A Bronze Age settlement site with well-preserved structures and artifacts.",
            "objectives": [
                "Document settlement layout",
                "Recover artifacts",
                "Analyze stratigraphy",
                "Date occupation periods"
            ],
            "methodology": [
                "Systematic excavation",
                "Grid-based recording",
                "Photographic documentation",
                "Artifact collection"
            ]
        },
        {
            "id": "exc_002",
            "name": "Temple Complex B-23",
            "site": "Site B-23",
            "status": "Planning",
            "priority": "Medium",
            "start_date": "2024-03-01",
            "end_date": "2024-09-01",
            "director": "Dr. Michael Chen",
            "institution": "Institute of Classical Studies",
            "grid_size": "15x15 meters",
            "layers": 8,
            "description": "A classical temple complex with multiple phases of construction.",
            "objectives": [
                "Map temple architecture",
                "Identify construction phases",
                "Recover votive offerings",
                "Document decorative elements"
            ],
            "methodology": [
                "Architectural recording",
                "Stratigraphic analysis",
                "Artifact documentation",
                "3D modeling"
            ]
        },
        {
            "id": "exc_003",
            "name": "Cemetery C-12",
            "site": "Site C-12",
            "status": "Completed",
            "priority": "Low",
            "start_date": "2023-06-01",
            "end_date": "2023-12-01",
            "director": "Dr. Emily Rodriguez",
            "institution": "Museum of Anthropology",
            "grid_size": "20x20 meters",
            "layers": 3,
            "description": "A medieval cemetery with well-preserved burials and grave goods.",
            "objectives": [
                "Document burial practices",
                "Analyze grave goods",
                "Study population health",
                "Date burial periods"
            ],
            "methodology": [
                "Individual burial recording",
                "Osteological analysis",
                "Artifact documentation",
                "Radiocarbon dating"
            ]
        }
    ]


def filter_excavations(excavations: List[Dict[str, Any]], search_term: str, status_filter: str, priority_filter: str) -> List[Dict[str, Any]]:
    """Filter excavations based on search criteria."""
    filtered = excavations
    
    if search_term:
        filtered = [e for e in filtered if search_term.lower() in e["name"].lower() or search_term.lower() in e["site"].lower()]
    
    if status_filter != "All":
        filtered = [e for e in filtered if e["status"] == status_filter]
    
    if priority_filter != "All":
        filtered = [e for e in filtered if e["priority"] == priority_filter]
    
    return filtered


def get_excavation_by_id(excavation_id: str) -> Optional[Dict[str, Any]]:
    """Get excavation by ID."""
    # Check session state first
    if "excavations" in st.session_state and excavation_id in st.session_state.excavations:
        return st.session_state.excavations[excavation_id]
    
    # Check mock data
    mock_excavations = get_mock_excavations()
    for excavation in mock_excavations:
        if excavation["id"] == excavation_id:
            return excavation
    
    return None


