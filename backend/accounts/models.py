from django.db import models
from django.conf import settings

class TelegramAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram")
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, default="")
    first_name = models.CharField(max_length=255, blank=True, default="")
    last_name = models.CharField(max_length=255, blank=True, default="")
    photo_url = models.URLField(blank=True, default="")
    auth_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.telegram_id} -> {self.user}"