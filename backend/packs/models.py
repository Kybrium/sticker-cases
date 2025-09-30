from django.db import models
from enum import StrEnum, auto


class PackStatus(StrEnum):
    # TODO: поменять на статусы OFF_CHAIN и ON_CHAIN

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
    class Meta:
        db_table = "Pack"

    pack_name = models.CharField(max_length=255)
    collection_name = models.CharField(max_length=255)
    contributor = models.CharField(max_length=255)
    floor_price = models.DecimalField(max_digits=20, decimal_places=3)
    status = models.CharField(max_length=50, choices=PackStatus.choices(), default=PackStatus.OUT_OF_STOCK)
    image_url = models.ImageField(upload_to="packs/", blank=True, null=True)

    def __str__(self):
        return f"{self.pack_name} {self.collection_name}"

    @property
    def liquidity_count(self):
        return self.liquidity_set.count()


class Liquidity(models.Model):
    class Meta:
        db_table = "Liquidity"

    pack = models.ForeignKey(Pack, models.CASCADE)
    number = models.IntegerField(null=False, blank=False)
    link = models.URLField(default="https://getgems.io/")
    in_case = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pack} {self.number}"
