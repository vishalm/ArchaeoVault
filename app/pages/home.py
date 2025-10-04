"""
Home page for ArchaeoVault.

This module contains the main landing page with overview of features
and quick access to different tools.
"""

import streamlit as st
from typing import Dict, Any

from ..components.artifact_card import ArtifactCard
from ..components.civilization_badge import CivilizationBadge
from ..components.timeline_widget import TimelineWidget


def show_home_page() -> None:
    """Display the home page."""
    st.title("🏺 Welcome to ArchaeoVault")
    st.markdown("**Your AI-Powered Archaeological Research Platform**")
    
    # Hero section
    st.markdown("""
    ArchaeoVault is a comprehensive archaeological research platform that leverages 
    advanced AI agents to analyze artifacts, research civilizations, plan excavations, 
    and generate professional reports. Our multi-agent AI system provides specialized 
    expertise across all aspects of archaeological research.
    """)
    
    # Feature overview
    st.header("🌟 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🏺 Artifact Analysis
        - AI-powered visual analysis
        - Material identification
        - Cultural context analysis
        - Dating estimation
        """)
    
    with col2:
        st.markdown("""
        ### ⏳ Carbon Dating
        - Scientific C-14 calculations
        - Calibration curves
        - Error analysis
        - Confidence intervals
        """)
    
    with col3:
        st.markdown("""
        ### 🌍 Civilization Research
        - Deep cultural analysis
        - Geographic research
        - Timeline building
        - Achievement mapping
        """)
    
    # Quick stats
    st.header("📊 Platform Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Artifacts Analyzed", "1,247", "23")
    
    with col2:
        st.metric("Civilizations Researched", "89", "5")
    
    with col3:
        st.metric("Excavations Planned", "34", "8")
    
    with col4:
        st.metric("Reports Generated", "156", "12")
    
    # Recent activity
    st.header("🕒 Recent Activity")
    
    # Mock recent activity data
    recent_activities = [
        {
            "type": "artifact_analysis",
            "title": "Ancient Greek Amphora Analysis",
            "timestamp": "2 hours ago",
            "status": "completed"
        },
        {
            "type": "civilization_research",
            "title": "Minoan Civilization Research",
            "timestamp": "4 hours ago",
            "status": "in_progress"
        },
        {
            "type": "excavation_planning",
            "title": "Site A-47 Excavation Plan",
            "timestamp": "1 day ago",
            "status": "completed"
        },
        {
            "type": "report_generation",
            "title": "Q3 2024 Excavation Report",
            "timestamp": "2 days ago",
            "status": "published"
        }
    ]
    
    for activity in recent_activities:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{activity['title']}**")
            
            with col2:
                status_color = "🟢" if activity['status'] == "completed" else "🟡"
                st.write(f"{status_color} {activity['status'].title()}")
            
            with col3:
                st.write(activity['timestamp'])
            
            st.divider()
    
    # Quick actions
    st.header("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏺 Analyze New Artifact", use_container_width=True):
            st.session_state.selected_page = "artifact_analyzer"
            st.rerun()
    
    with col2:
        if st.button("🌍 Research Civilization", use_container_width=True):
            st.session_state.selected_page = "civilizations"
            st.rerun()
    
    with col3:
        if st.button("⛏️ Plan Excavation", use_container_width=True):
            st.session_state.selected_page = "excavation_planner"
            st.rerun()
    
    # Featured artifacts
    st.header("🏺 Featured Artifacts")
    
    # Mock featured artifacts
    featured_artifacts = [
        {
            "id": "art_001",
            "name": "Minoan Snake Goddess",
            "period": "Bronze Age",
            "culture": "Minoan",
            "material": "Ceramic",
            "confidence": 0.95,
            "image_url": "https://via.placeholder.com/200x200?text=Minoan+Snake+Goddess"
        },
        {
            "id": "art_002",
            "name": "Roman Legionary Helmet",
            "period": "Classical",
            "culture": "Roman",
            "material": "Bronze",
            "confidence": 0.88,
            "image_url": "https://via.placeholder.com/200x200?text=Roman+Helmet"
        },
        {
            "id": "art_003",
            "name": "Egyptian Scarab",
            "period": "Classical",
            "culture": "Egyptian",
            "material": "Stone",
            "confidence": 0.92,
            "image_url": "https://via.placeholder.com/200x200?text=Egyptian+Scarab"
        }
    ]
    
    for artifact in featured_artifacts:
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image(artifact["image_url"], width=100)
            
            with col2:
                st.write(f"**{artifact['name']}**")
                st.write(f"**Period:** {artifact['period']} | **Culture:** {artifact['culture']}")
                st.write(f"**Material:** {artifact['material']} | **Confidence:** {artifact['confidence']:.1%}")
                
                if st.button(f"View Details", key=f"view_{artifact['id']}"):
                    st.session_state.selected_artifact = artifact['id']
                    st.session_state.selected_page = "artifact_analyzer"
                    st.rerun()
            
            st.divider()
    
    # AI Agent Status
    st.header("🤖 AI Agent Status")
    
    # Get agent status from session state
    if "services" in st.session_state:
        ai_orchestrator = st.session_state.services.get("ai_orchestrator")
        if ai_orchestrator:
            agent_status = ai_orchestrator.get_agent_status()
            
            for agent_type, status in agent_status.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    agent_name = agent_type.replace("_", " ").title()
                    st.write(f"**{agent_name}**")
                
                with col2:
                    status_icon = "🟢" if status["available"] else "🔴"
                    st.write(f"{status_icon} {'Online' if status['available'] else 'Offline'}")
                
                with col3:
                    st.write(f"Requests: {status['total_requests']}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>ArchaeoVault v1.0.0 | Built with ❤️ for the archaeological community</p>
        <p>Powered by AI agents and modern web technologies</p>
    </div>
    """, unsafe_allow_html=True)
