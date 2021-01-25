from django.contrib import admin
from users import models

# Register your models here.
admin.site.register(models.UserInfo)
admin.site.register(models.Menu_Level_One)
admin.site.register(models.Menu_Level_Two)