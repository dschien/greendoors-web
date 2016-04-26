

__author__ = 'schien'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin import BooleanFieldListFilter

from api.models import Scan, Measure, InstalledMeasure, MeasureCategory, App, MessageThread, RedirectUrl, TrackableURL, Click, UserProfile, Favourite, \
    LoggerMessage
from api.models import Device, House, Note, HomeOwnerProfile, Message


class TrackableUrlInline(admin.StackedInline):
    model = TrackableURL
    can_delete = False
    # verbose_name_plural = 'House'


class RedirectUrlAdmin(admin.ModelAdmin):
    #inlines = (TrackableUrlInline,)
    pass


admin.site.register(RedirectUrl, RedirectUrlAdmin)
admin.site.register(TrackableURL)
admin.site.register(Click)


class InstalledMeasureInline(admin.StackedInline):
    model = InstalledMeasure
    can_delete = False
    verbose_name_plural = 'House'


class HouseAdmin(admin.ModelAdmin):
    inlines = (InstalledMeasureInline,)


admin.site.register(House, HouseAdmin)


class MessagesAdmin(admin.ModelAdmin):
    readonly_fields = ('key',)
    date_hierarchy = 'created'


admin.site.register(Message, MessagesAdmin)

admin.site.register(MessageThread)


class HouseInline(admin.StackedInline):
    model = House
    can_delete = False
    verbose_name_plural = 'House'


class CreatedDateAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_filter = ('user', 'created')


admin.site.register(Device, CreatedDateAdmin)
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

class PhoneInline(admin.StackedInline):
    model = Device
    can_delete = False
    verbose_name_plural = 'Phone'
    extra = 0


class HomeOwnerProfileInline(admin.StackedInline):
    model = HomeOwnerProfile
    can_delete = False
    verbose_name_plural = 'Home Owners'
    extra = 0

class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    can_delete = False


# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (PhoneInline, HomeOwnerProfileInline, ScanInline, NoteInline, FavouriteInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')
    list_filter = ['is_staff', 'is_superuser', 'date_joined', 'last_login', ]

# bristol
admin.site.register(Measure)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(HomeOwnerProfile)
admin.site.register(InstalledMeasure)
admin.site.register(MeasureCategory)
admin.site.register(App)
admin.site.register(LoggerMessage)

# frome


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)