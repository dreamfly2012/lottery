import requests
from bs4 import BeautifulSoup
import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect("ssq.db")
c = conn.cursor()

# 创建表格
c.execute(
    """CREATE TABLE IF NOT EXISTS ssq
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              qihao TEXT NOT NULL,
              red1 INTEGER NOT NULL,
              red2 INTEGER NOT NULL,
              red3 INTEGER NOT NULL,
              red4 INTEGER NOT NULL,
              red5 INTEGER NOT NULL,
              red6 INTEGER NOT NULL,
              blue INTEGER NOT NULL,
              date TEXT NOT NULL)"""
)

# 爬取数据
start = "03001"
end = "23037"
url = f"http://datachart.500.com/ssq/history/newinc/history.php?start={start}&end={end}"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

rows = soup.find_all("tr", attrs={"class": "t_tr1"})

# 将数据保存到数据库
for row in rows:
    cells = row.find_all("td")
    qihao = cells[0].text.strip()
    red1 = int(cells[1].text.strip())
    red2 = int(cells[2].text.strip())
    red3 = int(cells[3].text.strip())
    red4 = int(cells[4].text.strip())
    red5 = int(cells[5].text.strip())
    red6 = int(cells[6].text.strip())
    blue = int(cells[7].text.strip())
    date = cells[15].text.strip()

    c.execute(
        "INSERT INTO ssq (qihao, red1, red2, red3, red4, red5, red6, blue, date) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (qihao, red1, red2, red3, red4, red5, red6, blue, date),
    )

# 查询数据
c.execute("SELECT * FROM ssq")
rows = c.fetchall()
for row in rows:
    print(row)

# 提交更改并关闭连接
conn.commit()
conn.close()
