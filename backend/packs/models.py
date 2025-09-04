from django.db import models
from enum import StrEnum, auto

class PackStatus(StrEnum):
    IN_STOCK = auto()
    OUT_OF_STOCK = auto()


    @classmethod
    def choices(cls):
        results = []

        for element in cls:
            _element = (element.value, element.name.replace("_", " ").lower().capitalize())
            results.append(_element)

        return results


class Pack(models.Model):
    pack_name = models.CharField(max_length=255)
    collection_name = models.CharField(max_length=255)
    contributor = models.CharField(max_length=255)
    floor_price = models.DecimalField(max_digits=20, decimal_places=3)
    status = models.CharField(max_length=50, choices=PackStatus.choices(), default=PackStatus.OUT_OF_STOCK)
    in_stock_count = models.IntegerField(default=0)
    image_url = models.ImageField(upload_to="packs/", blank=True, null=True)
