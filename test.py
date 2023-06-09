import requests
from bs4 import BeautifulSoup
import csv

def get_html(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

def get_data(html):
    soup = BeautifulSoup(html, "html.parser")
    data = []
    for tr in soup.find_all('tr')[2:]:
        tds = tr.find_all('td')
        row = [tds[0].text]
        for td in tds[1:]:
            row.append(td.text)
        data.append(row)
    return data

def save_data(data, path):
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def main():
    url = 'http://datachart.500.com/dlt/history/history.shtml'
    path = 'dlt.csv'
    html = get_html(url)
    data = get_data(html)
    save_data(data, path)

if __name__ == '__main__':
    main()
