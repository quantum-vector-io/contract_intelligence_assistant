"""
Interactive Dashboard for Contract Intelligence Assistant.

This module provides a comprehensive dashboard interface using Streamlit
for real-time analytics, metrics visualization, and system monitoring.
The dashboard displays document statistics, financial metrics, partner
analytics, and system health in an intuitive and interactive format.

Features:
- Real-time metrics and KPIs
- Interactive charts and visualizations
- System health monitoring
- Partner and document analytics
- Financial discrepancy tracking
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
DASHBOARD_TITLE = "📊 Contract Intelligence Dashboard"
REFRESH_INTERVAL = 30  # seconds


class DashboardAPI:
    """API client for dashboard data endpoints."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    def get_comprehensive_data(self) -> Optional[Dict[str, Any]]:
        """Get all dashboard data in a single request."""
        try:
            response = requests.get(f"{self.base_url}/dashboard/comprehensive", timeout=10)
            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                st.error(f"Failed to fetch dashboard data: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"API connection error: {e}")
            return None
    
    def get_quick_stats(self) -> Optional[Dict[str, Any]]:
        """Get quick summary statistics."""
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats/summary", timeout=5)
            if response.status_code == 200:
                return response.json().get("data", {})
            return None
        except requests.exceptions.RequestException:
            return None
    
    def refresh_cache(self) -> bool:
        """Refresh dashboard cache."""
        try:
            response = requests.post(f"{self.base_url}/dashboard/refresh", timeout=15)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


def init_dashboard_styling():
    """Initialize dashboard styling without page config."""
    # Custom CSS for better styling
    st.markdown("""
    <style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Metric cards styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        color: white;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Health indicators */
    .health-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .health-healthy { 
        background: linear-gradient(135deg, #4CAF50, #45a049);
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
    }
    .health-degraded { 
        background: linear-gradient(135deg, #FF9800, #F57C00);
        box-shadow: 0 0 20px rgba(255, 152, 0, 0.3);
    }
    .health-unhealthy { 
        background: linear-gradient(135deg, #F44336, #D32F2F);
        box-shadow: 0 0 20px rgba(244, 67, 54, 0.3);
    }
    
    /* Revolutionary Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        padding: 10px 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 70px;
        white-space: pre-wrap;
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        border: 2px solid transparent;
        border-radius: 16px;
        padding: 15px 25px;
        font-weight: 600;
        font-size: 16px;
        color: #495057;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 4px 6px rgba(0, 0, 0, 0.07),
            0 1px 3px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    /* Tab hover effect */
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 8px 25px rgba(0, 0, 0, 0.15),
            0 4px 6px rgba(0, 0, 0, 0.1);
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 2px solid #dee2e6;
    }
    
    /* Active tab styling */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 2px solid #5a67d8 !important;
        transform: translateY(-3px);
        box-shadow: 
            0 12px 40px rgba(102, 126, 234, 0.4),
            0 8px 16px rgba(102, 126, 234, 0.2);
        z-index: 10;
    }
    
    /* Active tab hover effect - ВАЖЛИВО: перевизначаємо hover для активної табки */
    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
        color: white !important;
        border: 2px solid #4c51bf !important;
        transform: translateY(-4px);
        box-shadow: 
            0 16px 50px rgba(102, 126, 234, 0.5),
            0 12px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Active tab before pseudo-element for glow effect */
    .stTabs [aria-selected="true"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
        border-radius: 14px;
        pointer-events: none;
    }
    
    /* Забезпечуємо що текст в активній табці завжди білий */
    .stTabs [aria-selected="true"] * {
        color: white !important;
    }
    
    /* Забезпечуємо що текст в активній табці при hover залишається білий */
    .stTabs [aria-selected="true"]:hover * {
        color: white !important;
    }
    
    /* Tab content container */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 30px 0;
        background: transparent;
    }
    
    /* Custom styling for the emoji icons in tabs */
    .tab-icon {
        font-size: 24px;
        margin-right: 8px;
        display: inline-block;
        line-height: 1;
    }
    
    /* Streamlit metrics enhancement */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 1px solid #e9ecef;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: transform 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Dashboard title styling */
    .dashboard-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Animation for tab transitions */
    @keyframes tabGlow {
        0% { box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6); }
        100% { box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4); }
    }
    
    .stTabs [aria-selected="true"] {
        animation: tabGlow 2s ease-in-out infinite;
    }
    
    /* Enhanced container styling */
    .element-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Plotly chart containers */
    .js-plotly-plot {
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07) !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07) !important;
    }
    
    /* Info boxes styling */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    
    /* Success styling */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border-left: 4px solid #28a745;
    }
    
    /* Info styling */
    .stInfo {
        background: linear-gradient(135deg, #cce7ff, #b3d9ff);
        border-left: 4px solid #17a2b8;
    }
    
    /* Error styling */
    .stError {
        background: linear-gradient(135deg, #f8d7da, #f1aeb5);
        border-left: 4px solid #dc3545;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        border-radius: 12px !important;
        border: 1px solid #dee2e6;
    }
    
    /* Додаткові стилі для табів - щоб текст завжди був видимий */
    .stTabs [data-baseweb="tab"] p {
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    
    .stTabs [data-baseweb="tab"] strong {
        font-size: 14px !important;
        display: block !important;
    }
    
    .stTabs [data-baseweb="tab"] em {
        font-size: 12px !important;
        opacity: 0.8 !important;
        font-style: normal !important;
    }
    
    /* Неактивні таби - темний текст */
    .stTabs [aria-selected="false"] {
        color: #495057 !important;
    }
    
    .stTabs [aria-selected="false"] * {
        color: #495057 !important;
    }
    
    /* При hover на неактивні таби */
    .stTabs [aria-selected="false"]:hover {
        color: #212529 !important;
    }
    
    .stTabs [aria-selected="false"]:hover * {
        color: #212529 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def display_health_indicator(status: str) -> str:
    """Display health status with colored indicator."""
    health_colors = {
        "healthy": "health-healthy",
        "green": "health-healthy",
        "degraded": "health-degraded", 
        "yellow": "health-degraded",
        "unhealthy": "health-unhealthy",
        "red": "health-unhealthy"
    }
    
    color_class = health_colors.get(status.lower(), "health-unhealthy")
    return f'<span class="health-indicator {color_class}"></span>{status.title()}'


def create_metrics_row(overview_data: Dict[str, Any]):
    """Create top-level metrics row."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_docs = overview_data.get("total_documents", 0)
        st.metric(
            label="📄 Total Documents",
            value=f"{total_docs:,}",
            help="Total number of indexed documents"
        )
    
    with col2:
        partner_stats = overview_data.get("partner_statistics", {})
        total_partners = partner_stats.get("total_partners", 0)
        st.metric(
            label="🤝 Partners", 
            value=f"{total_partners:,}",
            help="Number of unique partners in the system"
        )
    
    with col3:
        partners_with_docs = partner_stats.get("partners_with_documents", 0)
        coverage = partner_stats.get("coverage_percentage", 0)
        st.metric(
            label="📊 Partner Coverage",
            value=f"{coverage:.1f}%",
            delta=f"{partners_with_docs} partners",
            help="Percentage of partners with complete documentation"
        )
    
    with col4:
        doc_types = overview_data.get("document_types", {})
        contract_count = doc_types.get("contract", 0)
        payout_count = doc_types.get("payout_report", 0)
        st.metric(
            label="📋 Document Types",
            value=f"{len(doc_types)}",
            delta=f"Contracts: {contract_count}, Reports: {payout_count}",
            help="Number of different document types indexed"
        )


def create_document_analytics_tab(overview_data: Dict[str, Any]):
    """Create document analytics visualizations."""
    # Removed redundant st.subheader since we have gradient header now
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Document types pie chart
        doc_types = overview_data.get("document_types", {})
        if doc_types:
            fig_pie = px.pie(
                values=list(doc_types.values()),
                names=list(doc_types.keys()),
                title="Document Types Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No document type data available")
    
    with col2:
        # Top partners bar chart
        partner_stats = overview_data.get("partner_statistics", {})
        top_partners = partner_stats.get("top_partners", {})
        
        if top_partners:
            partners_df = pd.DataFrame([
                {"Partner": k, "Documents": v} 
                for k, v in list(top_partners.items())[:10]
            ])
            
            fig_bar = px.bar(
                partners_df,
                x="Documents",
                y="Partner",
                orientation="h",
                title="Top Partners by Document Count",
                color="Documents",
                color_continuous_scale="Blues"
            )
            fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No partner data available")
    
    # Recent activity
    st.subheader("📅 Recent Document Activity")
    recent_activity = overview_data.get("recent_activity", [])
    
    if recent_activity:
        # Convert to DataFrame for better display
        activity_df = pd.DataFrame(recent_activity[:20])  # Show last 20
        
        if not activity_df.empty:
            # Format created_at if it exists
            if 'created_at' in activity_df.columns:
                activity_df['created_at'] = pd.to_datetime(activity_df['created_at'], errors='coerce')
                activity_df = activity_df.sort_values('created_at', ascending=False, na_position='last')
                activity_df['created_at'] = activity_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
            
            # Display as table with custom formatting
            st.dataframe(
                activity_df[['title', 'type', 'partner', 'created_at']].rename(columns={
                    'title': 'Document Title',
                    'type': 'Type',
                    'partner': 'Partner',
                    'created_at': 'Created'
                }),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No recent activity data available")
    else:
        st.info("No recent document activity found")


def create_financial_analytics_tab(financial_data: Dict[str, Any]):
    """Create financial analytics visualizations."""
    # Removed redundant st.subheader since we have gradient header now
    
    # Financial document metrics
    financial_docs = financial_data.get("financial_documents", {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_financial = financial_docs.get("total_financial_documents", 0)
        st.metric("💼 Financial Documents", f"{total_financial:,}")
    
    with col2:
        avg_docs = financial_docs.get("avg_docs_per_partner", 0)
        st.metric("📊 Avg Docs/Partner", f"{avg_docs:.1f}")
    
    with col3:
        commission_analysis = financial_data.get("commission_analysis", {})
        commission_partners = commission_analysis.get("partners_with_commission_data", 0)
        st.metric("🤝 Partners w/ Commission", f"{commission_partners}")
    
    # Partner financial breakdown
    partner_breakdown = financial_docs.get("partner_breakdown", {})
    if partner_breakdown:
        st.subheader("📈 Financial Documents by Partner")
        
        # Create horizontal bar chart
        partners_df = pd.DataFrame([
            {"Partner": k, "Financial Documents": v}
            for k, v in list(partner_breakdown.items())[:15]
        ])
        
        fig = px.bar(
            partners_df,
            x="Financial Documents",
            y="Partner",
            orientation="h",
            title="Partners with Financial Document Coverage",
            color="Financial Documents",
            color_continuous_scale="Greens"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    
    # Commission structure analysis
    commission_types = commission_analysis.get("commission_structure_types", {})
    if commission_types:
        st.subheader("🏗️ Commission Structure Types")
        
        col1, col2 = st.columns(2)
        with col1:
            # Pie chart for commission types
            fig_commission = px.pie(
                values=list(commission_types.values()),
                names=list(commission_types.keys()),
                title="Commission Structure Distribution"
            )
            st.plotly_chart(fig_commission, use_container_width=True)
        
        with col2:
            # Display commission metrics
            for structure_type, count in commission_types.items():
                st.metric(f"{structure_type.title()} Structures", f"{count}")
    
    # Discrepancy statistics (placeholder for future implementation)
    st.subheader("🔍 Discrepancy Analysis")
    discrepancy_stats = financial_data.get("discrepancy_statistics", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_analyses = discrepancy_stats.get("total_analyses_performed", 0)
        st.metric("🔎 Total Analyses", f"{total_analyses:,}")
    with col2:
        discrepancies = discrepancy_stats.get("discrepancies_detected", 0)
        st.metric("⚠️ Discrepancies Found", f"{discrepancies:,}")
    with col3:
        discrepancy_rate = discrepancy_stats.get("discrepancy_rate", 0.0)
        st.metric("📊 Discrepancy Rate", f"{discrepancy_rate:.1f}%")
    with col4:
        avg_amount = discrepancy_stats.get("avg_discrepancy_amount", 0.0)
        st.metric("💲 Avg Discrepancy", f"${avg_amount:,.2f}")


def create_system_health_tab(health_data: Dict[str, Any]):
    """Create system health monitoring visualizations."""
    # Removed redundant st.subheader since we have gradient header now
    
    # Overall health status
    overall_status = health_data.get("overall_status", "unknown")
    last_checked = health_data.get("last_checked", "Never")
    
    col1, col2 = st.columns(2)
    with col1:
        health_html = display_health_indicator(overall_status)
        st.markdown(f"**Overall Status:** {health_html}", unsafe_allow_html=True)
    with col2:
        st.write(f"**Last Checked:** {last_checked}")
    
    # Service health breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 OpenSearch Health")
        opensearch_health = health_data.get("opensearch", {})
        opensearch_status = opensearch_health.get("status", "unknown")
        
        st.markdown(display_health_indicator(opensearch_status), unsafe_allow_html=True)
        
        # OpenSearch metrics
        if opensearch_status in ["green", "yellow"]:
            cluster_name = opensearch_health.get("cluster_name", "N/A")
            node_count = opensearch_health.get("number_of_nodes", 0)
            st.write(f"**Cluster:** {cluster_name}")
            st.write(f"**Nodes:** {node_count}")
    
    with col2:
        st.subheader("🚀 API Health")
        api_health = health_data.get("api", {})
        api_status = api_health.get("status", "unknown")
        
        st.markdown(display_health_indicator(api_status), unsafe_allow_html=True)
        
        # API metrics
        service = api_health.get("service", "N/A")
        version = api_health.get("version", "N/A")
        st.write(f"**Service:** {service}")
        st.write(f"**Version:** {version}")
    
    # Performance metrics
    st.subheader("📈 Performance Metrics")
    performance = health_data.get("performance", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_indexed = performance.get("total_documents_indexed", 0)
        st.metric("📄 Documents Indexed", f"{total_indexed:,}")
    
    with col2:
        index_size_mb = performance.get("index_size_mb", 0)
        st.metric("💾 Index Size", f"{index_size_mb:.1f} MB")
    
    with col3:
        avg_doc_size = performance.get("avg_document_size_kb", 0)
        st.metric("📊 Avg Doc Size", f"{avg_doc_size:.1f} KB")
    
    with col4:
        index_size_bytes = performance.get("index_size_bytes", 0)
        efficiency = (total_indexed / max(index_size_bytes / (1024*1024), 1)) if index_size_bytes > 0 else 0
        st.metric("⚡ Index Efficiency", f"{efficiency:.1f} docs/MB")


def create_query_analytics_tab(query_data: Dict[str, Any]):
    """Create query analytics visualizations."""
    # Removed redundant st.subheader since we have gradient header now
    
    # Query metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_queries = query_data.get("total_queries_today", 0)
        st.metric("📊 Queries Today", f"{total_queries:,}")
    
    with col2:
        avg_response = query_data.get("avg_response_time_ms", 0)
        st.metric("⚡ Avg Response Time", f"{avg_response:.0f}ms")
    
    with col3:
        success_rate = query_data.get("query_success_rate", 0)
        st.metric("✅ Success Rate", f"{success_rate:.1f}%")
    
    with col4:
        peak_hours = query_data.get("peak_usage_hours", [])
        peak_display = ", ".join(map(str, peak_hours[:3])) if peak_hours else "N/A"
        st.metric("🕐 Peak Hours", peak_display)
    
    # Query types
    common_queries = query_data.get("most_common_query_types", [])
    if common_queries:
        st.subheader("🔥 Most Common Query Types")
        
        # Create a simple bar chart for query types
        query_df = pd.DataFrame([
            {"Query Type": item.get("type", "Unknown"), "Count": item.get("count", 0)}
            for item in common_queries[:10]
        ])
        
        if not query_df.empty:
            fig = px.bar(
                query_df,
                x="Count",
                y="Query Type",
                orientation="h",
                title="Query Type Distribution",
                color="Count",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No query analytics data available yet")


def create_dashboard_sidebar(api_client: DashboardAPI):
    """Create dashboard sidebar with controls and quick stats."""
    st.sidebar.title("🎛️ Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh", value=False)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 10, 300, REFRESH_INTERVAL)
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now", type="primary"):
        with st.spinner("Refreshing data..."):
            success = api_client.refresh_cache()
            if success:
                st.sidebar.success("Cache refreshed successfully!")
                st.rerun()
            else:
                st.sidebar.error("Failed to refresh cache")
    
    # Quick stats in sidebar
    st.sidebar.subheader("📊 Quick Stats")
    quick_stats = api_client.get_quick_stats()
    
    if quick_stats:
        st.sidebar.metric("Documents", f"{quick_stats.get('total_documents', 0):,}")
        st.sidebar.metric("Partners", f"{quick_stats.get('total_partners', 0):,}")
        
        health_status = quick_stats.get('system_health', 'unknown')
        health_html = display_health_indicator(health_status)
        st.sidebar.markdown(f"**Health:** {health_html}", unsafe_allow_html=True)
    
    # System info
    st.sidebar.subheader("ℹ️ System Info")
    st.sidebar.write(f"**API Base:** {API_BASE_URL}")
    st.sidebar.write(f"**Updated:** {datetime.now().strftime('%H:%M:%S')}")
    
    return auto_refresh, refresh_interval


def render_dashboard():
    """Render the dashboard as a component (not a standalone app).""" 
    init_dashboard_styling()
    
    # Enhanced dashboard title with gradient styling
    st.markdown("""
    <div class="dashboard-title">
        📊 Contract Intelligence Dashboard
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; font-size: 1.2rem; color: #6c757d;">
        🚀 Real-time analytics for contract intelligence and financial analysis
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize API client
    api_client = DashboardAPI()
    
    # Add dashboard controls in the main area (not sidebar)
    with st.expander("🎛️ Dashboard Controls", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
        with col2:
            refresh_interval = st.slider("Refresh Interval (seconds)", 10, 300, REFRESH_INTERVAL)
        with col3:
            if st.button("🔄 Refresh Now", type="primary"):
                with st.spinner("Refreshing data..."):
                    success = api_client.refresh_cache()
                    if success:
                        st.success("Cache refreshed successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to refresh cache")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()
    
    # Load dashboard data
    with st.spinner("Loading dashboard data..."):
        dashboard_data = api_client.get_comprehensive_data()
    
    if not dashboard_data:
        st.error("Failed to load dashboard data. Please check API connectivity.")
        return
    
    # Extract data sections
    overview_data = dashboard_data.get("document_overview", {})
    financial_data = dashboard_data.get("financial_metrics", {})
    health_data = dashboard_data.get("system_health", {})
    query_data = dashboard_data.get("query_analytics", {})
    
    # Create top metrics row
    create_metrics_row(overview_data)
    
    st.divider()
    
    # Create tabs for different analytics views with enhanced styling
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄\n**Documents**\n*Analytics*", 
        "💰\n**Financial**\n*Metrics*", 
        "🏥\n**System Health**\n*Monitoring*", 
        "🔍\n**Query Analytics**\n*Performance*"
    ])
    
    with tab1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;">
            <h3 style="margin: 0; color: white;">📄 Document Analytics</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Comprehensive analysis of your document portfolio</p>
        </div>
        """, unsafe_allow_html=True)
        create_document_analytics_tab(overview_data)
    
    with tab2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;">
            <h3 style="margin: 0; color: white;">💰 Financial Metrics</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Deep insights into financial performance and discrepancies</p>
        </div>
        """, unsafe_allow_html=True)
        create_financial_analytics_tab(financial_data)
    
    with tab3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;">
            <h3 style="margin: 0; color: white;">🏥 System Health</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Real-time monitoring of system performance and stability</p>
        </div>
        """, unsafe_allow_html=True)
        create_system_health_tab(health_data)
    
    with tab4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                    padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white;">
            <h3 style="margin: 0; color: white;">🔍 Query Analytics</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Performance metrics and usage patterns analysis</p>
        </div>
        """, unsafe_allow_html=True)
        create_query_analytics_tab(query_data)
    
    # Footer with last update info
    st.divider()
    generated_at = dashboard_data.get("generated_at", "Unknown")
    cache_status = dashboard_data.get("cache_status", {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"📅 Last Updated: {generated_at}")
    with col2:
        cached_items = sum(1 for v in cache_status.values() if v)
        st.caption(f"💾 Cache Status: {cached_items}/{len(cache_status)} items cached")


if __name__ == "__main__":
    render_dashboard()