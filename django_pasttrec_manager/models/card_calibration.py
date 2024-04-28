import re

from django.db import models

# from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django import forms

from . import AsicBaselineSettings, AsicConfiguration, Card

class CardCalibration(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    config = models.ForeignKey(AsicConfiguration, related_name="card_config", on_delete=models.CASCADE)

    asic0 = models.OneToOneField(AsicBaselineSettings, related_name="card_asic_0", on_delete=models.CASCADE)
    asic1 = models.OneToOneField(AsicBaselineSettings, related_name="card_asic_1", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.card.febid} -- {self.config.name}"
