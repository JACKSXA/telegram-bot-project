# 🚀 Telegram Bot V2 部署指南

## 📋 前置要求

- Python 3.8+
- Telegram Bot Token
- DeepSeek API Key
- 管理员群组ID

---

## 🔧 快速部署（5步完成）

### 步骤1：安装依赖

```bash
cd /Users/hack/AI招聘
pip install -r requirements.txt
```

**新增依赖：**
- `solana` - Solana区块链客户端
- `solders` - Solana数据结构
- `httpx` - HTTP客户端
- `base58` - Base58编解码

---

### 步骤2：配置环境变量

创建 `.env` 文件：

```bash
# 方法1：复制模板
cp env_example_v2.txt .env

# 方法2：直接创建
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=你的Bot_Token
DEEPSEEK_API_KEY=你的DeepSeek密钥
ADMIN_GROUP_ID=-100xxxxxxxxxx
EOF
```

**填写你的真实信息：**
```env
TELEGRAM_BOT_TOKEN=7751111095:AAGy0YC7sVndtxboAaKYm1P_WPDsip9XVx0
DEEPSEEK_API_KEY=sk-74952315413e42eb881e184eed273df4
ADMIN_GROUP_ID=-1001234567890
```

---

### 步骤3：获取管理员群组ID

#### 方法A：使用API（推荐）

1. **创建Telegram群组**
   - 打开Telegram
   - 创建新群组
   - 命名（如：Web3 Admin）

2. **添加Bot到群组**
   - 在群组设置中添加成员
   - 搜索你的Bot
   - 添加为管理员

3. **获取群组ID**
   - 在群组中发送任意消息
   - 浏览器访问：
     ```
     https://api.telegram.org/bot<你的BOT_TOKEN>/getUpdates
     ```
   - 找到 `"chat":{"id":-100xxxxxxxxxx}`
   - 复制这个ID到 `.env` 文件

#### 方法B：使用测试脚本

```python
# 创建临时脚本 get_group_id.py
from telegram import Bot
import asyncio

async def main():
    bot = Bot(token="你的BOT_TOKEN")
    updates = await bot.get_updates()
    for update in updates:
        if update.message:
            print(f"Chat ID: {update.message.chat.id}")
            print(f"Chat Title: {update.message.chat.title}")

asyncio.run(main())
```

运行：
```bash
python get_group_id.py
```

---

### 步骤4：测试Solana连接

运行测试脚本：

```bash
python test_solana.py
```

**期望输出：**
```
============================================================
🧪 Solana功能测试
============================================================

🔗 测试Solana RPC连接...
✅ 连接成功！
   版本: {'solana-core': '1.18.0'}

🔍 测试地址验证...
✅ 有效的Solana地址: 7xKXtg2CWhyXL1kVHBf... -> True
✅ 无效地址: invalid_address... -> False
✅ 以太坊地址: 0x742d35Cc6634C053... -> False
✅ 空地址: ... -> False

💰 测试余额查询...
✅ 查询成功！
   地址: 7xKXtg2C...tJtaXE
   余额: 0.5000 SOL

📊 测试账户信息查询...
✅ 账户信息获取成功！

============================================================
📊 测试结果汇总
============================================================
✅ 通过 - 连接测试
✅ 通过 - 地址验证
✅ 通过 - 余额查询
✅ 通过 - 账户信息

总计: 4/4 测试通过

🎉 所有测试通过！Bot可以正常使用Solana功能！
```

**如果测试失败：**
```bash
# 重新安装Solana依赖
pip uninstall solana solders -y
pip install solana solders --upgrade
```

---

### 步骤5：启动Bot

```bash
python tg_bot_v2.py
```

**期望输出：**
```
🚀 启动 Telegram Bot...
✅ Bot已启动，等待消息...
```

---

## 🧪 功能测试

### 测试清单

#### 1. 语言选择
```
👤 用户操作：
1. 向Bot发送 /start
2. 看到语言选择按钮

✅ 预期结果：
显示：[中文 🇨🇳] [English 🇺🇸]
```

#### 2. 中文模式
```
👤 用户操作：
1. 点击"中文"按钮
2. 发送消息："你好"

✅ 预期结果：
Bot用中文回复
```

#### 3. 英文模式
```
👤 用户操作：
1. 点击"English"按钮
2. 发送消息："Hello"

✅ 预期结果：
Bot用英文回复
```

#### 4. 地址验证（有效地址）
```
👤 用户操作：
发送Solana地址：
7xKXtg2CWhyXL1kVHBfJfHHhbhRQPdVvEULM35qJtaXE

✅ 预期结果：
🔍 正在链上查询...
✅ 地址验证成功！
📊 钱包详情：
💰 余额：X.XXXX SOL
```

#### 5. 地址验证（无效地址）
```
👤 用户操作：
发送：invalid_address_123

✅ 预期结果：
❌ 地址格式错误！
请提供正确的 Solana (SOL) 链钱包地址...
```

#### 6. 存款监控
```
👤 用户操作：
1. 提供有效地址
2. 发送："已存入"

✅ 预期结果：
🔍 正在链上查询存款...
✅ 存款确认成功！（如果有余额）
或
⚠️ 未检测到存款（如果无余额）
```

#### 7. 管理员通知
```
✅ 预期结果：
管理员群组收到通知：
🆕 新用户钱包验证
👤 用户ID: xxx
💰 余额: xxx SOL
```

---

## 🐛 常见问题

### Q1: `ModuleNotFoundError: No module named 'solana'`

**解决方案：**
```bash
pip install solana solders
```

### Q2: `TypeError: Client() missing required argument`

**解决方案：**
```python
# 确保使用正确的RPC URL
client = Client("https://api.mainnet-beta.solana.com")
```

### Q3: Bot无法接收消息

**检查清单：**
1. ✅ Bot Token正确
2. ✅ 网络连接正常
3. ✅ 没有其他实例运行
4. ✅ Bot没有被Telegram封禁

### Q4: 管理员通知不发送

**检查清单：**
1. ✅ `ADMIN_GROUP_ID` 格式正确（-100开头）
2. ✅ Bot已添加到群组
3. ✅ Bot是群组管理员
4. ✅ 群组允许Bot发送消息

### Q5: Solana查询超时

**解决方案：**
```python
# 使用付费RPC服务
# Helius: https://helius.dev/
# QuickNode: https://www.quicknode.com/

# 更新代码中的RPC_URL
SOLANA_RPC_URL = "https://your-rpc-url.com"
```

---

## ⚙️ 高级配置

### 使用付费RPC

#### Helius（推荐）

1. **注册账号：** https://helius.dev/
2. **创建项目**
3. **获取API Key**
4. **更新代码：**

```python
# 在 tg_bot_v2.py 中
SOLANA_RPC_URL = "https://mainnet.helius-rpc.com/?api-key=YOUR_API_KEY"
```

**优势：**
- ✅ 每秒100+请求
- ✅ 增强的交易历史API
- ✅ WebSocket支持
- ✅ 免费套餐可用

---

### 启用交易历史查询

```python
# 安装Helius SDK
pip install helius-sdk

# 在代码中
from helius import HeliusAPI

def get_transaction_history(address: str):
    helius = HeliusAPI("YOUR_API_KEY")
    txs = helius.get_parsed_transactions(address)
    return txs
```

---

### 添加SPL Token余额查询

```python
from solana.rpc.api import Client
from solders.pubkey import Pubkey

def get_token_balance(address: str, token_mint: str):
    """查询SPL Token余额"""
    client = Client(SOLANA_RPC_URL)
    pubkey = Pubkey.from_string(address)
    mint = Pubkey.from_string(token_mint)
    
    # 获取Token账户
    response = client.get_token_accounts_by_owner(
        pubkey,
        {"mint": mint}
    )
    
    if response.value:
        # 解析余额
        for account in response.value:
            # ... 解析逻辑
            pass
```

**常用Token Mint地址：**
```python
USDT_MINT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
```

---

## 🔒 生产环境部署

### 使用PM2（推荐）

```bash
# 1. 安装PM2
npm install -g pm2

# 2. 启动Bot
pm2 start tg_bot_v2.py --name web3-bot --interpreter python3

# 3. 设置开机自启
pm2 startup
pm2 save

# 4. 查看状态
pm2 status

# 5. 查看日志
pm2 logs web3-bot

# 6. 重启Bot
pm2 restart web3-bot

# 7. 停止Bot
pm2 stop web3-bot
```

---

### 使用systemd

创建服务文件：

```bash
sudo nano /etc/systemd/system/web3-bot.service
```

内容：
```ini
[Unit]
Description=Web3 Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/Users/hack/AI招聘
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /Users/hack/AI招聘/tg_bot_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start web3-bot

# 开机自启
sudo systemctl enable web3-bot

# 查看状态
sudo systemctl status web3-bot

# 查看日志
sudo journalctl -u web3-bot -f
```

---

## 📊 监控和日志

### 日志级别

```python
# 在 tg_bot_v2.py 中
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO  # 改为 DEBUG 查看详细日志
)
```

### 日志输出到文件

```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
```

### 查看日志

```bash
# 实时查看
tail -f bot.log

# 搜索错误
grep "ERROR" bot.log

# 查看最近100行
tail -n 100 bot.log
```

---

## ✅ 部署完成检查

### 最终检查清单

- [ ] ✅ Python 3.8+ 已安装
- [ ] ✅ 依赖包已安装
- [ ] ✅ `.env` 文件已配置
- [ ] ✅ Bot Token 有效
- [ ] ✅ DeepSeek API Key 有效
- [ ] ✅ 管理员群组ID 正确
- [ ] ✅ Solana连接测试通过
- [ ] ✅ Bot启动成功
- [ ] ✅ 语言选择功能正常
- [ ] ✅ 地址验证功能正常
- [ ] ✅ 链上查询功能正常
- [ ] ✅ 管理员通知功能正常

---

## 📞 获取支持

### 问题反馈

如果遇到问题，请提供以下信息：
1. 错误消息完整内容
2. Python版本：`python --version`
3. 依赖版本：`pip list | grep solana`
4. 日志文件内容

---

## 🎉 部署成功！

Bot现在已经可以：
- ✅ 支持中英文双语
- ✅ 实时验证Solana地址
- ✅ 查询链上余额
- ✅ 监控用户存款
- ✅ 通知管理员

**下一步：**
1. 分享Bot链接给用户
2. 监控管理员群组通知
3. 根据需要优化功能

🚀 **祝使用愉快！**

