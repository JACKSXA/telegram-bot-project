#!/bin/bash

# 进入目录
cd "$(dirname "$0")"

# 激活虚拟环境
source ../venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -q -r requirements.txt

# 启动Flask应用
echo "🚀 启动管理后台..."
echo "📍 访问地址: http://127.0.0.1:5000"
echo "👤 默认账号: admin"
echo "🔑 默认密码: admin123"
echo ""
python flask_app.py

