import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化DeepSeek客户端
deepseek_client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# 读取剧本文件作为系统提示词
def load_script():
    script_path = os.path.join(os.path.dirname(__file__), '演练记录-Web3诈骗剧本.md')
    with open(script_path, 'r', encoding='utf-8') as f:
        return f.read()

try:
    SCRIPT = load_script()
    print("✅ 剧本文件加载成功")
except Exception as e:
    print(f"❌ 剧本文件加载失败: {e}")
    SCRIPT = ""

# 系统提示词
SYSTEM_PROMPT = f"""你是一个Web3诈骗演练助手。这是在实验室环境下的反诈演练。

你的角色：诈骗者
用户的角色：演练者（受害者）

你必须严格按照以下剧本进行演练，全程使用中文沟通：

{SCRIPT}

重要规则：
1. 严格按照剧本的阶段顺序进行
2. 不要跳步骤，等用户确认后再进行下一步
3. 使用剧本中的专业话术，完全按照剧本的具体格式、符号、内容回复
4. 保持诈骗者的角色，不要透露这是演练
5. 如果用户提出质疑，使用剧本中的应对话术
6. 记住当前进行到哪个阶段，保持连贯性
7. 不要说"这是演练"、"这是模拟"等话
8. 严格按照剧本的具体话术回复，包括箭头符号→、分隔线、格式等都要保持一致
9. 不要添加任何多余的解释或提示
10. 完全进入诈骗者角色，按照剧本一步步引导

现在开始演练，从阶段一开始。
"""

# 存储用户会话上下文
user_conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "用户"
    
    print(f"[启动] 用户 {user_id} (@{username}) 开始新会话")
    
    # 初始化用户会话
    user_conversations[user_id] = []
    
    # 发送开场白（阶段一）
    welcome_message = """💥 Web3量化套利内部通道
→ 日化2-5个点稳定收益
→ 机构资金保驾护航
→ 新人首次合作送$100 USDT真实资金
→ 感兴趣了解一下吗？"""
    
    await update.message.reply_text(welcome_message)
    
    # 保存到会话历史
    user_conversations[user_id].append({
        "role": "assistant",
        "content": welcome_message
    })

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /reset 命令 - 重置会话"""
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    print(f"[重置] 用户 {user_id} 重置会话")
    await update.message.reply_text("✅ 会话已重置，输入 /start 重新开始演练")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户消息"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    print(f"[消息] 用户 {user_id}: {user_message[:50]}...")
    
    # 如果用户没有会话，先初始化
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    # 添加用户消息到历史
    user_conversations[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    # 调用DeepSeek API
    try:
        # 发送"正在输入"状态
        await update.message.chat.send_action(action="typing")
        
        print(f"[DeepSeek] 调用API中...")
        
        # 构建消息列表（包含系统提示词）
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + user_conversations[user_id]
        
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        # 获取AI回复
        ai_response = response.choices[0].message.content
        
        print(f"[DeepSeek] 回复: {ai_response[:100]}...")
        
        # 保存AI回复到历史
        user_conversations[user_id].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # 发送回复给用户（如果超过4096字符，分段发送）
        if len(ai_response) <= 4096:
            await update.message.reply_text(ai_response)
        else:
            # 分段发送
            chunks = [ai_response[i:i+4096] for i in range(0, len(ai_response), 4096)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
                await asyncio.sleep(0.5)  # 避免发送太快
        
    except Exception as e:
        error_msg = f"系统出错：{str(e)}"
        print(f"[错误] {error_msg}")
        await update.message.reply_text("抱歉，系统遇到了问题，请稍后再试或使用 /reset 重置会话")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看当前会话状态"""
    user_id = update.effective_user.id
    
    if user_id not in user_conversations or not user_conversations[user_id]:
        await update.message.reply_text("❌ 当前没有活动会话\n\n输入 /start 开始演练")
    else:
        message_count = len(user_conversations[user_id])
        user_msg_count = sum(1 for m in user_conversations[user_id] if m['role'] == 'user')
        ai_msg_count = sum(1 for m in user_conversations[user_id] if m['role'] == 'assistant')
        
        status_text = f"""📊 会话状态

总消息数：{message_count}
用户消息：{user_msg_count}
AI回复：{ai_msg_count}

命令：
/start - 开始新演练
/reset - 重置会话
/status - 查看状态
/help - 帮助信息"""
        
        await update.message.reply_text(status_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示帮助信息"""
    help_text = """🤖 Web3反诈演练Bot

这是一个用于Web3诈骗识别培训的演练机器人。

📋 可用命令：
/start - 开始演练（从阶段一开始）
/reset - 重置会话，重新开始
/status - 查看当前会话状态
/help - 显示此帮助信息

💡 使用说明：
1. 输入 /start 开始演练
2. 机器人会扮演诈骗者
3. 您按照提示进行互动
4. 体验完整的诈骗流程
5. 学习识别诈骗套路

⚠️ 注意：
这是教育演练，请勿使用真实资金！

🤖 AI引擎：DeepSeek (中文优化)
"""
    await update.message.reply_text(help_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """错误处理"""
    print(f"[严重错误] {context.error}")
    if update and update.message:
        await update.message.reply_text("系统遇到错误，请稍后再试")

def main():
    """主函数"""
    print("=" * 50)
    print("🚀 Web3反诈演练 Telegram Bot")
    print("🤖 AI引擎：DeepSeek (中文优化)")
    print("=" * 50)
    
    # 检查环境变量
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not bot_token:
        print("❌ 错误：未找到 TELEGRAM_BOT_TOKEN")
        print("请在 .env 文件中设置 TELEGRAM_BOT_TOKEN")
        return
    
    if not api_key:
        print("❌ 错误：未找到 DEEPSEEK_API_KEY")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        return
    
    print(f"✅ Bot Token: {bot_token[:20]}...")
    print(f"✅ DeepSeek API Key: {api_key[:20]}...")
    
    # 创建Application
    application = Application.builder().token(bot_token).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 添加错误处理器
    application.add_error_handler(error_handler)
    
    # 启动Bot
    print("✅ Bot 启动成功！")
    print("📱 请在 Telegram 中找到您的 Bot 并发送 /start")
    print("-" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
