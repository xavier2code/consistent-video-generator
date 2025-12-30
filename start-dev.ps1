# Development Environment Startup Script
# Start both frontend and backend services

Write-Host "Starting development environment..." -ForegroundColor Green

# Start backend service
Write-Host "`nStarting backend service (http://localhost:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; & .\venv\Scripts\Activate.ps1; python main.py"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend service
Write-Host "Starting frontend service (http://127.0.0.1:3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\web'; npm run dev"

Write-Host "`nDevelopment environment started!" -ForegroundColor Green
Write-Host "- Frontend: http://127.0.0.1:3000" -ForegroundColor Yellow
Write-Host "- Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "- API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
