#!/bin/bash

# 快速更新招聘页面的Telegram Bot链接

echo "================================"
echo "  更新Telegram Bot链接工具"
echo "================================"
echo ""

# 获取用户输入
read -p "请输入您的Telegram Bot用户名（不含@）: " bot_username

if [ -z "$bot_username" ]; then
    echo "❌ 错误：Bot用户名不能为空"
    exit 1
fi

# 备份原文件
cp recruitment.html recruitment.html.bak
echo "✅ 已备份原文件为 recruitment.html.bak"

# 替换链接
sed -i '' "s|https://t.me/YOUR_BOT_USERNAME|https://t.me/$bot_username|g" recruitment.html
sed -i '' "s|@YOUR_BOT_USERNAME|@$bot_username|g" recruitment.html

echo "✅ 更新成功！"
echo ""
echo "新的Bot链接："
echo "  https://t.me/$bot_username"
echo ""
echo "预览页面："
open recruitment.html

echo ""
echo "================================"
echo "  更新完成！"
echo "================================"

