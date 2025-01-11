# coding=utf-8

import operator
import os
from collections import defaultdict

from django.db.models import Q

os.environ["DJANGO_SETTINGS_MODULE"] = "teleplay.settings"
import django

django.setup()
from user.models import *

# 物品特征表示
# 计算每个电影的排名，根据电影的平均分
def type_rank_map():
    """
    计算每类电影排名
    :return: map{'type':[(teleplay_id,平均评分,评分人数),...],...}
    """
    map = {}
    # 获取到所有的标签
    type_list = Tags.objects.all()
    # 创建一个dict 内容为元组 {tag_id: [(teleplay_id,avg_rate,count)]}
    for t in type_list:
        map[t.id] = []
    teleplays = Teleplay.objects.all()
    for teleplay in teleplays:
        # print('正在处理电影', teleplay)
        # 给该图书打分的人数
        count = int(teleplay.rate_set.count())
        # 该书本平均分
        avg_rate = teleplay.rate_set.all().aggregate(Avg('mark'))['mark__avg']
        tags = teleplay.tags.all()
        for t in tags:
            if avg_rate is not None:
                # 倒排，将该书本平均分，评分数，反向添加到所有的标签中，
                map[t.id].append((teleplay.id, avg_rate, count))
    # 排序，先根据评分高的优先，评分相同则评分人数多的优先
    for t in type_list:
        temp = map[t.id]
        # 根据评分和人数来排序
        temp.sort(key=lambda val: (val[1], val[2]), reverse=True)
        map[t.id] = temp
    return map

# 用户特征表示
# 构建用户偏好矩阵 每个用户对标签的喜爱程度
def get_user_favor_matrix():
    """
    构造用户偏好矩阵 {user_id: {tag_id: weight }}
    :return: [i,j]表示用户i对第j类型电影的喜爱程度
    """
    # 从数据库查找到所有的用户
    user_list = User.objects.all()
    # type_list = Tags.objects.all()
    matrix = {}
    for user in user_list:
        # 对 每个用户创建一个字典，内容为{tag_id: score}
        matrix[user.id] = defaultdict(int)
        # weight = 0
        # 获取到该用户的所有评分
        ratings = user.rate_set.all()
        for rating in ratings:
            # 该评分对应书籍的所有标签
            tags = rating.teleplay.tags.all()
            for t in tags:
                matrix[user.id][t.id] += rating.mark
                # weight += rating.mark
        print('finish init user', user.id)
    return matrix


# if os.path.exists('user_favor_matrix.pickle'):
#     print('load user_favor_matrix from cache !')
#     user_favor_matrix = pickle.load(open('user_favor_matrix.pickle', 'rb'))
# else:
user_favor_matrix = get_user_favor_matrix()
#     pickle.dump(user_favor_matrix, open('user_favor_matrix.pickle', 'wb'))
#
# if os.path.exists('type_rank_map.pickle'):
#     print('load type_rank_map from cache !')
#     type_rank_map = pickle.load(open('type_rank_map.pickle', 'rb'))
# else:
type_rank_map = type_rank_map()


#     pickle.dump(type_rank_map, open('type_rank_map.pickle', 'wb'))


def update_user_matrix(user_id, tags, mark):
    if user_favor_matrix.get(user_id) is None:
        user_favor_matrix[user_id] = defaultdict(int)
    for tag in tags:
        user_favor_matrix[user_id][tag.id] += mark
    # print(user_favor_matrix.keys())
    print('update user_matrix finished')


def recommend_by_content(user_id, rec_item=15):
    # 用户最喜欢的标签
    favors = user_favor_matrix.get(user_id)
    # 找出该用户未看过的15个书籍，做随机推荐
    rand_teleplays = Teleplay.objects.filter(~Q(rate__user_id=user_id)).order_by("?")[:15]
    rand_teleplays = list(rand_teleplays)
    # 如果该用户没有任何打分数据，随机推荐
    if favors is None or len(favors) == 0:
        user_favor_matrix[user_id] = defaultdict(int)
        return rand_teleplays
    # 获取用户的所有评分
    rated_teleplays = User.objects.get(id=user_id).rate_set.all().values_list('teleplay_id')
    rated_teleplays = [rated_teleplay[0] for rated_teleplay in rated_teleplays]
    # 按照权重排序，即该用户喜欢的所有标签，按照权重排序
    sorted(favors.items(), key=operator.itemgetter(1), reverse=True)
    candidate = []
    # favor: 喜欢的3个标签
    for favor in list(favors.keys())[:3]:
        # 该类标签的图书，排好序的
        teleplays = type_rank_map[favor]
        for teleplay in teleplays:
            print(teleplay)
            # 如果该书用户没有看过，添加到候选中
            if teleplay[0] not in rated_teleplays:
                candidate.append(teleplay)
    teleplays_id = [can[0] for can in candidate][:rec_item]
    teleplays = list(Teleplay.objects.filter(id__in=teleplays_id).order_by('?'))
    if len(teleplays) == 0:
        return rand_teleplays
    return teleplays


if __name__ == '__main__':
    recommend_by_content(1)
