# 🚀 A/B测试启动指南

## ✅ 当前状态

### Bot状态
- ✅ Bot已重启 (PID: 48918)
- ✅ 优化已生效（按钮响应0.1秒，AI响应2-3秒）

### 后台状态
- ✅ Flask后台运行中 (PID: 31559)
- ✅ 可访问：http://localhost:5000

---

## 🎯 立即开始A/B测试

### 步骤1：创建3个A/B测试实验

访问后台：http://localhost:5000/ab-test

#### 实验1：欢迎消息（welcome_message）

1. **实验名称**：`welcome_message`
2. **变体A（control）**：
   - 变体名称：`control`
   - 权重：50
3. **变体B（treatment）**：
   - 变体名称：`treatment`  
   - 权重：50

**预期效果**：Treatment版本（突出收益）转化率高20%+

---

#### 实验2：钱包引导（wallet_guide）

1. **实验名称**：`wallet_guide`
2. **变体A（control）**：
   - 变体名称：`control`
   - 权重：50
3. **变体B（treatment）**：
   - 变体名称：`treatment`
   - 权重：50

**预期效果**：Treatment版本（强调福利）信任度高10%+

---

#### 实验3：充值引导（deposit_prompt）

1. **实验名称**：`deposit_prompt`
2. **变体A（control）**：
   - 变体名称：`control`
   - 权重：50
3. **变体B（treatment）**：
   - 变体名称：`treatment`
   - 权重：50

**预期效果**：Treatment版本（强调VIP）客服添加率高15%+

---

### 步骤2：测试验证

#### 测试流程

1. **测试欢迎消息**
   - 打开Telegram，找到您的Bot
   - 发送 `/start`
   - 选择语言（中文 🇨🇳 或 English 🇺🇸）
   - 查看欢迎消息是否与A/B测试版本匹配

2. **测试钱包引导**
   - 发送一个Solana钱包地址
   - 收到"正在检测..."消息后
   - 发送"完成了"或"好了"
   - 查看钱包引导话术是否与A/B测试版本匹配

3. **测试充值引导**（需要实际充值场景）
   - 充值后查看引导话术是否与A/B测试版本匹配

---

### 步骤3：收集数据（7-14天）

#### 自动收集的数据

系统会自动记录：
- ✅ 用户看到的变体（`ab_test_seen`事件）
- ✅ 用户完成注册（`user_registered`事件）
- ✅ 用户完成充值（`deposit_completed`事件）

#### 查看数据的SQL

```sql
-- 查看各变体的转化率
SELECT 
    experiment,
    variant,
    COUNT(CASE WHEN event = 'ab_test_seen' THEN 1 END) as seen_count,
    COUNT(CASE WHEN event = 'user_registered' THEN 1 END) as registered_count,
    ROUND((COUNT(CASE WHEN event = 'user_registered' THEN 1 END) * 100.0 / 
           NULLIF(COUNT(CASE WHEN event = 'ab_test_seen' THEN 1 END), 0)), 2) as conversion_rate
FROM user_events
WHERE experiment IN ('welcome_message', 'wallet_guide', 'deposit_prompt')
GROUP BY experiment, variant
ORDER BY experiment, variant;
```

---

### 步骤4：分析结果（7-14天后）

#### 预期结果示例

| 实验 | 变体 | 看到消息 | 注册数 | 转化率 | 结论 |
|------|------|---------|--------|--------|------|
| welcome_message | control | 500 | 50 | 10% | |
| welcome_message | treatment | 500 | 100 | **20%** | ✅ **更好** |
| wallet_guide | control | 400 | 300 | 75% | |
| wallet_guide | treatment | 400 | 320 | **80%** | ✅ **更好** |
| deposit_prompt | control | 100 | 80 | 80% | |
| deposit_prompt | treatment | 100 | 95 | **95%** | ✅ **更好** |

#### 应用结果

发现Treatment版本效果更好后：
1. 将Treatment权重调整为100%
2. Control调整为0%（或删除）
3. 应用到所有新用户

---

## 📝 注意事项

### 1. 样本量要足够
- ❌ 10个用户 → 结果不可靠
- ✅ 1000+个用户 → 结果可靠

### 2. 测试时间要足够
- ❌ 1天 → 结果不稳定
- ✅ 7-14天 → 结果稳定

### 3. 只看一个变量
- 每个实验独立测试
- 不要同时修改多个因素

### 4. 及时应用结果
- 发现明显更优的版本，提前停止
- 应用到100%的用户

---

## 🔍 如何验证A/B测试是否工作？

### 方法1：查看日志

```bash
tail -f logs/bot.log | grep "A/B测试"
```

应该看到类似输出：
```
A/B测试: 用户123456分配到welcome_message变体: treatment
```

### 方法2：查看数据库

```python
# 在Python中
from database_manager import get_database

db = get_database()
events = db.get_all_user_events()

for event in events:
    if event['event'] == 'ab_test_seen':
        print(f"用户{event['user_id']}看到实验{event['experiment']}变体{event['variant']}")
```

### 方法3：后台查看

访问 http://localhost:5000/analytics
- 查看用户转化漏斗
- 对比不同时期的数据

---

## ✅ 检查清单

- [ ] Bot已重启
- [ ] Flask后台运行中
- [ ] 创建3个A/B测试实验
- [ ] 测试欢迎消息功能
- [ ] 测试钱包引导功能
- [ ] 测试充值引导功能
- [ ] 收集7-14天数据
- [ ] 分析转化率差异
- [ ] 应用最优版本

---

**开始收集数据！7-14天后见分晓！** 📊
