# 开发路径记录

## 📅 项目时间线

### 2025-10-27: 初始开发
- 创建 Telegram Bot 基础功能
- 实现多语言支持
- 钱包绑定逻辑

### 2025-10-28: 后台开发
- 集成 Flask 管理后台
- 实现用户管理功能
- 添加数据分析页面
- 优化 UI/UX（Tailwind CSS）

### 2025-10-28 下午: 功能完善
- 修复数据同步问题
- 实现转化漏斗统计
- 添加客服接入识别
- 严格 Solana 地址验证
- 批量操作功能

## 🎯 关键决策记录

### 技术选型
**为什么选择 SQLite + PostgreSQL 双模式？**
- SQLite: 本地开发快速迭代
- PostgreSQL: 云端生产稳定可靠
- 自动检测，无感知切换

### UI 重构
**为什么从 Bootstrap 改为 Tailwind CSS？**
- 更现代化设计
- 更好的响应式支持
- 更灵活的样式控制
- 支持深色模式

### 数据同步策略
**为什么采用数据库直连而不是 session 缓存？**
- session 缓存容易出现数据不一致
- 数据库作为单一数据源更可靠
- 实时同步，无延迟

## 🐛 问题修复历史

### 转化漏斗数据不同步
**问题**: 后台显示转化漏斗数据不匹配
**根因**: 
1. Jinja2 动态类名不支持 Tailwind CSS
2. 数据传递缺失统计字段
**解决**: 
- 使用 if/elif 显式写出 CSS 类名
- 从数据库直采快照统计
- Flask 传递完整统计字段

### Bot 不回复
**问题**: 用户发送消息 Bot 无响应
**根因**: 多个 Bot 实例同时运行冲突
**解决**: 确保只有一个 Bot 实例运行

### 对话历史不显示
**问题**: 用户详情页对话历史为空
**根因**: 数据库路径不一致，Bot 和 Web 读写不同数据库
**解决**: 统一数据库路径为项目根目录

## 📊 架构设计

### 数据流
```
用户 → Bot → database_manager.py → SQLite/PostgreSQL
                                   ↓
                             admin_web/flask_app.py → Web UI
```

### 状态机
```
idle → wallet_verified → bound_and_ready → waiting_customer_service → transfer_completed
```

### 文件依赖
```
tg_bot_v2.py → database_manager.py
admin_web/flask_app.py → database_manager.py
admin_web/flask_app.py → templates/*.html
templates/*.html → static/css/*.css (Tailwind CDN)
```

## 🔄 未来优化方向

1. **性能优化**
   - 数据库索引优化
   - 查询缓存
   - 分页加载

2. **功能扩展**
   - WebSocket 实时推送
   - 导出 Excel 报表
   - API 接口文档

3. **稳定性**
   - 单元测试覆盖
   - 集成测试
   - 自动化部署

4. **用户体验**
   - 移动端适配
   - 快捷键支持
   - 自定义主题

## 💡 开发经验总结

### 最佳实践
1. **数据库**: 统一使用 database_manager，不要直接 SQL
2. **日志**: 使用 logger 而不是 print
3. **状态**: 用字符串常量定义状态，避免硬编码
4. **错误处理**: 所有数据库操作都要 try-except

### 踩坑教训
1. **缓存问题**: Flask 模板缓存，修改后要重启服务
2. **Jinja2 限制**: 不能动态生成 Tailwind 类名
3. **数据库路径**: Bot 和 Web 必须共享同一数据库
4. **多实例**: Bot 不能同时运行多个实例

### 开发流程
1. 功能设计 → 数据库设计 → 后端实现 → 前端实现 → 测试
2. 每次修改提交代码，Render 自动部署
3. 遇到问题先看日志，再查数据库
4. 重要功能要写测试用例

---
**记录人**: AI Assistant  
**最后更新**: 2025-10-28
