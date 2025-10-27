# 🚀 Vercel部署指南 - 获取真实IP

## ✅ 准备就绪

IP查询API已经测试通过！现在可以部署了。

---

## 📋 部署步骤

### 方法1：通过Vercel CLI（推荐）

#### 1. 安装Vercel CLI
```bash
npm install -g vercel
```

#### 2. 登录Vercel
```bash
vercel login
```

#### 3. 部署项目
```bash
cd /Users/hack/AI招聘
vercel
```

#### 4. 设置环境变量
```bash
vercel env add TELEGRAM_BOT_TOKEN
vercel env add DEEPSEEK_API_KEY
# 输入相应的值
```

---

### 方法2：通过GitHub（自动化）

#### 1. 推送代码到GitHub
```bash
git init
git add .
git commit -m "Add Webhook support"
git push origin main
```

#### 2. 在Vercel连接GitHub仓库

1. 访问 https://vercel.com
2. 点击 "Import Project"
3. 选择你的GitHub仓库
4. 设置环境变量：
   - `TELEGRAM_BOT_TOKEN`
   - `DEEPSEEK_API_KEY`
5. 点击 "Deploy"

---

## 🔧 配置Webhook

部署完成后，在Vercel设置Webhook：

```python
import requests

# 你的Vercel部署URL
WEBHOOK_URL = "https://your-project.vercel.app/api/webhook"

# 设置Webhook
response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)

print(response.json())
```

---

## 📊 可获得的信息

部署后，在后台将显示：

```
用户ID: 123456789
真实IP: 123.456.789.0
国家: 🇺🇸 United States
地区: California
城市: San Francisco
ISP: AT&T
坐标: 37.7749, -122.4194
时区: America/Los_Angeles
代理: 否
```

---

## ⚡ 快速开始

我可以帮您：
1. 安装Vercel CLI
2. 部署代码
3. 配置Webhook
4. 测试功能

**需要我现在开始吗？**
