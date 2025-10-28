# Telegram Bot 管理后台项目

## 📋 项目概述

这是一个基于 Telegram Bot 的量化交易客户服务系统，包含：

1. **Telegram Bot** - 用户交互前端
   - 多语言支持（中文/英文）
   - 钱包绑定和验证
   - 自动状态流转
   - 客服接入识别

2. **Web 管理后台** - Flask 后台管理
   - 用户管理和监控
   - 消息推送功能
   - 数据分析统计
   - 转化漏斗追踪

## 🛠 技术栈

### 后端
- **Python 3.13+** - 主编程语言
- **Flask** - Web 框架（管理后台）
- **python-telegram-bot** - Telegram Bot 库
- **SQLite** - 本地数据库
- **PostgreSQL** - 云端数据库（Render）

### 前端
- **Tailwind CSS** - UI 框架
- **Alpine.js** - 交互增强
- **FontAwesome** - 图标库
- **Jinja2** - 模板引擎

## 📁 项目结构

```
AI招聘/
├── tg_bot_v2.py              # Bot 主程序
├── database_manager.py        # 数据库管理器
├── admin_web/                 # Web 后台目录
│   ├── flask_app.py           # Flask 应用
│   ├── requirements.txt       # Python 依赖
│   ├── templates/             # HTML 模板
│   │   ├── base_tailwind.html # 基础模板
│   │   ├── dashboard_tailwind.html # 仪表盘
│   │   ├── users_tailwind.html # 用户列表
│   │   ├── analytics_tailwind.html # 数据分析
│   │   ├── push_tailwind.html # 消息推送
│   │   └── user_detail_tailwind.html # 用户详情
│   └── static/                # 静态资源（CSS/JS）
├── tests/                      # 测试文件
├── logs/                       # 日志目录
├── user_data.db               # SQLite 数据库
└── sessions.pkl               # Bot 会话缓存（旧）
```

## 🚀 部署说明

### 本地开发

1. **环境准备**
```bash
# 安装依赖
pip install -r admin_web/requirements.txt

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

2. **启动 Bot**
```bash
python3 tg_bot_v2.py
```

3. **启动 Web 后台**
```bash
cd admin_web
export FLASK_APP=flask_app.py
flask run --host=0.0.0.0 --port=5000
```

访问: http://localhost:5000/login
- 账号: `admin`
- 密码: `admin123`

### 云端部署（Render）

#### Bot 部署
- Platform: Railway / Render
- 入口: `tg_bot_v2.py`
- 环境变量: `TELEGRAM_BOT_TOKEN`, `ADMIN_GROUP_ID`

#### Web 后台部署
- Platform: Render
- 入口: `admin_web/flask_app.py`
- 环境变量: `DATABASE_URL` (PostgreSQL)

## 🔑 核心功能

### 用户流程
1. 用户发送 /start → 注册
2. 发送钱包地址 → 钱包绑定
3. 群组确认转账 → 转接客服
4. 添加客服账号 → 后续服务

### 关键状态
- `idle` - 空闲（初始状态）
- `wallet_verified` - 钱包已验证
- `bound_and_ready` - 已绑定准备
- `waiting_customer_service` - 等待客服
- `transfer_completed` - 转账完成

### 转化漏斗
- **注册用户** → 用户总数
- **已绑定钱包** → 有钱包地址的用户
- **等待客服** → waiting_customer_service 状态
- **转账完成** → transfer_completed = 1

## 📊 数据同步

项目使用 `database_manager.py` 统一管理数据库：

- **SQLite** - 本地开发（user_data.db）
- **PostgreSQL** - 云端部署（自动检测 DATABASE_URL）

Bot 和 Web 后台共享同一个数据库，确保数据实时同步。

## 🔧 开发指南

### 添加新功能
1. 修改 `tg_bot_v2.py` 添加 Bot 逻辑
2. 修改 `admin_web/flask_app.py` 添加路由
3. 修改或新增 `admin_web/templates/*.html` 页面
4. 测试本地功能
5. 提交到 GitHub
6. Render 自动部署

### 调试技巧
```bash
# 查看 Bot 日志
tail -f logs/bot.log

# 查看 Flask 日志
tail -f logs/flask_app.log

# 查看数据库
sqlite3 user_data.db "SELECT * FROM users LIMIT 10;"
```

## 📝 重要文件说明

### tg_bot_v2.py
- Bot 主程序
- 处理用户消息和状态流转
- 集成客服接入识别
- 严格 Solana 地址验证

### admin_web/flask_app.py
- Flask 应用主入口
- 用户管理、分析、推送路由
- 数据库实时统计
- 会话管理

### database_manager.py
- 数据库抽象层
- 支持 SQLite 和 PostgreSQL
- 自动创建表和索引
- 提供统一的 CRUD 接口

## 🎯 开发里程碑

### 已完成 ✅
- [x] 基础 Bot 功能（多语言、钱包绑定）
- [x] Web 管理后台（用户列表、详情、分析）
- [x] 消息推送功能
- [x] 转化漏斗统计
- [x] UI/UX 全面优化（Tailwind CSS）
- [x] 客服接入自动识别
- [x] 严格 Solana 地址验证
- [x] 批量操作（更新、发送、删除）
- [x] 高级筛选（按日期、活动时间）
- [x] Bot 健康监控

### 待优化 🔄
- [ ] 用户对话历史实时同步
- [ ] 群组消息自动处理
- [ ] 多币种支持
- [ ] 数据分析报表导出
- [ ] API 接口文档

## 📌 注意事项

1. **数据库备份**: 定期备份 `user_data.db`
2. **环境变量**: 云端部署需要配置所有环境变量
3. **日志管理**: 日志文件自动滚动（5MB，5个备份）
4. **测试**: 新增功能前编写测试（tests/）

## 📞 联系支持

项目地址: https://github.com/JACKSXA/telegram-bot-project
部署地址: Render (自动部署)

---
**版本**: v1.0  
**更新日期**: 2025-10-28  
**维护者**: 项目团队
