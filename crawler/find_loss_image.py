# coding=utf-8

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teleplay.settings")
import django

django.setup()
from user.models import Teleplay

teleplays = Teleplay.objects.all()
all_images=os.listdir('../media/teleplay_cover')
print(all_images[:3])
for teleplay in teleplays:
    s=str(teleplay.image_link.name).split('/')[-1]
    print(s)
    all_images.remove(s)
    # if not os.path.exists('../media/' + str(teleplay.image_link)):
    #     print(teleplay.image_link)

print(all_images)