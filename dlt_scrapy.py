import requests
from html.parser import HTMLParser
import sqlite3
import time
from datetime import datetime, timedelta
import os

class LotteryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_tbody = False
        self.in_tr = False
        self.in_td = False
        self.current_data = []
        self.current_row = []
        self.lottery_data = []
        self.td_count = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'tbody':
            for attr in attrs:
                if attr == ('id', 'tdata'):
                    self.in_tbody = True
        elif self.in_tbody and tag == 'tr':
            self.in_tr = True
            self.current_row = []
            self.td_count = 0
        elif self.in_tr and tag == 'td':
            self.in_td = True

    def handle_endtag(self, tag):
        if tag == 'tbody':
            self.in_tbody = False
        elif tag == 'tr':
            self.in_tr = False
            if len(self.current_row) >= 15:  # 确保有足够的数据
                try:
                    self.lottery_data.append({
                        'qihao': self.current_row[0],
                        'red1': int(self.current_row[1]),
                        'red2': int(self.current_row[2]),
                        'red3': int(self.current_row[3]),
                        'red4': int(self.current_row[4]),
                        'red5': int(self.current_row[5]),
                        'blue1': int(self.current_row[6]),
                        'blue2': int(self.current_row[7]),
                        'date': self.current_row[14]
                    })
                except (IndexError, ValueError) as e:
                    print(f"解析行数据失败: {e}")
        elif tag == 'td':
            self.in_td = False
            self.td_count += 1

    def handle_data(self, data):
        if self.in_td:
            data = data.strip()
            if data:
                self.current_row.append(data)

def create_database(db_path="lottery.db"):
    """创建新的数据库"""
    # 如果数据库文件存在，先删除它
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"已删除旧的数据库文件: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS dlt
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               qihao TEXT NOT NULL UNIQUE,
               red1 INTEGER NOT NULL,
               red2 INTEGER NOT NULL,
               red3 INTEGER NOT NULL,
               red4 INTEGER NOT NULL,
               red5 INTEGER NOT NULL,
               blue1 INTEGER NOT NULL,
               blue2 INTEGER NOT NULL,
               date TEXT NOT NULL,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    )
    
    conn.commit()
    return conn, cursor

def calculate_latest_issue():
    """计算最新期号"""
    # 大乐透每周一、三、六开奖
    # 2025年第50期的日期是2025-05-07（周三）
    base_date = datetime(2025, 5, 7)
    base_issue = 25050
    
    today = datetime.now()
    
    # 如果今天在基准日期之前，直接返回基准期号
    if today <= base_date:
        return str(base_issue)
    
    # 计算从基准日期到今天的天数
    days_diff = (today - base_date).days
    
    # 计算周数和剩余天数
    weeks = days_diff // 7
    remaining_days = days_diff % 7
    
    # 基准日期是周三，计算额外的期数
    extra_periods = 0
    base_weekday = 2  # 周三是2
    today_weekday = today.weekday()
    
    if remaining_days > 0:
        # 根据剩余天数计算额外期数
        if base_weekday <= today_weekday:
            days_to_count = today_weekday - base_weekday
        else:
            days_to_count = 7 - (base_weekday - today_weekday)
            
        # 统计这些天中有多少个开奖日（周一、周三、六）
        for i in range(base_weekday, base_weekday + days_to_count + 1):
            day = i % 7
            if day in [0, 2, 5]:  # 周一(0)、周三(2)、周六(5)
                extra_periods += 1
    
    # 每周3期，加上额外的期数
    total_new_periods = weeks * 3 + extra_periods
    latest_issue = base_issue + total_new_periods
    
    # 返回8位期号格式
    year = str(today.year)[-2:]  # 取年份后两位
    period = str(latest_issue)[-3:]  # 取期号后三位
    return f"{year}{period.zfill(3)}"

def fetch_lottery_data(start, end, max_retries=3):
    """获取指定期号范围的大乐透数据"""
    url = f"https://datachart.500.com/dlt/history/newinc/history.php?start={start}&end={end}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 检查响应状态
            parser = LotteryParser()
            parser.feed(response.text)
            
            # 对数据进行去重处理
            unique_data = {}
            for item in parser.lottery_data:
                unique_data[item['qihao']] = item
            
            return list(unique_data.values())
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"获取数据失败: {e}")
                return []
            print(f"重试第 {attempt + 1} 次...")
            time.sleep(2)  # 延迟2秒后重试
        except Exception as e:
            print(f"解析数据失败: {e}")
            return []

def save_to_database(data, db_path="lottery.db"):
    """保存数据到数据库"""
    conn, cursor = create_database(db_path)
    success_count = 0
    
    # 按期号排序
    sorted_data = sorted(data, key=lambda x: x['qihao'])
    
    for item in sorted_data:
        try:
            cursor.execute(
                """INSERT INTO dlt 
                   (qihao, red1, red2, red3, red4, red5, blue1, blue2, date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (item['qihao'], item['red1'], item['red2'], item['red3'],
                 item['red4'], item['red5'], item['blue1'], item['blue2'],
                 item['date'])
            )
            success_count += 1
        except sqlite3.Error as e:
            print(f"保存数据失败 (期号: {item['qihao']}): {e}")
    
    conn.commit()
    print(f"成功保存 {success_count} 条数据")
    
    # 打印数据统计
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            MIN(qihao) as first_issue,
            MAX(qihao) as last_issue,
            COUNT(DISTINCT qihao) as unique_issues
        FROM dlt
    """)
    stats = cursor.fetchone()
    print(f"\n数据统计:")
    print(f"总记录数: {stats[0]}")
    print(f"期号范围: {stats[1]} - {stats[2]}")
    print(f"不重复期数: {stats[3]}")
    
    # 按年份统计
    cursor.execute("""
        SELECT 
            substr(date,1,4) as year,
            COUNT(*) as count
        FROM dlt 
        GROUP BY year 
        ORDER BY year
    """)
    print("\n按年份统计:")
    for year, count in cursor.fetchall():
        print(f"{year}年: {count}期")
    
    conn.close()

def main():
    """主函数"""
    start = "18021"  # 起始期号
    end = calculate_latest_issue()  # 动态计算最新期号
    
    print(f"开始获取大乐透数据 (期号范围: {start}-{end})...")
    lottery_data = fetch_lottery_data(start, end)
    
    if lottery_data:
        print(f"获取到 {len(lottery_data)} 条数据")
        save_to_database(lottery_data)
    else:
        print("未获取到数据")

if __name__ == "__main__":
    main()