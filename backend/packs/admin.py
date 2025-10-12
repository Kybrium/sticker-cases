from django.contrib import admin

from .models import Liquidity, Pack


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ["pack_name", "collection_name", "contributor", "floor_price", "id"]


@admin.register(Liquidity)
class LiquidityAdmin(admin.ModelAdmin):
    list_display = ["pack", "number", "link", "free", "id"]
