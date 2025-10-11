from django.contrib import admin
from .models import Upgrade


@admin.register(Upgrade)
class UpgradeAdmin(admin.ModelAdmin):
    list_display = ["user", "bet", "success", "drop", "date"]

# user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
#    bet = models.ForeignKey("packs.Pack", on_delete=models.CASCADE, related_name="upgrade_as_bet")
#    success = models.BooleanField()
#    drop = models.ForeignKey("packs.Pack", on_delete=models.SET_NULL, null=True, blank=True,
#                             related_name="upgrade_as_drop")
#    date = models.DateTimeField()
