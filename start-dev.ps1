# Development Environment Startup Script for Windows
# Start both frontend and backend services for sequence video generation

Write-Host "Starting development environment..." -ForegroundColor Green
Write-Host "Feature: Sequence Video Generation (2-6 images)" -ForegroundColor Magenta

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "`nWarning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please copy .env.example to .env and configure DASHSCOPE_API_KEY" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Start backend service
Write-Host "`nStarting backend service (http://localhost:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; & .\venv\Scripts\Activate.ps1; python main.py"

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start frontend service
Write-Host "Starting frontend service (http://127.0.0.1:3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\web'; npm run dev"

Write-Host "`nDevelopment environment started!" -ForegroundColor Green
Write-Host "- Frontend: http://127.0.0.1:3000" -ForegroundColor Yellow
Write-Host "- Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "- API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "`nTip: Upload 2-6 images to generate sequence video" -ForegroundColor Cyan
