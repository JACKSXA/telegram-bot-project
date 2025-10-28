# 贡献指南

## 📝 代码规范

### Python 代码规范
- 使用 **4个空格**缩进
- 每行不超过 **120字符**
- 函数和类需要添加 **docstring**
- 变量名使用 **snake_case**
- 类名使用 **PascalCase**

### 示例
```python
def save_user_data(user_id: int, data: dict) -> bool:
    """
    保存用户数据到数据库
    
    Args:
        user_id: 用户ID
        data: 用户数据字典
    
    Returns:
        bool: 成功返回True
    """
    try:
        # 实现逻辑
        return True
    except Exception as e:
        logger.error(f"保存失败: {e}")
        return False
```

## 🧪 测试规范

### 运行测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_database.py

# 运行并显示覆盖率
pytest --cov=. tests/
```

### 编写测试
```python
def test_save_user():
    """测试保存用户功能"""
    db = DatabaseManager(':memory:')
    db.save_user(123, {'name': 'test'})
    
    user = db.get_user(123)
    assert user['name'] == 'test'
```

## 🔄 Git 提交规范

### 提交信息格式
```
类型: 简短描述

详细说明（可选）
```

### 类型说明
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例
```
feat: 添加用户批量删除功能

- 支持多选用户删除
- 添加确认对话框
- 优化删除性能
```

## 📁 文件组织

### 新增功能
1. 修改 `tg_bot_v2.py` 添加Bot逻辑
2. 修改 `admin_web/flask_app.py` 添加路由
3. 更新/新增模板 `admin_web/templates/*.html`
4. 编写测试 `tests/test_*.py`
5. 更新文档 `README.md`

### 文件命名
- Python文件: `snake_case.py`
- 测试文件: `test_snake_case.py`
- HTML模板: `snake_case_tailwind.html`

## 🐛 Bug报告

### 报告格式
```markdown
**问题描述**
简要描述问题

**复现步骤**
1. 操作步骤1
2. 操作步骤2

**预期行为**
应该发生什么

**实际行为**
实际发生了什么

**环境信息**
- OS: macOS
- Python: 3.13
- 浏览器: Chrome
```

## ✅ Code Review

### 检查清单
- [ ] 代码符合PEP 8规范
- [ ] 添加了必要的注释
- [ ] 编写了测试用例
- [ ] 更新了文档
- [ ] 通过了所有测试
- [ ] 提交信息符合规范

---
**最后更新**: 2025-10-28
