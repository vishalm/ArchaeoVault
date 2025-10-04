"""
Carbon Dating page for ArchaeoVault.

This module provides the interface for carbon dating analysis using AI agents.
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
from ..services.ai_agents.dating_agent import CarbonDatingAgent
from ..services.ai_orchestrator import AIOrchestrator
from ..models.carbon_dating import CarbonSample, DatingResult
from ..utils.exceptions import CarbonDatingError


def show_carbon_dating_page() -> None:
    """Display the carbon dating page."""
    st.title("⏳ Carbon Dating Analysis")
    st.markdown("**Scientific C-14 Dating and Calibration**")
    
    # Initialize session state
    if "carbon_dating_results" not in st.session_state:
        st.session_state.carbon_dating_results = {}
    
    if "selected_sample" not in st.session_state:
        st.session_state.selected_sample = None
    
    # Sidebar for sample management
    with st.sidebar:
        st.header("🧪 Sample Management")
        
        # Search and filter
        search_term = st.text_input("🔍 Search samples", placeholder="Enter sample ID or name")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Status", ["All", "Pending", "Processing", "Completed", "Failed"])
        with col2:
            method_filter = st.selectbox("Method", ["All", "C-14", "AMS", "Beta Counting"])
        
        # Mock sample list
        samples = get_mock_samples()
        
        # Filter samples
        filtered_samples = filter_samples(samples, search_term, status_filter, method_filter)
        
        # Display sample list
        for sample in filtered_samples:
            if st.button(f"🧪 {sample['name']}", key=f"select_{sample['id']}", use_container_width=True):
                st.session_state.selected_sample = sample['id']
                st.rerun()
    
    # Main content area
    if st.session_state.selected_sample:
        show_sample_details(st.session_state.selected_sample)
    else:
        show_sample_upload_form()


def show_sample_upload_form() -> None:
    """Display the sample upload form."""
    st.header("📤 Upload New Sample")
    
    with st.form("sample_upload_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sample_name = st.text_input("Sample Name", placeholder="Enter sample name")
            sample_type = st.selectbox("Sample Type", ["Wood", "Charcoal", "Bone", "Shell", "Textile", "Other"])
            collection_date = st.date_input("Collection Date")
            collection_location = st.text_input("Collection Location", placeholder="Enter collection location")
        
        with col2:
            lab_id = st.text_input("Lab ID", placeholder="Enter laboratory ID")
            dating_method = st.selectbox("Dating Method", ["C-14", "AMS", "Beta Counting"])
            sample_weight = st.number_input("Sample Weight (mg)", min_value=0.0, value=10.0)
            expected_age = st.number_input("Expected Age (years BP)", min_value=0, value=1000)
        
        # Sample information
        st.subheader("📝 Sample Information")
        description = st.text_area("Description", placeholder="Enter sample description")
        context = st.text_area("Archaeological Context", placeholder="Enter archaeological context")
        notes = st.text_area("Notes", placeholder="Enter any additional notes")
        
        # Submit button
        if st.form_submit_button("🧪 Process Sample", use_container_width=True):
            if sample_name and lab_id:
                # Create sample object
                sample_data = {
                    "name": sample_name,
                    "type": sample_type,
                    "collection_date": collection_date,
                    "collection_location": collection_location,
                    "lab_id": lab_id,
                    "dating_method": dating_method,
                    "sample_weight": sample_weight,
                    "expected_age": expected_age,
                    "description": description,
                    "context": context,
                    "notes": notes
                }
                
                # Process sample
                process_sample_upload(sample_data)
            else:
                st.error("Please provide sample name and lab ID.")


def show_sample_details(sample_id: str) -> None:
    """Display detailed sample information and analysis."""
    # Get sample data
    sample = get_sample_by_id(sample_id)
    if not sample:
        st.error("Sample not found.")
        return
    
    # Display sample information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🧪 Sample Info")
        
        # Display basic info
        info_data = {
            "Name": sample["name"],
            "Type": sample["type"],
            "Lab ID": sample["lab_id"],
            "Method": sample["dating_method"],
            "Weight": f"{sample['sample_weight']} mg",
            "Collection Date": sample.get("collection_date", "Unknown"),
            "Collection Location": sample.get("collection_location", "Unknown")
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
        
        # Status
        status = sample.get("status", "Pending")
        status_color = {
            "Pending": "🟡",
            "Processing": "🔵",
            "Completed": "🟢",
            "Failed": "🔴"
        }.get(status, "⚪")
        
        st.write(f"**Status:** {status_color} {status}")
    
    with col2:
        st.subheader("📋 Sample Details")
        
        # Description
        if sample.get("description"):
            st.write(f"**Description:** {sample['description']}")
        
        # Context
        if sample.get("context"):
            st.write(f"**Archaeological Context:** {sample['context']}")
        
        # Notes
        if sample.get("notes"):
            st.write(f"**Notes:** {sample['notes']}")
    
    # AI Analysis section
    st.header("🤖 AI Analysis")
    
    # Analysis controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧪 Run C-14 Analysis", use_container_width=True):
            run_c14_analysis(sample_id)
    
    with col2:
        if st.button("📊 Calibration", use_container_width=True):
            run_calibration_analysis(sample_id)
    
    with col3:
        if st.button("📈 Error Analysis", use_container_width=True):
            run_error_analysis(sample_id)
    
    # Display analysis results
    if sample_id in st.session_state.carbon_dating_results:
        display_analysis_results(sample_id)
    
    # Calibration curve visualization
    if sample_id in st.session_state.carbon_dating_results:
        show_calibration_curve(sample_id)


def process_sample_upload(sample_data: Dict[str, Any]) -> None:
    """Process uploaded sample data."""
    try:
        # Create sample ID
        sample_id = f"sample_{len(st.session_state.get('samples', [])) + 1:03d}"
        
        # Store sample data
        if "samples" not in st.session_state:
            st.session_state.samples = {}
        
        st.session_state.samples[sample_id] = sample_data
        
        # Set as selected sample
        st.session_state.selected_sample = sample_id
        
        st.success(f"Sample '{sample_data['name']}' uploaded successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error uploading sample: {str(e)}")


def run_c14_analysis(sample_id: str) -> None:
    """Run C-14 analysis on the sample."""
    try:
        with st.spinner("Running C-14 analysis..."):
            # Get AI orchestrator from session state
            if "services" in st.session_state:
                ai_orchestrator = st.session_state.services.get("ai_orchestrator")
                if ai_orchestrator:
                    # Run analysis
                    result = asyncio.run(ai_orchestrator.analyze_carbon_dating(sample_id))
                    
                    # Store results
                    st.session_state.carbon_dating_results[sample_id] = result
                    
                    st.success("C-14 analysis completed successfully!")
                else:
                    st.error("AI orchestrator not available.")
            else:
                st.error("Services not initialized.")
                
    except Exception as e:
        st.error(f"Error running C-14 analysis: {str(e)}")


def run_calibration_analysis(sample_id: str) -> None:
    """Run calibration analysis on the sample."""
    try:
        with st.spinner("Running calibration analysis..."):
            # Mock calibration analysis
            result = {
                "calibration_analysis": {
                    "raw_age": 2450,
                    "calibrated_age": "800-900 CE",
                    "calibration_curve": "IntCal20",
                    "confidence_interval": "95%",
                    "probability_distribution": "Normal",
                    "calibration_notes": "High confidence calibration using IntCal20 curve"
                }
            }
            
            # Store results
            if sample_id not in st.session_state.carbon_dating_results:
                st.session_state.carbon_dating_results[sample_id] = {}
            st.session_state.carbon_dating_results[sample_id].update(result)
            
            st.success("Calibration analysis completed!")
            
    except Exception as e:
        st.error(f"Error running calibration analysis: {str(e)}")


def run_error_analysis(sample_id: str) -> None:
    """Run error analysis on the sample."""
    try:
        with st.spinner("Running error analysis..."):
            # Mock error analysis
            result = {
                "error_analysis": {
                    "measurement_error": "±25 years",
                    "calibration_error": "±15 years",
                    "total_error": "±30 years",
                    "error_sources": ["Measurement uncertainty", "Calibration curve uncertainty"],
                    "confidence_level": "95%",
                    "error_notes": "Error within acceptable range for C-14 dating"
                }
            }
            
            # Store results
            if sample_id not in st.session_state.carbon_dating_results:
                st.session_state.carbon_dating_results[sample_id] = {}
            st.session_state.carbon_dating_results[sample_id].update(result)
            
            st.success("Error analysis completed!")
            
    except Exception as e:
        st.error(f"Error running error analysis: {str(e)}")


def display_analysis_results(sample_id: str) -> None:
    """Display AI analysis results."""
    results = st.session_state.carbon_dating_results[sample_id]
    
    # C-14 Analysis
    if "c14_analysis" in results:
        st.subheader("🧪 C-14 Analysis")
        c14_data = results["c14_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Raw Age:** {c14_data['raw_age']} years BP")
            st.write(f"**C-14 Activity:** {c14_data['c14_activity']} Bq/kg")
            st.write(f"**Measurement Error:** {c14_data['measurement_error']}")
        
        with col2:
            st.write(f"**Dating Method:** {c14_data['dating_method']}")
            st.write(f"**Sample Quality:** {c14_data['sample_quality']}")
            st.write(f"**Analysis Notes:** {c14_data['analysis_notes']}")
    
    # Calibration Analysis
    if "calibration_analysis" in results:
        st.subheader("📊 Calibration Analysis")
        cal_data = results["calibration_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Raw Age:** {cal_data['raw_age']} years BP")
            st.write(f"**Calibrated Age:** {cal_data['calibrated_age']}")
            st.write(f"**Calibration Curve:** {cal_data['calibration_curve']}")
        
        with col2:
            st.write(f"**Confidence Interval:** {cal_data['confidence_interval']}")
            st.write(f"**Probability Distribution:** {cal_data['probability_distribution']}")
            st.write(f"**Calibration Notes:** {cal_data['calibration_notes']}")
    
    # Error Analysis
    if "error_analysis" in results:
        st.subheader("📈 Error Analysis")
        error_data = results["error_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Measurement Error:** {error_data['measurement_error']}")
            st.write(f"**Calibration Error:** {error_data['calibration_error']}")
            st.write(f"**Total Error:** {error_data['total_error']}")
        
        with col2:
            st.write(f"**Confidence Level:** {error_data['confidence_level']}")
            st.write(f"**Error Sources:** {', '.join(error_data['error_sources'])}")
            st.write(f"**Error Notes:** {error_data['error_notes']}")


def show_calibration_curve(sample_id: str) -> None:
    """Display calibration curve visualization."""
    if sample_id not in st.session_state.carbon_dating_results:
        return
    
    results = st.session_state.carbon_dating_results[sample_id]
    
    if "calibration_analysis" not in results:
        return
    
    st.subheader("📈 Calibration Curve")
    
    # Mock calibration curve data
    raw_ages = list(range(2000, 3000, 10))
    calibrated_ages = [age + (age - 2500) * 0.1 for age in raw_ages]
    
    # Create calibration curve plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=raw_ages,
        y=calibrated_ages,
        mode='lines',
        name='Calibration Curve',
        line=dict(color='blue', width=2)
    ))
    
    # Add sample point
    sample_raw_age = results["calibration_analysis"]["raw_age"]
    sample_calibrated_age = 800  # Mock calibrated age
    
    fig.add_trace(go.Scatter(
        x=[sample_raw_age],
        y=[sample_calibrated_age],
        mode='markers',
        name='Sample',
        marker=dict(color='red', size=10)
    ))
    
    fig.update_layout(
        title="C-14 Calibration Curve",
        xaxis_title="Raw Age (years BP)",
        yaxis_title="Calibrated Age (CE)",
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def get_mock_samples() -> List[Dict[str, Any]]:
    """Get mock sample data for testing."""
    return [
        {
            "id": "sample_001",
            "name": "Wood Sample A-47",
            "type": "Wood",
            "lab_id": "LAB-2024-001",
            "dating_method": "C-14",
            "sample_weight": 15.5,
            "expected_age": 1200,
            "status": "Completed",
            "collection_date": "2024-01-15",
            "collection_location": "Site A-47, Layer 3",
            "description": "Charred wood sample from hearth feature",
            "context": "Domestic structure, Bronze Age settlement",
            "notes": "Excellent preservation, minimal contamination"
        },
        {
            "id": "sample_002",
            "name": "Bone Sample B-23",
            "type": "Bone",
            "lab_id": "LAB-2024-002",
            "dating_method": "AMS",
            "sample_weight": 8.2,
            "expected_age": 800,
            "status": "Processing",
            "collection_date": "2024-02-03",
            "collection_location": "Site B-23, Grave 5",
            "description": "Human bone sample from burial context",
            "context": "Individual burial, Iron Age cemetery",
            "notes": "Good preservation, collagen extraction successful"
        },
        {
            "id": "sample_003",
            "name": "Shell Sample C-12",
            "type": "Shell",
            "lab_id": "LAB-2024-003",
            "dating_method": "Beta Counting",
            "sample_weight": 12.0,
            "expected_age": 1500,
            "status": "Pending",
            "collection_date": "2024-01-28",
            "collection_location": "Site C-12, Midden",
            "description": "Marine shell sample from midden deposit",
            "context": "Food waste deposit, Neolithic settlement",
            "notes": "Fresh shell, minimal weathering"
        }
    ]


def filter_samples(samples: List[Dict[str, Any]], search_term: str, status_filter: str, method_filter: str) -> List[Dict[str, Any]]:
    """Filter samples based on search criteria."""
    filtered = samples
    
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower() or search_term.lower() in s["lab_id"].lower()]
    
    if status_filter != "All":
        filtered = [s for s in filtered if s.get("status", "Pending") == status_filter]
    
    if method_filter != "All":
        filtered = [s for s in filtered if s["dating_method"] == method_filter]
    
    return filtered


def get_sample_by_id(sample_id: str) -> Optional[Dict[str, Any]]:
    """Get sample by ID."""
    # Check session state first
    if "samples" in st.session_state and sample_id in st.session_state.samples:
        return st.session_state.samples[sample_id]
    
    # Check mock data
    mock_samples = get_mock_samples()
    for sample in mock_samples:
        if sample["id"] == sample_id:
            return sample
    
    return None
