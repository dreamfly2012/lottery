import requests
from html.parser import HTMLParser
import sqlite3
import time
from datetime import datetime
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
            if len(self.current_row) >= 16:  # 确保有足够的数据
                try:
                    self.lottery_data.append({
                        'qihao': self.current_row[0],
                        'red1': int(self.current_row[1]),
                        'red2': int(self.current_row[2]),
                        'red3': int(self.current_row[3]),
                        'red4': int(self.current_row[4]),
                        'red5': int(self.current_row[5]),
                        'red6': int(self.current_row[6]),
                        'blue': int(self.current_row[7]),
                        'date': self.current_row[15]
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
    """创建新的数据库表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建双色球表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ssq
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         qihao TEXT NOT NULL UNIQUE,
         red1 INTEGER NOT NULL,
         red2 INTEGER NOT NULL,
         red3 INTEGER NOT NULL,
         red4 INTEGER NOT NULL,
         red5 INTEGER NOT NULL,
         red6 INTEGER NOT NULL,
         blue INTEGER NOT NULL,
         date TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    """)
    
    conn.commit()
    return conn, cursor

def calculate_latest_issue():
    """计算最新期号"""
    # 双色球每周二、四、日开奖
    # 以当前日期计算最新期号
    today = datetime.now()
    # 由于双色球期号规则比较复杂，这里返回一个足够大的期号
    # 实际数据会以网站上的为准
    return f"{today.year}150"

def fetch_lottery_data(start, end, max_retries=3):
    """获取指定期号范围的双色球数据"""
    url = f"https://datachart.500.com/ssq/history/newinc/history.php?start={start}&end={end}"
    
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
                """INSERT OR REPLACE INTO ssq 
                   (qihao, red1, red2, red3, red4, red5, red6, blue, date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (item['qihao'], item['red1'], item['red2'], item['red3'],
                 item['red4'], item['red5'], item['red6'], item['blue'],
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
        FROM ssq
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
        FROM ssq 
        GROUP BY year 
        ORDER BY year
    """)
    print("\n按年份统计:")
    for year, count in cursor.fetchall():
        print(f"{year}年: {count}期")
    
    conn.close()

def main():
    """主函数"""
    start = "03001"  # 起始期号
    end = calculate_latest_issue()  # 动态计算最新期号
    
    print(f"开始获取双色球数据 (期号范围: {start}-{end})...")
    lottery_data = fetch_lottery_data(start, end)
    
    if lottery_data:
        print(f"获取到 {len(lottery_data)} 条数据")
        save_to_database(lottery_data)
    else:
        print("未获取到数据")

if __name__ == "__main__":
    main()