from django.contrib import admin
from .models import Case, CaseItems, CaseOpen

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "current_fee", "status"]

@admin.register(CaseItems)
class CaseItemsAdmin(admin.ModelAdmin):
    list_display = ["case", "pack", "chance"]

@admin.register(CaseOpen)
class CaseOpenAdmin(admin.ModelAdmin):
    list_display = ["user", "case", "drop", "open_data"]
