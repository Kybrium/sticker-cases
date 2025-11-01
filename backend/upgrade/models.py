from django.db import models


class Upgrade(models.Model):
    class Meta:
        db_table = "Upgrade"

    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    bet = models.ForeignKey("packs.Pack", on_delete=models.CASCADE, related_name="upgrade_as_bet")
    success = models.BooleanField()
    drop = models.ForeignKey("packs.Pack", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="upgrade_as_drop")
    date = models.DateTimeField()

    @property
    def price(self) -> float | None:
        if self.bet:
            if self.success:
                if self.drop:
                    return float(self.drop.price - self.bet.price)
            return float(self.bet.price) * -1
        return None
