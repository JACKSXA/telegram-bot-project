# 🚀 Railway部署详细步骤

## ✅ 已登录Railway

### 接下来的步骤

#### 1. 创建新项目
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 会显示您的仓库列表

#### 2. 选择仓库
- 找到并点击 `telegram-bot-project`
- 允许Railway访问仓库

#### 3. 等待部署开始
- Railway会自动检测Python项目
- 开始构建和部署

---

## ⚙️ 配置环境变量

部署开始后，需要添加环境变量。

### 在Settings → Variables添加：

```
TELEGRAM_BOT_TOKEN=7751111095:AAGy0YC7sVndtxboAaKYm1P_WPDsip9XVx0
DEEPSEEK_API_KEY=sk-74952315413e42eb881e184eed273df4
ADMIN_GROUP_ID=-1003231939055
```

---

## 🎯 配置启动命令

### 在Deploy Settings → Start Command设置：

```
python tg_bot_v2.py
```

---

## ✅ 部署完成后的效果

### 将获得
- ✅ Bot 24/7运行
- ✅ 电脑关机不影响
- ✅ 可以部署Webhook
- ✅ 可以获取真实IP地址

---

## 📊 部署状态

访问Railway Dashboard可以看到：
- 构建日志
- 运行状态
- 日志输出
- 访问URL

---

**您现在在Railway上看到了什么界面？**

