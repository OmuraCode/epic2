from django.contrib import admin

# Register your models here.
from django.contrib import admin
from account.models import CustomUser
# Register your models here.

admin.site.register(CustomUser)