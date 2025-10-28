#!/bin/bash
echo "=== 检查本地Bot ==="
ps aux | grep tg_bot | grep -v grep || echo "无本地进程"
echo ""
echo "=== 测试Telegram连接是否被占用 ==="
curl -s "https://api.telegram.org/bot7751111095:AAGy0YC7sVndtxboAaKYm1P_WPDsip9XVx0/getUpdates" | head -100
