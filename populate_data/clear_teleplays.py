import os

import django

#
# 清空数据库中的电视剧数据和标签数据
#

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teleplay.settings")

django.setup()

from user.models import Teleplay, Tags


def clear_teleplay_tags():
    Teleplay.objects.all().delete()
    Tags.objects.all().delete()
