from django.contrib import admin

from .models import CustomUser, UserInventory


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "telegram_id"]


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ["user", "liquidity"]
