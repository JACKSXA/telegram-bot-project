#!/bin/bash

echo "================================"
echo "  GitHub Pages 快速部署"
echo "================================"
echo ""

# 检查是否安装git
if ! command -v git &> /dev/null; then
    echo "❌ 错误：未安装Git"
    echo "请先安装Git：https://git-scm.com/"
    exit 1
fi

# 获取用户信息
read -p "请输入您的GitHub用户名: " github_username
read -p "请输入仓库名称（例如：web3-recruitment）: " repo_name

if [ -z "$github_username" ] || [ -z "$repo_name" ]; then
    echo "❌ 错误：用户名和仓库名不能为空"
    exit 1
fi

echo ""
echo "📝 准备部署..."

# 创建临时目录
TEMP_DIR="temp_deploy"
mkdir -p $TEMP_DIR
cd $TEMP_DIR

# 复制文件并重命名为index.html
cp ../recruitment.html index.html

# 初始化git
git init
git add index.html
git commit -m "Initial deployment"

# 设置远程仓库
git branch -M main
git remote add origin https://github.com/$github_username/$repo_name.git

echo ""
echo "📤 正在推送到GitHub..."
echo "请在提示时输入GitHub密码或Personal Access Token"
echo ""

# 推送到GitHub
git push -u origin main

echo ""
echo "✅ 文件已推送到GitHub！"
echo ""
echo "📝 接下来的步骤："
echo "1. 访问：https://github.com/$github_username/$repo_name"
echo "2. 点击 Settings → Pages"
echo "3. Source 选择 'main' 分支"
echo "4. 点击 Save"
echo "5. 等待1-2分钟"
echo ""
echo "🌐 您的页面将发布在："
echo "   https://$github_username.github.io/$repo_name"
echo ""

# 清理
cd ..
# rm -rf $TEMP_DIR

echo "================================"
echo "  部署完成！"
echo "================================"

