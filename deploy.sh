#!/bin/bash

# 基金定投分析网站 - 快速部署脚本
# 使用方法: bash deploy.sh

set -e

echo "🚀 开始部署基金定投分析网站..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，正在安装..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down 2>/dev/null || true

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "▶️  启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示访问地址
echo ""
echo "✅ 部署完成！"
echo "🌐 访问地址: http://localhost:8000"
echo ""
echo "📋 常用命令:"
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
