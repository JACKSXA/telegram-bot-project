#!/bin/bash
# 设置定时备份任务

echo "🔧 设置自动备份任务..."
echo ""

# 获取当前脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 创建备份脚本路径
BACKUP_SCRIPT="$SCRIPT_DIR/auto_backup.py"

# 设置每日凌晨2点自动备份
CRON_JOB="0 2 * * * cd $SCRIPT_DIR && source venv/bin/activate && python auto_backup.py backup"

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "auto_backup.py"; then
    echo "⚠️  备份任务已存在"
    crontab -l | grep "auto_backup.py"
    echo ""
    echo "是否要更新？(y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        # 删除旧任务
        crontab -l 2>/dev/null | grep -v "auto_backup.py" | crontab -
        # 添加新任务
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        echo "✅ 备份任务已更新"
    fi
else
    # 添加新任务
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ 备份任务已添加"
fi

echo ""
echo "📋 当前定时任务："
crontab -l | grep "auto_backup.py"

echo ""
echo "💡 手动执行备份："
echo "   python auto_backup.py backup"
echo ""
echo "📋 查看备份列表："
echo "   python auto_backup.py list"

