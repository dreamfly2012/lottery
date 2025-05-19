import sqlite3

def verify_database():
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    
    # 获取总记录数和期号范围
    cursor.execute("SELECT COUNT(*) as total, MIN(qihao) as first_issue, MAX(qihao) as last_issue FROM dlt")
    total, first_issue, last_issue = cursor.fetchone()
    print(f"\n数据统计:")
    print(f"总记录数: {total}")
    print(f"期号范围: {first_issue} - {last_issue}")
    
    # 检查是否有重复期号
    cursor.execute("SELECT qihao, COUNT(*) as count FROM dlt GROUP BY qihao HAVING count > 1")
    duplicates = cursor.fetchall()
    if duplicates:
        print("\n发现重复期号:")
        for qihao, count in duplicates:
            print(f"期号 {qihao} 出现 {count} 次")
    else:
        print("\n未发现重复期号")
    
    # 检查数据分布
    cursor.execute("""
        SELECT 
            strftime('%Y', date) as year,
            COUNT(*) as count
        FROM dlt 
        GROUP BY year 
        ORDER BY year
    """)
    print("\n按年份统计:")
    for year, count in cursor.fetchall():
        print(f"{year}年: {count}期")
    
    conn.close()

if __name__ == "__main__":
    verify_database()