from django.db import models
from enum import StrEnum, auto


class CaseStatus(StrEnum):
    ACTIVE = auto() # доступный к крутке
    INACTIVE = auto() # не доступный
    OUT_OF_STICKERS = auto() # закончилась ликвидность

    @classmethod
    def choices(cls):
        results = []

        for element in cls:
            _element = (element.value, element.name.replace("_", " ").lower().capitalize())
            results.append(_element)

        return results


class Case(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=20, decimal_places=3)
    current_fee = models.FloatField()
    base_fee = models.FloatField(default=20.0)
    status = models.CharField(max_length=50, choices=CaseStatus.choices(), default=CaseStatus.INACTIVE)
    image_url = models.ImageField(upload_to="cases/", blank=True, null=True)


class CaseItems(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="case_items")
    pack = models.ForeignKey("packs.Pack", on_delete=models.CASCADE, related_name="packs")
    chance = models.FloatField()


class CaseOpen(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="users")
    drop = models.ForeignKey("packs.Pack", on_delete=models.SET_NULL, null=True)
    open_data = models.DateTimeField()
