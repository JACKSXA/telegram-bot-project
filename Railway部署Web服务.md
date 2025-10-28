# Railway部署Web服务（共享数据库）

## 当前问题
- Bot在Railway（使用 user_data.db）
- Web在Render（使用静态的 admin_web/user_data.db）
- 两者不同步

## 解决方案
在Railway部署Web服务，与Bot共享同一个数据库

## 检查Railway是否有Web服务

1. 打开Railway Dashboard
2. 查看服务列表
3. 应该有两个服务：
   - worker (Bot)
   - web (后台)

## 如果没有Web服务

Railway会自动检测Procfile中的web配置并创建服务

## 如果有Web服务

1. 查看Web服务的URL
2. 访问该URL
3. 应该能看到实时的用户数据

## 配置环境变量

Web服务需要的环境变量：
- TELEGRAM_BOT_TOKEN
- DEEPSEEK_API_KEY  
- ADMIN_GROUP_ID

请告诉我：
1. Railway是否有web服务？
2. Web服务的URL是什么？
