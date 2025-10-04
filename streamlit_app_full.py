#!/usr/bin/env python3
"""
Clean, minimal Streamlit app for ArchaeoVault.
"""

import streamlit as st
import sys
import time
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Page configuration
st.set_page_config(
    page_title="ArchaeoVault",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, minimal CSS
st.markdown("""
<style>
    /* Reset */
    * { box-sizing: border-box; }
    
    .stApp {
        background: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main { padding: 0; }
    
    .stApp .main .block-container {
        padding: 0 !important;
        max-width: none !important;
    }
    
    .stApp .main .block-container > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Hide the specific DOM element */
    html > body > div > div:nth-child(1) > div:nth-child(1) > div > div > div > section > div:nth-child(1) > div > div:nth-child(2) > div > div:nth-child(1) > div > div > div {
        display: none !important;
    }
    
    /* Main container */
    .main-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        min-height: calc(100vh - 2rem);
    }
    
    /* Header */
    .main-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        color: #1e293b;
    }
    
    .main-subtitle {
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
        color: #64748b;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Cards */
    .feature-card, .stat-card, .form-container, .analysis-section {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .feature-card h3, .analysis-section h3 {
        color: #1e293b;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.25rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: background 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #2563eb;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        background: white;
        color: #1e293b;
        transition: border-color 0.2s ease;
        font-size: 0.9rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }
    
    /* Stats */
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: #3b82f6;
    }
    
    .stat-label {
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.5rem 0 0 0;
        color: #64748b;
    }
    
    /* Artifacts */
    .artifact-item {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        cursor: pointer;
        transition: border-color 0.2s ease;
    }
    
    .artifact-item:hover {
        border-color: #3b82f6;
    }
    
    .artifact-name {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .artifact-meta {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.5;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .main-title {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "home"

if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {
        "theme": "light",
        "language": "english",
        "notifications": True
    }

def main():
    """Main application function."""
    # Main container wrapper
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # Clean header
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">ArchaeoVault</h1>
            <p class="main-subtitle">AI-Powered Archaeological Research Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Clean sidebar
        with st.sidebar:
            st.markdown("### Navigation")
            
            # Simple navigation
            pages = {
                "Home": "home",
                "Artifact Analyzer": "artifact_analyzer", 
                "Carbon Dating": "carbon_dating",
                "Civilizations": "civilizations",
                "Excavation Planner": "excavation_planner",
                "Report Generator": "report_generator",
                "Research Assistant": "research_assistant"
            }
            
            for page_name, page_key in pages.items():
                if st.button(page_name, key=f"nav_{page_key}", width='stretch'):
                    st.session_state.selected_page = page_key
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### Settings")
            
            # Simple settings
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], key="theme_selector")
            language = st.selectbox("Language", ["English", "Spanish", "French", "German"], key="language_selector")
            notifications = st.checkbox("Notifications", value=True, key="notifications")
        
        # Main content area
        if st.session_state.selected_page == "home":
            show_home_page()
        elif st.session_state.selected_page == "artifact_analyzer":
            show_artifact_analyzer()
        elif st.session_state.selected_page == "carbon_dating":
            show_carbon_dating()
        elif st.session_state.selected_page == "civilizations":
            show_civilizations()
        elif st.session_state.selected_page == "excavation_planner":
            show_excavation_planner()
        elif st.session_state.selected_page == "report_generator":
            show_report_generator()
        elif st.session_state.selected_page == "research_assistant":
            show_research_assistant()
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_home_page():
    """Show the home page."""
    st.markdown("## Welcome to ArchaeoVault")
    st.markdown("Your AI-powered archaeological research platform.")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">1,247</div>
            <div class="stat-label">Artifacts Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">89</div>
            <div class="stat-label">Excavations Planned</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">156</div>
            <div class="stat-label">Reports Generated</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">23</div>
            <div class="stat-label">Civilizations Studied</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("## Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
    <div class="feature-card">
            <h3>Recent Artifacts</h3>
            <div class="artifact-item">
                <div class="artifact-name">Roman Pottery Fragment</div>
                <div class="artifact-meta">Discovered: 2024-01-15 | Site: Pompeii</div>
            </div>
            <div class="artifact-item">
                <div class="artifact-name">Bronze Age Axe Head</div>
                <div class="artifact-meta">Discovered: 2024-01-14 | Site: Stonehenge</div>
            </div>
    </div>
    """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>Quick Actions</h3>
            <p>Start analyzing a new artifact or plan your next excavation.</p>
            <br>
            <button class="stButton">Analyze Artifact</button>
            <br><br>
            <button class="stButton">Plan Excavation</button>
        </div>
        """, unsafe_allow_html=True)
    
def show_artifact_analyzer():
    """Show the artifact analyzer page."""
    st.markdown("## Artifact Analyzer")
    st.markdown("Upload an image of an artifact for AI-powered analysis.")
    
    # Upload area
    uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Artifact", width='stretch')
        
        # Analysis form
        st.markdown("### Analysis Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            material = st.selectbox("Suspected Material", ["Ceramic", "Metal", "Stone", "Wood", "Unknown"])
            period = st.selectbox("Suspected Period", ["Prehistoric", "Ancient", "Medieval", "Modern", "Unknown"])
        
        with col2:
            origin = st.text_input("Suspected Origin", placeholder="e.g., Roman, Greek, Egyptian")
            condition = st.selectbox("Condition", ["Excellent", "Good", "Fair", "Poor"])
        
        if st.button("Analyze Artifact", type="primary"):
            with st.spinner("Analyzing artifact..."):
                time.sleep(2)  # Simulate analysis
                
                st.success("Analysis complete!")
                
                # Display results
                st.markdown("### Analysis Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Material:** Ceramic")
                    st.markdown("**Period:** Roman (1st-2nd century CE)")
                
                with col2:
                    st.markdown("**Origin:** Pompeii, Italy")
                    st.markdown("**Condition:** Good")
                
                with col3:
                    st.markdown("**Confidence:** 87%")
                    st.markdown("**Rarity:** Common")

def show_carbon_dating():
    """Show the carbon dating page."""
    st.markdown("## Carbon Dating Calculator")
    st.markdown("Calculate C-14 dating for archaeological samples.")
    
    # Input form
    st.markdown("### Sample Information")
        
    col1, col2 = st.columns(2)
    
    with col1:
        sample_name = st.text_input("Sample Name", placeholder="e.g., Wood fragment from Site A")
        c14_ratio = st.number_input("C-14 Ratio", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    
    with col2:
        sample_type = st.selectbox("Sample Type", ["Wood", "Charcoal", "Bone", "Shell", "Other"])
        lab_uncertainty = st.number_input("Lab Uncertainty (%)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    
    if st.button("Calculate Dating", type="primary"):
        with st.spinner("Calculating C-14 dating..."):
            time.sleep(1)  # Simulate calculation
            
            st.success("Dating calculation complete!")
            
            # Display results
            st.markdown("### Dating Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Age:** 2,350 ± 50 years")
                st.markdown("**Calibrated Age:** 400-200 BCE")
            
            with col2:
                st.markdown("**Confidence:** 95%")
                st.markdown("**Method:** C-14 AMS")
            
            with col3:
                st.markdown("**Period:** Iron Age")
                st.markdown("**Culture:** Celtic")

def show_civilizations():
    """Show the civilizations page."""
    st.markdown("## Civilizations Database")
    st.markdown("Explore archaeological civilizations and cultures.")
    
    # Search and filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("Search", placeholder="e.g., Roman, Greek, Egyptian")
    
    with col2:
        time_period = st.selectbox("Time Period", ["All", "Prehistoric", "Ancient", "Medieval", "Modern"])
    
    with col3:
        region = st.selectbox("Region", ["All", "Europe", "Asia", "Africa", "Americas", "Oceania"])
    
    # Display civilizations
    st.markdown("### Civilizations")
    
    civilizations = [
        {"name": "Roman Empire", "period": "753 BCE - 476 CE", "region": "Europe", "description": "Ancient Roman civilization"},
        {"name": "Ancient Greece", "period": "800 BCE - 146 BCE", "region": "Europe", "description": "Classical Greek civilization"},
        {"name": "Ancient Egypt", "period": "3100 BCE - 30 BCE", "region": "Africa", "description": "Pharaonic Egyptian civilization"},
        {"name": "Maya Civilization", "period": "2000 BCE - 900 CE", "region": "Americas", "description": "Mesoamerican civilization"},
        {"name": "Han Dynasty", "period": "206 BCE - 220 CE", "region": "Asia", "description": "Chinese imperial dynasty"}
    ]
    
    for civ in civilizations:
        st.markdown(f"""
        <div class="artifact-item">
            <div class="artifact-name">{civ['name']}</div>
            <div class="artifact-meta">{civ['period']} | {civ['region']}</div>
            <div class="artifact-meta">{civ['description']}</div>
        </div>
        """, unsafe_allow_html=True)
    
def show_excavation_planner():
    """Show the excavation planner page."""
    st.markdown("## Excavation Planner")
    st.markdown("Plan and manage archaeological excavations.")
    
    # Site information
    st.markdown("### Site Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        site_name = st.text_input("Site Name", placeholder="e.g., Pompeii Excavation Site")
        location = st.text_input("Location", placeholder="e.g., Naples, Italy")
    
    with col2:
        site_type = st.selectbox("Site Type", ["Settlement", "Burial", "Temple", "Fortress", "Other"])
        estimated_period = st.text_input("Estimated Period", placeholder="e.g., Roman (1st century CE)")
    
    # Excavation parameters
    st.markdown("### Excavation Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("Start Date")
        duration = st.number_input("Duration (weeks)", min_value=1, max_value=52, value=4)
    
    with col2:
        team_size = st.number_input("Team Size", min_value=1, max_value=100, value=10)
        budget = st.number_input("Budget (USD)", min_value=1000, max_value=1000000, value=50000)
    
    with col3:
        equipment = st.multiselect("Equipment", ["Shovels", "Trowels", "Brushes", "Screens", "GPS", "Photography"])
    
    if st.button("Create Excavation Plan", type="primary"):
        with st.spinner("Creating excavation plan..."):
            time.sleep(2)  # Simulate planning
            
            st.success("Excavation plan created!")
            
            # Display plan
            st.markdown("### Excavation Plan")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Site:** " + site_name)
                st.markdown("**Location:** " + location)
                st.markdown("**Type:** " + site_type)
                st.markdown("**Period:** " + estimated_period)
            
            with col2:
                st.markdown("**Start Date:** " + str(start_date))
                st.markdown("**Duration:** " + str(duration) + " weeks")
                st.markdown("**Team Size:** " + str(team_size))
                st.markdown("**Budget:** $" + str(budget))

def show_report_generator():
    """Show the report generator page."""
    st.markdown("## Report Generator")
    st.markdown("Generate professional archaeological reports.")
    
    # Report type selection
    report_type = st.selectbox("Report Type", [
        "Excavation Report",
        "Artifact Analysis Report", 
        "Site Survey Report",
        "Research Paper",
        "Cultural Assessment"
    ])
    
    # Report parameters
    st.markdown("### Report Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Report Title", placeholder="e.g., Excavation Report - Site A")
        author = st.text_input("Author", placeholder="e.g., Dr. John Smith")
    
    with col2:
        date = st.date_input("Report Date")
        site = st.text_input("Site/Project", placeholder="e.g., Pompeii Excavation")
    
    # Content sections
    st.markdown("### Content Sections")
    
    sections = st.multiselect("Include Sections", [
        "Executive Summary",
        "Introduction",
        "Methodology", 
        "Findings",
        "Analysis",
        "Conclusions",
        "Recommendations",
        "Bibliography"
    ])
    
    # Additional options
    st.markdown("### Additional Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_images = st.checkbox("Include Images", value=True)
        include_maps = st.checkbox("Include Maps", value=True)
    
    with col2:
        include_charts = st.checkbox("Include Charts", value=True)
        include_tables = st.checkbox("Include Tables", value=True)
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            time.sleep(3)  # Simulate report generation
            
            st.success("Report generated successfully!")
            
            # Display report preview
            st.markdown("### Report Preview")
            st.markdown(f"**Title:** {title}")
            st.markdown(f"**Author:** {author}")
            st.markdown(f"**Date:** {date}")
            st.markdown(f"**Site:** {site}")
            st.markdown(f"**Type:** {report_type}")
            
            st.markdown("**Sections Included:**")
            for section in sections:
                st.markdown(f"- {section}")
            
            st.markdown("**Additional Features:**")
            if include_images:
                st.markdown("- Images")
            if include_maps:
                st.markdown("- Maps")
            if include_charts:
                st.markdown("- Charts")
            if include_tables:
                st.markdown("- Tables")

def show_research_assistant():
    """Show the research assistant page."""
    st.markdown("## Research Assistant")
    st.markdown("Get AI-powered assistance with your archaeological research.")
    
    # Research query
    st.markdown("### Research Query")
    
    query = st.text_area("What would you like to research?", 
                        placeholder="e.g., Tell me about Roman pottery techniques in Pompeii",
                        height=100)
    
    # Research parameters
    st.markdown("### Research Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        research_type = st.selectbox("Research Type", [
            "General Information",
            "Specific Artifact",
            "Historical Context",
            "Cultural Analysis",
            "Methodology"
        ])
        
        time_period = st.selectbox("Time Period", [
            "All Periods",
            "Prehistoric",
            "Ancient",
            "Medieval", 
            "Modern"
        ])
    
    with col2:
        region = st.selectbox("Region", [
            "All Regions",
            "Europe",
            "Asia",
            "Africa",
            "Americas",
            "Oceania"
        ])
        
        detail_level = st.selectbox("Detail Level", [
            "Brief",
            "Moderate",
            "Detailed",
            "Comprehensive"
        ])
    
    if st.button("Start Research", type="primary"):
        with st.spinner("Conducting research..."):
            time.sleep(2)  # Simulate research
            
            st.success("Research complete!")
            
            # Display results
            st.markdown("### Research Results")
            
            st.markdown("**Query:** " + query)
            st.markdown("**Type:** " + research_type)
            st.markdown("**Period:** " + time_period)
            st.markdown("**Region:** " + region)
            st.markdown("**Detail Level:** " + detail_level)
            
            st.markdown("**Findings:**")
            st.markdown("Based on your query, here are the key findings:")
            st.markdown("- Roman pottery in Pompeii was primarily made using local clay")
            st.markdown("- Common techniques included wheel-throwing and hand-building")
            st.markdown("- Decorative methods included red-figure and black-figure painting")
            st.markdown("- Pottery was used for both domestic and commercial purposes")
            
            st.markdown("**Sources:**")
            st.markdown("- Archaeological excavations at Pompeii (1860-present)")
            st.markdown("- Roman pottery studies by various scholars")
            st.markdown("- Museum collections and catalogues")

if __name__ == "__main__":
    main()