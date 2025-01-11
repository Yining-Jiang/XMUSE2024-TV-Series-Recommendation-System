import ast
import datetime
import os

import django

# 将top250数据写入数据库

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teleplay.settings")

django.setup()

import csv
import re
from user.models import Tags, Teleplay
from populate_data.clear_teleplays import clear_teleplay_tags


# ss = '1994-09-10(多伦多电视剧节)'
def parse_time(time_str):
    time = time_str.split('-')
    years = time[0]
    if len(time) > 1:
        month = time[1]
    else:
        month = 1
    if len(time) > 2:
        day = time[2]
    else:
        day = 1
    time = datetime.date(int(years), int(month), int(day))

    return str(time)


def replace_special_char(name):
    special_char = r'[\\/:*?#@！%!"<>|：\s]'
    return re.sub(special_char, '_', name)


def populate_teleplays(filename):
    opener = open(filename, 'r', encoding='utf8')
    reader = csv.reader(opener)
    next(reader)
    for line in reader:
        id, title, image_link, country, years, director_description, leader, star, description, tags, imdb, language, time_length = line

        origin_years = years
        # 数据清洗
        years = re.search(pattern=r'\d{4}?(-\d{0,2})?(-\d{0,2})', string=years)
        if years is None:
            years = origin_years.split('(')[0]
        else:
            years = years[0]
        res = re.match('\d*', star)
        try:
            int_d_rate_num = int(res[0]) if res else 0
        except Exception:
            int_d_rate_num = 0
        # res = re.match('[\u4e00-\u9fa5]+', title)
        # if res is not None:
        #     title = res.group()
        pic_name = 'teleplay_cover/' + image_link.split('/')[-1]
        years = parse_time(years)
        leader = '/'.join(ast.literal_eval(leader))
        # 存入数据库
        teleplay, created = Teleplay.objects.get_or_create(name=title, defaults={'image_link': pic_name, 'country': country,
                                                                           'years': parse_time(years), 'leader': leader,
                                                                           'd_rate_nums': int_d_rate_num,
                                                                           'd_rate': star, 'intro': description,
                                                                           'director': director_description,
                                                                           'imdb_link': imdb
                                                                           })
        if not created:
            print('重复 电视剧', teleplay)

        tags = [tag.strip() for tag in tags.split('/')]
        for tag in tags:
            tag_obj, created = Tags.objects.get_or_create(name=tag)
            teleplay.tags.add(tag_obj.id)
    #


if __name__ == '__main__':
    file2 = '../csv_data/all_links_details.csv'
    # 清除数据
    clear_teleplay_tags()
    populate_teleplays(file2)
