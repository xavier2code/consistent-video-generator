# 开发环境启动脚本
# 同时启动前端和后端服务

Write-Host "启动开发环境..." -ForegroundColor Green

# 启动后端服务（后台运行）
Write-Host "`n启动后端服务 (http://localhost:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& .\venv\Scripts\Activate.ps1; python main.py"

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端服务（后台运行）
Write-Host "启动前端服务 (http://127.0.0.1:3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd web; npm run dev"

Write-Host "`n开发环境已启动！" -ForegroundColor Green
Write-Host "- 前端地址: http://127.0.0.1:3000" -ForegroundColor Yellow
Write-Host "- 后端地址: http://localhost:8000" -ForegroundColor Yellow
Write-Host "- API文档: http://localhost:8000/docs" -ForegroundColor Yellow
