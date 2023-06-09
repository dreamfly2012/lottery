import requests
from bs4 import BeautifulSoup
import sqlite3





# 爬取数据
start = "05001"
end = "23145"
url = f"https://datachart.500.com/plw/?expect=all&from={start}\
        &to={end}"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", attrs={"id": "chartsTable"})

rows = table.find_all("tr")

# 将数据保存到数据库
i =0
for row in rows:
    if i < 3 or i%5==3:
        pass
    else:
        cells = row.find_all("td")
        qihao = cells[0].text.strip()
        reds = row.find_all('td',class_='chartBall01')
        blues = row.find_all('td',class_='chartBall03')
       
        red1 = int(reds[0].text.strip())
        red2 = int(blues[0].text.strip())
        red3 = int(reds[1].text.strip())
        red4 = int(blues[1].text.strip())
        red5 = int(reds[2].text.strip())
        
      
        print(qihao, red1, red2, red3, red4, red5)
    i = i + 1
    # c.execute("INSERT INTO dlt (qihao, red1, red2, red3, red4, red5,\
    #                              date)\
    #             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    #           (qihao, red1, red2, red3, red4, red5, blue1, blue2, date))

# 查询数据
# c.execute("SELECT * FROM dlt")
# rows = c.fetchall()
# for row in rows:
#     print(row)

# # 提交更改并关闭连接
# conn.commit()
# conn.close()
