# Start Medical Telegram Warehouse Services

Write-Host "🚀 Starting Medical Telegram Warehouse..." -ForegroundColor Green
Write-Host "=" * 60

# Check Docker
Write-Host "
🐳 Checking Docker..." -ForegroundColor Cyan
docker --version
if (1 -ne 0) {
    Write-Host "❌ Docker not found. Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check if containers are already running
Write-Host "
📊 Checking existing containers..." -ForegroundColor Cyan
 = docker ps --format "table {{.Names}}\t{{.Status}}"
if ( -like "*medical-telegram*") {
    Write-Host "⚠️  Some services are already running" -ForegroundColor Yellow
    docker ps --filter "name=medical-telegram" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
     = Read-Host "
Restart services? (y/n)"
    if ( -eq 'y') {
        Write-Host "🔄 Stopping existing services..." -ForegroundColor Cyan
        docker-compose -f docker-compose.prod.yml down
        Start-Sleep -Seconds 3
    }
}

# Start services
Write-Host "
🚀 Starting services..." -ForegroundColor Cyan
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
Write-Host "
⏳ Waiting for services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check service status
Write-Host "
📊 Service Status:" -ForegroundColor Cyan
docker ps --filter "name=medical-telegram" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test API health
Write-Host "
🌐 Testing API health..." -ForegroundColor Cyan
try {
     = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10
    if (.StatusCode -eq 200) {
        Write-Host "✅ API is healthy" -ForegroundColor Green
         = .Content | ConvertFrom-Json
        Write-Host "   Status: "
        Write-Host "   Version: "
    }
} catch {
    Write-Host "❌ API health check failed" -ForegroundColor Red
}

# Open browser tabs
Write-Host "
🔗 Opening applications..." -ForegroundColor Cyan
 = Read-Host "Open applications in browser? (y/n)"
if ( -eq 'y') {
    Start-Process "http://localhost:8000/docs"
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:3000"
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:3001"
}

Write-Host "
🎉 Services started successfully!" -ForegroundColor Green
Write-Host "
📋 Access Points:" -ForegroundColor Yellow
Write-Host "   FastAPI Docs: http://localhost:8000/docs"
Write-Host "   Dagster UI: http://localhost:3000"
Write-Host "   Grafana: http://localhost:3001 (admin/admin)"
Write-Host "   Prometheus: http://localhost:9090"

Write-Host "
🔧 Management Commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
Write-Host "   Stop services: docker-compose -f docker-compose.prod.yml down"
Write-Host "   Restart: docker-compose -f docker-compose.prod.yml restart"
Write-Host "   View containers: docker ps --filter name=medical-telegram"

Write-Host "
📈 To run the pipeline:" -ForegroundColor Cyan
Write-Host "   1. Go to http://localhost:3000"
Write-Host "   2. Select 'medical_telegram_etl_job'"
Write-Host "   3. Click 'Launchpad' and then 'Materialize'"

Write-Host "
" + "=" * 60
