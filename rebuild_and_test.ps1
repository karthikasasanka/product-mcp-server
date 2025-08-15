# PowerShell script to rebuild and restart containers with enhanced logging

Write-Host "🔧 Rebuilding and restarting containers with enhanced logging..." -ForegroundColor Green

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Remove old images to ensure fresh build
Write-Host "🧹 Removing old images..." -ForegroundColor Yellow
docker-compose down --rmi all

# Build and start containers
Write-Host "🔨 Building and starting containers..." -ForegroundColor Yellow
docker-compose up --build -d

# Wait for containers to be ready
Write-Host "⏳ Waiting for containers to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check container status
Write-Host "📊 Container status:" -ForegroundColor Cyan
docker-compose ps

# Show logs from all containers
Write-Host "📋 Recent logs from all containers:" -ForegroundColor Cyan
docker-compose logs --tail=20

Write-Host "✅ Containers rebuilt and restarted!" -ForegroundColor Green
Write-Host "🎯 You can now run: python test_containers.py" -ForegroundColor Cyan
Write-Host "📋 Or check individual container logs with: docker logs <container-name>" -ForegroundColor Cyan
