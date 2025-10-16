from django.contrib import admin
from .models import Party,Company,CompanyContact,CompanyRegistraionDetails,CompanyBank

# Register your models here.

admin.site.register(Party)
admin.site.register(Company)
admin.site.register(CompanyContact)
admin.site.register(CompanyRegistraionDetails)
admin.site.register(CompanyBank)

