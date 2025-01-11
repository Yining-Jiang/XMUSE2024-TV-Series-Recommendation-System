import json
import csv
import re
import requests
import datetime
from bs4 import BeautifulSoup
import os

# 获取豆瓣 TOP250 电影的名称以及主页链接
def crawl_douban_top250():
    headers = {
        'User-Agent': 'User-Agent:Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'
    }
    movies = []
    try:
        # STEP 1 获取250个榜单中的电影主页和名称
            response = requests.get(f"https://movie.douban.com/tv/", headers=headers)
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            ol = soup.find('ul', attrs={'class':"explore-list"})
            lis = ol.find_all('li')
            for li in lis:
                movie = {}
               # movie['rank'] = "No." + str(i)
                #i = i + 1
                #a = li.find('a')
                movie['link'] = a.get('href')
               # movie['name'] = a.find('img').get('alt')
                movies.append(movie)

        # STEP 2 将数据保存到 CSV 文件
            with open('movies.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['link']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(movies)

    except Exception as e:
        print("豆瓣限制了请求频率，请稍后再试！")

if __name__ == '__main__':
    # 爬取电影名称、排名、链接并保存到 CSV 文件
    crawl_douban_top250()
    print("所有信息爬取完成！")
