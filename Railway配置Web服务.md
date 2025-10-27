# Railway配置Web服务步骤

## ✅ 代码已更新并推送

Flask现在使用根目录的 user_data.db（与Bot共享）

## 📋 接下来需要在Railway操作

### 1. 检查服务列表
在Railway Dashboard中，您应该看到：
- ✅ worker（已有）- Bot服务
- 🆕 web（需要创建或已自动创建）- 后台服务

### 2. 如果Railway已自动创建web服务

Railway会检测Procfile，自动创建web服务。

#### 需要配置的环境变量（复制worker的）：

在web服务的Settings → Variables中添加：

```
TELEGRAM_BOT_TOKEN = (复制worker服务的值)
DEEPSEEK_API_KEY = (复制worker服务的值)
ADMIN_GROUP_ID = (复制worker服务的值)
```

### 3. 如果没有自动创建web服务

需要手动添加服务：
1. 在Railway项目中点击 "New"
2. 选择 "Empty Service"
3. 连接到同一个GitHub仓库
4. Railway会自动检测Procfile中的web配置

### 4. 获取Web服务URL

1. 在web服务中，点击 "Settings"
2. 找到 "Domains"
3. 点击 "Generate Domain"
4. 复制生成的URL（类似：xxx.up.railway.app）

### 5. 访问测试

访问：https://你的域名.up.railway.app/users
- 使用 admin / admin123 登录
- 应该能看到实时的用户数据

## 🎯 完成后

Bot和Web共享同一个数据库，数据实时同步！

---

请按以下步骤操作：
1. 打开Railway Dashboard
2. 查看是否有web服务
3. 如果有，告诉我URL
4. 如果没有，告诉我，我继续指导
