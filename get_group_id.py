#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取Telegram群组ID的辅助脚本
"""

import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def main():
    print("=" * 60)
    print("📱 获取Telegram群组ID")
    print("=" * 60)
    print()
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ 错误：TELEGRAM_BOT_TOKEN 未设置")
        print("请在 .env 文件中配置")
        return
    
    print("✅ Bot Token已配置")
    print()
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        print("🔍 获取最近的更新...")
        updates = await bot.get_updates()
        
        if not updates:
            print()
            print("⚠️ 没有找到任何更新")
            print()
            print("📝 请按照以下步骤操作：")
            print("1. 创建一个新的Telegram群组")
            print("2. 将Bot添加到群组（搜索Bot用户名）")
            print("3. 将Bot设为管理员")
            print("4. 在群组中发送任意消息（如：测试）")
            print("5. 再次运行此脚本")
            print()
            return
        
        print(f"✅ 找到 {len(updates)} 条更新\n")
        print("=" * 60)
        print("📋 群组列表")
        print("=" * 60)
        
        groups_found = False
        for update in updates:
            if update.message and update.message.chat:
                chat = update.message.chat
                if chat.type in ['group', 'supergroup']:
                    groups_found = True
                    print()
                    print(f"🏢 群组名称: {chat.title}")
                    print(f"🆔 群组ID: {chat.id}")
                    print(f"📝 类型: {chat.type}")
                    print("-" * 60)
        
        if not groups_found:
            print()
            print("⚠️ 没有找到群组消息")
            print()
            print("📝 请确保：")
            print("1. Bot已添加到群组")
            print("2. 在群组中发送过消息")
            print("3. Bot有接收消息的权限")
        else:
            print()
            print("=" * 60)
            print("✅ 请将上面的群组ID复制到 .env 文件中")
            print("=" * 60)
            print()
            print("示例：")
            print("ADMIN_GROUP_ID=-1001234567890")
            print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print()
        print("请检查：")
        print("1. Bot Token是否正确")
        print("2. 网络连接是否正常")

if __name__ == '__main__':
    asyncio.run(main())

