import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from datetime import datetime
import os

def create_database(db_path="lottery.db"):
    """创建新的数据库表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fc3d
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         qihao TEXT NOT NULL UNIQUE,
         bai INTEGER NOT NULL,
         shi INTEGER NOT NULL,
         ge INTEGER NOT NULL,
         date TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    """)
    
    conn.commit()
    return conn, cursor

def get_today_end_qihao():
    today = datetime.today()
    year = today.year
    # 计算今天是今年的第几天（假设每天一期，实际如有调整需根据官方规则修正）
    day_of_year = today.timetuple().tm_yday
    return f"{year}{day_of_year:03d}"

def fetch_lottery_data(start="2004001", end=None, limit=21117, max_retries=3):
    if end is None:
        end = get_today_end_qihao()
    """获取福彩3D数据"""
    url = f"https://datachart.500.com/sd/history/inc/history.php?limit={limit}&start={start}&end={end}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"尝试获取数据，URL: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试查找表格
            print("尝试查找表格...")
            table = soup.find('table', {'class': 'chart-table'})
            if not table:
                table = soup.find('table', {'id': 'tdata'})
                if not table:
                    table = soup.find('table')
                    if not table:
                        print("错误: 未找到任何表格")
                        print("页面标题:", soup.title.string if soup.title else "无标题")
                        return []
            
            print("找到表格，开始解析数据...")
            lottery_data = []
            rows = table.find_all('tr')
            print(f"找到 {len(rows)} 行数据")
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:  # 至少需要期号和3个号码
                    try:
                        qihao = cells[0].text.strip()
                        date = cells[10].text.strip()
                        if not qihao.isdigit():
                            continue
                            
                        print(f"解析期号: {qihao}")
                        parts = cells[1].text.strip().split(' ')  
                        if len(parts) == 3:
                            bai, shi, ge = map(int, parts)
                        else:
                            # 处理异常情况
                            print(f"解析号码失败: {parts}")
                        lottery_data.append({
                            'qihao': qihao,
                            'bai': bai,
                            'shi': shi,
                            'ge': ge,
                            'date':date
                           
                        })
                    except (IndexError, ValueError, AttributeError) as e:
                        print(f"解析行数据失败: {e}")
                        continue
            
            return lottery_data
            
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            if attempt == max_retries - 1:
                return []
            time.sleep(2)
        except Exception as e:
            print(f"解析数据失败: {e}")
            return []

def save_to_database(data, db_path="lottery.db"):
    """保存数据到数据库"""
    if not data:
        print("无数据需要保存")
        return
        
    conn, cursor = create_database(db_path)
    success_count = 0
    
    for item in data:
        try:
            cursor.execute(
                """INSERT OR REPLACE INTO fc3d 
                   (qihao, bai, shi, ge, date)
                   VALUES (?, ?, ?, ?, ?)""",
                (item['qihao'], item['bai'], item['shi'], item['ge'], item['date'])
            )
            success_count += 1
        except sqlite3.Error as e:
            print(f"保存数据失败 (期号: {item['qihao']}): {e}")
    
    conn.commit()
    print(f"成功保存 {success_count} 条数据")
    
    cursor.execute("SELECT COUNT(*) FROM fc3d")
    print(f"当前福彩3D总记录数: {cursor.fetchone()[0]}")
    
    conn.close()

def main():
    """主函数"""
    print("开始获取福彩3D数据...")
    lottery_data = fetch_lottery_data()
    
    if lottery_data:
        print(f"获取到 {len(lottery_data)} 条数据")
        save_to_database(lottery_data)
    else:
        print("未获取到数据")

if __name__ == "__main__":
    main()