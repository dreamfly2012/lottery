import sqlite3
from pprint import pprint

def check_db_structure(db_path):
    """检查数据库表结构"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查fc3d表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fc3d';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("fc3d表已存在，表结构如下:")
            cursor.execute("PRAGMA table_info(fc3d);")
            pprint(cursor.fetchall())
        else:
            print("fc3d表不存在，需要创建表")
            print("建议的表结构SQL:")
            print("""
            CREATE TABLE fc3d (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                numbers TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
        
        conn.close()
    except Exception as e:
        print(f"数据库检查出错: {e}")

if __name__ == "__main__":
    check_db_structure("/root/code/lottery/lottery.db")