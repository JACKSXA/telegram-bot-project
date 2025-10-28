# Railway Web服务部署检查

## Procfile配置
✅ web: cd admin_web && gunicorn -w 1 -b 0.0.0.0:$PORT flask_app:app

## 需要确认

在Railway Dashboard检查：

1. **是否已有web服务？**
   - 在项目服务列表中查找
   - 应该看到一个"web"服务

2. **如果没有，Railway应该自动创建**
   - Procfile已经配置好了
   - Railway会自动检测并部署

3. **环境变量配置**
   在web服务中添加：
   - TELEGRAM_BOT_TOKEN
   - DEEPSEEK_API_KEY
   - ADMIN_GROUP_ID
   - DATABASE_URL = postgresql://postgres:moMItSdJzQuFkarnqTDqnsCnTBODFzQB@postgres.railway.internal:5432/railway

请告诉我：
- Railway上是否已经有web服务？
- 如果有，web服务的URL是什么？
