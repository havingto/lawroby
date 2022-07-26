from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Abort)
admin.site.register(Exit)
admin.site.register(Law)
admin.site.register(Other)
admin.site.register(Direction)
admin.site.register(Reference)
admin.site.register(Choice)
admin.site.register(Comment)
admin.site.register(Question)
admin.site.register(Dependency)
