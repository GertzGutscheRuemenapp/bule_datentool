from django.contrib import admin
from .models import (DemandRateSet, DemandRate)

# Register your models here.
class DemandRateSetAdmin(admin.ModelAdmin):
    """"""


class DemandRateAdmin(admin.ModelAdmin):
    """"""

admin.site.register(DemandRateSet, DemandRateSetAdmin)
admin.site.register(DemandRate, DemandRateAdmin)
