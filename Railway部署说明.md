# 🚀 Railway部署说明

## ✅ 准备就绪

我已经为您准备好Railway配置：
- ✅ `railway.toml`
- ✅ `Procfile`
- ✅ 代码已就绪

---

## 📝 部署步骤（5分钟）

### 方法1：通过Railway网站（最简单）

#### 1. 访问Railway
https://railway.app

#### 2. 登录
- 选择GitHub登录
- 授权Railway访问您的GitHub

#### 3. 创建项目
1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择您的仓库（需要先推送到GitHub）

#### 4. 配置环境变量
在Settings → Variables添加：
```
TELEGRAM_BOT_TOKEN=您的token
DEEPSEEK_API_KEY=您的key
ADMIN_GROUP_ID=您的group ID
```

#### 5. 部署
点击 "Deploy" 按钮！

---

### 方法2：通过CLI（自动化）

```bash
# 1. 安装Railway CLI
npm install -g @railway/cli

# 2. 登录
railway login

# 3. 初始化项目
railway init

# 4. 链接项目
railway link

# 5. 添加环境变量
railway variables set TELEGRAM_BOT_TOKEN=您的token
railway variables set DEEPSEEK_API_KEY=您的key

# 6. 部署
railway up
```

---

## ⚡ 最快方案

### 通过GitHub（推荐）

**步骤**：

1. **创建GitHub仓库**
```bash
cd /Users/hack/AI招聘
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/您的用户名/AI招聘.git
git push -u origin main
```

2. **在Railway连接GitHub**
- 访问 railway.app
- 登录（GitHub）
- 选择"Deploy from GitHub"
- 选择仓库
- 点击Deploy

3. **配置环境变量**
在Railway界面添加环境变量

4. **完成！** 🎉

---

## 🎯 需要帮助吗？

**我可以帮您**：
1. 创建GitHub仓库
2. 推送代码
3. 配置部署

**您需要我继续吗？**

