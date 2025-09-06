# Contract Intelligence Assistant - Local Development Mode
# This script sets up the local development environment with Docker OpenSearch and local FastAPI/Streamlit

# Start development environment
#.\windows_dev_mode.ps1

# Stop all services
#.\windows_dev_mode.ps1 -StopOnly

# Start without health checks (faster)
#.\windows_dev_mode.ps1 -NoHealthCheck

# 🎯 What the Script Does:
# Validates Environment: Checks if venv and Docker are available
# Cleans Up: Stops any existing services
# Starts Docker: docker-compose up -d opensearch opensearch-dashboards
# Starts Backend: .\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
# Starts Frontend: .\venv\Scripts\python.exe -m streamlit run src\ui\app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
# Health Checks: Verifies all services are responding correctly
# Status Report: Shows URLs and helpful commands

# 🔧 Additional Commands:
# The script provides helpful development commands at the end:

# View backend/frontend logs: Get-Job | Receive-Job
# View Docker logs: docker-compose logs -f opensearch
# Stop everything: .[windows_dev_mode.ps1](http://_vscodecontentref_/3) -StopOnly
#
# function prompt { "(venv) PS $(Split-Path -Leaf $PWD)> " } - make your power shell prompt simpler ( just for dev manual mode )
param(
    [switch]$StopOnly,
    [switch]$NoHealthCheck
)

# Color functions for better output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }

# Configuration
$OPENSEARCH_URL = "http://localhost:9200"
$OPENSEARCH_DASHBOARD_URL = "http://localhost:5601"
$BACKEND_URL = "http://localhost:8000"
$FRONTEND_URL = "http://localhost:8501"
$HEALTH_ENDPOINT = "$BACKEND_URL/documents/health/embedding"

# Function to check if a service is running
function Test-ServiceHealth {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$TimeoutSeconds = 10
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSeconds -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "$ServiceName is healthy (Status: $($response.StatusCode))"
            return $true
        } else {
            Write-Warning "$ServiceName responded with status: $($response.StatusCode)"
            return $false
        }
    }
    catch {
        Write-Error "$ServiceName is not responding: $($_.Exception.Message)"
        return $false
    }
}

# Function to wait for service to be ready
function Wait-ForService {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$MaxAttempts = 30,
        [int]$SleepSeconds = 2
    )
    
    Write-Info "Waiting for $ServiceName to be ready..."
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        if (Test-ServiceHealth -Url $Url -ServiceName $ServiceName -TimeoutSeconds 5) {
            return $true
        }
        Write-Host "." -NoNewline
        Start-Sleep $SleepSeconds
    }
    Write-Host ""
    Write-Error "$ServiceName failed to start after $($MaxAttempts * $SleepSeconds) seconds"
    return $false
}

# Function to stop all services
function Stop-Services {
    Write-Info "Stopping all services..."
    
    # Stop Docker services
    Write-Info "Stopping Docker services..."
    docker-compose stop opensearch opensearch-dashboards 2>$null
    
    # Kill FastAPI and Streamlit processes
    Write-Info "Stopping local services..."
    Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*streamlit*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Success "All services stopped"
}

# Main script logic
Write-Host "🚀 Contract Intelligence Assistant - Development Mode" -ForegroundColor Magenta
Write-Host "=" * 60 -ForegroundColor Magenta

# If only stopping services
if ($StopOnly) {
    Stop-Services
    exit 0
}

# Check if virtual environment exists
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Error "Virtual environment not found! Please create it first with: python -m venv venv"
    exit 1
}

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Success "Docker is running"
} catch {
    Write-Error "Docker is not running! Please start Docker Desktop first."
    exit 1
}

# Stop any existing services first
Write-Info "Cleaning up existing services..."
Stop-Services
Start-Sleep 3

Write-Host ""
Write-Info "Starting services in development mode..."
Write-Host ""

# 1. Start Docker services (OpenSearch + Dashboard)
Write-Info "1. Starting OpenSearch and Dashboard..."
try {
    $dockerOutput = docker-compose up -d opensearch opensearch-dashboards 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker services started successfully"
    } else {
        Write-Error "Failed to start Docker services: $dockerOutput"
        exit 1
    }
} catch {
    Write-Error "Failed to start Docker services: $($_.Exception.Message)"
    exit 1
}

# Wait for OpenSearch to be ready
if (-not (Wait-ForService -Url $OPENSEARCH_URL -ServiceName "OpenSearch")) {
    Write-Error "OpenSearch failed to start. Stopping script."
    exit 1
}

# Wait for OpenSearch Dashboard
if (-not (Wait-ForService -Url $OPENSEARCH_DASHBOARD_URL -ServiceName "OpenSearch Dashboard")) {
    Write-Warning "OpenSearch Dashboard is not ready, but continuing..."
}

Write-Host ""

# 2. Start FastAPI Backend
Write-Info "2. Starting FastAPI Backend..."
try {
    $backendJob = Start-Job -ScriptBlock {
        param($WorkingDir)
        Set-Location $WorkingDir
        .\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
    } -ArgumentList (Get-Location).Path
    
    Write-Success "FastAPI backend job started (Job ID: $($backendJob.Id))"
} catch {
    Write-Error "Failed to start FastAPI backend: $($_.Exception.Message)"
    exit 1
}

# Wait for Backend to be ready
Start-Sleep 5
if (-not (Wait-ForService -Url $HEALTH_ENDPOINT -ServiceName "FastAPI Backend")) {
    Write-Error "FastAPI Backend failed to start. Stopping script."
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""

# 3. Start Streamlit Frontend
Write-Info "3. Starting Streamlit Frontend..."
try {
    $frontendJob = Start-Job -ScriptBlock {
        param($WorkingDir)
        Set-Location $WorkingDir
        .\venv\Scripts\python.exe -m streamlit run src\ui\app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
    } -ArgumentList (Get-Location).Path
    
    Write-Success "Streamlit frontend job started (Job ID: $($frontendJob.Id))"
} catch {
    Write-Error "Failed to start Streamlit frontend: $($_.Exception.Message)"
    exit 1
}

# Wait for Frontend to be ready
Start-Sleep 8
if (-not (Wait-ForService -Url $FRONTEND_URL -ServiceName "Streamlit Frontend")) {
    Write-Warning "Streamlit Frontend might still be starting up..."
}

Write-Host ""
Write-Host "🎉 Development Environment Status" -ForegroundColor Magenta
Write-Host "=" * 60 -ForegroundColor Magenta

# Perform comprehensive health checks
if (-not $NoHealthCheck) {
    Write-Info "Performing health checks..."
    Write-Host ""
    
    $services = @(
        @{ Name = "OpenSearch Database"; Url = $OPENSEARCH_URL },
        @{ Name = "OpenSearch Dashboard"; Url = $OPENSEARCH_DASHBOARD_URL },
        @{ Name = "FastAPI Backend"; Url = $HEALTH_ENDPOINT },
        @{ Name = "Streamlit Frontend"; Url = $FRONTEND_URL }
    )
    
    $allHealthy = $true
    foreach ($service in $services) {
        $isHealthy = Test-ServiceHealth -Url $service.Url -ServiceName $service.Name
        if (-not $isHealthy) {
            $allHealthy = $false
        }
    }
    
    Write-Host ""
    if ($allHealthy) {
        Write-Success "🎊 All services are running and healthy!"
        
        # Open Streamlit in browser with correct localhost URL
        Write-Info "Opening Streamlit app in your default browser..."
        Start-Process "http://localhost:8501"
    } else {
        Write-Warning "Some services may need more time to start up"
    }
}

# Service URLs
Write-Host ""
Write-Info "📋 Service URLs:"
Write-Host "   • OpenSearch:          $OPENSEARCH_URL" -ForegroundColor White
Write-Host "   • OpenSearch Dashboard: $OPENSEARCH_DASHBOARD_URL" -ForegroundColor White
Write-Host "   • FastAPI Backend:     $BACKEND_URL" -ForegroundColor White
Write-Host "   • FastAPI Docs:        $BACKEND_URL/docs" -ForegroundColor White
Write-Host "   • Streamlit Frontend:  $FRONTEND_URL" -ForegroundColor White

Write-Host ""
Write-Info "📝 Development Commands:"
Write-Host "   • Stop all services:   .\windows_dev_mode.ps1 -StopOnly" -ForegroundColor Yellow
Write-Host "   • View backend logs:   Get-Job | Receive-Job" -ForegroundColor Yellow
Write-Host "   • Docker logs:         docker-compose logs -f opensearch" -ForegroundColor Yellow

Write-Host ""
Write-Success "🚀 Development environment is ready! Happy coding!"
Write-Host ""
