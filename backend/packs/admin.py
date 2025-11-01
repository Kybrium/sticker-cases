from django.contrib import admin

from .models import Liquidity, Pack, UserInventory


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ["pack_name", "collection_name", "contributor", "price", "id"]


@admin.register(Liquidity)
class LiquidityAdmin(admin.ModelAdmin):
    list_display = ["pack", "number", "link", "free", "id"]


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ["user", "liquidity"]
