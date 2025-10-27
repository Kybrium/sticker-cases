from django.utils import timezone
from users.models import CustomUser
from packs.models import Liquidity
from users.models import CustomUser

from django.db import models


class Roulette(models.Model):
    class Meta:
        db_table = "roulette"

    ticket_price = models.DecimalField(max_digits=20, decimal_places=3, default=0)
    time_to_bet = models.IntegerField(default=30)
    bet_in_ton = models.BooleanField(default=True)
    bet_in_nft = models.BooleanField(default=True)
    ton_fee = models.DecimalField(max_digits=5, decimal_places=3, default=0.2)

    total_bet = models.DecimalField(max_digits=20, decimal_places=3, default=0)
    total_free_tickets = models.BigIntegerField(default=0)
    total_paid_tickets = models.BigIntegerField(default=0)
    total_sum_paid_tickets = models.DecimalField(max_digits=20, decimal_places=3, default=0)

    def __str__(self):
        return f"Base Roulette"


class Round(models.Model):
    class Meta:
        db_table = "round"

    roulette = models.ForeignKey(Roulette, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    executed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    secret_hash = models.CharField(max_length=64, null=True, blank=True)
    secret = models.CharField(max_length=64, null=True, blank=True)


def __str__(self):
    return f"Round #{self.id} of Roulette #{self.roulette.id}"


class BaseBet(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['round', 'user']),
        ]


class TonBet(BaseBet):
    amount = models.DecimalField(max_digits=20, decimal_places=3)

    class Meta(BaseBet.Meta):
        db_table = "ton_bet"

    def __str__(self):
        return f"TonBet #{self.id} by {self.user}"


class NFTBet(BaseBet):
    liquidity = models.ForeignKey(Liquidity, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta(BaseBet.Meta):
        db_table = "nft_bet"

    def __str__(self):
        return f"NFTBet #{self.id} by {self.user}"


class RoundResult(models.Model):
    class Meta:
        db_table = "round_result"

    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    winner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sum = models.DecimalField(max_digits=20, decimal_places=3)
    meta_data = models.JSONField(default=dict)

    def __str__(self):
        return f"Result for Round #{self.round.id}, Winner: {self.winner}"


class TicketUsage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'round')  # билет можно потратить только один раз за раунд
