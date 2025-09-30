from django.contrib import admin
from .models import Pack, Liquidity


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ["pack_name", "collection_name", "contributor", "floor_price"]


@admin.register(Liquidity)
class LiquidityAdmin(admin.ModelAdmin):
    list_display = ["pack", "number", "link", "in_case"]
