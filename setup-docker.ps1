#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Quick setup script for Contract Intelligence Assistant

.DESCRIPTION
    This script sets up and runs the Contract Intelligence Assistant using Docker.
    It handles environment setup and starts all required services.

.PARAMETER ApiKey
    Your OpenAI API key. If not provided, you'll be prompted to enter it.

.PARAMETER Mode
    Deployment mode: 'dev' or 'prod'. Default is 'dev'.

.EXAMPLE
    .\setup-docker.ps1 -ApiKey "your-api-key-here"
    
.EXAMPLE  
    .\setup-docker.ps1 -Mode prod
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod")]
    [string]$Mode = "dev"
)

Write-Host "🚀 Contract Intelligence Assistant - Docker Setup" -ForegroundColor Cyan
Write-Host "=" * 60

# Check if Docker is installed
try {
    docker --version | Out-Null
    docker-compose --version | Out-Null
    Write-Host "✅ Docker and Docker Compose are installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker or Docker Compose not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Get API key if not provided
if (-not $ApiKey) {
    $ApiKey = Read-Host "Enter your OpenAI API key"
    if (-not $ApiKey) {
        Write-Host "❌ OpenAI API key is required" -ForegroundColor Red
        exit 1
    }
}

# Set environment variable
$env:OPENAI_API_KEY = $ApiKey
Write-Host "✅ OpenAI API key configured" -ForegroundColor Green

# Set additional environment variables based on mode
if ($Mode -eq "prod") {
    $env:ENVIRONMENT = "production"
    $env:DEBUG = "false"
    Write-Host "✅ Production mode enabled" -ForegroundColor Green
} else {
    $env:ENVIRONMENT = "development"  
    $env:DEBUG = "true"
    Write-Host "✅ Development mode enabled" -ForegroundColor Green
}

# Create necessary directories
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Name "logs" | Out-Null
    Write-Host "✅ Created logs directory" -ForegroundColor Green
}

# Stop any existing containers
Write-Host "🛑 Stopping any existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# Build and start services
Write-Host "🏗️ Building and starting services..." -ForegroundColor Yellow
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SUCCESS! All services are starting up..." -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Access your application:" -ForegroundColor Cyan
    Write-Host "   • Main UI (Streamlit):     http://localhost:8501" -ForegroundColor White
    Write-Host "   • API Documentation:      http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   • API Health Check:       http://localhost:8000/health" -ForegroundColor White
    Write-Host "   • OpenSearch:             http://localhost:9200" -ForegroundColor White
    Write-Host "   • OpenSearch Dashboard:   http://localhost:5601" -ForegroundColor White
    Write-Host ""
    Write-Host "⏳ Services are starting up. Please wait 30-60 seconds before accessing." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📊 Monitor service status:" -ForegroundColor Cyan
    Write-Host "   docker-compose ps" -ForegroundColor White
    Write-Host "   docker-compose logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "🛑 To stop all services:" -ForegroundColor Cyan
    Write-Host "   docker-compose down" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Failed to start services. Check the logs:" -ForegroundColor Red
    Write-Host "   docker-compose logs" -ForegroundColor White
    exit 1
}
