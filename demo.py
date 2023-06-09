import requests
from bs4 import BeautifulSoup

# 发送HTTP GET请求，获取排列五历史开奖页面的HTML内容
url = 'https://www.500.com/info/kaijiang/plw/'
response = requests.get(url)
html_content = response.text

# 使用BeautifulSoup解析HTML内容
soup = BeautifulSoup(html_content, 'html.parser')

# 找到历史开奖记录所在的HTML元素
history_table = soup.find('table', class_='kj_tablelist02')
if history_table:
    rows = history_table.find_all('tr')
    
    # 遍历每一行，提取开奖号码和其他信息
    for row in rows[1:]:
        data = row.find_all('td')
        date = data[0].text.strip()  # 开奖日期
        numbers = [num.text.strip() for num in data[1:6]]  # 开奖号码
        prize_pool = data[6].text.strip()  # 奖池金额
        
        # 打印开奖信息
        print(f"日期: {date}")
        print(f"号码: {numbers}")
        print(f"奖池金额: {prize_pool}")
        print("-----------------------")
else:
    print("未找到历史开奖记录表格。")
