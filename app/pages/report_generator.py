"""
Report Generator page for ArchaeoVault.

This module provides the interface for generating archaeological reports using AI agents.
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
from ..services.ai_agents.report_agent import ReportGenerationAgent
from ..services.ai_orchestrator import AIOrchestrator
from ..models.report import Report
from ..utils.exceptions import ReportGenerationError


def show_report_generator_page() -> None:
    """Display the report generator page."""
    st.title("📄 Report Generator")
    st.markdown("**AI-Powered Archaeological Report Creation**")
    
    # Initialize session state
    if "report_generation_results" not in st.session_state:
        st.session_state.report_generation_results = {}
    
    if "selected_report" not in st.session_state:
        st.session_state.selected_report = None
    
    # Sidebar for report selection
    with st.sidebar:
        st.header("📄 Report Library")
        
        # Search and filter
        search_term = st.text_input("🔍 Search reports", placeholder="Enter report title or ID")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            type_filter = st.selectbox("Type", ["All", "Excavation", "Analysis", "Research", "Summary"])
        with col2:
            status_filter = st.selectbox("Status", ["All", "Draft", "Review", "Published", "Archived"])
        
        # Mock report list
        reports = get_mock_reports()
        
        # Filter reports
        filtered_reports = filter_reports(reports, search_term, type_filter, status_filter)
        
        # Display report list
        for report in filtered_reports:
            if st.button(f"📄 {report['title']}", key=f"select_{report['id']}", use_container_width=True):
                st.session_state.selected_report = report['id']
                st.rerun()
    
    # Main content area
    if st.session_state.selected_report:
        show_report_details(st.session_state.selected_report)
    else:
        show_report_overview()


def show_report_overview() -> None:
    """Display report overview and statistics."""
    st.header("📊 Report Overview")
    
    # Get mock reports
    reports = get_mock_reports()
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reports", len(reports))
    
    with col2:
        published_count = len([r for r in reports if r["status"] == "Published"])
        st.metric("Published", published_count)
    
    with col3:
        draft_count = len([r for r in reports if r["status"] == "Draft"])
        st.metric("Draft", draft_count)
    
    with col4:
        excavation_count = len([r for r in reports if r["type"] == "Excavation"])
        st.metric("Excavation Reports", excavation_count)
    
    # Type distribution
    st.subheader("📈 Report Type Distribution")
    type_counts = {}
    for report in reports:
        report_type = report["type"]
        type_counts[report_type] = type_counts.get(report_type, 0) + 1
    
    fig = px.pie(
        values=list(type_counts.values()),
        names=list(type_counts.keys()),
        title="Reports by Type"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Status distribution
    st.subheader("📊 Status Distribution")
    status_counts = {}
    for report in reports:
        status = report["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    fig = px.bar(
        x=list(status_counts.keys()),
        y=list(status_counts.values()),
        title="Reports by Status"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Timeline visualization
    st.subheader("⏰ Report Timeline")
    timeline_data = []
    for report in reports:
        timeline_data.append({
            "Report": report["title"],
            "Created": report["created_date"],
            "Updated": report["updated_date"],
            "Type": report["type"],
            "Status": report["status"]
        })
    
    df = pd.DataFrame(timeline_data)
    
    fig = px.timeline(
        df,
        x_start="Created",
        x_end="Updated",
        y="Report",
        color="Type",
        title="Report Timeline"
    )
    st.plotly_chart(fig, use_container_width=True)


def show_report_details(report_id: str) -> None:
    """Display detailed report information and generation."""
    # Get report data
    report = get_report_by_id(report_id)
    if not report:
        st.error("Report not found.")
        return
    
    # Display report information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📄 Basic Info")
        
        # Display basic info
        info_data = {
            "Title": report["title"],
            "Type": report["type"],
            "Status": report["status"],
            "Created": report["created_date"],
            "Updated": report["updated_date"],
            "Author": report.get("author", "Unknown"),
            "Institution": report.get("institution", "Unknown")
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
        
        # Word count
        if report.get("word_count"):
            st.write(f"**Word Count:** {report['word_count']}")
        
        # Pages
        if report.get("pages"):
            st.write(f"**Pages:** {report['pages']}")
    
    with col2:
        st.subheader("📋 Description")
        
        # Description
        if report.get("description"):
            st.write(report["description"])
        
        # Objectives
        if report.get("objectives"):
            st.subheader("🎯 Objectives")
            for objective in report["objectives"]:
                st.write(f"• {objective}")
        
        # Methodology
        if report.get("methodology"):
            st.subheader("🔬 Methodology")
            for method in report["methodology"]:
                st.write(f"• {method}")
    
    # AI Generation section
    st.header("🤖 AI Report Generation")
    
    # Generation controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Generate Report", use_container_width=True):
            run_report_generation(report_id)
    
    with col2:
        if st.button("📊 Add Charts", use_container_width=True):
            run_chart_generation(report_id)
    
    with col3:
        if st.button("📚 Add Citations", use_container_width=True):
            run_citation_generation(report_id)
    
    # Display generation results
    if report_id in st.session_state.report_generation_results:
        display_generation_results(report_id)
    
    # Report preview
    if report_id in st.session_state.report_generation_results:
        show_report_preview(report_id)


def run_report_generation(report_id: str) -> None:
    """Run report generation for the report."""
    try:
        with st.spinner("Generating report..."):
            # Get AI orchestrator from session state
            if "services" in st.session_state:
                ai_orchestrator = st.session_state.services.get("ai_orchestrator")
                if ai_orchestrator:
                    # Run generation
                    result = asyncio.run(ai_orchestrator.generate_report(report_id))
                    
                    # Store results
                    st.session_state.report_generation_results[report_id] = result
                    
                    st.success("Report generated successfully!")
                else:
                    st.error("AI orchestrator not available.")
            else:
                st.error("Services not initialized.")
                
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")


def run_chart_generation(report_id: str) -> None:
    """Run chart generation for the report."""
    try:
        with st.spinner("Generating charts..."):
            # Mock chart generation
            result = {
                "chart_generation": {
                    "charts_created": 5,
                    "chart_types": ["Bar", "Line", "Pie", "Scatter", "Timeline"],
                    "data_sources": ["Excavation data", "Artifact analysis", "Carbon dating"],
                    "chart_notes": "Charts generated based on available data"
                }
            }
            
            # Store results
            if report_id not in st.session_state.report_generation_results:
                st.session_state.report_generation_results[report_id] = {}
            st.session_state.report_generation_results[report_id].update(result)
            
            st.success("Charts generated successfully!")
            
    except Exception as e:
        st.error(f"Error generating charts: {str(e)}")


def run_citation_generation(report_id: str) -> None:
    """Run citation generation for the report."""
    try:
        with st.spinner("Generating citations..."):
            # Mock citation generation
            result = {
                "citation_generation": {
                    "citations_added": 12,
                    "citation_style": "Chicago",
                    "sources": [
                        "Smith, J. (2020). Archaeological Methods. Journal of Archaeology.",
                        "Johnson, M. (2019). Bronze Age Settlements. Ancient History Review.",
                        "Brown, K. (2021). Carbon Dating Techniques. Scientific Archaeology."
                    ],
                    "citation_notes": "Citations generated based on report content"
                }
            }
            
            # Store results
            if report_id not in st.session_state.report_generation_results:
                st.session_state.report_generation_results[report_id] = {}
            st.session_state.report_generation_results[report_id].update(result)
            
            st.success("Citations generated successfully!")
            
    except Exception as e:
        st.error(f"Error generating citations: {str(e)}")


def display_generation_results(report_id: str) -> None:
    """Display AI generation results."""
    results = st.session_state.report_generation_results[report_id]
    
    # Report Generation
    if "report_generation" in results:
        st.subheader("📝 Report Generation")
        report_data = results["report_generation"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Report Type:** {report_data['report_type']}")
            st.write(f"**Word Count:** {report_data['word_count']}")
            st.write(f"**Sections:** {report_data['sections']}")
        
        with col2:
            st.write(f"**Language:** {report_data['language']}")
            st.write(f"**Style:** {report_data['style']}")
            st.write(f"**Generation Notes:** {report_data['generation_notes']}")
    
    # Chart Generation
    if "chart_generation" in results:
        st.subheader("📊 Chart Generation")
        chart_data = results["chart_generation"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Charts Created:** {chart_data['charts_created']}")
            st.write(f"**Chart Types:** {', '.join(chart_data['chart_types'])}")
        
        with col2:
            st.write(f"**Data Sources:** {', '.join(chart_data['data_sources'])}")
            st.write(f"**Chart Notes:** {chart_data['chart_notes']}")
    
    # Citation Generation
    if "citation_generation" in results:
        st.subheader("📚 Citation Generation")
        citation_data = results["citation_generation"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Citations Added:** {citation_data['citations_added']}")
            st.write(f"**Citation Style:** {citation_data['citation_style']}")
        
        with col2:
            st.write("**Sources:**")
            for source in citation_data["sources"]:
                st.write(f"• {source}")
        
        st.write(f"**Citation Notes:** {citation_data['citation_notes']}")


def show_report_preview(report_id: str) -> None:
    """Display report preview."""
    if report_id not in st.session_state.report_generation_results:
        return
    
    results = st.session_state.report_generation_results[report_id]
    
    if "report_generation" not in results:
        return
    
    st.subheader("👁️ Report Preview")
    
    # Mock report content
    report_content = """
    # Archaeological Excavation Report
    
    ## Executive Summary
    
    This report presents the results of the archaeological excavation conducted at Site A-47 between January and July 2024. The excavation revealed a well-preserved Bronze Age settlement with multiple phases of occupation.
    
    ## Introduction
    
    Site A-47 is located in the central region of the study area and was identified through surface survey in 2023. The site shows evidence of continuous occupation from the Early Bronze Age through the Late Bronze Age.
    
    ## Methodology
    
    The excavation employed a systematic grid-based approach with 1x1 meter squares. All artifacts were recorded in three dimensions and photographed. Soil samples were collected for analysis.
    
    ## Results
    
    ### Stratigraphy
    
    The site revealed five distinct cultural layers:
    1. Layer 1: Modern disturbance (0-20cm)
    2. Layer 2: Late Bronze Age (20-40cm)
    3. Layer 3: Middle Bronze Age (40-60cm)
    4. Layer 4: Early Bronze Age (60-80cm)
    5. Layer 5: Natural subsoil (80cm+)
    
    ### Artifacts
    
    A total of 247 artifacts were recovered, including:
    - Ceramic vessels: 156
    - Stone tools: 45
    - Metal objects: 23
    - Organic remains: 23
    
    ## Discussion
    
    The excavation provides important insights into Bronze Age settlement patterns and material culture. The presence of imported ceramics suggests trade connections with distant regions.
    
    ## Conclusions
    
    Site A-47 represents a significant Bronze Age settlement that contributes to our understanding of regional cultural development.
    
    ## References
    
    1. Smith, J. (2020). Archaeological Methods. Journal of Archaeology.
    2. Johnson, M. (2019). Bronze Age Settlements. Ancient History Review.
    3. Brown, K. (2021). Carbon Dating Techniques. Scientific Archaeology.
    """
    
    st.markdown(report_content)


def get_mock_reports() -> List[Dict[str, Any]]:
    """Get mock report data for testing."""
    return [
        {
            "id": "rep_001",
            "title": "Site A-47 Excavation Report",
            "type": "Excavation",
            "status": "Published",
            "created_date": "2024-01-15",
            "updated_date": "2024-07-15",
            "author": "Dr. Sarah Johnson",
            "institution": "University of Archaeology",
            "word_count": 15000,
            "pages": 45,
            "description": "Comprehensive report on the Bronze Age settlement excavation at Site A-47.",
            "objectives": [
                "Document excavation results",
                "Analyze artifacts",
                "Interpret cultural context",
                "Provide recommendations"
            ],
            "methodology": [
                "Systematic excavation",
                "Artifact documentation",
                "Stratigraphic analysis",
                "Radiocarbon dating"
            ]
        },
        {
            "id": "rep_002",
            "title": "Artifact Analysis Summary",
            "type": "Analysis",
            "status": "Draft",
            "created_date": "2024-02-01",
            "updated_date": "2024-02-15",
            "author": "Dr. Michael Chen",
            "institution": "Institute of Classical Studies",
            "word_count": 8000,
            "pages": 25,
            "description": "Detailed analysis of ceramic artifacts from the temple complex excavation.",
            "objectives": [
                "Classify ceramic types",
                "Analyze manufacturing techniques",
                "Determine cultural affiliations",
                "Assess preservation state"
            ],
            "methodology": [
                "Typological analysis",
                "Petrographic analysis",
                "Chemical analysis",
                "Comparative study"
            ]
        },
        {
            "id": "rep_003",
            "title": "Research Findings Summary",
            "type": "Research",
            "status": "Review",
            "created_date": "2024-01-01",
            "updated_date": "2024-03-01",
            "author": "Dr. Emily Rodriguez",
            "institution": "Museum of Anthropology",
            "word_count": 12000,
            "pages": 35,
            "description": "Summary of research findings from the cemetery excavation project.",
            "objectives": [
                "Summarize research findings",
                "Present statistical analysis",
                "Discuss implications",
                "Suggest future research"
            ],
            "methodology": [
                "Statistical analysis",
                "Comparative study",
                "Literature review",
                "Data synthesis"
            ]
        }
    ]


def filter_reports(reports: List[Dict[str, Any]], search_term: str, type_filter: str, status_filter: str) -> List[Dict[str, Any]]:
    """Filter reports based on search criteria."""
    filtered = reports
    
    if search_term:
        filtered = [r for r in filtered if search_term.lower() in r["title"].lower()]
    
    if type_filter != "All":
        filtered = [r for r in filtered if r["type"] == type_filter]
    
    if status_filter != "All":
        filtered = [r for r in filtered if r["status"] == status_filter]
    
    return filtered


def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    """Get report by ID."""
    # Check session state first
    if "reports" in st.session_state and report_id in st.session_state.reports:
        return st.session_state.reports[report_id]
    
    # Check mock data
    mock_reports = get_mock_reports()
    for report in mock_reports:
        if report["id"] == report_id:
            return report
    
    return None


