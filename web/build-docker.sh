#!/bin/bash

# DeerFlow Web Docker Build Script
# 用于构建前端 Docker 镜像的脚本

set -e  # 遇到错误时退出

echo "🚀 开始构建 DeerFlow Web Docker 镜像..."

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：请在 web 目录下运行此脚本"
    exit 1
fi

# 设置镜像名称和标签
IMAGE_NAME="deer-flow-web"
TAG=${1:-latest}
FULL_IMAGE_NAME="$IMAGE_NAME:$TAG"

echo "📦 构建镜像: $FULL_IMAGE_NAME"

# 构建 Docker 镜像
docker build \
    --build-arg NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000} \
    -t "$FULL_IMAGE_NAME" \
    .

if [ $? -eq 0 ]; then
    echo "✅ Docker 镜像构建成功: $FULL_IMAGE_NAME"
    echo ""
    echo "🔧 运行镜像："
    echo "docker run -p 3000:3000 $FULL_IMAGE_NAME"
    echo ""
    echo "🔧 或者使用环境变量："
    echo "docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://your-api-url:8000 $FULL_IMAGE_NAME"
else
    echo "❌ Docker 镜像构建失败"
    exit 1
fi
