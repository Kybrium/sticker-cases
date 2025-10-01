from django.db import models
from users.models import CustomUser
from packs.models import Pack


class Deposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sum = models.DecimalField(max_digits=20, decimal_places=3)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.wallet} {self.date}"


class Withdrawal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    liquidity = models.ForeignKey("packs.Liquidity", models.CASCADE, null=True, blank=True)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.pack} {self.date}"

    @property
    def sum(self):
        if self.liquidity and self.liquidity.pack:
            return self.liquidity.pack.floor_price
        return None
