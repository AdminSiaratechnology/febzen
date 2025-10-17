from django.contrib import admin
from .models import Party,Company,CompanyBank

# Register your models here.

admin.site.register(Party)
admin.site.register(Company)
admin.site.register(CompanyBank)

