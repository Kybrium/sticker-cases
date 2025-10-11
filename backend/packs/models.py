from django.db import models


class Pack(models.Model):
    class Meta:
        db_table = "Pack"

    pack_name = models.CharField(max_length=255)
    collection_name = models.CharField(max_length=255)
    contributor = models.CharField(max_length=255)
    floor_price = models.DecimalField(max_digits=20, decimal_places=3)
    image_url = models.URLField(
        max_length=500,
        default="https://stickercasebucket.s3.eu-north-1.amazonaws.com/packs/plug.png"
    )

    def __str__(self) -> str:
        return f"{self.pack_name} {self.collection_name}"

    @property
    def liquidity_count(self) -> int:
        return self.liquidity_set.count()


class Liquidity(models.Model):
    class Meta:
        db_table = "Liquidity"

    pack = models.ForeignKey(Pack, models.CASCADE)
    number = models.IntegerField(null=False, blank=False)
    nft_address = models.TextField()
    link = models.URLField(default="https://getgems.io/")
    free = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.id}. {self.pack} {self.number}"


class PackSell(models.Model):
    class Meta:
        db_table = "PackSell"

    liquidity = models.ForeignKey("packs.Liquidity", models.CASCADE, null=True, blank=True)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    date = models.DateTimeField()

    @property
    def price(self) -> float | None:
        if self.liquidity and self.liquidity.pack:
            return float(self.liquidity.pack.floor_price)
        return None
