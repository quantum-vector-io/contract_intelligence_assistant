#!/usr/bin/env python3
"""
Revolutionary Dashboard Launcher Script

This script launches the Contract Intelligence Dashboard with advanced health monitoring
and critical endpoint checking capabilities.
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the revolutionary dashboard."""
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Set the working directory
    os.chdir(project_root)
    
    # Dashboard module path
    dashboard_module = "src.ui.dashboard_revolutionary"
    
    # Command to run Streamlit dashboard
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "src/ui/dashboard_revolutionary.py",
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
        "--theme.primaryColor", "#667eea",
        "--theme.backgroundColor", "#0e1117",
        "--theme.secondaryBackgroundColor", "#1e1e1e",
        "--theme.textColor", "#ffffff"
    ]
    
    print("🚀 Launching Revolutionary Dashboard...")
    print(f"📁 Working Directory: {project_root}")
    print(f"🎯 Dashboard URL: http://localhost:8501")
    print("✨ Features: Glassmorphism UI, Health Monitoring, Critical Endpoints")
    print("-" * 60)
    
    try:
        # Launch the dashboard
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)