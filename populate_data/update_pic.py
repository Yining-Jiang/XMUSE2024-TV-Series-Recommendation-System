import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user.settings")

django.setup()

base_dir = '../media/teleplay_cover'
files = os.listdir(base_dir)
from populate_data.populate_teleplays import replace_special_char

for file in files:
    os.rename(os.path.join(base_dir, file), os.path.join(base_dir, replace_special_char(file)))

# from user.models import Teleplay
#
# teleplays = Teleplay.objects.all()
# for user in teleplays:
#     user.image_link = replace_special_char(str(user.image_link))
#     # user.pic.file.name=user.pic.file.name.replac
#     # user.pic=user.pic.replace(' ','_')
#     user.save()
