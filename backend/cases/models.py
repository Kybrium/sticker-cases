from enum import StrEnum, auto

from django.db import models


class CaseStatus(StrEnum):
    ACTIVE = auto()  # доступный к крутке
    INACTIVE = auto()  # не доступный
    OUT_OF_STICKERS = auto()  # закончилась ликвидность

    @classmethod
    def choices(cls) -> list:
        results = []

        for element in cls:
            _element = (
                element.value,
                element.name.replace("_", " ").lower().capitalize(),
            )
            results.append(_element)

        return results


class Case(models.Model):
    class Meta:
        db_table = "Case"

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=20, decimal_places=3)
    current_fee = models.FloatField()
    base_fee = models.FloatField(default=20.0)
    status = models.CharField(max_length=50, choices=CaseStatus.choices(), default=CaseStatus.INACTIVE)
    image_url = models.ImageField(upload_to="cases/", blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class CaseItem(models.Model):
    class Meta:
        db_table = "CaseItem"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="case_item")
    pack = models.ForeignKey("packs.Pack", on_delete=models.CASCADE, related_name="packs")
    chance = models.FloatField()


class CaseLiquidity(models.Model):
    class Meta:
        db_table = "CaseLiquidity"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="case_liquidity")
    liquidity = models.ForeignKey("packs.Liquidity", models.CASCADE, null=True, blank=True)


class CaseOpen(models.Model):
    class Meta:
        db_table = "CaseOpen"

    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="users")
    drop = models.ForeignKey("packs.Liquidity", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField()

    @property
    def price(self) -> float | None:
        if self.drop and self.drop.pack:
            return float(self.drop.pack.floor_price)
        return None
