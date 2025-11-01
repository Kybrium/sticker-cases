from typing import Any

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models import QuerySet
from packs.models import Liquidity


class CustomUser(AbstractUser):
    class Meta:
        db_table = "User"

    username = models.CharField(max_length=32, unique=True, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True)
    is_bot = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=20, decimal_places=3, default=0, blank=True, null=True)
    wallet = models.TextField(blank=True, null=True)
    wallet_connection_date = models.DateTimeField(blank=True, null=True)
    tickets = models.IntegerField(default=0)
    image_url = models.URLField(
        max_length=500,
        default="https://stickercasebucket.s3.eu-north-1.amazonaws.com/users/plug.png"
    )
    groups = models.ManyToManyField(  # type: ignore[assignment]
        Group,
        blank=True,
        related_name="customuser_groups",
        related_query_name="customuser",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(  # type: ignore[assignment]
        Permission,
        blank=True,
        related_name="customuser_permissions",
        related_query_name="customuser_perm",
        verbose_name="user permissions",
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username

    @property
    def get_liquidity(self) -> QuerySet[Liquidity, Liquidity]:
        return Liquidity.objects.filter(userinventory__user=self)


class UserInventory(models.Model):
    class Meta:
        db_table = "UserInventory"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    liquidity = models.ForeignKey("packs.Liquidity", models.CASCADE, null=True, blank=True)
