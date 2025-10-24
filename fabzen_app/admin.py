from django.contrib import admin
from .models import Party,Company,CompanyBank,Fabric,Size,Garment,Process,Machine

# Register your models here.

admin.site.register(Party)
admin.site.register(Company)
admin.site.register(CompanyBank)
admin.site.register(Fabric)
admin.site.register(Size)
admin.site.register(Garment)
admin.site.register(Process)
admin.site.register(Machine)

