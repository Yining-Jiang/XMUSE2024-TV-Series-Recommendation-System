import os

os.environ["DJANGO_SETTINGS_MODULE"] = "teleplay.settings"
import django

django.setup()
from user.models import *
from math import sqrt, pow
import operator
from django.db.models import Q, Count, Subquery
from collections import defaultdict
import pickle


# 计算相似度
def similarity(teleplay1_id, teleplay2_id):
    teleplay1_set = Rate.objects.filter(teleplay_id=teleplay1_id)
    # teleplay1的打分用户数
    teleplay1_sum = teleplay1_set.count()
    # teleplay_2的打分用户数
    teleplay2_sum = Rate.objects.filter(teleplay_id=teleplay2_id).count()
    # 两者的交集
    common = Rate.objects.filter(user_id__in=Subquery(teleplay1_set.values('user_id')), teleplay=teleplay2_id).values('user_id').count()
    # 没有人给当前电视剧打分
    if teleplay1_sum == 0 or teleplay2_sum == 0:
        return 0
    similar_value = common / sqrt(teleplay1_sum * teleplay2_sum)
    return similar_value


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
    def recommend(self, username, n=3):
        recommend = {}
        nearest_user = self.nearest_user(username, n)
        for user, score in dict(nearest_user).items():  # 最相近的n个用户
            for teleplays, scores in self.all_user[user].items():  # 推荐的用户的商品列表
                if teleplays not in self.all_user[username].keys():  # 当前username没有看过
                    if teleplays not in recommend.keys():  # 添加到推荐列表中
                        recommend[teleplays] = scores
        # 对推荐的结果按照商品浏览次数排序
        return sorted(recommend.items(), key=operator.itemgetter(1), reverse=True)

    # 某个用户给电视剧打分后，更新all_user dict
    def update_all_user(self, user):
        rates = user.rate_set.all()
        rate = {}
        # 用户有给电视剧打分 在rate和all_user中进行设置
        if rates:
            for i in rates:
                rate.setdefault(str(i.teleplay.id), i.mark)
        all_user.setdefault(user.username, rate)


def get_all_user():
    all_user = {}
    users_rate = Rate.objects.values('user').annotate(mark_num=Count('user')).order_by('-mark_num')
    user_ids = [user_rate['user'] for user_rate in users_rate]
    # user_ids.append(user_id)
    users = User.objects.filter(id__in=user_ids)
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
    print('user_recommend initial finished')
    return all_user


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
    import random
    recommend_list = [each[0] for each in user_cf.recommend(current_user.username, 15)]
    teleplay_list = list(Teleplay.objects.filter(id__in=recommend_list))[:15]
    random.shuffle(teleplay_list)
    other_length = 15 - len(teleplay_list)
    if other_length > 0:
        fix_list = Teleplay.objects.filter(~Q(rate__user_id=user_id)).order_by('-num')
        for fix in fix_list:
            if fix not in teleplay_list:
                teleplay_list.append(fix)
            if len(teleplay_list) >= 15:
                break
    return teleplay_list


# item_based

class ItemBasedCF:
    # 初始化参数
    def __init__(self):
        # 找到相似的20部电视剧，为目标用户推荐10部电视剧
        self.n_sim_teleplay = 100
        self.n_rec_teleplay = 15

        # 用户相似度矩阵
        self.teleplay_sim_matrix = defaultdict(lambda: defaultdict(float))
        # 物品共现矩阵
        self.cooccur = defaultdict(lambda: defaultdict(int))
        self.teleplay_popular = defaultdict(int)
        self.teleplay_count = 0
        print('Similar user number = %d' % self.n_sim_teleplay)
        print('Recommended user number = %d' % self.n_rec_teleplay)
        self.calc_teleplay_sim()

    # 计算电视剧之间的相似度
    def calc_teleplay_sim(self):
        model_path = 'item_rec.pkl'
        # 已有的话，就不重新计算
        # try:
        # 重新计算
        # except FileNotFoundError:
        users = User.objects.all()
        for user in users:
            teleplays = Rate.objects.filter(user=user).values_list('teleplay_id', flat=True)
            for teleplay in teleplays:
                self.teleplay_popular[teleplay] += 1
        self.teleplay_count = len(self.teleplay_popular)
        print("Total user number = %d" % self.teleplay_count)
        for user in users:
            teleplays = Rate.objects.filter(user=user).values_list('teleplay_id', flat=True)
            for m1 in teleplays:
                for m2 in teleplays:
                    if m1 == m2:
                        continue
                    self.cooccur[m1][m2] += 1
                    # self.teleplay_sim_matrix[m1][m2] += 1
        print("Build co-rated users matrix success!")
        # 计算电视剧之间的相似性
        print("Calculating user similarity matrix ...")
        for m1, related_teleplays in self.cooccur.items():
            for m2, count in related_teleplays.items():
                # 注意0向量的处理，即某电视剧的用户数为0
                if self.teleplay_popular[m1] == 0 or self.teleplay_popular[m2] == 0:
                    self.teleplay_sim_matrix[m1][m2] = 0
                else:
                    # 根据公式计算w[i][j]
                    self.teleplay_sim_matrix[m1][m2] = count / sqrt(self.teleplay_popular[m1] * self.teleplay_popular[m2])
                    print('Calculate user similarity matrix success!')
        # 保存模型
        with open(model_path, 'wb')as opener:
            pickle.dump(dict(self.teleplay_sim_matrix), opener)
        print('保存模型成功!')

    # 针对目标用户U，找到K部相似的电视剧，并推荐其N部电视剧
    def recommend(self, user_id):
        K = self.n_sim_teleplay
        N = self.n_rec_teleplay
        rank = defaultdict(int)
        # user = User.objects.get(id=user_id)
        watched_teleplays = Rate.objects.filter(user_id=user_id).values_list('teleplay_id', 'mark')
        print('this is watched teleplays', watched_teleplays)
        watched_ids = [w[0] for w in watched_teleplays]
        try:
            for teleplay, rating in watched_teleplays:
                for related_teleplay, w in sorted(self.teleplay_sim_matrix[teleplay].items(), key=operator.itemgetter(1), reverse=True)[:K]:
                    # print('this is related', related_teleplay)
                    if related_teleplay in watched_ids:
                        continue
                    rank[related_teleplay] += w * float(rating)
        except KeyError:
            self.calc_teleplay_sim()
            return self.recommend(user_id)
        return sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[:N]


# 在评分后去更新相似度矩阵
def update_item_teleplay_sim_matrix(teleplay_id, user_id):
    # 更新电视剧被喜欢的num
    item_cf.teleplay_popular[teleplay_id] += 1
    # 更新teleplay_sim_matrix
    teleplays = Rate.objects.filter(user_id=user_id).values_list('teleplay_id', flat=True)
    for m1 in teleplays:
        if m1 == teleplay_id:
            continue
        #     更新共现矩阵
        item_cf.cooccur[m1][teleplay_id] += 1
        item_cf.cooccur[teleplay_id][m1] += 1
    # 重新计算相似度矩阵
    for teleplay1_id, count in item_cf.cooccur[teleplay_id].items():
        if item_cf.teleplay_popular[teleplay1_id] == 0 or item_cf.teleplay_popular[teleplay_id] == 0:
            item_cf.teleplay_sim_matrix[teleplay_id][teleplay1_id] = 0
        else:
            # 根据公式计算w[i][j]
            # 更新相似度矩阵
            value = count / sqrt(item_cf.teleplay_popular[teleplay1_id] * item_cf.teleplay_popular[teleplay_id])
            item_cf.teleplay_sim_matrix[teleplay1_id][teleplay_id] = value
            item_cf.teleplay_sim_matrix[teleplay_id][teleplay1_id] = value
            print('update user similarity matrix success!')

    # 在更新完成后重新写入本地
    with open('item_rec.pkl', 'wb')as opener:
        pickle.dump(dict(item_cf.teleplay_sim_matrix), opener)
    print('保存更新成功!')


#
def recommend_by_item_id(user_id, k=15):
    # 前三的tag
    user_prefer = UserTagPrefer.objects.filter(user_id=user_id).order_by('-score').values_list('tag_id', flat=True)
    user_prefer = list(user_prefer)[:3]
    current_user = User.objects.get(id=user_id)
    # 如果当前用户没有打分 则看是否选择过标签，选过的话，就从标签中找
    # 没有的话，就按照浏览度推荐15个
    if current_user.rate_set.count() == 0:
        if len(user_prefer) != 0:
            teleplay_list = Teleplay.objects.filter(tags__in=user_prefer)[:15]
        else:
            teleplay_list = Teleplay.objects.order_by("-num")[:15]
        print('from here')
        return teleplay_list
    # most_tags = Tags.objects.annotate(tags_sum=Count('name')).order_by('-tags_sum').filter(teleplay__rate__user_id=user_id).order_by('-tags_sum')
    # 选用户最喜欢的标签中的电视剧，用户没看过的30部，对这30部电视剧，计算距离最近
    un_watched = Teleplay.objects.filter(~Q(rate__user_id=user_id), tags__in=user_prefer).order_by('?')[:30]  # 看过的电视剧
    watched = Rate.objects.filter(user_id=user_id).values_list('teleplay_id', 'mark')
    distances = []
    names = []
    # 在未看过的电视剧中找到
    # 后续改进，选择top15
    for un_watched_teleplay in un_watched:
        for watched_teleplay in watched:
            if un_watched_teleplay not in names:
                names.append(un_watched_teleplay)
                distances.append((similarity(un_watched_teleplay.id, watched_teleplay[0]) * watched_teleplay[1], un_watched_teleplay))
    distances.sort(key=lambda x: x[0], reverse=True)
    print('this is distances', distances[:15])
    recommend_list = []
    for mark, teleplay in distances:
        if len(recommend_list) >= k:
            break
        if teleplay not in recommend_list:
            recommend_list.append(teleplay)
    # print('this is recommend list', recommend_list)
    # 如果得不到有效数量的推荐 按照未看过的电视剧中的热度进行填充
    print('recommend list', recommend_list)
    return recommend_list


all_user = get_all_user()
user_cf = UserCf(all_user=all_user)
item_cf = ItemBasedCF()
