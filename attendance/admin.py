from django.contrib import admin

# Register your models here.
from .models import SchoolActivity, Attendance

admin.site.register(SchoolActivity)
admin.site.register(Attendance)
