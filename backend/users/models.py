from django.db import models
from enum import StrEnum, auto
from django.contrib.auth.models import AbstractUser, Group, Permission


class UserStatus(StrEnum):
    ALIVE = auto()  # бот доступный юзеру все ок
    BLOCKED_BOT = auto()  # юзер блокнул бота
    DELETED = auto()  # акк юзера удален
    ADMIN = auto()  # если регнулся через админку

    @classmethod
    def choices(cls):
        results = []

        for element in cls:
            _element = (element.value, element.name.replace("_", " ").lower().capitalize())
            results.append(_element)

        return results


class CustomUser(AbstractUser):
    class Meta:
        db_table = "User"

    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    status = models.CharField(max_length=50, choices=UserStatus.choices(), default=UserStatus.ALIVE)
    language = models.CharField(max_length=10, blank=True, null=True)
    is_bot = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=20, decimal_places=3, default=0, blank=True, null=True)
    wallet = models.TextField(blank=True, null=True)
    wallet_connection_date = models.DateTimeField(blank=True, null=True)
    image_url = models.ImageField(upload_to="users/", default="users/plug.png")
    groups = models.ManyToManyField(
        Group, blank=True,
        related_name='customuser_groups',
        related_query_name='customuser',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission, blank=True,
        related_name='customuser_permissions',
        related_query_name='customuser_perm',
        verbose_name='user permissions'
    )

    def save(self, *args, **kwargs):
        if self.is_staff or self.is_superuser:
            self.status = UserStatus.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class UserInventory(models.Model):
    class Meta:
        db_table = "UserInventory"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    liquidity = models.ForeignKey("packs.Liquidity", models.CASCADE, null=True, blank=True)
