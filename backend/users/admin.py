from django.contrib import admin
from .models import CustomUser, UserInventory, Deposit, Withdrawal

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "telegram_id", "status"]

@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ["user", "pack"]

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ["user", "wallet", "sum", "date"]

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ["user", "sum", "date"]


