#!/usr/bin/env pwsh
# Simple Dashboard Launch Script (Dashboard Only)
# This script starts only the Streamlit dashboard without FastAPI server

param(
    [int]$Port = 8501,
    [switch]$NoBrowser,
    [switch]$Verbose
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VenvPath = Join-Path $ProjectRoot "venv"
$StreamlitExe = Join-Path $VenvPath "Scripts\streamlit.exe"

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Kill existing Streamlit processes
function Stop-ExistingStreamlit {
    Write-Log "Checking for existing Streamlit processes..." "INFO"
    
    try {
        Get-Process -Name "streamlit" -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-Log "Stopped existing streamlit processes" "INFO"
    }
    catch {
        # Process not found, continue
    }
    
    # Check port
    try {
        $netstat = netstat -ano | Select-String ":$Port "
        if ($netstat) {
            $processId = ($netstat -split '\s+')[-1]
            if ($processId -and $processId -ne "0") {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Write-Log "Killed process on port $Port (PID: $processId)" "INFO"
            }
        }
    }
    catch {
        # Port not in use, continue
    }
    
    Start-Sleep -Seconds 1
}

# Main execution
try {
    Write-Log "🎯 Starting Contract Intelligence Dashboard (Demo Mode)..." "SUCCESS"
    Write-Log "Port: $Port | Open Browser: $(-not $NoBrowser)" "INFO"
    
    # Validate virtual environment
    if (-not (Test-Path $StreamlitExe)) {
        throw "Streamlit not found. Please install dependencies: pip install streamlit"
    }
    
    # Stop existing processes
    Stop-ExistingStreamlit
    
    # Change to project directory
    Set-Location $ProjectRoot
    
    # Start streamlit
    Write-Log "🚀 Starting Streamlit dashboard..." "INFO"
    $dashboardFile = Join-Path $ProjectRoot "src\ui\dashboard_revolutionary.py"
    
    $arguments = @(
        "run"
        $dashboardFile
        "--server.port"
        $Port
        "--server.address"
        "0.0.0.0"
        "--theme.primaryColor"
        "#667eea"
        "--theme.backgroundColor"
        "#0e1117"
        "--theme.secondaryBackgroundColor"
        "#262730"
        "--theme.textColor"
        "#ffffff"
    )
    
    if ($NoBrowser) {
        $arguments += "--server.headless"
        $arguments += "true"
    }
    
    if ($Verbose) {
        Write-Log "Streamlit command: $StreamlitExe $($arguments -join ' ')" "INFO"
    }
    
    # Start Streamlit
    & $StreamlitExe $arguments
    
}
catch {
    Write-Log "❌ Error: $($_.Exception.Message)" "ERROR"
    exit 1
}
finally {
    Write-Log "🎯 Dashboard shutdown" "SUCCESS"
}