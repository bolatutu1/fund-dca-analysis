# 基金定投分析网站 - Windows 快速部署脚本
# 使用方法: powershell -ExecutionPolicy Bypass -File deploy.ps1

Write-Host "🚀 开始部署基金定投分析网站..." -ForegroundColor Green

# 检查 Python 是否安装
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python 未安装，请先安装 Python 3.10+" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 检查 pip 是否安装
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "❌ pip 未安装" -ForegroundColor Red
    exit 1
}

# 创建虚拟环境
Write-Host "🔧 创建虚拟环境..." -ForegroundColor Cyan
python -m venv venv

# 激活虚拟环境
Write-Host "▶️  激活虚拟环境..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "📦 安装 Python 依赖..." -ForegroundColor Cyan
pip install -r requirements.txt

# 创建数据目录
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data"
}

# 启动服务
Write-Host "🌐 启动服务..." -ForegroundColor Cyan
cd src
python -m uvicorn main:app --host 0.0.0.0 --port 8000

Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host "🌐 访问地址: http://localhost:8000" -ForegroundColor Yellow
