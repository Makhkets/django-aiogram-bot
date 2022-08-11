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
    list_display = ('id', 'create_time', 'product', 'address', 'price',
                    'phone', 'status', 'note',
                    'driver', 'location', "delivery_information", 'bool_status', 'user')
    search_fields = ['id', 'note', 'address', 'phone', 'price',
                     'time_update_location', 'product',
                     'user__first_name', 'status', 'location']
    # list_editable = ('note', 'address', 'phone', 'price', 'product', 'user', 'status', 'driver', "location")
    list_filter = ('phone', 'time_update_location', 'status',
                   'driver')

    def get_fields(self, request, obj):
        return ["note", "address", "product", "price", "phone", "status", "bool_status"]

    def save_model(self, request, obj, form, change):
        obj.user = Profile.objects.all().first()
        obj.save()


class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'count', 'opt_price', "product_suum", "product_percent", 'availability')
    search_fields = ['id', 'product', 'count', 'opt_price', 'availability']
    list_filter = ('availability',)
    list_editable = ('product', 'opt_price', 'count', 'product_suum')

    def get_fields(self, request, obj):
        return ['product', 'count', 'opt_price', 'photo', "availability"]

    def save_model(self, request, obj, form, change):

        if obj.fake_count <= obj.count:
            obj.fake_count = obj.count

        obj.product_suum = obj.opt_price * obj.fake_count
        obj.product_percent = ((obj.opt_price * obj.fake_count) // 100) * 2.5
        obj.product = obj.product.lower()

        if obj.fake_count == 0:
            obj.fake_count = obj.count

        if obj.count == 0:
            obj.availability = False

        if obj.count != 0:
            obj.availability = True

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
admin.site.register(Products, ProductsAdmin)
admin.site.register(RoleCode, RoleAdmin)
