# PostgreSQL数据库配置步骤

## 📊 当前状态
- ✅ 已添加PostgreSQL支持
- ⏰ 需要配置环境变量

## 🎯 在Railway配置PostgreSQL

### 步骤1：添加环境变量

#### Worker服务（Bot）：
1. Railway Dashboard → Worker服务
2. Settings → Variables
3. 添加：
   - Name: `DATABASE_URL`
   - Value: `postgresql://postgres:moMItSdJzQuFkarnqTDqnsCnTBODFzQB@postgres.railway.internal:5432/railway`

#### Web服务（需要在Railway部署）：
1. Railway Dashboard → Web服务
2. Settings → Variables  
3. 添加相同的 `DATABASE_URL`

### 步骤2：等待重启

配置后Railway会自动重启服务

## 🎯 在Render配置PostgreSQL

### 问题：
Render无法访问Railway的内部地址！

### 解决方案：
获取PostgreSQL的外部地址

### 步骤：
1. Railway Dashboard → Postgres服务
2. 点击服务
3. 查看"Connect"标签
4. 复制"Public Network"的连接URL
5. 应该是类似：`postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway`

### 然后在Render配置：
1. Render Dashboard → Web服务
2. Settings → Environment Variables
3. 添加 `DATABASE_URL` = PostgreSQL外部URL

