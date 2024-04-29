from django.db import models

from . import Card


class CardsSetup(models.Model):
    name = models.CharField(max_length=16)
    cards = models.ManyToManyField(Card)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
