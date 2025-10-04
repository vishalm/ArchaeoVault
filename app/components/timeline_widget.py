"""
Timeline Widget component for ArchaeoVault.

This module provides a reusable component for displaying timeline information
with events, periods, and interactive features.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


class TimelineWidget:
    """A reusable component for displaying timeline information."""
    
    def __init__(self, timeline_data: List[Dict[str, Any]]):
        """Initialize the timeline widget with timeline data.
        
        Args:
            timeline_data: List of dictionaries containing timeline information
        """
        self.timeline_data = timeline_data
    
    def render(self, show_controls: bool = True) -> None:
        """Render the timeline widget.
        
        Args:
            show_controls: Whether to show control buttons
        """
        with st.container():
            # Timeline header
            st.subheader("⏰ Timeline")
            
            # Controls
            if show_controls:
                self._render_controls()
            
            # Timeline visualization
            self._render_timeline()
            
            # Event details
            self._render_event_details()
    
    def _render_controls(self) -> None:
        """Render timeline controls."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Time range filter
            time_range = st.selectbox(
                "Time Range",
                ["All", "Last 1000 years", "Last 5000 years", "Last 10000 years"],
                key="timeline_time_range"
            )
        
        with col2:
            # Event type filter
            event_types = list(set([event.get('type', 'Unknown') for event in self.timeline_data]))
            event_type = st.selectbox(
                "Event Type",
                ["All"] + event_types,
                key="timeline_event_type"
            )
        
        with col3:
            # Sort order
            sort_order = st.selectbox(
                "Sort Order",
                ["Chronological", "Reverse Chronological", "By Type"],
                key="timeline_sort_order"
            )
    
    def _render_timeline(self) -> None:
        """Render the timeline visualization."""
        if not self.timeline_data:
            st.write("No timeline data available.")
            return
        
        # Filter data based on controls
        filtered_data = self._filter_timeline_data()
        
        if not filtered_data:
            st.write("No data matches the selected filters.")
            return
        
        # Create timeline visualization
        df = pd.DataFrame(filtered_data)
        
        # Create timeline plot
        fig = px.timeline(
            df,
            x_start="start_date",
            x_end="end_date",
            y="event",
            color="type",
            title="Timeline of Events"
        )
        
        # Update layout
        fig.update_layout(
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_event_details(self) -> None:
        """Render event details."""
        if not self.timeline_data:
            return
        
        # Filter data based on controls
        filtered_data = self._filter_timeline_data()
        
        if not filtered_data:
            return
        
        # Display event details
        st.subheader("📋 Event Details")
        
        for event in filtered_data:
            with st.expander(f"{event.get('event', 'Unknown Event')} ({event.get('start_date', 'Unknown')} - {event.get('end_date', 'Unknown')})"):
                # Event information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Type:** {event.get('type', 'Unknown')}")
                    st.write(f"**Start Date:** {event.get('start_date', 'Unknown')}")
                    st.write(f"**End Date:** {event.get('end_date', 'Unknown')}")
                    st.write(f"**Duration:** {event.get('duration', 'Unknown')}")
                
                with col2:
                    st.write(f"**Location:** {event.get('location', 'Unknown')}")
                    st.write(f"**Confidence:** {event.get('confidence', 'Unknown')}")
                    st.write(f"**Source:** {event.get('source', 'Unknown')}")
                
                # Description
                if event.get('description'):
                    st.write("**Description:**")
                    st.write(event['description'])
                
                # Additional information
                if event.get('additional_info'):
                    st.write("**Additional Information:**")
                    for key, value in event['additional_info'].items():
                        st.write(f"• **{key}:** {value}")
    
    def _filter_timeline_data(self) -> List[Dict[str, Any]]:
        """Filter timeline data based on controls."""
        filtered = self.timeline_data.copy()
        
        # Time range filter
        time_range = st.session_state.get('timeline_time_range', 'All')
        if time_range != "All":
            current_year = datetime.now().year
            if time_range == "Last 1000 years":
                cutoff_year = current_year - 1000
            elif time_range == "Last 5000 years":
                cutoff_year = current_year - 5000
            elif time_range == "Last 10000 years":
                cutoff_year = current_year - 10000
            else:
                cutoff_year = 0
            
            filtered = [event for event in filtered if self._get_event_year(event) >= cutoff_year]
        
        # Event type filter
        event_type = st.session_state.get('timeline_event_type', 'All')
        if event_type != "All":
            filtered = [event for event in filtered if event.get('type') == event_type]
        
        # Sort order
        sort_order = st.session_state.get('timeline_sort_order', 'Chronological')
        if sort_order == "Chronological":
            filtered.sort(key=lambda x: self._get_event_year(x))
        elif sort_order == "Reverse Chronological":
            filtered.sort(key=lambda x: self._get_event_year(x), reverse=True)
        elif sort_order == "By Type":
            filtered.sort(key=lambda x: x.get('type', ''))
        
        return filtered
    
    def _get_event_year(self, event: Dict[str, Any]) -> int:
        """Get the year of an event for sorting."""
        start_date = event.get('start_date', '')
        if start_date:
            try:
                # Try to extract year from date string
                if 'BCE' in start_date or 'BC' in start_date:
                    year_str = start_date.replace('BCE', '').replace('BC', '').strip()
                    return -int(year_str)
                elif 'CE' in start_date or 'AD' in start_date:
                    year_str = start_date.replace('CE', '').replace('AD', '').strip()
                    return int(year_str)
                else:
                    # Try to parse as integer
                    return int(start_date)
            except (ValueError, TypeError):
                return 0
        return 0


def render_timeline_widget(timeline_data: List[Dict[str, Any]], show_controls: bool = True) -> None:
    """Render a timeline widget component.
    
    Args:
        timeline_data: List of dictionaries containing timeline information
        show_controls: Whether to show control buttons
    """
    widget = TimelineWidget(timeline_data)
    widget.render(show_controls)


def render_simple_timeline(events: List[Dict[str, Any]]) -> None:
    """Render a simple timeline without controls.
    
    Args:
        events: List of event dictionaries
    """
    if not events:
        st.write("No events to display.")
        return
    
    # Create simple timeline
    for i, event in enumerate(events):
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Event date
                st.write(f"**{event.get('date', 'Unknown Date')}**")
            
            with col2:
                # Event description
                st.write(f"**{event.get('title', 'Unknown Event')}**")
                if event.get('description'):
                    st.write(event['description'])
            
            # Add divider between events
            if i < len(events) - 1:
                st.divider()


def render_period_timeline(periods: List[Dict[str, Any]]) -> None:
    """Render a timeline of historical periods.
    
    Args:
        periods: List of period dictionaries
    """
    if not periods:
        st.write("No periods to display.")
        return
    
    # Create period timeline
    df = pd.DataFrame(periods)
    
    fig = px.timeline(
        df,
        x_start="start_date",
        x_end="end_date",
        y="period",
        color="region",
        title="Historical Periods Timeline"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_artifact_timeline(artifacts: List[Dict[str, Any]]) -> None:
    """Render a timeline of artifacts.
    
    Args:
        artifacts: List of artifact dictionaries
    """
    if not artifacts:
        st.write("No artifacts to display.")
        return
    
    # Prepare artifact timeline data
    timeline_data = []
    for artifact in artifacts:
        timeline_data.append({
            "artifact": artifact.get('name', 'Unknown Artifact'),
            "date": artifact.get('discovery_date', 'Unknown Date'),
            "period": artifact.get('period', 'Unknown Period'),
            "culture": artifact.get('culture', 'Unknown Culture'),
            "material": artifact.get('material', 'Unknown Material')
        })
    
    df = pd.DataFrame(timeline_data)
    
    # Create artifact timeline
    fig = px.scatter(
        df,
        x="date",
        y="artifact",
        color="period",
        size="material",
        title="Artifact Discovery Timeline"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_excavation_timeline(excavations: List[Dict[str, Any]]) -> None:
    """Render a timeline of excavations.
    
    Args:
        excavations: List of excavation dictionaries
    """
    if not excavations:
        st.write("No excavations to display.")
        return
    
    # Prepare excavation timeline data
    timeline_data = []
    for excavation in excavations:
        timeline_data.append({
            "excavation": excavation.get('name', 'Unknown Excavation'),
            "start_date": excavation.get('start_date', 'Unknown Start'),
            "end_date": excavation.get('end_date', 'Unknown End'),
            "status": excavation.get('status', 'Unknown Status'),
            "site": excavation.get('site', 'Unknown Site')
        })
    
    df = pd.DataFrame(timeline_data)
    
    # Create excavation timeline
    fig = px.timeline(
        df,
        x_start="start_date",
        x_end="end_date",
        y="excavation",
        color="status",
        title="Excavation Timeline"
    )
    
    st.plotly_chart(fig, use_container_width=True)


