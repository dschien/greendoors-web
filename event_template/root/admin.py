__author__ = 'schien'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# @todo check name substition

#from <%= name %>.models import Scan, Measure, InstalledMeasure, MeasureCategory, App, Favourite, House, Note,     HomeOwnerProfile,     BackboneRouteEvent


class InstalledMeasureInline(admin.StackedInline):
    model = InstalledMeasure
    can_delete = False
    verbose_name_plural = 'House'


class HouseAdmin(admin.ModelAdmin):
    inlines = (InstalledMeasureInline,)


admin.site.register(House, HouseAdmin)


class HouseInline(admin.StackedInline):
    model = House
    can_delete = False
    verbose_name_plural = 'House'


class CreatedDateAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_filter = ('user', 'created')


admin.site.register(Scan, CreatedDateAdmin)
admin.site.register(Note, CreatedDateAdmin)


class ScanInline(admin.StackedInline):
    model = Scan
    extra = 0


class NoteInline(admin.StackedInline):
    model = Note
    extra = 0


class FavouriteInline(admin.StackedInline):
    model = Favourite
    extra = 0


class HomeOwnerProfileInline(admin.StackedInline):
    model = HomeOwnerProfile
    can_delete = False
    verbose_name_plural = 'Home Owners'
    extra = 0

# admin.site.register(Measure)
admin.site.register(HomeOwnerProfile)
admin.site.register(InstalledMeasure)
# admin.site.register(MeasureCategory)
admin.site.register(App)
admin.site.register(BackboneRouteEvent)
admin.site.register(Measure)
admin.site.register(MeasureCategory)
