
# 电视剧推荐系统

## 〇、小组成员

| 姓名   | 学号           |
| ------ | -------------- |
| 蒋怡宁 | 22920212204109 |
| 张瑞龙 | 22920212204294 |
| 朱睿瑞 | 22920212204335 |
| 董梅   | 36720212204617 |

## 一、项目简介

本项目是基于 Django 框架的电视剧推荐系统，实现了用户注册登录、管理员后台管理、基于协同过滤的电视剧推荐、电视剧评分等功能。

## 二、技术方案

- 前端: Bootstrap 3 CSS 框架
- 后端: Django 2.2.1 + SQlite3 数据库(MVC 框架)
- 数据集: 豆瓣 TOP250(用 Python 异步爬虫)
- 推荐算法: 协同过滤

## 三、安装运行

### 3.1 安装依赖

1. 项目运行环境: 测试在 Python 3.8 可正常运行，其他版本未测试
2. 使用 pip 安装依赖: `pip install -r requirements.txt`

### 3.2 运行

1. 运行服务器: `python manage.py runserver`
2. 创建超级管理员: `python manage.py createsuperuser`
3. 进入后台: 127.0.0.1:8000/admin
4. 电视剧推荐系统: 127.0.0.1

注: 若为普通用户，则通过 Web 界面注册。


## 四、实现功能

1. 用户的登录、注册功能
2. 管理员对用户账号、电视剧等的后台管理系统
2. 电视剧分类功能 
3. 基于协同过滤的浏览最多、评分最多、收藏最多的电视剧推荐
5. 基于协同过滤的"猜你喜欢"的个性化推荐

## 五、数据库模型

- `class User(models.Model)`: 主要实现了用户的登录，注册和管理功能
- `class Tags(models.Model)`: 用来实现电视剧的分类，比如喜剧类，玄幻类
- `class UserTagPrefer(models.Model)`: 用来处理冷启动和更新用户对电视剧分类的偏好程度
- `class Teleplay(models.Model)`: 电视剧模型，用来描述电视剧的信息，比如上映年代，电视剧名称之类的
- `class Rate(models.Model)`: 用来记录用户的打分数据。
- `class Comment(models.Model)`: 用来记录用户对电视剧的评论.
- `class LikeComment(models.Model)`: 用来记录其他用户对评论的点赞

## 六、协同过滤

协同过滤分析用户兴趣，在用户群中找到指定用户的相似（兴趣）用户，综合这些相似用户对某一信息的评价，形成系统对该指定用户对此信息的喜好程度预测。

注: 如果用户未评分、用户数量不足或推荐数目不够 15 条，会从所有未打分的电视剧中按照浏览数降序选择填充。

### 6.1 基于用户的推荐

1. 通过要推荐的用户对电视剧的评分，利用皮尔逊相关系数计算与其他用户之间的相似度。
2. 最近邻搜索，找到相似度最高的最近的 N 个用户。
3. 将这些用户中评分高且要推荐的用户未看过的的电视剧推荐给该用户。

### 6.2 基于项目的推荐

1. 计算电视剧的相似度矩阵。
2. 基于要推荐的用户已评分的电视剧，得到未评分的电视剧的相似度。
3. 将这些电视剧按相似度降序推荐给该用户。

## 七、各文件功能

1. `crawler/`: 存放异步爬虫代码和爬取得到的链接和详细信息等数据。
2. `csv_data/`: 数据处理代码。
3. `media/`: 存放静态文件，爬取得到的电视剧的海报。
4. `populate_data`: 存放数据库相关代码，如清空数据库、填空电视剧数据到数据库和随机生成用户评分等。
5. `static/`: 存放 CSS 和 JavaScript 文件。
6. `teleplay/`: Django 的默认 app，负责设置的配置、url 路由和部署等功能。
7. `user/`: 存放程序的各种代码:
  - `user/migrations`: 自动生成的数据库迁移文件。
  - `user/templates`: 前端页面模板文件。
  - `user/admins.py`: 管理员后台代码。
  - `user/forms.py`: 前端表单代码。
  - `user/models.py`: 为数据库 orm 模型。
  - `user/serializers.py`: restful 文件。
  - `user/urls`: 路由注册文件。
  - `user/views`:  controller 模块，负责处理前端请求和与后端数据库交互。
8. `cache_keys.py`: 缓存的 key 值名称存放文件。
9. `db.sqlite3`: 数据库文件。
10. `manage.py`: 电视剧推荐系统运行的主程序，从这里启动。
11. `recommend_teleplays.py:` 推荐算法协同过滤代码。




**附**依赖包(requirements.txt):
```text
Django  2.2.10
PySocks 1.7.1
aiohttp 3.9.1  
aiosignal   1.3.1
async-timeout   4.0.3  
attrs   23.1.0
beautifulsoup4  4.12.2
bs4 0.0.1  
certifi 2023.11.17
cffi    1.16.0 
charset-normalizer  3.3.2
django-simpleui 2.1    
djangorestframework 3.9.1
exceptiongroup  1.2.0  
frozenlist  1.4.1
h11 0.14.0
idna    3.6    
multidict   6.0.4  
numpy   1.24.4 
outcome 1.3.0.post0
pandas  2.0.3  
pip 23.2.1
pycparser   2.21
python-dateutil 2.8.2  
pytz    2023.3.post1
requests    2.31.0
selenium    3.141.0    
setuptools  68.2.0 
six 1.16.0
sniffio 1.3.0
sortedcontainers    2.4.0  
soupsieve   2.5    
sqlparse    0.4.4
trio    0.23.2 
trio-websocket  0.11.1
tzdata  2023.3 
urllib3 1.26.2 
wheel   0.41.2
wsproto 1.2.0
yarl    1.9.4  
```
