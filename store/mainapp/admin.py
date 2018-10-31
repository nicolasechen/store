from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'category', 'name', 'price')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')


@admin.register(BuyingOrder)
class BuyingOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'date', 'vendor')


@admin.register(Buying)
class BuyingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'buying_order', 'item', 'cost', 'qty_buy')
