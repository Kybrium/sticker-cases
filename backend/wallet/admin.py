from django.contrib import admin
from .models import Deposit, Withdrawal


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ["user", "sum", "date"]


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ["user", "liquidity", "date"]
