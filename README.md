# 彩票数据自动更新系统

本系统用于自动抓取并更新彩票开奖数据，支持大乐透、双色球和福彩3D，提供定时更新和数据存储功能。

## 功能特点

- 支持三种彩票数据抓取：
  - 大乐透
  - 双色球
  - 福彩3D
- 自动计算最新期号
- 每天凌晨2点自动更新数据
- 支持数据去重和完整性检查
- 数据存储在SQLite数据库中

## 系统要求

- Python 3.x
- 虚拟环境（推荐）
- 必要的Python包（见requirements.txt）：
  - requests==2.31.0
  - schedule==1.2.2

## 安装步骤

1. 创建并激活虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 手动运行数据更新

更新大乐透数据：
```bash
python3 dlt_scrapy.py
```

更新双色球数据：
```bash
python3 ssq_scrapy.py
```

更新福彩3D数据：
```bash
python3 fc3d_scrapy.py
```

### 启动自动更新服务（同时更新三种彩票）

```bash
python3 update_lottery.py
```

自动更新服务会：
- 立即执行一次数据更新（三种彩票）
- 设置每天凌晨2点自动更新
- 保持后台运行直到手动停止（Ctrl+C）

### 后台运行（Linux/Unix系统）

使用 nohup 命令在后台运行：
```bash
nohup python3 update_lottery.py > lottery_update.log 2>&1 &
```

使用 screen 会话运行：
```bash
screen -S lottery
python3 update_lottery.py
# 按 Ctrl+A 然后按 D 分离会话
```

重新连接 screen 会话：
```bash
screen -r lottery
```

## 数据库说明

数据存储在 `lottery.db` 文件中，使用SQLite数据库。

### 大乐透表结构（dlt）：
```sql
CREATE TABLE dlt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qihao TEXT NOT NULL UNIQUE,
    red1 INTEGER NOT NULL,
    red2 INTEGER NOT NULL,
    red3 INTEGER NOT NULL,
    red4 INTEGER NOT NULL,
    red5 INTEGER NOT NULL,
    blue1 INTEGER NOT NULL,
    blue2 INTEGER NOT NULL,
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 双色球表结构（ssq）：
```sql
CREATE TABLE ssq (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qihao TEXT NOT NULL UNIQUE,
    red1 INTEGER NOT NULL,
    red2 INTEGER NOT NULL,
    red3 INTEGER NOT NULL,
    red4 INTEGER NOT NULL,
    red5 INTEGER NOT NULL,
    red6 INTEGER NOT NULL,
    blue INTEGER NOT NULL,
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 福彩3D表结构（fc3d）：
```sql
CREATE TABLE fc3d (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qihao TEXT NOT NULL UNIQUE,
    bai INTEGER NOT NULL,
    shi INTEGER NOT NULL,
    ge INTEGER NOT NULL,
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 数据查询示例

### 大乐透查询：
```sql
-- 查询最新一期数据
SELECT * FROM dlt ORDER BY qihao DESC LIMIT 1;
```

### 双色球查询：
```sql
-- 查询最新一期数据
SELECT * FROM ssq ORDER BY qihao DESC LIMIT 1;
```

### 福彩3D查询：
```sql
-- 查询最新一期数据
SELECT * FROM fc3d ORDER BY qihao DESC LIMIT 1;

-- 查询某个日期范围的数据
SELECT * FROM fc3d 
WHERE date BETWEEN '2023-01-01' AND '2023-12-31' 
ORDER BY qihao;
```

### 福彩3D Python查询API

系统提供 `FC3DQuery` 类用于高级查询功能：

```python
from fc3d_query import FC3DQuery

# 初始化查询器
query = FC3DQuery()

# 查询最近5期开奖结果
results = query.get_recent_results(5)
for r in results:
    print(f"{r.qihao}期: {r.bai}{r.shi}{r.ge}")

# 统计号码出现次数
count = query.count_occurrences((6,2,1))  # 统计号码621出现次数
print(f"出现次数: {count}")

# 查询前后记录
adjacent = query.get_adjacent_records("2025118")
print(f"前一期: {adjacent['prev'].qihao if adjacent['prev'] else '无'}")
print(f"后一期: {adjacent['next'].qihao if adjacent['next'] else '无'}")
```

#### API功能说明
- `get_recent_results(limit)` - 查询最近N期开奖结果
- `count_occurrences((bai,shi,ge))` - 统计指定号码出现次数
- `get_adjacent_records(qihao)` - 查询指定期号的前后记录
- `get_by_qihao(qihao)` - 按期号查询详细开奖信息

### 历史号码上下文查询
系统提供历史号码查询功能，可以查找特定号码的所有历史记录及其前后期数据：

```python
from fc3d_history_context import FC3DHistoryContext

query = FC3DHistoryContext()
# 查找号码645的历史记录及前后3期数据
results = query.find_number_with_context((6,4,5), 3)

# 显示所有匹配记录及其上下文
for result in results:
    for period in result["all_periods"]:
        print(format_period(period, (6,4,5)))
```

输出示例：
```
=== 记录组 1 ===
期号: 2025130 号码: 204 日期: 2025-05-20
期号: 2025131 号码: 203 日期: 2025-05-21
期号: 2025132 号码: 689 日期: 2025-05-22
期号: 2025133 号码: [645] 日期: 2025-05-23  # 匹配号码用[]标记
...
```

特点：
- 按时间顺序显示所有期数
- 使用方括号[]标记匹配的号码
- 每组记录显示完整的前后文信息

### 连续和值查询
系统提供连续和值查询功能，可以查找连续几期和值符合指定序列的期数：

```python
from fc3d_sum_sequence import FC3DSumSequence

query = FC3DSumSequence()
# 查找连续三期和值为5,23,15的期数及前后3期数据
results = query.find_consecutive_sums([5, 23, 15], 3)

# 显示所有匹配记录及其上下文
for result in results:
    print(f"匹配期数范围: {result['match_start_qihao']} 至 {result['match_end_qihao']}")
    for period in result["all_periods"]:
        print(format_period(period, is_match=True if period[0] >= result['match_start_qihao'] and period[0] <= result['match_end_qihao'] else False))
```

输出示例：
```
=== 匹配记录 1 ===
匹配期数范围: 2025131 至 2025133

期号: 2025128 号码: 814 和值: 13 日期: 2025-05-18
期号: 2025129 号码: 915 和值: 15 日期: 2025-05-19
期号: 2025130 号码: 204 和值: 6 日期: 2025-05-20
期号: 2025131 号码: [203] 和值: [5] 日期: 2025-05-21
期号: 2025132 号码: [689] 和值: [23] 日期: 2025-05-22
期号: 2025133 号码: [645] 和值: [15] 日期: 2025-05-23
```

特点：
- 可查询连续多期和值符合特定序列的期数
- 显示匹配期数及其前后期数据
- 使用方括号[]标记匹配的号码和和值

### 条件概率统计
系统提供条件概率统计功能，可以分析某个数字后面出现各个数字的概率：

```python
from fc3d_conditional_probability import FC3DConditionalProbability

query = FC3DConditionalProbability()

# 统计百位6后面出现各个数字的概率
probs = query.calculate_next_digit_probability('bai', 6)
for digit, prob in sorted(probs.items()):
    print(f"数字 {digit}: {prob:.2%}")

# 统计指定组合后面出现各个数字的概率
conditions = {'bai': 6, 'shi': 4, 'ge': 5}
probs = query.calculate_next_digits_probability(conditions)
for position in ['bai', 'shi', 'ge']:
    print(f"\n{position}位:")
    for digit, prob in sorted(probs[position].items()):
        print(f"数字 {digit}: {prob:.2%}")
```

输出示例：
```
百位6后面出现各个数字的概率:
数字 0: 10.48%
数字 1: 9.68%
数字 2: 9.15%
...

组合 {'bai': 6, 'shi': 4, 'ge': 5} 后面出现各个数字的概率:
bai位:
数字 0: 12.50%
数字 1: 0.00%
数字 2: 0.00%
...
```

特点：
- 支持单个位置的后续数字概率统计
- 支持多个位置组合的后续数字概率统计
- 概率以百分比形式展示

### 连号查询功能
系统提供专门的连号查询功能，可以查找百位、十位、个位的连号情况：

```python
from fc3d_consecutive import FC3DConsecutiveQuery

query = FC3DConsecutiveQuery()

# 查询百位连号
results = query.find_consecutive_numbers('bai')
for qihao1, num1, qihao2, num2 in results:
    print(f"期号: {qihao1} -> {qihao2}, 号码: {num1} -> {num2}")

# 查询十位连号
results = query.find_consecutive_numbers('shi')

# 查询个位连号
results = query.find_consecutive_numbers('ge')
```

示例输出：
```
=== 百位连号情况 ===
期号: 2025128 -> 2025129 号码: 8 -> 9
期号: 2025126 -> 2025127 号码: 3 -> 4
...

=== 十位连号情况 ===
期号: 2025130 -> 2025129 号码: 0 -> 1
期号: 2025126 -> 2025127 号码: 2 -> 3
...

=== 个位连号情况 ===
期号: 2025131 -> 2025130 号码: 3 -> 4
期号: 2025130 -> 2025129 号码: 4 -> 5
...
```

## 注意事项

1. 程序会自动计算最新期号，但实际数据以500彩票网的更新为准
2. 每次更新会保留现有数据，使用INSERT OR REPLACE语句更新数据
3. 建议在服务器上使用 screen 或 nohup 运行自动更新服务
4. 确保系统时间准确，因为自动更新基于系统时间

## 错误处理

如果遇到数据更新失败，程序会：
1. 自动重试（最多3次）
2. 记录错误信息
3. 继续保持运行，等待下次更新
4. 单个彩种更新失败不会影响其他彩种的更新

## 维护建议

1. 定期检查日志，确保更新正常进行
2. 监控数据库大小和完整性
3. 必要时可以手动触发更新
4. 定期备份数据库文件

## 版本历史

- v1.2.0 (2024-05-09)
  - 添加福彩3D数据抓取功能
  - 更新自动更新服务支持三种彩票
  - 优化数据库结构

- v1.1.0 (2024-05-09)
  - 添加双色球数据抓取功能
  - 更新自动更新服务支持多彩种
  - 改进错误处理机制

- v1.0.0 (2024-05-09)
  - 初始版本
  - 实现大乐透数据抓取和自动更新功能
  - 添加数据库存储和查询功能