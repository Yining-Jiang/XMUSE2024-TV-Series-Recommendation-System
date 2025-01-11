# coding=utf-8

# 入口函数
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "teleplay.settings"
import django

django.setup()

from user.models import *
from math import sqrt, pow
import operator
from django.db.models import Q, Count


# from django.shortcuts import render,render_to_response
class UserCf:

    # 获得初始化数据
    def __init__(self, all_user):
        self.all_user = all_user

    # 通过用户名获得商品列表，仅调试使用
    def getItems(self, username1, username2):
        return self.all_user[username1], self.all_user[username2]

    # 计算两个用户的皮尔逊相关系数
    def pearson(self, user1, user2):  # 数据格式为：商品id，浏览此
        sum_xy = 0.0  # user1,user2 每项打分的成绩的累加
        n = 0  # 公共浏览次数
        sum_x = 0.0  # user1 的打分总和
        sum_y = 0.0  # user2 的打分总和
        sumX2 = 0.0  # user1每项打分平方的累加
        sumY2 = 0.0  # user2每项打分平方的累加
        for teleplay1, score1 in user1.items():
            if teleplay1 in user2.keys():  # 计算公共的浏览次数
                n += 1
                sum_xy += score1 * user2[teleplay1]
                sum_x += score1
                sum_y += user2[teleplay1]
                sumX2 += pow(score1, 2)
                sumY2 += pow(user2[teleplay1], 2)
        if n == 0:
            # print("p氏距离为0")
            return 0
        molecule = sum_xy - (sum_x * sum_y) / n  # 分子
        denominator = sqrt((sumX2 - pow(sum_x, 2) / n) * (sumY2 - pow(sum_y, 2) / n))  # 分母
        if denominator == 0:
            return 0
        r = molecule / denominator
        return r

    # 计算与当前用户的距离，获得最临近的用户
    def nearest_user(self, current_user, n=1):
        distances = {}
        # 用户，相似度
        # 遍历整个数据集
        for user, rate_set in self.all_user.items():
            # 非当前的用户
            if user != current_user:
                distance = self.pearson(self.all_user[current_user], self.all_user[user])
                # 计算两个用户的相似度
                distances[user] = distance
        closest_distance = sorted(
            distances.items(), key=operator.itemgetter(1), reverse=True
        )
        # 最相似的N个用户
        # print("closest user:", closest_distance[:n])
        return closest_distance[:n]

    # 给用户推荐商品
    def recommend(self, username, n=15):
        # n代表用户数
        recommend = {}
        watched = 0
        nearest_user = self.nearest_user(username, n)
        for user, score in dict(nearest_user).items():  # 最相近的n个用户
            for teleplays, scores in self.all_user[user].items():  # 推荐的用户的商品列表
                if teleplays not in self.all_user[username].keys():  # 当前username没有看过
                    if teleplays not in recommend.keys():  # 添加到推荐列表中
                        recommend[teleplays] = scores
                        # 记录看过的数字
                else:
                    watched += 1
        precesion = watched / (watched + len(recommend.keys())/n)
        # print('this is watched', watched, precesion)
        return sorted(recommend.items(), key=operator.itemgetter(1), reverse=True), precesion


# 入口函数
def recommend_by_user_id(user_id):
    user_prefer = UserTagPrefer.objects.filter(user_id=user_id).order_by('-score').values_list('tag_id', flat=True)
    current_user = User.objects.get(id=user_id)
    # 如果当前用户没有打分 则看是否选择过标签，选过的话，就从标签中找
    # 没有的话，就按照浏览度推荐15个
    if current_user.rate_set.count() == 0:
        if len(user_prefer) != 0:
            teleplay_list = Teleplay.objects.filter(tags__in=user_prefer)[:15]
        else:
            teleplay_list = Teleplay.objects.order_by("-num")[:15]
        return teleplay_list
    # 选取评分最多的10个用户
    users_rate = Rate.objects.values('user').annotate(mark_num=Count('user')).order_by('-mark_num')
    user_ids = [user_rate['user'] for user_rate in users_rate]
    user_ids.append(user_id)
    users = User.objects.filter(id__in=user_ids)
    all_user = {}
    for user in users:
        rates = user.rate_set.all()
        rate = {}
        # 用户有给电视剧打分 在rate和all_user中进行设置
        if rates:
            for i in rates:
                rate.setdefault(str(i.teleplay.id), i.mark)
            all_user.setdefault(user.username, rate)
        else:
            # 用户没有为电视剧打过分，设为0
            all_user.setdefault(user.username, {})
    user_cf = UserCf(all_user=all_user)
    recommend_list, percision = user_cf.recommend(current_user.username, 15)
    good_list = [each[0] for each in recommend_list]
    teleplay_list = list(Teleplay.objects.filter(id__in=good_list).order_by("-num")[:15])
    other_length = 15 - len(teleplay_list)
    if other_length > 0:
        fix_list = Teleplay.objects.filter(~Q(rate__user_id=user_id)).order_by('-collect')
        for fix in fix_list:
            if fix not in teleplay_list:
                teleplay_list.append(fix)
            if len(teleplay_list) >= 15:
                break
    return teleplay_list, percision


user_ids = User.objects.all().values('id')
user_ids = list(map(lambda x: x['id'], user_ids))

max_precision = 0
min_precision = 0
user_num = len(user_ids)
print(user_num)
x1_list = []
y1_list = []

all_precision = 0
for user_id in user_ids:
    teleplay_list, precision = recommend_by_user_id(user_id)
    if precision == 0:
        user_num -= 1
        continue
    if precision > max_precision:
        max_precision = precision
    if precision < min_precision:
        min_precision = precision
    print('user id: precision: ', user_id, precision)
    all_precision += precision

print('average precision:  max_precision:  min_precision:', all_precision / user_num)
# similarity(2003, 2008)
# recommend_by_item_id(1)
