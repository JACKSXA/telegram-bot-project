# 🚀 Railway部署步骤

## ✅ GitHub推送完成

代码已推送到：https://github.com/JACKSXA/telegram-bot-project

---

## 📝 Railway部署步骤

### 1. 访问Railway
https://railway.app

### 2. 登录
- 点击 "Login"
- 选择 "GitHub" 登录
- 授权Railway

### 3. 创建项目
1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 找到并选择 `telegram-bot-project`
4. 点击 "Deploy"

### 4. 配置环境变量
在项目 → Settings → Variables 添加：

```
TELEGRAM_BOT_TOKEN=您的Bot Token
DEEPSEEK_API_KEY=您的API Key
ADMIN_GROUP_ID=您的群组ID
```

### 5. 配置启动命令
在Settings → Deploy → Start Command：
```
python tg_bot_v2.py
```

---

## ✅ 部署后

### 访问地址
- Railway会提供一个URL（如：xxx.railway.app）

### 功能
- ✅ Bot 24/7运行
- ✅ 可以部署Webhook
- ✅ 可以获取真实IP
- ✅ 自动重启

---

## 🎯 立即开始

访问：https://railway.app → 开始部署！

