# Render统一部署方案

## 目标
在Render同时部署Bot和Web，共享数据库

## 方案
创建两个Render服务：
1. Background Worker（Bot） - 运行 tg_bot_v2.py
2. Web Service（后台） - 运行 Flask

两者共享Render的持久化磁盘（Persistent Disk）

## 步骤

### 1. 停用Railway的Bot
先不要删除，待Render部署成功后再停用

### 2. 在Render创建Background Worker
- Service Type: Background Worker
- Build Command: pip install -r requirements.txt
- Start Command: python tg_bot_v2.py
- 添加环境变量

### 3. 配置持久化磁盘
让Bot和Web共享同一个磁盘存储数据库

### 4. Web服务连接到同一磁盘

这样Bot和Web就能共享数据库了！

开始配置...
