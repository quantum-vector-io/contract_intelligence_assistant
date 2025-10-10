#!/usr/bin/env pwsh
# Enhanced Dashboard Launch Script with Health Monitoring
# This script starts both FastAPI server and Streamlit dashboard

param(
    [string]$Mode = "full",  # Options: "full", "dashboard-only", "api-only"
    [int]$ApiPort = 8000,
    [int]$DashboardPort = 8501,
    [switch]$SkipHealthCheck,
    [switch]$Verbose
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VenvPath = Join-Path $ProjectRoot "venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$StreamlitExe = Join-Path $VenvPath "Scripts\streamlit.exe"
$UvicornExe = Join-Path $VenvPath "Scripts\uvicorn.exe"

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

# Health check function
function Test-ServiceHealth {
    param([string]$Url, [int]$TimeoutSeconds = 5)
    try {
        $response = Invoke-RestMethod -Uri $Url -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Wait for service to be ready
function Wait-ForService {
    param([string]$Url, [string]$ServiceName, [int]$MaxWaitSeconds = 30)
    Write-Log "Waiting for $ServiceName to be ready at $Url..." "INFO"
    
    $attempts = 0
    $maxAttempts = $MaxWaitSeconds
    
    while ($attempts -lt $maxAttempts) {
        if (Test-ServiceHealth -Url $Url) {
            Write-Log "$ServiceName is ready!" "SUCCESS"
            return $true
        }
        
        Start-Sleep -Seconds 1
        $attempts++
        
        if ($attempts % 5 -eq 0) {
            Write-Log "Still waiting for $ServiceName... ($attempts/$maxAttempts)" "INFO"
        }
    }
    
    Write-Log "$ServiceName failed to start within $MaxWaitSeconds seconds" "ERROR"
    return $false
}

# Kill existing processes
function Stop-ExistingProcesses {
    Write-Log "Stopping existing processes..." "INFO"
    
    # Kill processes by name
    $processNames = @("uvicorn", "streamlit")
    foreach ($processName in $processNames) {
        try {
            Get-Process -Name $processName -ErrorAction SilentlyContinue | Stop-Process -Force
            Write-Log "Stopped existing $processName processes" "INFO"
        }
        catch {
            # Process not found, continue
        }
    }
    
    # Kill processes by port
    $ports = @($ApiPort, $DashboardPort)
    foreach ($port in $ports) {
        try {
            $netstat = netstat -ano | Select-String ":$port "
            if ($netstat) {
                $pid = ($netstat -split '\s+')[-1]
                if ($pid -and $pid -ne "0") {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-Log "Killed process on port $port (PID: $pid)" "INFO"
                }
            }
        }
        catch {
            # Port not in use, continue
        }
    }
    
    Start-Sleep -Seconds 2
}

# Start FastAPI server
function Start-FastAPIServer {
    Write-Log "Starting FastAPI server on port $ApiPort..." "INFO"
    
    # Change to project directory
    Set-Location $ProjectRoot
    
    # Start uvicorn in background
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $UvicornExe
    $startInfo.Arguments = "src.api.main:app --host 0.0.0.0 --port $ApiPort --reload"
    $startInfo.WorkingDirectory = $ProjectRoot
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    
    try {
        $process.Start() | Out-Null
        Write-Log "FastAPI server started (PID: $($process.Id))" "SUCCESS"
        
        # Wait for API to be ready
        $apiHealthUrl = "http://localhost:$ApiPort/health"
        if (Wait-ForService -Url $apiHealthUrl -ServiceName "FastAPI API" -MaxWaitSeconds 15) {
            return $process
        } else {
            $process.Kill()
            throw "FastAPI server failed to become ready"
        }
    }
    catch {
        Write-Log "Failed to start FastAPI server: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Start Streamlit dashboard
function Start-StreamlitDashboard {
    Write-Log "Starting Streamlit dashboard on port $DashboardPort..." "INFO"
    
    # Change to project directory
    Set-Location $ProjectRoot
    
    # Start streamlit
    $dashboardFile = Join-Path $ProjectRoot "src\ui\dashboard_revolutionary.py"
    
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $StreamlitExe
    $startInfo.Arguments = "run `"$dashboardFile`" --server.port $DashboardPort --server.address 0.0.0.0"
    $startInfo.WorkingDirectory = $ProjectRoot
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    
    try {
        $process.Start() | Out-Null
        Write-Log "Streamlit dashboard started (PID: $($process.Id))" "SUCCESS"
        
        # Wait for dashboard to be ready
        $dashboardHealthUrl = "http://localhost:$DashboardPort/healthz"
        if (Wait-ForService -Url "http://localhost:$DashboardPort" -ServiceName "Streamlit Dashboard" -MaxWaitSeconds 10) {
            return $process
        } else {
            Write-Log "Streamlit dashboard may take a moment to fully load..." "WARN"
            return $process
        }
    }
    catch {
        Write-Log "Failed to start Streamlit dashboard: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Main execution
try {
    Write-Log "🚀 Starting Contract Intelligence Dashboard..." "INFO"
    Write-Log "Mode: $Mode | API Port: $ApiPort | Dashboard Port: $DashboardPort" "INFO"
    
    # Validate virtual environment
    if (-not (Test-Path $PythonExe)) {
        throw "Virtual environment not found at $VenvPath. Please run setup.ps1 first."
    }
    
    if (-not (Test-Path $StreamlitExe)) {
        throw "Streamlit not found. Please install dependencies: pip install streamlit"
    }
    
    if (-not (Test-Path $UvicornExe)) {
        throw "Uvicorn not found. Please install dependencies: pip install uvicorn"
    }
    
    # Stop existing processes
    Stop-ExistingProcesses
    
    $processes = @()
    
    # Start services based on mode
    if ($Mode -eq "full" -or $Mode -eq "api-only") {
        try {
            $apiProcess = Start-FastAPIServer
            $processes += $apiProcess
        }
        catch {
            Write-Log "Failed to start API server. Continuing with dashboard only..." "WARN"
        }
    }
    
    if ($Mode -eq "full" -or $Mode -eq "dashboard-only") {
        try {
            Start-Sleep -Seconds 2  # Give API time to fully start
            $dashboardProcess = Start-StreamlitDashboard
            $processes += $dashboardProcess
        }
        catch {
            Write-Log "Failed to start dashboard: $($_.Exception.Message)" "ERROR"
            # Kill API if dashboard fails in full mode
            if ($Mode -eq "full" -and $processes.Count -gt 0) {
                $processes[0].Kill()
            }
            throw
        }
    }
    
    # Success message
    Write-Log "✅ Dashboard system started successfully!" "SUCCESS"
    Write-Log "" "INFO"
    
    if ($Mode -eq "full" -or $Mode -eq "api-only") {
        Write-Log "🔗 FastAPI Server: http://localhost:$ApiPort" "SUCCESS"
        Write-Log "📊 API Docs: http://localhost:$ApiPort/docs" "SUCCESS"
    }
    
    if ($Mode -eq "full" -or $Mode -eq "dashboard-only") {
        Write-Log "🎯 Dashboard: http://localhost:$DashboardPort" "SUCCESS"
    }
    
    Write-Log "" "INFO"
    Write-Log "Press Ctrl+C to stop all services..." "INFO"
    
    # Wait for user interrupt
    try {
        while ($true) {
            Start-Sleep -Seconds 1
            
            # Check if processes are still running
            $runningProcesses = $processes | Where-Object { -not $_.HasExited }
            if ($runningProcesses.Count -eq 0) {
                Write-Log "All processes have stopped" "WARN"
                break
            }
        }
    }
    catch {
        Write-Log "Interrupt received, shutting down..." "INFO"
    }
    
}
catch {
    Write-Log "❌ Error: $($_.Exception.Message)" "ERROR"
    exit 1
}
finally {
    # Cleanup
    Write-Log "🧹 Cleaning up processes..." "INFO"
    
    foreach ($process in $processes) {
        if (-not $process.HasExited) {
            try {
                $process.Kill()
                $process.WaitForExit(5000)
                Write-Log "Stopped process PID: $($process.Id)" "INFO"
            }
            catch {
                Write-Log "Failed to stop process PID: $($process.Id)" "WARN"
            }
        }
    }
    
    Write-Log "🎯 Dashboard shutdown complete" "SUCCESS"
}