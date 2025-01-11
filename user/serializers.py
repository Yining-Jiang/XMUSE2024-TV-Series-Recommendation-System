"""
@time: 2020-06-04 11:10
@author: colaplusice
@contact: fjl2401@163.com vx:18340071291
"""
from rest_framework import serializers

from user.models import Teleplay


class TeleplaySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Teleplay
        fields = ['image_link', 'name']
