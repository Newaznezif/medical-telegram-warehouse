Write-Host "🚀 Deploying Telegram Medical Warehouse API" -ForegroundColor Cyan
Write-Host "=" * 50

# Check Docker installation
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host "
📦 Building Docker images..." -ForegroundColor Yellow
docker-compose build

Write-Host "
🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "
⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "
🧪 Testing API..." -ForegroundColor Cyan
try {
     = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    Write-Host "✅ API is running: " -ForegroundColor Green
} catch {
    Write-Host "❌ API test failed: " -ForegroundColor Red
}

Write-Host "
🌐 Services deployed:" -ForegroundColor Cyan
Write-Host "API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "PostgreSQL: localhost:5432" -ForegroundColor Yellow
Write-Host "PgAdmin: http://localhost:5050" -ForegroundColor Yellow
Write-Host "Redis: localhost:6379" -ForegroundColor Yellow

Write-Host "
📋 Docker containers:" -ForegroundColor Cyan
docker-compose ps

Write-Host "
🎯 Deployment complete!" -ForegroundColor Green
Write-Host "Use 'docker-compose logs -f api' to view logs" -ForegroundColor Gray
Write-Host "Use 'docker-compose down' to stop services" -ForegroundColor Gray
