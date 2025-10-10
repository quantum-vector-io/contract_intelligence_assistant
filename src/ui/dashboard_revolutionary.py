"""
Interactive Dashboard for Contract Intelligence Assistant.

This module provides a next-generation dashboard interface using Streamlit
with cutting-edge design, holographic effects, glassmorphism, and advanced
visual elements that create an immersive user experience.

Features:
- Holographic gradient animations
- Glassmorphism UI elements
- 3D transformation effects
- Advanced hover interactions
- Animated background patterns
- Premium typography (Inter font)
- Modern tab design
- Real-time pulsing health indicators
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
DASHBOARD_TITLE = "🚀 Contract Intelligence Dashboard"
REFRESH_INTERVAL = 30  # seconds


class DashboardAPI:
    """API client for dashboard data endpoints with fallback to mock data."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.use_mock_data = False
        
    def _get_mock_data(self) -> Dict[str, Any]:
        """Generate comprehensive mock data for dashboard demonstration."""
        from datetime import datetime, timedelta
        import random
        
        # Current timestamp
        now = datetime.now()
        
        # Generate realistic mock data
        partners = [
            "JustEat UK", "Lieferando DE", "Thuisbezorgd NL", "SkipTheDishes CA",
            "Grubhub US", "DoorDash US", "Uber Eats Global", "Deliveroo UK",
            "Foodpanda Asia", "Zomato India", "Swiggy India", "iFood Brazil"
        ]
        
        # Recent activity data
        recent_activity = []
        for i in range(50):
            activity_date = now - timedelta(days=random.randint(0, 30))
            partner = random.choice(partners)
            doc_types = ["contract", "payout_report", "amendment", "addendum"]
            activity = {
                "title": f"{partner}_{'Contract' if random.choice(doc_types) == 'contract' else 'PayoutReport'}_{activity_date.strftime('%Y-%m-%d')}",
                "type": random.choice(doc_types),
                "partner": partner,
                "created_at": activity_date.isoformat()
            }
            recent_activity.append(activity)
        
        # Partner statistics
        top_partners = {}
        for partner in partners:
            top_partners[partner] = random.randint(5, 45)
        
        return {
            "document_overview": {
                "total_documents": 247,
                "document_types": {
                    "contract": 89,
                    "payout_report": 134,
                    "amendment": 15,
                    "addendum": 9
                },
                "partner_statistics": {
                    "total_partners": len(partners),
                    "partners_with_documents": len(partners) - 1,
                    "coverage_percentage": 91.7,
                    "top_partners": top_partners
                },
                "recent_activity": recent_activity
            },
            "financial_metrics": {
                "financial_documents": {
                    "total_financial_documents": 143,
                    "avg_docs_per_partner": 11.9,
                    "partner_breakdown": {
                        partner: random.randint(5, 25) for partner in partners[:8]
                    }
                },
                "commission_analysis": {
                    "partners_with_commission_data": 9,
                    "commission_structure_types": {
                        "percentage": 6,
                        "fixed": 2,
                        "hybrid": 1
                    }
                },
                "discrepancy_statistics": {
                    "total_analyses_performed": 89,
                    "discrepancies_detected": 12,
                    "discrepancy_rate": 13.5,
                    "avg_discrepancy_amount": 1247.83
                }
            },
            "system_health": {
                "overall_status": "healthy",
                "last_checked": now.strftime("%Y-%m-%d %H:%M:%S"),
                "streamlit": {
                    "status": "healthy",
                    "port": 8501,
                    "pid": 12345
                },
                "python": {
                    "status": "healthy",
                    "version": "3.10.0",
                    "path": "G:/Software_Engineering/contract_intelligence_assistant/venv/Scripts/python.exe"
                },
                "fastapi": self.check_api_health(),
                "performance": {
                    "total_documents_indexed": 247,
                    "index_size_mb": 145.7,
                    "avg_document_size_kb": 627.3,
                    "index_size_bytes": 152698880
                }
            },
            "query_analytics": {
                "total_queries_today": random.randint(50, 200),
                "avg_response_time_ms": random.randint(150, 800),
                "query_success_rate": random.uniform(85.0, 98.5),
                "peak_usage_hours": [9, 14, 16],
                "most_common_query_types": [
                    {"type": "Document Search", "count": random.randint(20, 50)},
                    {"type": "Financial Analysis", "count": random.randint(15, 35)},
                    {"type": "Partner Query", "count": random.randint(10, 25)},
                    {"type": "Discrepancy Check", "count": random.randint(5, 15)}
                ]
            },
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "cache_status": {
                "documents": True,
                "financial": True,
                "health": True,
                "analytics": False
            }
        }
    
    def get_comprehensive_data(self) -> Optional[Dict[str, Any]]:
        """Get all dashboard data in a single request with fallback to mock data."""
        if not self.use_mock_data:
            try:
                response = requests.get(f"{self.base_url}/dashboard/comprehensive", timeout=15)
                if response.status_code == 200:
                    return response.json().get("data", {})
                else:
                    st.warning(f"API returned status {response.status_code}. Using demo data.")
                    self.use_mock_data = True
            except requests.exceptions.RequestException as e:
                st.info(f"💡 API not available. Running in demo mode with sample data.")
                self.use_mock_data = True
        
        # Return mock data
        return self._get_mock_data()
    
    def get_quick_stats(self) -> Optional[Dict[str, Any]]:
        """Get quick summary statistics with fallback."""
        if not self.use_mock_data:
            try:
                response = requests.get(f"{self.base_url}/dashboard/stats/summary", timeout=10)
                if response.status_code == 200:
                    return response.json().get("data", {})
            except requests.exceptions.RequestException:
                self.use_mock_data = True
        
        # Return simplified mock stats
        return {
            "total_documents": 247,
            "total_partners": 12,
            "system_status": "demo_mode"
        }
    
    def refresh_cache(self) -> bool:
        """Refresh dashboard cache with fallback."""
        if not self.use_mock_data:
            try:
                response = requests.post(f"{self.base_url}/dashboard/refresh", timeout=10)
                return response.status_code == 200
            except requests.exceptions.RequestException:
                self.use_mock_data = True
        
        # Simulate cache refresh in demo mode
        st.success("🎭 Demo data refreshed successfully!")
        return True
    
    def check_api_health(self) -> Dict[str, Any]:
        """Check real-time API health status."""
        endpoints = {
            "/health": "Health",
            "/dashboard/health": "Dashboard",
            "/dashboard/comprehensive": "Comprehensive",
            "/opensearch/health": "OpenSearch",
            "/documents/stats": "Documents",
            "/financial-analysis/health": "Financial Analysis"
        }
        
        endpoint_status = {}
        overall_healthy = True
        
        for endpoint, name in endpoints.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=8)
                if response.status_code == 200:
                    endpoint_status[endpoint] = "healthy"
                else:
                    endpoint_status[endpoint] = "unhealthy"
                    overall_healthy = False
            except requests.exceptions.RequestException:
                endpoint_status[endpoint] = "unhealthy"
                overall_healthy = False
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "service": "Contract Intelligence API",
            "version": "0.1.0",
            "critical_endpoints": endpoint_status
        }


def create_document_analytics_tab(overview_data: Dict[str, Any]):
    """Create document analytics visualizations."""
    # First row - two equal charts side by side
    col1, col2 = st.columns(2)
    
    with col1:
        # Document types pie chart
        doc_types = overview_data.get("document_types", {})
        if doc_types:
            fig_pie = px.pie(
                values=list(doc_types.values()),
                names=list(doc_types.keys()),
                title="Document Types Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3,
                height=350
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                height=350,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No document type data available")
    
    with col2:
        # Partner activity timeline chart
        recent_activity = overview_data.get("recent_activity", [])
        if recent_activity and len(recent_activity) > 0:
            # Create partner activity timeline
            activity_df = pd.DataFrame(recent_activity[:30])  # Last 30 activities
            
            if not activity_df.empty and 'created_at' in activity_df.columns:
                # Convert to datetime and group by date
                activity_df['created_at'] = pd.to_datetime(activity_df['created_at'], errors='coerce')
                activity_df = activity_df.dropna(subset=['created_at'])
                activity_df['date'] = activity_df['created_at'].dt.date
                
                # Group by date and count activities
                daily_activity = activity_df.groupby('date').size().reset_index(name='count')
                daily_activity['date'] = pd.to_datetime(daily_activity['date'])
                
                fig_timeline = px.line(
                    daily_activity,
                    x='date',
                    y='count',
                    title="Daily Document Activity",
                    markers=True,
                    color_discrete_sequence=['#667eea'],
                    height=350
                )
                fig_timeline.update_traces(
                    line=dict(width=3),
                    marker=dict(size=8, line=dict(width=2, color='white'))
                )
                fig_timeline.update_layout(
                    height=350,
                    margin=dict(t=50, b=50, l=50, r=50),
                    xaxis_title="Date",
                    yaxis_title="Documents Processed"
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                # Fallback: Partner document count distribution
                partner_stats = overview_data.get("partner_statistics", {})
                top_partners = partner_stats.get("top_partners", {})
                
                if top_partners:
                    # Create a histogram-style chart
                    partner_counts = list(top_partners.values())
                    
                    fig_hist = px.histogram(
                        x=partner_counts,
                        nbins=10,
                        title="Partner Document Count Distribution",
                        color_discrete_sequence=['#f093fb'],
                        height=350
                    )
                    fig_hist.update_layout(
                        height=350,
                        margin=dict(t=50, b=50, l=50, r=50),
                        xaxis_title="Documents Count",
                        yaxis_title="Number of Partners",
                        showlegend=False
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.info("No partner activity data available")
        else:
            st.info("No recent activity data available")
    
    # Second row - full width bar chart
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    
    # Top partners bar chart (full width, wider)
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
            color_continuous_scale="Blues",
            height=450  # Slightly taller for better visibility
        )
        fig_bar.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=450,
            margin=dict(t=50, b=50, l=50, r=50)
        )
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
                }) if 'title' in activity_df.columns else activity_df,
                use_container_width=True,
                height=400
            )
        else:
            st.info("No recent activity data available")
    else:
        st.info("No recent document activity found")


def create_financial_analytics_tab(financial_data: Dict[str, Any]):
    """Create financial analytics visualizations."""
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
            color_continuous_scale="Greens",
            height=400
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
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
                title="Commission Structure Distribution",
                height=400
            )
            fig_commission.update_layout(
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig_commission, use_container_width=True)
        
        with col2:
            # Display commission metrics
            for structure_type, count in commission_types.items():
                st.metric(f"{structure_type.title()} Structures", f"{count}")
    
    # Discrepancy statistics
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
    # Overall health status
    overall_status = health_data.get("overall_status", "unknown")
    last_checked = health_data.get("last_checked", "Never")
    
    col1, col2 = st.columns(2)
    with col1:
        health_html = display_health_indicator(overall_status)
        st.markdown(f"**Overall Status:** {health_html}", unsafe_allow_html=True)
    with col2:
        st.write(f"**Last Checked:** {last_checked}")
    
    # Service health breakdown - show all available services
    st.subheader("🔧 Service Health Status")
    
    # Define service icons and display names (only for real services in the project)
    service_config = {
        "opensearch": {"icon": "🔍", "name": "OpenSearch"},
        "api": {"icon": "🚀", "name": "API Server"}, 
        "fastapi": {"icon": "⚡", "name": "FastAPI"},
        "streamlit": {"icon": "📊", "name": "Streamlit Dashboard"},
        "python": {"icon": "🐍", "name": "Python Runtime"},
        "docker": {"icon": "�", "name": "Docker Engine"},
        "docker": {"icon": "�", "name": "Docker Engine"}
    }
    
    # Find all services in health_data (excluding special keys)
    excluded_keys = {"overall_status", "last_checked", "performance", "cache_status"}
    available_services = []
    
    for key, value in health_data.items():
        if key not in excluded_keys and isinstance(value, dict):
            available_services.append(key)
    
    # Display services in responsive grid
    if available_services:
        # Calculate columns (max 3 per row for better layout)
        num_services = len(available_services)
        cols_per_row = min(3, num_services)
        rows_needed = (num_services + cols_per_row - 1) // cols_per_row
        
        for row in range(rows_needed):
            cols = st.columns(cols_per_row)
            
            for col_idx in range(cols_per_row):
                service_idx = row * cols_per_row + col_idx
                
                if service_idx < len(available_services):
                    service_key = available_services[service_idx]
                    service_data = health_data.get(service_key, {})
                    
                    # Get service config
                    config = service_config.get(service_key, {"icon": "⚙️", "name": service_key.title()})
                    
                    with cols[col_idx]:
                        st.markdown(f"**{config['icon']} {config['name']}**")
                        
                        # Service status
                        service_status = service_data.get("status", "unknown")
                        st.markdown(display_health_indicator(service_status), unsafe_allow_html=True)
                        
                        # Service-specific metrics
                        if service_key == "opensearch":
                            if service_status in ["green", "yellow", "healthy"]:
                                cluster_name = service_data.get("cluster_name", "N/A")
                                node_count = service_data.get("number_of_nodes", 0)
                                st.write(f"**Cluster:** {cluster_name}")
                                st.write(f"**Nodes:** {node_count}")
                        
                        elif service_key in ["api", "fastapi"]:
                            service_name = service_data.get("service", "N/A")
                            version = service_data.get("version", "N/A")
                            st.write(f"**Service:** {service_name}")
                            st.write(f"**Version:** {version}")
                            
                            # Critical endpoints health check
                            critical_endpoints = service_data.get("critical_endpoints", {})
                            if critical_endpoints:
                                st.write("**Critical Endpoints:**")
                                for endpoint, status in critical_endpoints.items():
                                    endpoint_name = endpoint.replace("/", "").replace("-", " ").title()
                                    if endpoint_name == "":
                                        endpoint_name = "Root"
                                    
                                    # Create mini health indicator for each endpoint
                                    if status == "healthy":
                                        endpoint_icon = "🟢"
                                    elif status == "degraded":
                                        endpoint_icon = "🟡"
                                    else:
                                        endpoint_icon = "🔴"
                                    
                                    st.write(f"  {endpoint_icon} {endpoint_name}")
                            else:
                                st.write("**Status:** Basic API online")
                        
                        elif service_key == "streamlit":
                            port = service_data.get("port", "N/A")
                            pid = service_data.get("pid", "N/A")
                            st.write(f"**Port:** {port}")
                            st.write(f"**PID:** {pid}")
                        
                        elif service_key == "python":
                            version = service_data.get("version", "N/A")
                            path = service_data.get("path", "N/A")
                            st.write(f"**Version:** {version}")
                            if len(str(path)) > 20:
                                st.write(f"**Path:** ...{str(path)[-20:]}")
                            else:
                                st.write(f"**Path:** {path}")
                        
                        elif service_key == "docker":
                            version = service_data.get("version", "N/A")
                            containers = service_data.get("running_containers", 0)
                            st.write(f"**Version:** {version}")
                            st.write(f"**Containers:** {containers}")
                        
                        else:
                            # Generic metrics for other services
                            for metric_key, metric_value in service_data.items():
                                if metric_key != "status" and isinstance(metric_value, (str, int, float)):
                                    display_key = metric_key.replace("_", " ").title()
                                    if len(str(metric_value)) > 20:
                                        display_value = f"...{str(metric_value)[-15:]}"
                                    else:
                                        display_value = str(metric_value)
                                    st.write(f"**{display_key}:** {display_value}")
    else:
        st.info("No service health data available")
    
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
                color_continuous_scale="Viridis",
                height=400
            )
            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No query analytics data available")


def init_revolutionary_styling():
    """Initialize dashboard styling with cutting-edge design."""
    # Ultra-modern CSS with advanced effects
    st.markdown("""
    <style>
    /* Import Google Fonts for premium typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container with animated background */
    .main > div {
        padding-top: 2rem;
        background: 
            radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 106, 107, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 60% 10%, rgba(79, 172, 254, 0.1) 0%, transparent 50%);
        background-size: 100% 100%;
        animation: backgroundShift 20s ease-in-out infinite;
        min-height: 100vh;
    }
    
    @keyframes backgroundShift {
        0%, 100% { 
            background-position: 0% 0%, 100% 100%, 50% 50%, 25% 75%; 
        }
        25% { 
            background-position: 100% 0%, 0% 100%, 75% 25%, 50% 50%; 
        }
        50% { 
            background-position: 100% 100%, 0% 0%, 25% 75%, 75% 25%; 
        }
        75% { 
            background-position: 0% 100%, 100% 0%, 50% 50%, 25% 75%; 
        }
    }
    
    /* Revolutionary metric cards with glassmorphism */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.25),
            0 0 50px rgba(102, 126, 234, 0.1);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transition: left 0.8s;
    }
    
    [data-testid="metric-container"]::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(102, 126, 234, 0.1), transparent, rgba(255, 106, 107, 0.1), transparent);
        animation: rotate 10s linear infinite;
        z-index: -1;
    }
    
    @keyframes rotate {
        100% { transform: rotate(360deg); }
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-12px) scale(1.03) rotateX(2deg);
        box-shadow: 
            0 25px 80px rgba(102, 126, 234, 0.25),
            0 20px 50px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.35),
            0 0 80px rgba(102, 126, 234, 0.2);
        border: 1px solid rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="metric-container"]:hover::before {
        left: 100%;
    }
    
    /* Premium health indicators with advanced pulsing */
    .health-indicator {
        display: inline-block;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        margin-right: 14px;
        position: relative;
        animation: advancedPulse 3s ease-in-out infinite;
    }
    
    .health-indicator::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 50%;
        animation: ripple 2s ease-out infinite;
    }
    
    @keyframes advancedPulse {
        0%, 100% { 
            transform: scale(1); 
            opacity: 1; 
        }
        33% { 
            transform: scale(1.15); 
            opacity: 0.9; 
        }
        66% { 
            transform: scale(1.05); 
            opacity: 0.95; 
        }
    }
    
    @keyframes ripple {
        0% {
            transform: scale(1);
            opacity: 0.8;
        }
        100% {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .health-healthy { 
        background: radial-gradient(circle, #4CAF50, #45a049, #2E7D32);
        box-shadow: 
            0 0 25px rgba(76, 175, 80, 0.7),
            0 0 50px rgba(76, 175, 80, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .health-healthy::before {
        background: radial-gradient(circle, rgba(76, 175, 80, 0.6), transparent);
    }
    
    .health-degraded { 
        background: radial-gradient(circle, #FF9800, #F57C00, #E65100);
        box-shadow: 
            0 0 25px rgba(255, 152, 0, 0.7),
            0 0 50px rgba(255, 152, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .health-degraded::before {
        background: radial-gradient(circle, rgba(255, 152, 0, 0.6), transparent);
    }
    
    .health-unhealthy { 
        background: radial-gradient(circle, #F44336, #D32F2F, #C62828);
        box-shadow: 
            0 0 25px rgba(244, 67, 54, 0.7),
            0 0 50px rgba(244, 67, 54, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .health-unhealthy::before {
        background: radial-gradient(circle, rgba(244, 67, 54, 0.6), transparent);
    }
    
    /* Next-level tab styling with holographic effects */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        padding: 20px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        margin-bottom: 3rem;
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab-list"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
        animation: tabListShimmer 4s ease-in-out infinite;
    }
    
    @keyframes tabListShimmer {
        0%, 100% { left: -100%; }
        50% { left: 100%; }
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        min-width: 160px;
        white-space: pre-wrap;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.35);
        border-radius: 22px;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 8px;
        color: #2d3748;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.1),
            0 6px 15px rgba(0, 0, 0, 0.07),
            inset 0 1px 0 rgba(255, 255, 255, 0.6);
        position: relative;
        overflow: hidden;
        cursor: pointer;
        transform-style: preserve-3d;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
        transition: left 0.6s ease;
    }
    
    .stTabs [data-baseweb="tab"]::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: conic-gradient(from 0deg, transparent 0deg, rgba(102, 126, 234, 0.1) 90deg, transparent 180deg);
        opacity: 0;
        transition: opacity 0.3s ease;
        border-radius: 20px;
    }
    
    /* Tab hover with advanced 3D transformation */
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-8px) rotateX(8deg) rotateY(2deg) scale(1.02);
        box-shadow: 
            0 20px 60px rgba(102, 126, 234, 0.2),
            0 12px 30px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.7),
            0 0 40px rgba(102, 126, 234, 0.1);
        background: rgba(255, 255, 255, 0.92);
        border: 2px solid rgba(102, 126, 234, 0.4);
        perspective: 1200px;
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }
    
    .stTabs [data-baseweb="tab"]:hover::after {
        opacity: 1;
    }
    
    /* Revolutionary active tab with holographic effect */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, 
            #667eea 0%, 
            #764ba2 20%, 
            #f093fb 40%, 
            #f5576c 60%, 
            #4facfe 80%,
            #00f2fe 100%) !important;
        background-size: 500% 500%;
        animation: holographicShift 12s ease infinite;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-12px) scale(1.08) rotateX(3deg);
        box-shadow: 
            0 25px 80px rgba(102, 126, 234, 0.5),
            0 20px 50px rgba(118, 75, 162, 0.4),
            0 0 60px rgba(102, 126, 234, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.4),
            0 0 100px rgba(245, 87, 108, 0.2);
        z-index: 10;
        font-weight: 700;
        position: relative;
    }
    
    @keyframes holographicShift {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 50%; }
        50% { background-position: 50% 100%; }
        75% { background-position: 50% 0%; }
        100% { background-position: 0% 50%; }
    }
    
    .stTabs [aria-selected="true"]::before {
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
        animation: activeTabShimmer 3s ease-in-out infinite;
    }
    
    @keyframes activeTabShimmer {
        0%, 100% { left: -100%; }
        50% { left: 100%; }
    }
    
    /* Active tab hover with enhanced holographic effect */
    .stTabs [aria-selected="true"]:hover {
        transform: translateY(-16px) scale(1.12) rotateX(5deg) rotateY(3deg) !important;
        box-shadow: 
            0 35px 100px rgba(102, 126, 234, 0.6),
            0 25px 70px rgba(118, 75, 162, 0.5),
            0 0 80px rgba(245, 87, 108, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.5),
            0 0 120px rgba(79, 172, 254, 0.3) !important;
        animation: holographicShift 6s ease infinite, holographicGlow 3s ease infinite;
    }
    
    @keyframes holographicGlow {
        0%, 100% { 
            filter: hue-rotate(0deg) brightness(1) saturate(1.2); 
        }
        33% { 
            filter: hue-rotate(20deg) brightness(1.1) saturate(1.4); 
        }
        66% { 
            filter: hue-rotate(-15deg) brightness(1.05) saturate(1.3); 
        }
    }
    
    /* Ensure perfect text visibility in active tabs */
    .stTabs [aria-selected="true"] *,
    .stTabs [aria-selected="true"]:hover * {
        color: white !important;
        text-shadow: 
            0 1px 3px rgba(0, 0, 0, 0.4),
            0 0 10px rgba(255, 255, 255, 0.3);
        font-weight: 700 !important;
    }
    
    /* Premium dashboard title with animated holographic gradient */
    .dashboard-title {
        background: linear-gradient(135deg, 
            #667eea 0%, 
            #764ba2 20%, 
            #f093fb 40%, 
            #f5576c 60%, 
            #4facfe 80%,
            #00f2fe 100%);
        background-size: 500% 500%;
        animation: holographicShift 15s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 4rem;
        letter-spacing: -0.03em;
        position: relative;
        user-select: none; /* Prevent text selection to avoid white color issue */
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
    }
    
    /* Fix text selection for dashboard title */
    .dashboard-title::selection {
        background: rgba(102, 126, 234, 0.3);
        -webkit-text-fill-color: transparent;
    }
    
    .dashboard-title::-moz-selection {
        background: rgba(102, 126, 234, 0.3);
        -webkit-text-fill-color: transparent;
    }
    
    .dashboard-title::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.1), 
            rgba(118, 75, 162, 0.1), 
            rgba(240, 147, 251, 0.1));
        filter: blur(20px);
        z-index: -1;
        animation: titleGlow 8s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.05); opacity: 0.8; }
    }
    
    /* Enhanced section headers with advanced glass effect */
    .section-header {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 24px;
        padding: 30px 35px;
        margin-bottom: 30px;
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.25),
            0 0 60px rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
        animation: shimmer 4s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { left: -100%; }
        50% { left: 100%; }
    }
    
    /* Revolutionary chart containers with advanced glass effect */
    .js-plotly-plot {
        border-radius: 24px !important;
        overflow: hidden !important;
        box-shadow: 
            0 15px 50px rgba(0, 0, 0, 0.12),
            0 10px 25px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(15px) !important;
        background: rgba(255, 255, 255, 0.08) !important;
        min-height: 280px !important;
        height: auto !important;
        margin: 1rem 0 !important;
        transition: all 0.3s ease !important;
    }
    
    /* Enhanced hover effect for charts */
    .js-plotly-plot:hover {
        transform: translateY(-4px) !important;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.15),
            0 15px 35px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        border: 1px solid rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Fix Plotly chart sizing */
    .stPlotlyChart {
        min-height: 280px !important;
        height: auto !important;
        margin: 1rem 0 !important;
    }
    
    .stPlotlyChart > div {
        min-height: 280px !important;
        height: auto !important;
    }
    
    .plot-container {
        min-height: 280px !important;
        height: auto !important;
    }
    
    .svg-container {
        min-height: 280px !important;
        height: auto !important;
    }
    
    .main-svg {
        min-height: 280px !important;
        height: auto !important;
    }
    
    /* Enhanced dataframe styling */
    .stDataFrame {
        border-radius: 24px !important;
        overflow: hidden !important;
        box-shadow: 
            0 15px 50px rgba(0, 0, 0, 0.12),
            0 10px 25px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(15px) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Premium alert boxes with glassmorphism */
    .stAlert {
        border-radius: 20px;
        border: none;
        backdrop-filter: blur(15px);
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stSuccess {
        background: rgba(212, 237, 218, 0.7);
        border-left: 5px solid #28a745;
    }
    
    .stInfo {
        background: rgba(204, 231, 255, 0.7);
        border-left: 5px solid #17a2b8;
    }
    
    .stError {
        background: rgba(248, 215, 218, 0.7);
        border-left: 5px solid #dc3545;
    }
    
    /* Floating elements with advanced animation */
    .floating-element {
        animation: advancedFloat 8s ease-in-out infinite;
    }
    
    @keyframes advancedFloat {
        0%, 100% { 
            transform: translateY(0px) rotateX(0deg); 
        }
        25% { 
            transform: translateY(-8px) rotateX(1deg); 
        }
        50% { 
            transform: translateY(-12px) rotateX(0deg); 
        }
        75% { 
            transform: translateY(-6px) rotateX(-1deg); 
        }
    }
    
    /* Tab content with advanced entrance animation */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 50px 0;
        background: transparent;
        animation: advancedSlideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes advancedSlideIn {
        from { 
            opacity: 0; 
            transform: translateY(30px) scale(0.95); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
        }
    }
    
    /* Responsive design with enhanced breakpoints */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            min-width: 150px;
            height: 45px;
            padding: 10px 18px;
            font-size: 7px;
        }
        
        .dashboard-title {
            font-size: 2.5rem;
        }
        
        [data-testid="metric-container"] {
            padding: 1.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .stTabs [data-baseweb="tab"] {
            min-width: 120px;
            height: 40px;
            padding: 8px 12px;
            font-size: 6px;
        }
        
        .dashboard-title {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def display_health_indicator(status: str) -> str:
    """Display health status with advanced colored indicator."""
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


def create_revolutionary_metrics_row(overview_data: Dict[str, Any]):
    """Create top-level metrics row with glassmorphism effects."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_docs = overview_data.get("total_documents", 0)
        st.metric(
            label="📄 Total Documents",
            value=f"{total_docs:,}",
            help="Total number of indexed documents in the system"
        )
    
    with col2:
        partner_stats = overview_data.get("partner_statistics", {})
        total_partners = partner_stats.get("total_partners", 0)
        st.metric(
            label="🤝 Active Partners", 
            value=f"{total_partners:,}",
            help="Number of unique partners with active contracts"
        )
    
    with col3:
        partners_with_docs = partner_stats.get("partners_with_documents", 0)
        coverage = partner_stats.get("coverage_percentage", 0)
        st.metric(
            label="📊 Documentation Coverage",
            value=f"{coverage:.1f}%",
            delta=f"{partners_with_docs} partners",
            help="Percentage of partners with complete documentation"
        )
    
    with col4:
        doc_types = overview_data.get("document_types", {})
        contract_count = doc_types.get("contract", 0)
        payout_count = doc_types.get("payout_report", 0)
        st.metric(
            label="📋 Document Categories",
            value=f"{len(doc_types)}",
            delta=f"Contracts: {contract_count}, Reports: {payout_count}",
            help="Number of different document types in the system"
        )


def render_revolutionary_dashboard():
    """Render the dashboard with cutting-edge design.""" 
    try:
        init_revolutionary_styling()
        
        # Dashboard title with holographic gradient
        st.markdown("""
        <div class="dashboard-title">
            Dashboard
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 3rem; font-size: 1.3rem; color: #6c757d; font-weight: 500;">
            ✨ Next-Generation Analytics with Advanced UI Design
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize API client
        api_client = DashboardAPI()
        
        # Check if running in demo mode and show status
        if hasattr(api_client, 'use_mock_data') and api_client.use_mock_data:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("🎭 **Demo Mode Active** - Displaying sample data for demonstration purposes")
            with col2:
                if st.button("🔄 Try API", help="Attempt to reconnect to real API"):
                    api_client.use_mock_data = False
                    st.rerun()
        
        # Dashboard controls
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
                            if hasattr(api_client, 'use_mock_data') and api_client.use_mock_data:
                                st.success("🎭 Demo data refreshed!")
                            else:
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
            st.error("❌ Unable to load any data (API and demo mode failed)")
            st.stop()
        
        # Show demo mode notification after data loads
        if hasattr(api_client, 'use_mock_data') and api_client.use_mock_data:
            st.info("🎭 **Demo Mode**: Showing sample data for Contract Intelligence Dashboard demonstration")
        
        # Extract data sections
        overview_data = dashboard_data.get("document_overview", {})
        financial_data = dashboard_data.get("financial_metrics", {})
        health_data = dashboard_data.get("system_health", {})
        query_data = dashboard_data.get("query_analytics", {})
        
        # Create metrics row
        create_revolutionary_metrics_row(overview_data)
        
        st.divider()
        
        # Create tabs with holographic effects
        tab1, tab2, tab3, tab4 = st.tabs([
            "📄\n**Documents**\n*Intelligence*", 
            "💰\n**Financial**\n*Analytics*", 
            "🏥\n**System Health**\n*Monitoring*", 
            "🔍\n**Query Analytics**\n*Performance*"
        ])
        
        with tab1:
            st.markdown("""
            <div class="section-header">
                <h3 style="margin: 0; color: #2d3748; font-weight: 700;">📄 Document Intelligence Center</h3>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-weight: 500;">Comprehensive analysis of your document portfolio with AI insights</p>
            </div>
            """, unsafe_allow_html=True)
            create_document_analytics_tab(overview_data)
        
        with tab2:
            st.markdown("""
            <div class="section-header">
                <h3 style="margin: 0; color: #2d3748; font-weight: 700;">💰 Financial Analytics Hub</h3>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-weight: 500;">Advanced financial insights and discrepancy analysis with ML algorithms</p>
            </div>
            """, unsafe_allow_html=True)
            create_financial_analytics_tab(financial_data)
        
        with tab3:
            st.markdown("""
            <div class="section-header">
                <h3 style="margin: 0; color: #2d3748; font-weight: 700;">🏥 System Health Command Center</h3>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-weight: 500;">Real-time monitoring with predictive health analytics and alerts</p>
            </div>
            """, unsafe_allow_html=True)
            create_system_health_tab(health_data)
        
        with tab4:
            st.markdown("""
            <div class="section-header">
                <h3 style="margin: 0; color: #2d3748; font-weight: 700;">🔍 Query Performance Observatory</h3>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-weight: 500;">Advanced query analytics with real-time performance optimization</p>
            </div>
            """, unsafe_allow_html=True)
            create_query_analytics_tab(query_data)
        
        # Revolutionary footer
        st.divider()
        generated_at = dashboard_data.get("generated_at", "Unknown")
        cache_status = dashboard_data.get("cache_status", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"⚡ Last Updated: {generated_at}")
        with col2:
            cached_items = sum(1 for v in cache_status.values() if v)
            st.caption(f"🚀 Cache Performance: {cached_items}/{len(cache_status)} systems optimized")
            
    except Exception as e:
        st.error(f"❌ Dashboard Rendering Error: {e}")
        import traceback
        st.code(f"Error traceback:\n{traceback.format_exc()}")
        st.info("🔧 Please check console logs for detailed error information")


if __name__ == "__main__":
    render_revolutionary_dashboard()