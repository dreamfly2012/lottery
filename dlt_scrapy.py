import requests
from bs4 import BeautifulSoup
import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect("lottery.db")
c = conn.cursor()

# 创建表格
c.execute(
    """CREATE TABLE IF NOT EXISTS dlt
          (id INTEGER PRIMARY KEY AUTOINCREMENT,
           qihao TEXT NOT NULL,
           red1 INTEGER NOT NULL,
           red2 INTEGER NOT NULL,
           red3 INTEGER NOT NULL,
           red4 INTEGER NOT NULL,
           red5 INTEGER NOT NULL,
           blue1 INTEGER NOT NULL,
           blue2 INTEGER NOT NULL,
           date TEXT NOT NULL)"""
)

# 爬取数据
start = "07001"
end = "23045"
url = f"http://datachart.500.com/dlt/history/newinc/history.php?start={start}\
        &end={end}"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

tbody = soup.find("tbody", attrs={"id": "tdata"})

rows = tbody.find_all("tr")

# 将数据保存到数据库
for row in rows:
    cells = row.find_all("td")
    qihao = cells[0].text.strip()
    red1 = int(cells[1].text.strip())
    red2 = int(cells[2].text.strip())
    red3 = int(cells[3].text.strip())
    red4 = int(cells[4].text.strip())
    red5 = int(cells[5].text.strip())
    blue1 = int(cells[6].text.strip())
    blue2 = int(cells[7].text.strip())
    date = cells[14].text.strip()
    print(qihao, red1, red2, red3, red4, red5, blue1, blue2, date)
    c.execute("INSERT INTO dlt (qihao, red1, red2, red3, red4, red5,\
                                blue1, blue2, date)\
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (qihao, red1, red2, red3, red4, red5, blue1, blue2, date))

# 查询数据
c.execute("SELECT * FROM dlt")
rows = c.fetchall()
for row in rows:
    print(row)

# 提交更改并关闭连接
conn.commit()
conn.close()
