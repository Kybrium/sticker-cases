from django.db import models
from users.models import CustomUser


class Deposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sum = models.DecimalField(max_digits=20, decimal_places=3)
    date = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.user} {self.date}"


class Withdrawal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pack = models.ForeignKey("packs.Pack", models.CASCADE, null=True, blank=True)
    date = models.DateTimeField()
    sum = models.DecimalField(max_digits=20, decimal_places=3, default=0, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.pack} {self.date}"
