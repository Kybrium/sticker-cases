from django.db import models
from enum import StrEnum, auto


class CaseStatus(StrEnum):
    ACTIVE = auto()  # доступный к крутке
    INACTIVE = auto()  # не доступный
    OUT_OF_STICKERS = auto()  # закончилась ликвидность

    @classmethod
    def choices(cls):
        results = []

        for element in cls:
            _element = (element.value, element.name.replace("_", " ").lower().capitalize())
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

    # TODO: сделать метод который возвращает True/False есть ли в нем ликвидность. Если False, статус переходит в OUT_OF_STICKERS

    def __str__(self):
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
    open_data = models.DateTimeField()
