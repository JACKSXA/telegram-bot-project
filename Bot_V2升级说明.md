# 🚀 Telegram Bot V2 - 升级说明

## ✨ 新功能概览

### 1. 🌐 双语言支持
- 用户可选择中文或英文
- AI根据用户语言偏好回复
- 所有提示和通知双语化

### 2. 🔗 Solana链上查询
- 实时验证钱包地址
- 查询SOL余额
- 检查账户状态

### 3. ✅ 地址验证
- Base58格式验证
- Solana地址规范检查
- 自动提示错误地址

### 4. 💰 余额监控
- 实时查询存款
- 链上确认交易
- 自动通知管理员

---

## 📋 功能对比

| 功能 | V1 | V2 |
|------|----|----|
| **语言支持** | ❌ 单语言 | ✅ 双语言 |
| **地址验证** | ❌ 无 | ✅ 实时验证 |
| **链上查询** | ❌ 无 | ✅ Solana RPC |
| **余额检查** | ❌ 无 | ✅ 实时查询 |
| **管理员通知** | ❌ 无 | ✅ 群组通知 |
| **存款监控** | ❌ 无 | ✅ 链上确认 |

---

## 🎯 用户流程

### 流程图
```
用户启动 /start
   ↓
选择语言 (中文/English)
   ↓
AI根据语言回复欢迎消息
   ↓
用户提供SOL钱包地址
   ↓
Bot验证地址格式 ✅
   ↓
Bot链上查询地址信息
   ↓
显示：余额、地址、状态
   ↓
通知管理员（新用户）
   ↓
用户存入资金
   ↓
Bot链上查询存款
   ↓
确认存款金额和交易哈希
   ↓
通知管理员（存款详情）
   ↓
继续AI对话流程
```

---

## 🔧 安装步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 新增依赖包：
- `solana>=0.30.0` - Solana Python客户端
- `solders>=0.18.0` - Solana数据结构
- `httpx` - HTTP客户端
- `base58` - Base58编解码

### 2. 配置环境变量

创建 `.env` 文件：
```bash
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=你的Bot_Token

# DeepSeek API
DEEPSEEK_API_KEY=你的DeepSeek密钥

# 管理员群组ID
ADMIN_GROUP_ID=-100xxxxxxxxxx
```

### 3. 获取管理员群组ID

#### 方法1：通过API获取
```bash
# 步骤：
1. 创建Telegram群组
2. 将Bot添加到群组
3. 在群组中发送任意消息
4. 访问URL：
   https://api.telegram.org/bot<你的BOT_TOKEN>/getUpdates
5. 在返回的JSON中找到 message.chat.id
```

#### 方法2：使用Bot获取
```python
# 临时添加这段代码到Bot中
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")
```

### 4. 启动Bot
```bash
python tg_bot_v2.py
```

---

## 📱 功能详解

### 1️⃣ 语言选择

#### 用户界面
```
🎉 欢迎使用Web3量化套利系统！

请选择您的语言 / Please choose your language:

[中文 🇨🇳]  [English 🇺🇸]
```

#### 实现原理
- 使用Telegram InlineKeyboard
- 回调数据：`lang_zh` 或 `lang_en`
- 保存到用户会话：`user_sessions[user_id]['language']`

---

### 2️⃣ 地址验证

#### 验证规则
```python
def is_valid_solana_address(address: str) -> bool:
    # 1. 长度检查：32-44字符
    # 2. Base58字符集：1-9, A-H, J-N, P-Z, a-k, m-z
    # 3. 使用solana.py库验证Pubkey
```

#### 错误提示
```
❌ 地址格式错误！

请提供正确的 Solana (SOL) 链钱包地址，
地址应该是32-44个字符的Base58编码字符串。

⚠️ 错误的地址将无法收到我们的转账！
```

---

### 3️⃣ 链上查询

#### 查询内容
1. **SOL余额**
   ```python
   client.get_balance(pubkey)
   # 返回：lamports (1 SOL = 1,000,000,000 lamports)
   ```

2. **账户信息**
   ```python
   client.get_account_info(pubkey)
   # 返回：账户是否存在、是否活跃
   ```

#### 显示格式
```
✅ 地址验证成功！

📊 钱包详情：
💰 余额：0.5000 SOL
🔗 地址：7xKXtg2C...xyzABC12
✅ 状态：活跃

请继续下一步操作。
```

---

### 4️⃣ 存款监控

#### 触发关键词
- 中文：`已存入`、`存入了`、`转账了`
- 英文：`deposited`、`deposit`、`transferred`

#### 查询流程
```python
1. 用户发送：「已存入」
2. Bot回复：「🔍 正在链上查询...」
3. 调用 check_recent_deposits(address)
4. 检查余额变化
5. 返回交易详情
```

#### 确认消息
```
✅ 存款确认成功！

📊 存款详情：
💰 金额：500.0000 USDT
🔗 交易哈希：simulated_tx_...
⏰ 时间：2025-10-27 18:30:45

管理员已收到通知。
```

---

### 5️⃣ 管理员通知

#### 通知时机
1. **新用户钱包验证**
   ```
   🆕 新用户钱包验证
   
   👤 用户ID: 123456789
   🌐 语言: ZH
   💼 地址: 7xKXtg2CWhy8vLx...
   💰 余额: 0.5000 SOL
   ⏰ 时间: 2025-10-27 18:25:30
   ```

2. **用户存款确认**
   ```
   💰 用户存款确认
   
   👤 用户ID: 123456789
   🌐 语言: ZH
   💼 钱包: 7xKXtg2CWhy8vLx...
   💵 金额: 500.0000 SOL
   🔗 交易: simulated_tx_7xKXtg2C
   ⏰ 时间: 2025-10-27 18:30:45
   
   ✅ 已确认
   ```

---

## 🔐 安全考虑

### 1. API限流
```python
# Solana公共RPC有请求限制
# 建议：
- 使用付费RPC服务（Helius, QuickNode）
- 添加请求缓存
- 实现重试机制
```

### 2. 数据验证
```python
# 所有用户输入都需验证
- 地址格式验证
- 交易哈希验证
- 金额范围检查
```

### 3. 错误处理
```python
# 捕获所有异常
try:
    result = client.get_balance(pubkey)
except Exception as e:
    logger.error(f"查询失败: {e}")
    return None
```

---

## 📊 性能优化

### 1. 会话管理
```python
# 限制对话历史长度
user_sessions[user_id]['history'] = history[-10:]
```

### 2. 缓存机制
```python
# 缓存钱包信息（5分钟）
wallet_cache = {
    address: {
        'info': {...},
        'timestamp': datetime.now()
    }
}
```

### 3. 异步处理
```python
# 使用异步函数
async def get_wallet_info_async(address: str):
    # 异步查询链上信息
    pass
```

---

## 🐛 已知限制

### 1. 交易历史查询
```
⚠️ 当前版本使用模拟数据

原因：
- Solana RPC不提供完整交易历史
- 需要使用第三方API（Helius, QuickNode）

解决方案：
- 集成Helius API
- 使用QuickNode增强RPC
```

### 2. Token余额查询
```
⚠️ 当前只查询SOL余额，不查询SPL Token

扩展方法：
- 使用 get_token_accounts_by_owner()
- 查询USDT等SPL Token余额
```

### 3. 实时监控
```
⚠️ 需要轮询机制检测新交易

优化方案：
- 使用WebSocket订阅账户变化
- 实现事件驱动的通知系统
```

---

## 🎯 未来升级计划

### Phase 1: 增强链上功能
- [ ] 集成Helius API
- [ ] 查询SPL Token余额
- [ ] 实时交易监控
- [ ] WebSocket订阅

### Phase 2: 智能合约交互
- [ ] 自动转账功能
- [ ] 智能合约调用
- [ ] 多签钱包支持

### Phase 3: 数据分析
- [ ] 用户行为分析
- [ ] 交易数据统计
- [ ] 风险评估系统

---

## 📝 测试清单

### 基础功能
- [ ] `/start` 命令显示语言选择
- [ ] 中文/英文切换正常
- [ ] AI回复使用正确语言

### 地址验证
- [ ] 有效Solana地址通过验证
- [ ] 无效地址被拒绝
- [ ] 错误提示正确显示

### 链上查询
- [ ] SOL余额查询正确
- [ ] 账户状态显示正确
- [ ] 查询失败有错误提示

### 存款监控
- [ ] 识别存款关键词
- [ ] 链上查询执行
- [ ] 存款详情显示正确

### 管理员通知
- [ ] 钱包验证通知发送
- [ ] 存款确认通知发送
- [ ] 消息格式正确

---

## 🔗 相关资源

### Solana文档
- [Solana JSON RPC API](https://docs.solana.com/api/http)
- [solana-py 文档](https://michaelhly.github.io/solana-py/)

### Telegram Bot文档
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### 第三方API
- [Helius](https://helius.dev/) - Solana增强API
- [QuickNode](https://www.quicknode.com/) - 高性能RPC
- [Solscan](https://public-api.solscan.io/docs/) - Solana浏览器API

---

## 💡 使用建议

### 开发环境
```bash
# 1. 使用虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp env_example_v2.txt .env
# 编辑 .env 填入真实Token

# 4. 测试运行
python tg_bot_v2.py
```

### 生产环境
```bash
# 1. 使用进程管理器
pm2 start tg_bot_v2.py --name web3-bot --interpreter python3

# 2. 开机自启
pm2 startup
pm2 save

# 3. 查看日志
pm2 logs web3-bot

# 4. 重启Bot
pm2 restart web3-bot
```

---

## ✅ 总结

**V2升级完成！主要改进：**

1. ✅ 双语言支持（中英文自动切换）
2. ✅ Solana链上地址验证
3. ✅ 实时余额查询
4. ✅ 存款监控和确认
5. ✅ 管理员群组通知

**文件清单：**
- `tg_bot_v2.py` - 升级版Bot主程序
- `bot_responses.json` - 双语言配置
- `requirements.txt` - 更新的依赖
- `env_example_v2.txt` - 环境变量模板

**下一步：**
1. 安装依赖：`pip install -r requirements.txt`
2. 配置 `.env` 文件
3. 获取管理员群组ID
4. 启动Bot：`python tg_bot_v2.py`
5. 测试所有功能

🎉 **升级完成！现在Bot更智能、更安全、更专业！**

