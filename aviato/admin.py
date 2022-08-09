from django.contrib import admin

from loguru import logger as l

from .models import *
from .forms import *

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'first_name', 'username', 'role')
    search_fields = ('user_id', 'first_name', 'username', 'role')
    list_editable = ('user_id', 'first_name', 'username', 'role')
    list_filter = ('id', 'user_id', 'first_name', 'username', 'role')

    def get_fields(self, obj, request):
        return []

class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'address', 'phone', 'price', 'time_update_location', 'product', 'user', 'status', 'driver', 'location')
    search_fields = ['id', 'note', 'address', 'phone', 'price', 'time_update_location', 'product', 'user__first_name', 'status', 'location']
    # list_editable = ('note', 'address', 'phone', 'price', 'product', 'user', 'status', 'driver', "location")
    list_filter = ('id', 'note', 'phone', 'price', 'time_update_location', 'product', 'user', 'status', 'driver', 'location')

    def get_fields(self, request, obj):
        return ["note", "address", "product", "price", "phone", "photo", "status"]

    def save_model(self, request, obj, form, change):
        obj.user = Profile.objects.all().first()
        obj.save()

class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'active_user', 'code', 'role')
    search_fields = ('id', 'code', 'role')
    list_editable = ('user', 'active_user', 'code', 'role')
    list_filter = ('id', 'user', 'active_user', 'code', 'role')

    def get_fields(self, request, obj):
        return ["code", "role"]

    def save_model(self, request, obj, form, change):
        obj.user = Profile.objects.all().first()
        obj.save()


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Applications, ApplicationsAdmin)
admin.site.register(RoleCode, RoleAdmin)

