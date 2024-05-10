from django.contrib import admin
from .models import Company, UserProfile

# Register your models here.

admin.site.register(Company)
admin.site.register(UserProfile)